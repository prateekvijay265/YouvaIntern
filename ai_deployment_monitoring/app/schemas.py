"""
schemas.py
----------
Pydantic models used for request validation and response serialisation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ── Request schemas ────────────────────────────────────────────────────────────

class IrisFeatures(BaseModel):
    """
    Four numeric measurements of a single iris flower sample.

    Ranges derived from the UCI Iris dataset:
      - sepal_length : 4.3 – 7.9 cm
      - sepal_width  : 2.0 – 4.4 cm
      - petal_length : 1.0 – 6.9 cm
      - petal_width  : 0.1 – 2.5 cm
    """
    sepal_length: float = Field(
        ..., ge=0.0, le=20.0,
        description="Sepal length in cm",
        json_schema_extra={"example": 5.1}
    )
    sepal_width: float = Field(
        ..., ge=0.0, le=20.0,
        description="Sepal width in cm",
        json_schema_extra={"example": 3.5}
    )
    petal_length: float = Field(
        ..., ge=0.0, le=20.0,
        description="Petal length in cm",
        json_schema_extra={"example": 1.4}
    )
    petal_width: float = Field(
        ..., ge=0.0, le=20.0,
        description="Petal width in cm",
        json_schema_extra={"example": 0.2}
    )

    @field_validator("sepal_length", "sepal_width", "petal_length", "petal_width")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Feature values must be non-negative")
        return v


class BatchIrisFeatures(BaseModel):
    """A list of iris samples for batch prediction."""
    samples: List[IrisFeatures] = Field(
        ...,
        min_length=1,
        max_length=256,
        description="1 – 256 iris samples"
    )


# ── Response schemas ───────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """Prediction result for a single sample."""
    prediction: int = Field(..., description="Predicted class index (0, 1, or 2)")
    class_name: str = Field(..., description="Human-readable class name")
    confidence: float = Field(..., description="Probability of the predicted class")
    probabilities: dict = Field(..., description="Class-wise probabilities")


class BatchPredictionResponse(BaseModel):
    """Prediction results for a batch of samples."""
    predictions: List[PredictionResponse]
    batch_size: int


class HealthResponse(BaseModel):
    """Liveness / readiness probe result."""
    status: str
    model_loaded: bool
    uptime_seconds: float
    version: str


class MetricsResponse(BaseModel):
    """Snapshot of in-process operational metrics."""
    total_requests: int
    successful_predictions: int
    failed_requests: int
    avg_latency_ms: float
    p95_latency_ms: float
    error_rate_percent: float
    requests_per_class: dict
