"""
embeddings.py
- Lazy-loads SentenceTransformer
- Provides encode() and similarity() utilities
"""
from typing import List
import threading

_MODEL_NAME = "all-MiniLM-L6-v2"
_model = None
_lock = threading.Lock()
_use_model = None

def _load_model():
    global _model, _use_model
    try:
        from sentence_transformers import SentenceTransformer, util
        _model = SentenceTransformer(_MODEL_NAME)
        _use_model = True
    except Exception as e:
        # model not available
        _model = None
        _use_model = False

def ensure_model():
    if _model is None:
        with _lock:
            if _model is None:
                _load_model()

def encode(texts: List[str], convert_to_tensor: bool = True):
    """
    Encode list of texts to embeddings (or raise if model not available).
    """
    ensure_model()
    if not _use_model:
        raise RuntimeError("SentenceTransformer model not available. Install sentence-transformers.")
    return _model.encode(texts, convert_to_tensor=convert_to_tensor)

def similarity(text_a: str, text_b: str) -> float:
    """
    Returns cosine similarity between two texts (0..1). If model missing,
    falls back to token-overlap heuristic (0..1).
    """
    ensure_model()
    if _use_model:
        from sentence_transformers import util
        emb_a = _model.encode([text_a], convert_to_tensor=True)
        emb_b = _model.encode([text_b], convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb_a, emb_b).item()
        # clamp to 0..1
        return max(0.0, min(1.0, float(sim)))
    # fallback: simple overlap ratio
    sa = set(text_a.lower().split())
    sb = set(text_b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
