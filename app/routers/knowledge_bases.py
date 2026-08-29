from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import KnowledgeBase

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


class KnowledgeBaseCreate(BaseModel):
    name: str


@router.post("", status_code=201)
def create_knowledge_base(body: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """创建知识库（此前无任何写入入口，导致新环境上传即外键报错）"""
    if db.query(KnowledgeBase).filter(KnowledgeBase.name == body.name).first():
        raise HTTPException(status_code=409, detail="知识库已存在")
    kb = KnowledgeBase(name=body.name)
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return {"id": kb.id, "name": kb.name}


@router.get("")
def list_knowledge_bases(db: Session = Depends(get_db)):
    kbs = db.query(KnowledgeBase).all()
    return [
        {"id": kb.id, "name": kb.name, "created_at": str(kb.created_at)}
        for kb in kbs
    ]
