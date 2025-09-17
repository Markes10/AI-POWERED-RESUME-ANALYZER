import re
from typing import List

def normalize_text(text: str) -> str:
    """
    Lowercase, remove punctuation, collapse whitespace.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text: str) -> List[str]:
    """
    Split normalized text into unique tokens.
    """
    return list(set(normalize_text(text).split())) 
