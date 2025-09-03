import os
from pypdf import PdfReader
from docx import Document as DocxDocument

def extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            reader = PdfReader(path)
            pages_text = [p.extract_text() or "" for p in reader.pages]
            return "\n".join(pages_text)
        elif ext in (".docx",):
            d = DocxDocument(path)
            return "\n".join([p.text for p in d.paragraphs])
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        return ""
