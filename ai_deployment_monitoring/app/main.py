"""
main.py
-------
FastAPI application — AI Model Deployment & Monitoring demonstration.

Endpoints
---------
GET  /health          → liveness + readiness probe
GET  /metrics         → in-process operational metrics
GET  /model/info      → model metadata (version, accuracy, features)
POST /predict         → single-sample prediction
POST /predict/batch   → batch prediction (up to 256 samples)
GET  /docs            → interactive Swagger UI (automatic)
GET  /redoc           → ReDoc documentation (automatic)
"""

import time
import traceback
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import model as model_module
from app.logger_config import get_logger
from app.monitoring import metrics
from app.schemas import (
    BatchIrisFeatures,
    BatchPredictionResponse,
    HealthResponse,
    IrisFeatures,
    MetricsResponse,
    PredictionResponse,
)

logger = get_logger(__name__)

# ── Application version ────────────────────────────────────────────────────────
API_VERSION = "1.0.0"


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model on startup; clean up on shutdown."""
    logger.info("Application starting up …", extra={"version": API_VERSION})
    model_module.load_model()
    yield
    logger.info("Application shutting down.")


# ── FastAPI instance ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Iris Species Prediction API",
    description=(
        "A production-style REST API that serves predictions from a "
        "RandomForestClassifier trained on the Iris dataset. "
        "Includes structured logging, in-process metrics, health checks, "
        "and batch inference support."
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request-ID middleware ──────────────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = time.perf_counter()

    logger.info(
        "Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
        },
    )

    response = await call_next(request)

    latency_ms = (time.perf_counter() - request.state.start_time) * 1000
    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 3),
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


# ── Global exception handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": getattr(request.state, "request_id", "unknown"),
            "path": request.url.path,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        },
    )
    metrics.record_request(latency_ms=0.0, success=False)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check logs for details."},
    )


# ── Health endpoint ────────────────────────────────────────────────────────────
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness and readiness probe",
    tags=["Operations"],
)
async def health():
    """
    Returns the current health status of the service.

    - **status**: `"healthy"` when the model is loaded, `"degraded"` otherwise.
    - **model_loaded**: whether the classifier is in memory.
    - **uptime_seconds**: seconds since the process started.
    - **version**: API version string.
    """
    loaded = model_module.is_loaded()
    return HealthResponse(
        status="healthy" if loaded else "degraded",
        model_loaded=loaded,
        uptime_seconds=metrics.uptime(),
        version=API_VERSION,
    )


# ── Metrics endpoint ───────────────────────────────────────────────────────────
@app.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Operational metrics snapshot",
    tags=["Operations"],
)
async def get_metrics():
    """
    Returns a snapshot of in-process operational metrics:
    - Request counts (total, success, failed)
    - Average and P95 latency in milliseconds
    - Error rate percentage
    - Per-class prediction distribution
    """
    snap = metrics.snapshot()
    return MetricsResponse(**snap)


# ── Model info endpoint ────────────────────────────────────────────────────────
@app.get(
    "/model/info",
    summary="Model metadata",
    tags=["Model"],
)
async def model_info():
    """Returns training metadata for the deployed model."""
    meta = model_module.get_metadata()
    if not meta:
        raise HTTPException(status_code=503, detail="Model metadata not available")
    return meta


# ── Single-sample prediction ───────────────────────────────────────────────────
@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Single-sample Iris prediction",
    tags=["Inference"],
)
async def predict(payload: IrisFeatures, request: Request):
    """
    Accepts four measurements for a single iris flower and returns
    the predicted species along with class probabilities.

    **Example input**
    ```json
    {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    }
    ```
    """
    request_id = getattr(request.state, "request_id", "unknown")
    t0 = time.perf_counter()

    features = [
        payload.sepal_length,
        payload.sepal_width,
        payload.petal_length,
        payload.petal_width,
    ]

    logger.info(
        "Prediction request",
        extra={"request_id": request_id, "features": features},
    )

    try:
        result = model_module.predict_single(features)
    except RuntimeError as exc:
        latency_ms = (time.perf_counter() - t0) * 1000
        metrics.record_request(latency_ms=latency_ms, success=False)
        logger.error(
            "Prediction failed",
            extra={"request_id": request_id, "error": str(exc)},
        )
        raise HTTPException(status_code=503, detail=str(exc))

    latency_ms = (time.perf_counter() - t0) * 1000
    metrics.record_request(
        latency_ms=latency_ms,
        predicted_class=result["class_name"],
        success=True,
    )

    logger.info(
        "Prediction success",
        extra={
            "request_id": request_id,
            "prediction": result["class_name"],
            "confidence": result["confidence"],
            "latency_ms": round(latency_ms, 3),
        },
    )

    return PredictionResponse(**result)


# ── Batch prediction ───────────────────────────────────────────────────────────
@app.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Batch Iris prediction",
    tags=["Inference"],
)
async def predict_batch(payload: BatchIrisFeatures, request: Request):
    """
    Accepts a list of 1–256 iris samples and returns predictions for each.

    **Example input**
    ```json
    {
      "samples": [
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2},
        {"sepal_length": 6.7, "sepal_width": 3.0, "petal_length": 5.2, "petal_width": 2.3}
      ]
    }
    ```
    """
    request_id = getattr(request.state, "request_id", "unknown")
    t0 = time.perf_counter()

    feature_matrix = [
        [s.sepal_length, s.sepal_width, s.petal_length, s.petal_width]
        for s in payload.samples
    ]

    logger.info(
        "Batch prediction request",
        extra={"request_id": request_id, "batch_size": len(feature_matrix)},
    )

    try:
        results = model_module.predict_batch(feature_matrix)
    except RuntimeError as exc:
        latency_ms = (time.perf_counter() - t0) * 1000
        metrics.record_request(latency_ms=latency_ms, success=False)
        raise HTTPException(status_code=503, detail=str(exc))

    latency_ms = (time.perf_counter() - t0) * 1000
    for res in results:
        metrics.record_request(
            latency_ms=latency_ms / len(results),
            predicted_class=res["class_name"],
            success=True,
        )

    logger.info(
        "Batch prediction success",
        extra={
            "request_id": request_id,
            "batch_size": len(results),
            "latency_ms": round(latency_ms, 3),
        },
    )

    return BatchPredictionResponse(
        predictions=[PredictionResponse(**r) for r in results],
        batch_size=len(results),
    )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning",   # suppress uvicorn's own logs; ours are JSON
    )
