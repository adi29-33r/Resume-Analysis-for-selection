"""
ranker.py
- a lightweight trainable scikit-learn ranker
- saves model to backend/app/models/ranker.joblib
"""
import os
from typing import List
import joblib
import numpy as np

_MODEL_FILE = os.path.join(os.path.dirname(__file__), "ranker.joblib")

try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    _SKLEARN_AVAILABLE = True
except Exception:
    _SKLEARN_AVAILABLE = False

class Ranker:
    def __init__(self):
        self.scaler = None
        self.model = None
        if os.path.exists(_MODEL_FILE) and _SKLEARN_AVAILABLE:
            try:
                self.scaler, self.model = joblib.load(_MODEL_FILE)
            except Exception:
                self.scaler = None
                self.model = None

    def fit(self, X: List[List[float]], y: List[int]):
        if not _SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn required to train ranker")
        self.scaler = StandardScaler()
        Xs = self.scaler.fit_transform(X)
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(Xs, y)
        joblib.dump((self.scaler, self.model), _MODEL_FILE)

    def predict_proba(self, X: List[List[float]]):
        if not self.model or not self.scaler:
            # fallback: return normalized score of first feature
            arr = np.array(X, dtype=float)
            if arr.size == 0:
                return [0.0] * len(X)
            scal = (arr[:,0] - arr[:,0].min()) / (arr[:,0].ptp() + 1e-9)
            return scal.tolist()
        Xs = self.scaler.transform(X)
        return self.model.predict_proba(Xs)[:,1].tolist()

# Singleton
ranker = Ranker()
