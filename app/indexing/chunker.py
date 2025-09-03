def chunk_text(text: str, max_chars: int = 2000, overlap: int = 200):
    if not text:
        return []
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + max_chars, L)
        if end < L:
            nl = text.rfind("\n", start, end)
            if nl and nl > start + max_chars // 2:
                end = nl
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks
