from fastapi import FastAPI

app = FastAPI(title="RAG API", version="0.1.0")

@app.get("/healthz")
async def healthz():
    return {"status":"ok"}
