import re

def normalize_text(text: str) -> str:
    """Normalize text by lowercasing and removing extra whitespace."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.strip().lower())
