
import logging
logger = logging.getLogger(__name__)
import uuid
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_path = Column(String, nullable=False)
    mime_type = Column(String)
    metadata_ = Column("metadata", JSON, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PGUUID(as_uuid=True), ForeignKey("documents.id", ondelete="cascade"), nullable=False)
    seq = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    hash = Column(String, nullable=False, index=True)
    embedding = Column(Vector(1536), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
