# REFERENCE.md — 速查表

> 今天忘了什么，这里一眼能找到。不用切项目。

---

## SQLAlchemy 模型

```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from app.database import Base

class Xxx(Base):
    __tablename__ = "xxxs"              # 类属性，不是函数。双下划线 + 表名复数

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
```

## database.py 三件套

```python
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## lifespan（FastAPI 启动建表）

```python
from contextlib import asynccontextmanager
from app.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
```

## pydantic-settings

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://..."
    LLM_API_KEY: str = ""

settings = Settings()
```

## docker-compose 最小骨架

```yaml
services:
  db:
    image: postgres:16                    # 冒号后不能有空格
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mydb
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data
  app:
    build: .
    ports: ["8000:8000"]
    depends_on: [db]
    environment:
      DATABASE_URL: postgresql+psycopg2://postgres:postgres@db:5432/mydb  # 用容器名 db，不是 localhost

volumes:
  pgdata:
```
