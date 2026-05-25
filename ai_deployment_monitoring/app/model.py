"""
model.py
--------
Loads the persisted joblib model and exposes a thin prediction interface.
The model is loaded once at application startup and cached as a module-level
singleton to avoid repeated disk I/O.
"""

import json
import os
import time
from typing import List

import joblib
import numpy as np

from app.logger_config import get_logger

logger = get_logger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, "model", "iris_model.joblib")
METADATA_PATH = os.path.join(_BASE_DIR, "model", "model_metadata.json")

# ── Module-level singletons ────────────────────────────────────────────────────
_clf = None
_metadata: dict = {}


def load_model() -> None:
    """Load the classifier from disk into the module-level singleton."""
    global _clf, _metadata

    logger.info("Loading model from disk", extra={"path": MODEL_PATH})
    t0 = time.perf_counter()

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at {MODEL_PATH}. "
            "Run `python model/train_and_save.py` first."
        )

    _clf = joblib.load(MODEL_PATH)

    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH) as fh:
            _metadata = json.load(fh)

    elapsed = (time.perf_counter() - t0) * 1000
    logger.info(
        "Model loaded successfully",
        extra={"load_time_ms": round(elapsed, 2), "model_type": type(_clf).__name__},
    )


def is_loaded() -> bool:
    return _clf is not None


def get_metadata() -> dict:
    return _metadata


def predict_single(features: List[float]) -> dict:
    """
    Run a single prediction.

    Parameters
    ----------
    features : list of 4 floats
        [sepal_length, sepal_width, petal_length, petal_width]

    Returns
    -------
    dict with keys: prediction, class_name, confidence, probabilities
    """
    if _clf is None:
        raise RuntimeError("Model is not loaded. Call load_model() first.")

    X = np.array([features])
    pred_idx = int(_clf.predict(X)[0])
    proba = _clf.predict_proba(X)[0]

    target_names: List[str] = _metadata.get(
        "target_names", ["setosa", "versicolor", "virginica"]
    )

    return {
        "prediction": pred_idx,
        "class_name": target_names[pred_idx],
        "confidence": round(float(proba[pred_idx]), 6),
        "probabilities": {
            name: round(float(p), 6)
            for name, p in zip(target_names, proba)
        },
    }


def predict_batch(feature_matrix: List[List[float]]) -> List[dict]:
    """Run predictions for a batch of samples."""
    return [predict_single(row) for row in feature_matrix]
