"""
generate_report.py
------------------
Generates DEPLOYMENT_REPORT.pdf — a comprehensive, ≥1500-word deployment
documentation using the reportlab library.

Run:
    pip install reportlab
    python generate_report.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DEPLOYMENT_REPORT.pdf")

# ── Colour palette ─────────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor("#1a237e")   # deep indigo
SECONDARY = colors.HexColor("#0d47a1")   # blue
ACCENT    = colors.HexColor("#42a5f5")   # light blue
LIGHT_BG  = colors.HexColor("#e8eaf6")   # lavender tint
CODE_BG   = colors.HexColor("#263238")   # dark slate
WHITE     = colors.white
DARK_TEXT = colors.HexColor("#212121")
MID_TEXT  = colors.HexColor("#424242")


def build_styles():
    base = getSampleStyleSheet()

    h1 = ParagraphStyle(
        "H1", parent=base["Heading1"],
        fontSize=22, textColor=PRIMARY, spaceAfter=8,
        spaceBefore=14, fontName="Helvetica-Bold",
    )
    h2 = ParagraphStyle(
        "H2", parent=base["Heading2"],
        fontSize=16, textColor=SECONDARY, spaceAfter=6,
        spaceBefore=12, fontName="Helvetica-Bold",
    )
    h3 = ParagraphStyle(
        "H3", parent=base["Heading3"],
        fontSize=13, textColor=SECONDARY, spaceAfter=4,
        spaceBefore=8, fontName="Helvetica-Bold",
    )
    body = ParagraphStyle(
        "Body", parent=base["Normal"],
        fontSize=10.5, leading=16, textColor=DARK_TEXT,
        spaceAfter=6, alignment=TA_JUSTIFY, fontName="Helvetica",
    )
    bullet = ParagraphStyle(
        "Bullet", parent=body,
        bulletIndent=10, leftIndent=20, spaceAfter=3,
    )
    code = ParagraphStyle(
        "Code", parent=base["Code"],
        fontSize=8.5, leading=12, textColor=colors.HexColor("#a5d6a7"),
        backColor=CODE_BG, fontName="Courier",
        leftIndent=10, rightIndent=10, spaceAfter=8, spaceBefore=4,
        borderPadding=(6, 8, 6, 8),
    )
    caption = ParagraphStyle(
        "Caption", parent=body,
        fontSize=9, textColor=MID_TEXT, alignment=TA_CENTER,
        italic=True,
    )
    title_style = ParagraphStyle(
        "Title", parent=base["Title"],
        fontSize=28, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=body,
        fontSize=13, textColor=colors.HexColor("#bbdefb"),
        alignment=TA_CENTER,
    )
    return {
        "h1": h1, "h2": h2, "h3": h3,
        "body": body, "bullet": bullet,
        "code": code, "caption": caption,
        "title": title_style, "subtitle": subtitle_style,
    }


def hr(styles):
    return HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=8, spaceBefore=4)


def build_document():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=2.2 * cm,
        leftMargin=2.2 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="AI Model Deployment & Monitoring — Deployment Report",
        author="AI Deployment Project",
    )

    s = build_styles()
    story = []

    # ── Cover ──────────────────────────────────────────────────────────────────
    cover_data = [[
        Paragraph("AI Model Deployment &amp; Monitoring", s["title"]),
    ]]
    cover_table = Table(cover_data, colWidths=[16.6 * cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("TOPPADDING",    (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 30),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Deployment Documentation · Version 1.0.0 · May 2026",
        s["subtitle"]
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(hr(s))

    # ── Abstract ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Abstract", s["h1"]))
    story.append(Paragraph(
        "This report documents the end-to-end deployment of a RandomForestClassifier "
        "trained on the UCI Iris dataset as a production-ready REST API service. The "
        "project demonstrates containerisation with Docker, API design with FastAPI, "
        "structured JSON logging, in-process operational metrics, and health-check "
        "mechanisms. The documentation covers configuration details, endpoint "
        "specifications, monitoring strategies, and best practices drawn from "
        "industry standards for maintaining ML services in production.",
        s["body"]
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(hr(s))

    # ── 1. Significance of Deployment ─────────────────────────────────────────
    story.append(Paragraph("1. The Significance of AI Deployment Practices", s["h1"]))
    story.append(Paragraph(
        "Developing an accurate machine-learning model is only the first step in "
        "delivering value from artificial intelligence. The model must be packaged, "
        "deployed, and maintained in an environment where real users or downstream "
        "systems can consume its predictions reliably, safely, and at scale. The gap "
        "between an experimental notebook and a production service involves a "
        "substantial set of engineering concerns that, if neglected, can undermine "
        "even the most sophisticated model.",
        s["body"]
    ))
    story.append(Paragraph(
        "Industry research consistently shows that the majority of ML projects "
        "fail to move from prototype to production. The barriers are rarely "
        "algorithmic — they are operational: poor reproducibility, lack of monitoring, "
        "inadequate error handling, and the absence of systematic deployment "
        "pipelines. Deployment engineering addresses these barriers by turning a "
        "trained artefact into a managed, observable service.",
        s["body"]
    ))

    story.append(Paragraph("1.1 Reproducibility and Consistency", s["h2"]))
    story.append(Paragraph(
        "A model trained on a data scientist's laptop may behave differently in "
        "a cloud environment due to library version mismatches, operating-system "
        "differences, or environment variables. Containerisation with Docker "
        "eliminates this class of defect by bundling the entire runtime — interpreter, "
        "libraries, model artefact — into a single immutable image. The Dockerfile "
        "in this project uses a multi-stage build: a builder stage that compiles "
        "dependencies and a lean runtime stage that excludes build tools, "
        "minimising the attack surface and image size.",
        s["body"]
    ))

    story.append(Paragraph("1.2 Scalability and Availability", s["h2"]))
    story.append(Paragraph(
        "A containerised service can be horizontally scaled by running multiple "
        "replicas behind a load balancer. Orchestration platforms such as Kubernetes "
        "or AWS ECS manage replica counts, rolling updates, and automatic restart "
        "on failure. The REST API design in this project is stateless — each request "
        "carries all the information required for a prediction — which is a prerequisite "
        "for seamless horizontal scaling.",
        s["body"]
    ))

    story.append(Paragraph("1.3 Security and Governance", s["h2"]))
    story.append(Paragraph(
        "Production ML services handle sensitive data and must be auditable. The "
        "Dockerfile runs the application as a non-root user (UID 1001), reducing "
        "the blast radius of a container escape. Structured JSON logging ensures that "
        "every request — including the input features and predicted class — is "
        "captured in a machine-readable format suitable for audit trails and GDPR "
        "compliance workflows.",
        s["body"]
    ))

    story.append(Paragraph("1.4 Continuous Monitoring and Model Health", s["h2"]))
    story.append(Paragraph(
        "A deployed model is subject to two classes of degradation. "
        "Technical degradation occurs when the serving infrastructure fails — "
        "elevated error rates, increased latency, or memory exhaustion. "
        "Statistical degradation (often called data drift or concept drift) occurs "
        "when the statistical properties of incoming data diverge from the training "
        "distribution, causing prediction quality to erode silently. Monitoring must "
        "address both dimensions. This project implements infrastructure monitoring "
        "(request counts, latency percentiles, error rates) as a foundation, and "
        "describes how statistical monitoring can be layered on top.",
        s["body"]
    ))

    story.append(hr(s))

    # ── 2. Container Configuration ─────────────────────────────────────────────
    story.append(Paragraph("2. Container Configuration", s["h1"]))
    story.append(Paragraph(
        "The containerisation strategy employs Docker with a two-stage build "
        "pattern. The first stage (builder) installs all Python dependencies "
        "using pip with the --prefix flag to isolate installed packages. The "
        "second stage (runtime) starts from a fresh python:3.11-slim base and "
        "copies only the installed packages and application code, discarding the "
        "gcc toolchain and other build-time dependencies.",
        s["body"]
    ))

    story.append(Paragraph("2.1 Dockerfile Walkthrough", s["h2"]))

    dockerfile_lines = [
        "FROM python:3.11-slim AS builder",
        "WORKDIR /build",
        "RUN apt-get update && apt-get install -y gcc \\",
        "    && rm -rf /var/lib/apt/lists/*",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir --prefix=/install -r requirements.txt",
        "",
        "FROM python:3.11-slim AS runtime",
        "RUN groupadd --gid 1001 appgroup && \\",
        "    useradd --uid 1001 --gid appgroup appuser",
        "WORKDIR /app",
        "COPY --from=builder /install /usr/local",
        "COPY app/ ./app/  |  COPY model/ ./model/",
        "RUN mkdir -p logs && chown -R appuser:appgroup /app",
        "USER appuser",
        "EXPOSE 8000",
        "HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\",
        '    CMD python -c "import urllib.request; \\',
        "    urllib.request.urlopen('http://localhost:8000/health')"
    ]
    story.append(Paragraph("<br/>".join(dockerfile_lines), s["code"]))

    story.append(Paragraph(
        "Key decisions: (a) <b>python:3.11-slim</b> reduces the base image size "
        "by approximately 80 % compared to the full Debian image; "
        "(b) <b>--no-cache-dir</b> prevents pip from writing a local wheel cache "
        "that would inflate the image; (c) the <b>HEALTHCHECK</b> instruction causes "
        "Docker to mark the container as unhealthy if the /health endpoint does not "
        "respond within 10 seconds, enabling automatic replacement in orchestrated "
        "environments.",
        s["body"]
    ))

    story.append(Paragraph("2.2 Docker Compose Configuration", s["h2"]))
    story.append(Paragraph(
        "The docker-compose.yml file defines the service, maps port 8000, "
        "mounts the host ./logs directory into the container at /app/logs so "
        "that structured log files survive container restarts, and sets resource "
        "limits (1 CPU core, 512 MB RAM). Resource limits prevent a single "
        "runaway service from starving co-located workloads on the host.",
        s["body"]
    ))
    story.append(hr(s))

    # ── 3. API Endpoints ───────────────────────────────────────────────────────
    story.append(Paragraph("3. API Endpoint Reference", s["h1"]))
    story.append(Paragraph(
        "The API is built with FastAPI, which provides automatic OpenAPI "
        "documentation at /docs (Swagger UI) and /redoc. All requests and "
        "responses use JSON. Input validation is handled by Pydantic v2, "
        "which returns RFC 7807-style 422 Unprocessable Entity responses when "
        "validation fails.",
        s["body"]
    ))

    endpoint_data = [
        ["Method", "Path", "Description", "Auth"],
        ["GET",  "/health",        "Liveness & readiness probe",         "None"],
        ["GET",  "/metrics",       "Operational metrics snapshot",       "None"],
        ["GET",  "/model/info",    "Model training metadata",            "None"],
        ["POST", "/predict",       "Single-sample Iris prediction",      "None"],
        ["POST", "/predict/batch", "Batch prediction (1–256 samples)",   "None"],
        ["GET",  "/docs",          "Swagger UI (interactive)",           "None"],
        ["GET",  "/redoc",         "ReDoc documentation",               "None"],
    ]
    ep_table = Table(endpoint_data, colWidths=[1.5*cm, 4.0*cm, 7.5*cm, 2.5*cm])
    ep_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ep_table)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3.1 POST /predict — Request & Response", s["h2"]))
    story.append(Paragraph("Request body (JSON):", s["body"]))
    story.append(Paragraph(
        '{ "sepal_length": 5.1, "sepal_width": 3.5,<br/>'
        '  "petal_length": 1.4, "petal_width": 0.2 }',
        s["code"]
    ))
    story.append(Paragraph("Successful response (HTTP 200):", s["body"]))
    story.append(Paragraph(
        '{ "prediction": 0, "class_name": "setosa",<br/>'
        '  "confidence": 1.0,<br/>'
        '  "probabilities": {"setosa":1.0,"versicolor":0.0,"virginica":0.0} }',
        s["code"]
    ))

    story.append(Paragraph("3.2 Request-ID Middleware", s["h2"]))
    story.append(Paragraph(
        "Every request receives a UUID4 identifier attached to the "
        "X-Request-ID response header and logged with every log line "
        "associated with that request. This enables end-to-end traceability "
        "across distributed log aggregation systems such as Elasticsearch or "
        "Google Cloud Logging.",
        s["body"]
    ))
    story.append(hr(s))

    # ── 4. Logging and Monitoring ──────────────────────────────────────────────
    story.append(Paragraph("4. Logging and Monitoring Implementation", s["h1"]))

    story.append(Paragraph("4.1 Structured JSON Logging", s["h2"]))
    story.append(Paragraph(
        "The application uses Python's built-in logging module extended by "
        "python-json-logger to emit every log record as a single-line JSON "
        "object. Each record includes: timestamp (ISO 8601), logger name, "
        "level, message, service name (static: 'iris-prediction-api'), and "
        "arbitrary key–value fields supplied by the caller. Structured logs "
        "are machine-parseable, eliminating the need for brittle regex-based "
        "log parsing in downstream analytics pipelines.",
        s["body"]
    ))

    story.append(Paragraph("Example log record (formatted for readability):", s["body"]))
    story.append(Paragraph(
        '{ "asctime": "2026-05-25T17:42:01.123Z",<br/>'
        '  "name": "app.main", "level": "INFO",<br/>'
        '  "message": "Prediction success",<br/>'
        '  "service": "iris-prediction-api",<br/>'
        '  "request_id": "a1b2c3d4-...",<br/>'
        '  "prediction": "setosa", "confidence": 1.0,<br/>'
        '  "latency_ms": 2.41 }',
        s["code"]
    ))

    story.append(Paragraph("4.2 Rotating File Handler", s["h2"]))
    story.append(Paragraph(
        "In addition to the stdout console handler (for Docker log drivers), "
        "a RotatingFileHandler writes logs to logs/api.log with a maximum "
        "file size of 10 MB and up to 5 backup files (api.log.1 … api.log.5). "
        "When the active file exceeds 10 MB, it is renamed and a new file is "
        "opened. This prevents unbounded disk consumption without losing "
        "recent history.",
        s["body"]
    ))

    story.append(Paragraph("4.3 In-Process Operational Metrics", s["h2"]))
    story.append(Paragraph(
        "The MetricsStore class (app/monitoring.py) maintains thread-safe "
        "counters for total_requests, successful_predictions, failed_requests, "
        "and per-class prediction counts. A rolling deque of the last 1,000 "
        "latency measurements (in milliseconds) enables computation of the "
        "average and 95th-percentile latency without unbounded memory growth. "
        "All counters are protected by a threading.Lock to prevent race "
        "conditions under concurrent requests.",
        s["body"]
    ))

    metrics_data = [
        ["Metric", "Description", "Alerting Threshold (example)"],
        ["total_requests",        "Cumulative request count",          "—"],
        ["successful_predictions","Requests returning HTTP 200",        "—"],
        ["failed_requests",       "Requests returning non-2xx",        "> 1 % of total"],
        ["avg_latency_ms",        "Rolling mean latency",              "> 100 ms"],
        ["p95_latency_ms",        "95th-percentile latency",           "> 500 ms"],
        ["error_rate_percent",    "failed / total × 100",              "> 5 %"],
        ["requests_per_class",    "Per-class prediction distribution", "Skew > 3σ"],
    ]
    mt = Table(metrics_data, colWidths=[4.0*cm, 6.5*cm, 5.0*cm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SECONDARY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.3*cm))

    story.append(hr(s))

    # ── 5. Health Check Best Practices ────────────────────────────────────────
    story.append(Paragraph("5. Health Check Best Practices", s["h1"]))
    story.append(Paragraph(
        "Health checks are a fundamental primitive of cloud-native deployments. "
        "Kubernetes, Docker Swarm, AWS ECS, and most other orchestrators use "
        "health probes to determine whether a replica should receive traffic and "
        "whether it should be automatically replaced.",
        s["body"]
    ))

    story.append(Paragraph("5.1 Liveness vs. Readiness", s["h2"]))
    story.append(Paragraph(
        "A <b>liveness probe</b> answers the question: 'Is the process alive?' "
        "If the probe fails, the container is killed and restarted. It should "
        "only fail for unrecoverable conditions — a deadlock, an OOM-killed "
        "subprocess, or a corrupted global state. A <b>readiness probe</b> "
        "answers: 'Is the service ready to accept traffic?' It may fail transiently "
        "while the model is loading or while a dependency (database, feature store) "
        "is unavailable. Failing the readiness probe removes the pod from the "
        "load-balancer rotation without restarting it.",
        s["body"]
    ))

    story.append(Paragraph(
        "The /health endpoint in this project combines both concerns into a single "
        "response. In a Kubernetes deployment manifest, the same path can be "
        "referenced for both livenessProbe and readinessProbe; the distinction is "
        "made by configuring different failure thresholds for each probe type.",
        s["body"]
    ))

    story.append(Paragraph("5.2 Health Check Parameters", s["h2"]))
    hc_data = [
        ["Parameter",       "Docker Compose Value", "Kubernetes Equivalent"],
        ["initialDelaySeconds", "15 s (start_period)", "initialDelaySeconds: 15"],
        ["periodSeconds",       "30 s (interval)",      "periodSeconds: 30"],
        ["timeoutSeconds",      "10 s (timeout)",       "timeoutSeconds: 10"],
        ["failureThreshold",    "3 (retries)",          "failureThreshold: 3"],
    ]
    hc_table = Table(hc_data, colWidths=[4.5*cm, 5.5*cm, 5.5*cm])
    hc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(hc_table)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5.3 Deep Health Checks", s["h2"]))
    story.append(Paragraph(
        "A shallow health check merely verifies that the HTTP server is "
        "accepting connections. A deep health check also validates that the "
        "model is loaded, that critical file paths are accessible, and "
        "optionally that a canary prediction on a known input returns the "
        "expected output. This project's /health endpoint currently implements "
        "a mid-depth check: it confirms that the model object is in memory. "
        "In a production setting, the canary prediction check can be added "
        "with a performance budget of a few milliseconds.",
        s["body"]
    ))
    story.append(hr(s))

    # ── 6. Handling Unexpected Behaviour & Drift ──────────────────────────────
    story.append(Paragraph("6. Handling Unexpected Behaviour and Performance Drift", s["h1"]))

    story.append(Paragraph("6.1 Input Validation as the First Line of Defence", s["h2"]))
    story.append(Paragraph(
        "Pydantic schemas enforce type correctness and value ranges at the API "
        "boundary before any inference code is reached. Fields with out-of-range "
        "values or wrong types return a 422 response with a detailed error message. "
        "This prevents obviously malformed inputs from consuming model resources "
        "and polluting performance metrics.",
        s["body"]
    ))

    story.append(Paragraph("6.2 Data Drift Detection", s["h2"]))
    story.append(Paragraph(
        "Data drift occurs when the distribution of incoming feature values "
        "shifts away from the training distribution. In a production system, "
        "this can be detected by logging feature values with each request and "
        "running a statistical test (Kolmogorov–Smirnov, Population Stability "
        "Index, or Jensen–Shannon divergence) on a rolling window of recent "
        "requests compared to the training distribution. Tools such as "
        "Evidently AI, WhyLogs, or Amazon SageMaker Model Monitor provide "
        "managed implementations of this pattern.",
        s["body"]
    ))

    story.append(Paragraph("6.3 Concept Drift and Retraining Triggers", s["h2"]))
    story.append(Paragraph(
        "Even when input distributions are stable, the relationship between "
        "inputs and the correct output may change (concept drift). Detecting "
        "concept drift requires ground truth labels for recent predictions, "
        "which are not always available in real time. Common strategies include: "
        "(a) shadow deployment — running the new and old models in parallel and "
        "comparing outputs; (b) canary release — routing a small percentage of "
        "traffic to the new model and monitoring error rates; (c) champion/ "
        "challenger testing — periodically retraining on recent data and "
        "promoting the challenger if it outperforms the champion on a held-out "
        "evaluation set.",
        s["body"]
    ))

    story.append(Paragraph("6.4 Circuit Breaker Pattern", s["h2"]))
    story.append(Paragraph(
        "When the model service is overloaded or a downstream dependency fails, "
        "the circuit breaker pattern prevents cascading failures by returning a "
        "fast error to callers rather than queuing requests until timeouts occur. "
        "In Python, the tenacity or pybreaker libraries implement this pattern. "
        "The /health endpoint can expose circuit-breaker state so that load "
        "balancers can shed traffic proactively.",
        s["body"]
    ))
    story.append(hr(s))

    # ── 7. Maintenance of Deployed AI Services ────────────────────────────────
    story.append(Paragraph("7. Maintenance of Deployed AI Services", s["h1"]))

    story.append(Paragraph("7.1 Versioning Strategy", s["h2"]))
    story.append(Paragraph(
        "The API version (1.0.0) is embedded in the Docker image tag and "
        "returned by the /health endpoint. When a new model version is "
        "released, the image is rebuilt with an incremented tag. Rolling "
        "updates in Kubernetes replace old pods with new ones without "
        "downtime, using the RollingUpdate deployment strategy with a "
        "maxSurge of 1 and maxUnavailable of 0.",
        s["body"]
    ))

    story.append(Paragraph("7.2 Model Artefact Management", s["h2"]))
    story.append(Paragraph(
        "The iris_model.joblib artefact is baked into the Docker image at "
        "build time, ensuring that the image is fully self-contained and "
        "deployable without external dependencies. For larger models or "
        "frequent retraining cycles, the artefact should be stored in object "
        "storage (S3, GCS) and fetched at container startup, with the "
        "artefact URI passed as an environment variable.",
        s["body"]
    ))

    story.append(Paragraph("7.3 Log Aggregation and Alerting", s["h2"]))
    story.append(Paragraph(
        "Structured JSON logs emitted to stdout are captured by the Docker "
        "log driver (json-file by default). In production, a log-shipper "
        "sidecar (Fluent Bit, Filebeat) forwards logs to a central store "
        "(Elasticsearch, Loki, Cloud Logging). Dashboards in Grafana or "
        "Kibana visualise request volume, error rates, and latency "
        "percentiles. Alert rules fire when error_rate_percent exceeds 5 % "
        "or p95_latency_ms exceeds 500 ms for a sustained window.",
        s["body"]
    ))

    story.append(Paragraph("7.4 Dependency Patching", s["h2"]))
    story.append(Paragraph(
        "The base image (python:3.11-slim) should be rebuilt regularly to "
        "incorporate OS security patches. Dependabot or Renovate can "
        "automate dependency version updates in requirements.txt, and a CI "
        "pipeline can rebuild and re-test the image on every pull request. "
        "Container image scanning tools (Trivy, Snyk, Grype) should be "
        "integrated into the CI pipeline to detect known CVEs before "
        "an image is promoted to production.",
        s["body"]
    ))

    story.append(Paragraph("7.5 Capacity Planning", s["h2"]))
    story.append(Paragraph(
        "The Iris classifier is a lightweight sklearn model; a single "
        "CPU-bound worker can handle thousands of requests per second at "
        "sub-millisecond latency. For larger deep-learning models, capacity "
        "planning must account for GPU availability, batch size, and model "
        "warm-up time. Horizontal Pod Autoscaler (HPA) in Kubernetes scales "
        "the number of replicas based on CPU utilisation or custom metrics "
        "exposed by the /metrics endpoint.",
        s["body"]
    ))
    story.append(hr(s))

    # ── 8. Project Summary ─────────────────────────────────────────────────────
    story.append(Paragraph("8. Project Summary and File Reference", s["h1"]))

    file_data = [
        ["File / Directory",           "Purpose"],
        ["model/train_and_save.py",    "Trains RandomForest on Iris data; saves iris_model.joblib + metadata"],
        ["app/main.py",                "FastAPI app: endpoints, middleware, lifespan model loading"],
        ["app/model.py",               "Singleton model loader and predict_single / predict_batch functions"],
        ["app/monitoring.py",          "Thread-safe MetricsStore: counters + rolling latency deque"],
        ["app/logger_config.py",       "JSON logger with rotating file handler"],
        ["app/schemas.py",             "Pydantic v2 request/response schemas with field validation"],
        ["tests/test_api.py",          "pytest suite covering all endpoints"],
        ["Dockerfile",                 "Multi-stage build; non-root user; HEALTHCHECK"],
        ["docker-compose.yml",         "Service definition; volume mounts; resource limits"],
        ["requirements.txt",           "Pinned Python dependencies"],
        ["generate_report.py",         "Generates this PDF using reportlab"],
    ]
    ft = Table(file_data, colWidths=[6.0*cm, 9.5*cm])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#b0bec5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("WORDWRAP", (0, 0), (-1, -1), True),
    ]))
    story.append(ft)
    story.append(Spacer(1, 0.4*cm))

    story.append(hr(s))

    # ── 9. Conclusion ──────────────────────────────────────────────────────────
    story.append(Paragraph("9. Conclusion", s["h1"]))
    story.append(Paragraph(
        "This project demonstrates that transforming a machine-learning model "
        "from an experiment into a maintainable production service requires "
        "deliberate engineering investment across containerisation, API design, "
        "structured observability, and health management. The Iris classifier "
        "example is intentionally simple, allowing attention to focus on the "
        "deployment infrastructure rather than model complexity. The patterns "
        "established here — immutable container images, stateless REST APIs, "
        "structured JSON logs, rolling metric counters, and health endpoints — "
        "scale directly to production ML systems serving millions of requests "
        "per day.",
        s["body"]
    ))
    story.append(Paragraph(
        "Future work for a production hardening of this system would include: "
        "(1) integration with Prometheus and Grafana for time-series metrics and "
        "alerting dashboards; (2) OpenTelemetry distributed tracing across "
        "microservice boundaries; (3) automated retraining pipelines triggered "
        "by data-drift detection; (4) A/B testing infrastructure for safe "
        "model upgrades; and (5) formal SLO definitions (e.g., 99.9 % "
        "availability, p99 latency < 200 ms) with automated SLO burn-rate alerts.",
        s["body"]
    ))

    story.append(hr(s))
    story.append(Paragraph(
        "© 2026 AI Deployment Project — Generated by generate_report.py using ReportLab",
        s["caption"]
    ))

    doc.build(story)
    print(f"[OK] Report saved -> {OUTPUT_PATH}")


if __name__ == "__main__":
    build_document()
