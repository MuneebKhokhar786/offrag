import os
import uuid
import hashlib
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Document, Chunk
from app.indexing.extract_text import extract_text_from_file
from app.indexing.chunker import chunk_text

router = APIRouter()

DATA_DIR = os.getenv("DATA_DIR", "/data")

@router.post("/ingest")
async def ingest(file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs(DATA_DIR, exist_ok=True)
    doc_id = uuid.uuid4()
    filename = f"{doc_id}_{file.filename}"
    path = os.path.join(DATA_DIR, filename)

    contents = await file.read()
    with open(path, "wb") as f:
        f.write(contents)

    text = extract_text_from_file(path)
    chunks = chunk_text(text)

    doc = Document(id=doc_id, source_path=path, mime_type=file.content_type)
    db.add(doc)
    db.flush()

    objs = []
    for i, c in enumerate(chunks):
        h = hashlib.sha256(c.encode("utf-8")).hexdigest()
        objs.append(Chunk(document_id=doc_id, seq=i, text=c, hash=h))
    if objs:
        db.bulk_save_objects(objs)
    db.commit()
    return {"document_id": str(doc_id), "chunks_indexed": len(objs)}
