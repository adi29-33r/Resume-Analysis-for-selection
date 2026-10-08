"""
preprocessing.py
- Cleaning utilities
- stopword removal optional
"""
import re
from typing import List

def clean_text(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\r", " ").replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^\w\s\.-/]", " ", t)  # keep letters, digits, underscore, ., -, /
    t = t.strip()
    return t

def tokenize(text: str) -> List[str]:
    text = clean_text(text).lower()
    return [t for t in re.split(r"\W+", text) if t]
