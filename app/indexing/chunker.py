import logging

logger = logging.getLogger(__name__)

def chunk_text(text: str, max_chars: int = 2000, overlap: int = 200) -> list[str]:
    # Validation (same as before)
    if max_chars <= 0:
        max_chars = 2000
    if overlap < 0:
        overlap = 0
    if overlap >= max_chars:
        overlap = max_chars // 2
    
    # sanitize input early: remove NUL bytes which can break SQL string literals
    if text and "\x00" in text:
        nuls = text.count("\x00")
        logger.warning("chunk_text: input contains %d NUL bytes; replacing with space", nuls)
        text = text.replace("\x00", " ")

    if not text:
        logger.debug("chunk_text received empty text")
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        logger.debug("chunk_text processing from start=%d", start)
        end = min(start + max_chars, text_length)
        
        # Try to break at newline if possible
        if end < text_length:
            last_newline = text.rfind("\n", start, end)
            if last_newline != -1 and last_newline > start:
                end = last_newline + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Calculate next start with overlap, ensuring progress
        next_start = max(start + 1, end - overlap)  # Always move forward by at least 1
        start = min(next_start, text_length)
    
    logger.info("chunk_text completed: created %d chunks", len(chunks))
    return chunks