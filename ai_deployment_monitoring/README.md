# 🤖 AI Model Deployment & Monitoring

> **Proof-of-concept** deployment of an Iris species classifier using Docker, FastAPI, and structured logging.

---

## 📁 Repository Structure

```
ai_deployment_monitoring/
├── app/
│   ├── __init__.py
│   ├── main.py            ← FastAPI application (endpoints, middleware)
│   ├── model.py           ← Model loader & prediction logic
│   ├── monitoring.py      ← Thread-safe in-process metrics store
│   ├── logger_config.py   ← Structured JSON logger (console + rotating file)
│   └── schemas.py         ← Pydantic request/response schemas
├── model/
│   ├── train_and_save.py  ← Train + serialise the RandomForest model
│   ├── iris_model.joblib  ← Persisted model (created by train script)
│   └── model_metadata.json
├── logs/                  ← Runtime JSON log files (volume-mounted in Docker)
├── tests/
│   └── test_api.py        ← pytest smoke-test suite
├── Dockerfile             ← Multi-stage build; non-root user
├── docker-compose.yml     ← Compose file with health-checks & resource limits
├── requirements.txt
├── generate_report.py     ← Generates DEPLOYMENT_REPORT.pdf
├── DEPLOYMENT_REPORT.pdf  ← ≥1500-word deployment documentation
└── README.md
```

---

## ⚡ Quick Start (Local — No Docker)

### 1 — Install dependencies

```bash
cd ai_deployment_monitoring
pip install -r requirements.txt
```

### 2 — Train the model

```bash
python model/train_and_save.py
```

### 3 — Start the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4 — Explore the interactive docs

Open **http://localhost:8000/docs** in your browser.

---

## 🐳 Docker Deployment

### Build & run (single command)

```bash
docker compose up --build
```

### Verify the container is healthy

```bash
docker inspect iris_api --format "{{.State.Health.Status}}"
# → healthy
```

---

## 🌐 API Endpoints

| Method | Endpoint        | Description                          |
|--------|-----------------|--------------------------------------|
| GET    | `/health`       | Liveness + readiness probe           |
| GET    | `/metrics`      | In-process operational metrics       |
| GET    | `/model/info`   | Model training metadata              |
| POST   | `/predict`      | Single-sample Iris prediction        |
| POST   | `/predict/batch`| Batch prediction (1–256 samples)     |
| GET    | `/docs`         | Swagger UI (auto-generated)          |
| GET    | `/redoc`        | ReDoc documentation (auto-generated) |

### Sample — single prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

Expected response:
```json
{
  "prediction": 0,
  "class_name": "setosa",
  "confidence": 1.0,
  "probabilities": {"setosa": 1.0, "versicolor": 0.0, "virginica": 0.0}
}
```

### Sample — health check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime_seconds": 42.3,
  "version": "1.0.0"
}
```

### Sample — metrics

```bash
curl http://localhost:8000/metrics
```

```json
{
  "total_requests": 150,
  "successful_predictions": 148,
  "failed_requests": 2,
  "avg_latency_ms": 3.2,
  "p95_latency_ms": 8.1,
  "error_rate_percent": 1.33,
  "requests_per_class": {"setosa": 60, "versicolor": 55, "virginica": 33}
}
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📄 Documentation

See **DEPLOYMENT_REPORT.pdf** for the full ≥1500-word deployment documentation covering:

- Significance of AI deployment practices
- Container configuration details
- API endpoint reference
- Logging & monitoring strategy
- Health check best practices
- Handling unexpected behaviour & performance drift
- Maintenance of deployed AI services

To regenerate the PDF:

```bash
pip install reportlab
python generate_report.py
```

---

## 📦 Environment Variables

| Variable    | Default  | Description                      |
|-------------|----------|----------------------------------|
| `LOG_LEVEL` | `INFO`   | Python logging level             |
| `LOG_DIR`   | `logs`   | Directory for rotating log files |
