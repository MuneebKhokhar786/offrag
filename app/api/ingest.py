import logging
import os
import uuid
import hashlib
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Document, Chunk
from app.indexing.extract_text import extract_text_from_file
from app.indexing.chunker import chunk_text
from app.workers.tasks import embed_pending_chunks


router = APIRouter()

logger = logging.getLogger(__name__)

DATA_DIR = os.getenv("DATA_DIR", "/data")

@router.post("/ingest")
async def ingest(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info("Ingest called: filename=%s content_type=%s", file.filename, file.content_type)
    os.makedirs(DATA_DIR, exist_ok=True)
    doc_id = uuid.uuid4()
    filename = f"{doc_id}_{file.filename}"
    path = os.path.join(DATA_DIR, filename)

    contents = await file.read()
    logger.debug("Read %d bytes from upload", len(contents))
    with open(path, "wb") as f:
        f.write(contents)
    logger.info("Saved uploaded file to %s", path)

    text = extract_text_from_file(path)
    chunks = chunk_text(text)
    logger.info("Extracted %d chunks from document", len(chunks))

    doc = Document(id=doc_id, source_path=path, mime_type=file.content_type)
    db.add(doc)
    db.flush()
    logger.debug("Inserted document record id=%s", doc_id)

    objs = []
    for i, c in enumerate(chunks):
        h = hashlib.sha256(c.encode("utf-8")).hexdigest()
        objs.append(Chunk(document_id=doc_id, seq=i, text=c, hash=h))
    if objs:
        db.bulk_save_objects(objs)
        logger.debug("Bulk saved %d chunk objects", len(objs))
    db.commit()
    batch_size = len(objs)
    logger.info("Ingest completed for document id=%s, chunks_indexed=%d", doc_id, batch_size)
    embed_pending_chunks.apply_async(queue='agents', kwargs={'batch_size': batch_size, 'doc_id': str(doc_id)})
    return {"document_id": str(doc_id), "chunks_indexed": batch_size, "embedding_status": "queued"}
