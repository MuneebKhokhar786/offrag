import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("INIT_DB", "true").lower() in ("1", "true", "yes"):
        await asyncio.to_thread(init_db)
    yield

app = FastAPI(title="RAG API", version="0.1.0", lifespan=lifespan)

@app.get("/healthz")
async def healthz():
    return {"status":"ok"}
