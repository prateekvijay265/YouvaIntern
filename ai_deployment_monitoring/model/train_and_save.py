"""
train_and_save.py
-----------------
Trains a RandomForestClassifier on the Iris dataset and saves it
to model/iris_model.joblib for use by the FastAPI application.
"""

import os
import json
import joblib
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix
)

# ── Configuration ─────────────────────────────────────────────────────────────
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "iris_model.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 100

# ── Data ──────────────────────────────────────────────────────────────────────
print("Loading Iris dataset …")
iris = load_iris()
X, y = iris.data, iris.target
feature_names = list(iris.feature_names)
target_names = list(iris.target_names)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
)

# ── Training ──────────────────────────────────────────────────────────────────
print(f"Training RandomForestClassifier (n_estimators={N_ESTIMATORS}) …")
clf = RandomForestClassifier(
    n_estimators=N_ESTIMATORS,
    max_depth=None,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)
clf.fit(X_train, y_train)

# ── Evaluation ────────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
cv_scores = cross_val_score(clf, X, y, cv=5, scoring="accuracy")

print(f"\n[OK] Test Accuracy : {accuracy:.4f}")
print(f"[OK] CV Accuracy   : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_names))

# ── Persist ───────────────────────────────────────────────────────────────────
joblib.dump(clf, MODEL_PATH)
print(f"\nModel saved -> {MODEL_PATH}")

metadata = {
    "model_type": "RandomForestClassifier",
    "n_estimators": N_ESTIMATORS,
    "random_state": RANDOM_STATE,
    "dataset": "Iris",
    "feature_names": feature_names,
    "target_names": target_names,
    "test_accuracy": round(float(accuracy), 4),
    "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
    "cv_accuracy_std": round(float(cv_scores.std()), 4),
    "training_samples": int(X_train.shape[0]),
    "test_samples": int(X_test.shape[0]),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
}

with open(METADATA_PATH, "w") as fh:
    json.dump(metadata, fh, indent=2)
print(f"Metadata saved -> {METADATA_PATH}")
