import os

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.vector_store import VectorStore
from pydantic import BaseModel
from app.llm import call_llm, call_llm_stream
from fastapi.responses import StreamingResponse
from app.rate_limit import check_rate_limit, get_redis


router = APIRouter(prefix="/knowledge-bases/{kb_id}", tags=["asks"])


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(kb_id: int, body: AskRequest, request: Request, db: Session = Depends(get_db)):
    # 读 RATE_LIMIT_MAX_REQ（.env 已配 60），未配置时兜底 5 次/分钟/IP；
    # 之前硬编码 5 会把 .env 的配置压住，压测/运维都没法调
    max_req = int(os.getenv("RATE_LIMIT_MAX_REQ", "5"))
    if not check_rate_limit(request.client.host, max_req=max_req, window_sec=60):
        raise HTTPException(status_code=429, detail="访问次数过多，请稍后访问")
    cache_key = f"ask:{kb_id}:{body.question}"
    r = get_redis()
    if r:
        cached = r.get(cache_key)
        if cached:
            return {"answer": cached, "sources": []}
    docs = await VectorStore(f"kb_{kb_id}").query(body.question)
    context = "\n".join(docs)
    prompt = f"请根据下面资料回答问题，如果资料中没有相关信息，请回答“抱歉，我无法回答这个问题。”。\n\n资料:\n{context}\n\n问题:\n{body.question}\n\n回答:"
    answer = await call_llm(prompt)
    if r:
        r.set(cache_key, answer, ex=3600)
    return {"answer": answer, "sources": docs}


@router.post("/ask-stream")
async def ask_question_stream(kb_id: int, body: AskRequest, db: Session = Depends(get_db)):
    docs = await VectorStore(f"kb_{kb_id}").query(body.question)
    context = "\n".join(docs)
    prompt = f"请根据下面资料回答问题，如果资料中没有相关信息，请回答“抱歉，我无法回答这个问题。”\n\n资料：{context}\n\n问题：{body.question}\n\n回答："

    async def event_stream():
        async for chunk in call_llm_stream(prompt):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
