"""
anonymizer.py
- Uses regex + spaCy NER (if available) to remove PII
"""
import re

# Basic regex PII
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{10}|\d{3}[-.\s]\d{3}[-.\s]\d{4}|\d{4}[-.\s]\d{6})\b")
_URL = re.compile(r"https?://\S+|www\.\S+")

# Try to load spaCy NER for better name/address detection; optional
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    _SPACY_AVAILABLE = True
except Exception:
    _nlp = None
    _SPACY_AVAILABLE = False

def anonymize_text(text: str) -> str:
    t = text
    # regex-based replacements
    t = _EMAIL.sub("[EMAIL]", t)
    t = _PHONE.sub("[PHONE]", t)
    t = _URL.sub("[URL]", t)

    # spaCy NER: replace PERSON, GPE, LOC, ORG as simple heuristic
    if _SPACY_AVAILABLE and t.strip():
        doc = _nlp(t)
        spans = []
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "GPE", "LOC", "ORG", "NORP", "FAC", "ADDRESS"):
                spans.append((ent.start_char, ent.end_char))
        # replace from end to start to not break offsets
        for s, e in sorted(spans, reverse=True):
            t = t[:s] + f"[{doc.char_span(s, e).label_}]" + t[e:]
    else:
        # a gentle name pattern replacement: First Last (capitalized)
        t = re.sub(r"\b([A-Z][a-z]{1,}\s[A-Z][a-z]{1,})\b", "[NAME]", t)
    return t




