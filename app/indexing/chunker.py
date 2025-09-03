import logging

logger = logging.getLogger(__name__)

def chunk_text(text: str, max_chars: int = 2000, overlap: int = 200) -> list[str]:
    if max_chars <= 0:
        logger.warning("max_chars must be positive, using default value 2000")
        max_chars = 2000
    if overlap < 0:
        logger.warning("overlap cannot be negative, setting to 0")
        overlap = 0
    if overlap >= max_chars:
        logger.warning("overlap cannot be >= max_chars, reducing overlap to max_chars//2")
        overlap = max_chars // 2

    logger.debug("chunk_text called: text_length=%d, max_chars=%d, overlap=%d", 
                len(text) if text else 0, max_chars, overlap)
    
    if not text:
        logger.debug("chunk_text received empty text")
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    logger.info("chunk_text processing: start=%d, text_length=%d", start, text_length)
    
    while start < text_length:
        logger.debug("chunk_text processing from start=%d", start)
        
        end = min(start + max_chars, text_length)

        if end < text_length:
            last_newline = text.rfind("\n", start, end)
            if last_newline != -1 and last_newline > start + (max_chars // 2):
                end = last_newline + 1  

        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
            logger.debug("chunk_text created chunk of length %d", len(chunk))

        start = end - overlap

        if start <= end - overlap:
            logger.warning("No progress made in chunking, breaking loop")
            break

        if start < 0:
            start = 0

        if start >= text_length:
            break
    
    logger.info("chunk_text completed: created %d chunks", len(chunks))
    return chunks