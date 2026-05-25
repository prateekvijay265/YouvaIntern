"""
monitoring.py
-------------
Thread-safe in-process metrics store.

Tracks:
  - total_requests
  - successful_predictions
  - failed_requests
  - per-class prediction counts
  - request latencies (rolling window of last 1000 samples)

Metrics are exposed via the /metrics endpoint and are also written
to the structured log every N requests as a periodic snapshot.
"""

import threading
import time
from collections import deque
from typing import Dict

import numpy as np  # type: ignore


class MetricsStore:
    """Thread-safe metrics container."""

    _LATENCY_WINDOW = 1000   # keep last N latency samples
    _LOG_EVERY = 50          # emit a metrics snapshot log every N requests

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._start_time = time.time()

        self.total_requests: int = 0
        self.successful_predictions: int = 0
        self.failed_requests: int = 0
        self.requests_per_class: Dict[str, int] = {}

        # Rolling latency window (milliseconds)
        self._latencies: deque = deque(maxlen=self._LATENCY_WINDOW)

    # ── Mutation helpers ───────────────────────────────────────────────────────

    def record_request(
        self,
        latency_ms: float,
        predicted_class: str | None = None,
        success: bool = True,
    ) -> None:
        with self._lock:
            self.total_requests += 1
            self._latencies.append(latency_ms)

            if success and predicted_class is not None:
                self.successful_predictions += 1
                self.requests_per_class[predicted_class] = (
                    self.requests_per_class.get(predicted_class, 0) + 1
                )
            else:
                self.failed_requests += 1

    # ── Read-only snapshot ────────────────────────────────────────────────────

    def snapshot(self) -> dict:
        with self._lock:
            latencies = list(self._latencies)
            total = self.total_requests or 1   # avoid division by zero

            avg_latency = float(np.mean(latencies)) if latencies else 0.0
            p95_latency = float(np.percentile(latencies, 95)) if latencies else 0.0
            error_rate = round(self.failed_requests / total * 100, 2)

            return {
                "total_requests": self.total_requests,
                "successful_predictions": self.successful_predictions,
                "failed_requests": self.failed_requests,
                "avg_latency_ms": round(avg_latency, 3),
                "p95_latency_ms": round(p95_latency, 3),
                "error_rate_percent": error_rate,
                "requests_per_class": dict(self.requests_per_class),
                "uptime_seconds": round(time.time() - self._start_time, 1),
            }

    def uptime(self) -> float:
        return round(time.time() - self._start_time, 1)


# Singleton — shared across the entire FastAPI process
metrics = MetricsStore()
