from app.config import settings
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import sqlite3


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# SQLite 默认不校验外键，导致本地行为与 PostgreSQL（强制外键）不一致：
# 本地能插入不存在的 kb_id，容器里 500。此处对齐两者行为。
if "sqlite" in settings.DATABASE_URL:
    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()