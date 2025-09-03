import logging
import os
from fastapi import HTTPException
from pypdf import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

def extract_extension(path: str) -> str:
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="File path does not exist")
    
    ext = os.path.splitext(path)[1].lower()
    return ext

def extract_text_from_file(path: str) -> str:
    ext = extract_extension(path)
    logger.info("extract_text_from_file called for path=%s ext=%s", path, ext)
    
    try:
        if ext == ".pdf":
            logger.info("Extracting text from PDF file: %s", path)
            with open(path, "rb") as file:
                reader = PdfReader(file)
                pages_text = [page.extract_text() or "" for page in reader.pages]
                logger.debug("Extracted %d pages from PDF", len(pages_text))
                return "\n".join(pages_text)
                
        elif ext == ".docx":
            logger.info("Extracting text from DOCX file: %s", path)
            doc = DocxDocument(path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]
            logger.debug("Extracted %d paragraphs from docx", len(paragraphs))
            return "\n".join(paragraphs)
            
        else:
            logger.info("Extracting text from plain text file: %s", path)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                data = file.read()
                logger.debug("Read %d characters from text file", len(data))
                return data
                
    except HTTPException:
        # Re-raise HTTP exceptions to maintain proper error handling
        raise
    except Exception as e:
        logger.exception("Failed to extract text from %s", path)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to extract text from file: {str(e)}"
        )