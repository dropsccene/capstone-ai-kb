from app.database import Base
from sqlalchemy import Column,Integer,String,DateTime,Text,ForeignKey,func
from sqlalchemy.orm import relationship

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    id = Column(Integer,primary_key = True,autoincrement = True)
    name = Column(String(255),unique = True,nullable = False)
    created_at = Column(DateTime,server_default = func.now())

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer,primary_key = True,autoincrement = True)
    filename = Column(String(255),nullable = False)
    content = Column(Text,nullable = True)
    kb_id = Column(Integer,ForeignKey("knowledge_bases.id"),nullable = False)
    uploaded_at = Column(DateTime,server_default = func.now())
    kb = relationship("KnowledgeBase",backref = "documents")
    file_size = Column(Integer,nullable = True)

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer,primary_key = True,autoincrement = True)
    doc_id = Column(Integer,ForeignKey("documents.id",ondelete= "CASCADE"),nullable = False)
    content = Column(Text)
    chunk_index = Column(Integer)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key = True,autoincrement = True)
    username = Column(String(50),unique = True,nullable = False)
    email = Column(String(255),unique = True,nullable = False)
    hashed_password = Column(String(255),nullable = False)
    created_at = Column(DateTime,server_default=func.now())
