from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routers import documents,asks

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind = engine)
    yield

app = FastAPI(lifespan = lifespan)
app.include_router(documents.router)
app.include_router(asks.router)

@app.get("/health")
async def health():
    return{"status":"ok"}