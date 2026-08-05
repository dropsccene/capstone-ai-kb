from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.agent import ReActAgent, tools
from app.llm import client
from pydantic import BaseModel


class AskDatabaseRequest(BaseModel):
    question: str


router = APIRouter(prefix="/api/agent", tags=["Agent"])


@router.post("/ask-database")
async def ask_database(body: AskDatabaseRequest, db: Session = Depends(get_db)):
    agent = ReActAgent(tools=tools, client=client)
    result = await agent.run(messages=[{
        "role": "system",
        "content": "你是一个数据库查询助手。数据库是 SQLite。只生成SQLite兼容的SQL语句。先查表结构，再回答用户问题。如果查询结果为空，直接说数据为空。如果 SQL 执行出错，根据错误信息修正 SQL 后重试，最多修正重试 2 次，仍失败就如实告诉用户错误原因。只能执行 SELECT 语句。"
    }],
        user_query=body.question
    )
    return {"answer": result}
