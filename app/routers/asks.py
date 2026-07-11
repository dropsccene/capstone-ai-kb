from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.vector_store import VectorStore
from pydantic import BaseModel
from app.llm import call_llm


router = APIRouter(prefix = "/knowledge-bases/{kb_id}",tags = ["asks"])

class AskRequest(BaseModel):
    question:str

@router.post("/ask")
async def ask_question(kb_id:int,body:AskRequest,db:Session = Depends(get_db)):
    docs = VectorStore(f"kb_{kb_id}").query(body.question)
    context = "\n".join(docs)
    prompt = f"请根据下面资料回答问题，如果资料中没有相关信息，请回答“抱歉，我无法回答这个问题。”。\n\n资料:\n{context}\n\n问题:\n{body.question}\n\n回答:"
    answer = call_llm(prompt)
    return {"answer":answer,"sources":docs}
    