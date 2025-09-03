import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db
from app.api.ingest import router as ingest_router
from app.api.embed import router as embed_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("INIT_DB", "true").lower() in ("1", "true", "yes"):
        await asyncio.to_thread(init_db)
    yield

app = FastAPI(title="RAG API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOW_CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api")
app.include_router(embed_router, prefix="/api")


@app.get("/healthz")
async def healthz():
    return {"status":"ok"}
