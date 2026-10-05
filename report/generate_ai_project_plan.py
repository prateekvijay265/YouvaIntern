"""
AI Project Plan PDF Generator
Generates a comprehensive 2000+ word AI project planning document with Gantt chart.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics import renderPDF
import datetime

# ─────────────────────────────── Color Palette ───────────────────────────────
NAVY        = colors.HexColor("#0D1B2A")
ROYAL_BLUE  = colors.HexColor("#1A56DB")
STEEL_BLUE  = colors.HexColor("#3A86FF")
ACCENT_TEAL = colors.HexColor("#06B6D4")
LIGHT_BLUE  = colors.HexColor("#EFF6FF")
MEDIUM_GRAY = colors.HexColor("#6B7280")
LIGHT_GRAY  = colors.HexColor("#F3F4F6")
DARK_GRAY   = colors.HexColor("#1F2937")
WHITE       = colors.white
SUCCESS     = colors.HexColor("#10B981")
WARNING     = colors.HexColor("#F59E0B")
DANGER      = colors.HexColor("#EF4444")


# ─────────────────────────── Custom Gantt Chart ──────────────────────────────
class GanttChart(Flowable):
    """Custom Gantt chart flowable."""

    def __init__(self, tasks, width=17*cm, row_height=0.65*cm):
        super().__init__()
        self.tasks = tasks          # list of (phase, task, start_week, duration_weeks, color)
        self.width = width
        self.row_height = row_height
        self.header_height = 1.2 * cm
        self.left_col = 5.5 * cm   # width of label column
        self.total_weeks = 26
        self.height = self.header_height + len(tasks) * self.row_height + 0.4 * cm

    def draw(self):
        chart_width = self.width - self.left_col
        week_width  = chart_width / self.total_weeks
        y_top       = self.height - self.header_height

        # ── Background ──
        self.canv.setFillColor(LIGHT_GRAY)
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)

        # ── Header bar ──
        self.canv.setFillColor(NAVY)
        self.canv.roundRect(0, y_top, self.width, self.header_height, 4, fill=1, stroke=0)
        self.canv.setFillColor(WHITE)
        self.canv.setFont("Helvetica-Bold", 8)
        self.canv.drawString(6, y_top + self.header_height/2 - 4, "Task / Milestone")

        # Week headers
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        for i, month in enumerate(months):
            x = self.left_col + i * (chart_width / 6)
            self.canv.setFillColor(WHITE)
            self.canv.setFont("Helvetica-Bold", 7)
            self.canv.drawCentredString(x + chart_width/12, y_top + self.header_height/2 - 4, month)

        # Week tick marks
        for w in range(self.total_weeks + 1):
            x = self.left_col + w * week_width
            self.canv.setStrokeColor(colors.HexColor("#334155"))
            self.canv.setLineWidth(0.3)
            self.canv.line(x, y_top, x, y_top + 5)

        # ── Phase groupings (alternating row bg) ──
        current_phase = None
        for idx, (phase, task, start, dur, clr) in enumerate(self.tasks):
            row_y = y_top - (idx + 1) * self.row_height
            bg = colors.HexColor("#E2E8F0") if idx % 2 == 0 else WHITE
            self.canv.setFillColor(bg)
            self.canv.rect(0, row_y, self.width, self.row_height, fill=1, stroke=0)

            # Task label
            self.canv.setFillColor(DARK_GRAY)
            self.canv.setFont("Helvetica", 7)
            label = task if len(task) <= 32 else task[:30] + "…"
            self.canv.drawString(6, row_y + self.row_height/2 - 3.5, label)

        # ── Vertical grid lines ──
        for w in range(self.total_weeks + 1):
            x = self.left_col + w * week_width
            self.canv.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.canv.setLineWidth(0.3)
            self.canv.line(x, 0, x, y_top)

        # ── Gantt bars ──
        for idx, (phase, task, start, dur, clr) in enumerate(self.tasks):
            row_y   = y_top - (idx + 1) * self.row_height
            bar_x   = self.left_col + start * week_width
            bar_w   = dur * week_width
            bar_pad = self.row_height * 0.15
            bar_h   = self.row_height - 2 * bar_pad

            # Shadow
            self.canv.setFillColor(colors.HexColor("#94A3B8"))
            self.canv.roundRect(bar_x + 1, row_y + bar_pad - 1, bar_w, bar_h, 2, fill=1, stroke=0)

            # Bar
            self.canv.setFillColor(clr)
            self.canv.roundRect(bar_x, row_y + bar_pad, bar_w, bar_h, 2, fill=1, stroke=0)

            # Highlight strip
            self.canv.setFillColor(colors.HexColor("#FFFFFF"))
            self.canv.setFillAlpha(0.25)
            self.canv.roundRect(bar_x, row_y + bar_pad + bar_h*0.6, bar_w, bar_h*0.35, 2, fill=1, stroke=0)
            self.canv.setFillAlpha(1.0)

        # ── Border ──
        self.canv.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.canv.setLineWidth(0.5)
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=0, stroke=1)


# ──────────────────────────── Risk Matrix Table ───────────────────────────────
def build_risk_matrix():
    data = [
        ["Risk Factor", "Likelihood", "Impact", "Score", "Mitigation Strategy"],
        ["Data quality / missing values",     "High",   "High",   "9",
         "Multi-source validation + imputation pipelines"],
        ["Model overfitting",                 "Medium", "High",   "6",
         "Cross-validation, regularisation, dropout"],
        ["Regulatory / privacy compliance",   "Medium", "High",   "6",
         "GDPR-aligned governance, anonymisation"],
        ["Infrastructure cost overrun",       "Low",    "Medium", "3",
         "Cloud budget alerts, serverless scaling"],
        ["Algorithmic bias / fairness issues","Medium", "High",   "6",
         "Bias audits, fairness metrics in eval suite"],
        ["Key personnel departure",           "Low",    "High",   "4",
         "Documentation, cross-training, knowledge base"],
        ["External API / data source changes","Medium", "Medium", "4",
         "Versioned ingestion adapters, fallback mirrors"],
        ["Scope creep",                       "High",   "Medium", "6",
         "Strict change-control board & sprint reviews"],
    ]

    def risk_color(score):
        s = int(score)
        if s >= 7: return DANGER
        if s >= 4: return WARNING
        return SUCCESS

    col_widths = [4.5*cm, 2*cm, 2*cm, 1.5*cm, 6.5*cm]
    style = [
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 8),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("FONTSIZE",      (0,1), (-1,-1), 7.5),
        ("ALIGN",         (0,1), (0,-1), "LEFT"),
        ("ALIGN",         (4,1), (4,-1), "LEFT"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]
    for i, row in enumerate(data[1:], 1):
        clr = risk_color(row[3])
        style.append(("BACKGROUND", (3, i), (3, i), clr))
        style.append(("TEXTCOLOR",  (3, i), (3, i), WHITE))
        style.append(("FONTNAME",   (3, i), (3, i), "Helvetica-Bold"))

    return Table(data, colWidths=col_widths, style=TableStyle(style), repeatRows=1)


# ──────────────────────────── Styles Setup ────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontSize=28, fontName="Helvetica-Bold",
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=6, leading=34
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle", fontSize=14, fontName="Helvetica",
        textColor=ROYAL_BLUE, alignment=TA_CENTER, spaceAfter=4
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta", fontSize=10, fontName="Helvetica",
        textColor=MEDIUM_GRAY, alignment=TA_CENTER, spaceAfter=3
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontSize=16, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=18, spaceAfter=8, leading=20
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontSize=12, fontName="Helvetica-Bold",
        textColor=ROYAL_BLUE, spaceBefore=12, spaceAfter=5, leading=15
    )
    styles["h3"] = ParagraphStyle(
        "h3", fontSize=10.5, fontName="Helvetica-Bold",
        textColor=DARK_GRAY, spaceBefore=8, spaceAfter=4
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=9.5, fontName="Helvetica",
        textColor=DARK_GRAY, spaceAfter=6, leading=14, alignment=TA_JUSTIFY
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontSize=9.5, fontName="Helvetica",
        textColor=DARK_GRAY, spaceAfter=3, leading=13,
        leftIndent=14, bulletIndent=4, alignment=TA_LEFT
    )
    styles["caption"] = ParagraphStyle(
        "caption", fontSize=8, fontName="Helvetica-Oblique",
        textColor=MEDIUM_GRAY, alignment=TA_CENTER, spaceAfter=4
    )
    styles["callout"] = ParagraphStyle(
        "callout", fontSize=9.5, fontName="Helvetica",
        textColor=DARK_GRAY, leading=14, alignment=TA_JUSTIFY,
        leftIndent=10, rightIndent=10, spaceAfter=6
    )
    return styles


# ──────────────────────────── Helper: section divider ────────────────────────
def divider(color=STEEL_BLUE, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=2)


def callout_box(text, styles, bg=LIGHT_BLUE, border=STEEL_BLUE):
    """Returns a styled callout box as a Table."""
    p = Paragraph(text, styles["callout"])
    t = Table([[p]], colWidths=[16.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LINECOLOR",  (0,0), (-1,-1), border),
        ("LINEWIDTH",  (0,0), (-1,-1), 1),
        ("BOX",        (0,0), (-1,-1), 1.5, border),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    return t


# ──────────────────────────── Cover Page ─────────────────────────────────────
def build_cover(styles):
    elems = []

    # Decorative top banner drawn via a Table with colored background
    banner_data = [[Paragraph(
        "<font color='white'><b>CONFIDENTIAL &nbsp;|&nbsp; AI INITIATIVE PLANNING DOCUMENT</b></font>",
        ParagraphStyle("banner", fontSize=9, fontName="Helvetica-Bold",
                       textColor=WHITE, alignment=TA_CENTER)
    )]]
    banner = Table(banner_data, colWidths=[17*cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    elems.append(banner)
    elems.append(Spacer(1, 1.5*cm))

    # Title block
    elems.append(Paragraph("Predictive Analytics AI Initiative", styles["cover_title"]))
    elems.append(Spacer(1, 0.3*cm))

    accent_line = Table([[""]], colWidths=[6*cm])
    accent_line.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), STEEL_BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))
    # Centre the accent line
    wrapper = Table([[accent_line]], colWidths=[17*cm])
    wrapper.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    elems.append(wrapper)
    elems.append(Spacer(1, 0.5*cm))

    elems.append(Paragraph(
        "Comprehensive Project Plan for an End-to-End Machine Learning Solution<br/>"
        "Leveraging Publicly Available Datasets for Demand Forecasting",
        styles["cover_subtitle"]
    ))
    elems.append(Spacer(1, 2*cm))

    # Meta table
    meta = [
        ["Document Version:", "1.0 — Final Draft"],
        ["Prepared By:",      "AI Strategy & Data Science Team"],
        ["Project Sponsor:",  "Chief Data Officer"],
        ["Classification:",   "Internal — Restricted"],
        ["Date:",             datetime.date.today().strftime("%B %d, %Y")],
        ["Project Duration:", "6 Months (January – June 2026)"],
    ]
    meta_table = Table(meta, colWidths=[5*cm, 10*cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR",     (0,0), (0,-1), NAVY),
        ("TEXTCOLOR",     (1,0), (1,-1), DARK_GRAY),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
    ]))
    # Centre the meta table
    centre_meta = Table([[meta_table]], colWidths=[17*cm])
    centre_meta.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "CENTER")]))
    elems.append(centre_meta)
    elems.append(Spacer(1, 2*cm))

    elems.append(Paragraph(
        "This document is prepared in accordance with organisational AI governance standards and "
        "complies with GDPR, ISO/IEC 42001, and internal data handling policies.",
        ParagraphStyle("disclaimer", fontSize=8, fontName="Helvetica-Oblique",
                       textColor=MEDIUM_GRAY, alignment=TA_CENTER)
    ))
    elems.append(PageBreak())
    return elems


# ──────────────────────────── Executive Summary ───────────────────────────────
def build_executive_summary(styles):
    elems = []
    elems.append(Paragraph("Executive Summary", styles["h1"]))
    elems.append(divider())

    text = (
        "Organisations operating in data-rich environments are increasingly relying on predictive analytics "
        "to move from reactive to proactive decision-making. This document presents a complete project plan for "
        "designing, developing, validating, and deploying a production-grade Machine Learning (ML) system focused "
        "on retail demand forecasting — one of the highest-value predictive analytics use-cases with measurable "
        "return on investment."
    )
    elems.append(Paragraph(text, styles["body"]))

    text2 = (
        "The proposed initiative will harness publicly available datasets — primarily the UCI Online Retail II "
        "dataset, the M5 Forecasting Competition data, Google Trends API signals, and macroeconomic indicators "
        "from the World Bank Open Data portal — to train, validate, and continuously improve a suite of "
        "forecasting models. The six-month roadmap spans data engineering, model development, ethical review, "
        "stakeholder validation, and phased production rollout."
    )
    elems.append(Paragraph(text2, styles["body"]))

    kpi_data = [
        ["Key Metric", "Baseline", "Target (6 months)"],
        ["Forecast MAE (units)", "~420", "≤ 260 (−38%)"],
        ["Inventory holding cost", "Baseline", "−15% reduction"],
        ["Stockout rate",          "8.2%",     "≤ 4.5%"],
        ["Model inference latency","N/A",       "< 200 ms (p99)"],
        ["Data pipeline SLA",      "Manual",    "99.5% automated"],
    ]
    kpi_table = Table(kpi_data, colWidths=[5.5*cm, 3.5*cm, 5.5*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), ROYAL_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elems.append(Spacer(1, 6))
    elems.append(kpi_table)
    elems.append(Paragraph("Table 1 — Key Performance Indicators", styles["caption"]))
    elems.append(PageBreak())
    return elems


# ──────────────────────────── Section 1: Objectives ──────────────────────────
def build_objectives(styles):
    elems = []
    elems.append(Paragraph("1. Project Objectives", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph("1.1 Primary Objective", styles["h2"]))
    elems.append(Paragraph(
        "To design and deploy a scalable, explainable, and ethically-governed predictive analytics platform "
        "that generates 28-day ahead retail demand forecasts at SKU-store granularity with a Mean Absolute "
        "Percentage Error (MAPE) of less than 12%, improving current manual forecasting accuracy by at least 35%.",
        styles["body"]
    ))

    elems.append(Paragraph("1.2 Secondary Objectives", styles["h2"]))
    secondary = [
        ("Data Engineering Excellence",
         "Build a robust, versioned, and auditable data pipeline that ingests, validates, and transforms "
         "publicly available datasets into ML-ready feature stores with zero manual intervention."),
        ("Model Transparency & Explainability",
         "Implement SHAP (SHapley Additive exPlanations) and LIME frameworks to ensure all predictions "
         "are interpretable by business stakeholders, regulators, and the end-user dashboard."),
        ("Ethical AI Integration",
         "Conduct bias audits, fairness assessments, and document model cards for every candidate model "
         "prior to production deployment, in alignment with the EU AI Act requirements."),
        ("Operational Resilience",
         "Implement MLOps best practices including model versioning (MLflow), CI/CD pipelines (GitHub Actions), "
         "drift detection (Evidently AI), and automated retraining triggers."),
        ("Stakeholder Enablement",
         "Deliver an interactive BI dashboard (Apache Superset / Streamlit) that surfaces forecast insights "
         "to supply-chain planners without requiring ML expertise."),
    ]
    for title, body in secondary:
        elems.append(Paragraph(f"<b>{title}:</b> {body}", styles["bullet"]))

    elems.append(Paragraph("1.3 Hypothesis Formulation", styles["h2"]))
    elems.append(callout_box(
        "<b>Primary Hypothesis (H₁):</b> A gradient-boosted ensemble model trained on historical retail "
        "transaction data enriched with external signals (Google Trends, weather, macro indicators) will "
        "produce demand forecasts with statistically significantly lower error (MAPE, RMSE) compared to a "
        "naïve seasonal baseline model at the 5% significance level (p &lt; 0.05), when evaluated on a "
        "held-out test set spanning 90 days.",
        styles, bg=LIGHT_BLUE, border=STEEL_BLUE
    ))
    elems.append(Spacer(1, 6))
    elems.append(callout_box(
        "<b>Null Hypothesis (H₀):</b> No statistically significant difference exists between the predictive "
        "accuracy of the proposed ML model and the seasonal naïve baseline.",
        styles, bg=colors.HexColor("#FEF3C7"), border=WARNING
    ))
    elems.append(Spacer(1, 6))

    elems.append(Paragraph("1.4 SMART Goal Framework", styles["h2"]))
    smart = [
        ["Criterion",   "Definition",                                               "This Project"],
        ["Specific",    "Well-defined, clear goal",                                 "Forecast retail demand at SKU-store level"],
        ["Measurable",  "Quantifiable success indicator",                           "MAPE ≤ 12%, MAE ≤ 260 units"],
        ["Achievable",  "Realistic given resources",                                "6-person team, 6-month horizon"],
        ["Relevant",    "Aligned with business priorities",                         "Supply-chain cost reduction initiative"],
        ["Time-bound",  "Clear deadline",                                           "Production launch by end of Month 6"],
    ]
    t = Table(smart, colWidths=[2.5*cm, 5*cm, 9*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 2 — SMART Goal Framework", styles["caption"]))
    elems.append(PageBreak())
    return elems


# ──────────────────────── Section 2: Technology Stack ────────────────────────
def build_technology(styles):
    elems = []
    elems.append(Paragraph("2. Tool & Technology Selection", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph(
        "Technology selection follows a four-dimensional evaluation framework: (1) technical fit, "
        "(2) open-source community maturity, (3) total cost of ownership, and (4) compliance with "
        "organisational security standards. All tooling is open-source or freely licensed for non-commercial "
        "academic benchmarking.",
        styles["body"]
    ))

    tech_data = [
        ["Layer",           "Technology / Tool",        "Version",  "Rationale"],
        ["Data Storage",    "PostgreSQL + MinIO",       "15 / 2023","ACID-compliant RDBMS + S3-compatible object store"],
        ["Data Pipeline",   "Apache Airflow",           "2.8",      "DAG-based orchestration with retry and SLA monitoring"],
        ["Feature Store",   "Feast",                    "0.38",     "Point-in-time correct feature retrieval prevents data leakage"],
        ["ML Framework",    "scikit-learn / XGBoost",   "1.4 / 2.0","Mature gradient boosting with SHAP native support"],
        ["Deep Learning",   "PyTorch + Darts",          "2.2 / 0.27","N-BEATS / TFT for sequence modelling"],
        ["Experiment Track","MLflow",                   "2.11",     "Model registry, metrics logging, artifact management"],
        ["Serving",         "FastAPI + BentoML",        "0.110 / 1.2","REST API serving with model packaging"],
        ["Drift Detection", "Evidently AI",             "0.4",      "Data drift + model performance monitoring reports"],
        ["Explainability",  "SHAP + LIME",              "0.45 / 0.28","Local and global feature attribution"],
        ["Visualisation",   "Streamlit + Plotly",       "1.32 / 5.20","Rapid interactive dashboard development"],
        ["CI/CD",           "GitHub Actions",           "—",        "Automated testing, linting, model validation gates"],
        ["Container",       "Docker + Kubernetes",      "25.0 / 1.29","Reproducible environments, horizontal scaling"],
        ["Cloud",           "GCP (Vertex AI + BigQuery)","—",        "Managed training, serverless SQL analytics"],
    ]
    col_widths = [2.8*cm, 3.5*cm, 2.2*cm, 8*cm]
    t = Table(tech_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 3 — Technology Stack Matrix", styles["caption"]))
    elems.append(PageBreak())
    return elems


# ────────────────────── Section 3: Methodology ───────────────────────────────
def build_methodology(styles):
    elems = []
    elems.append(Paragraph("3. Methodology", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph("3.1 Data Collection Strategy", styles["h2"]))
    elems.append(Paragraph(
        "The project adopts a multi-source data ingestion strategy to maximise signal richness while remaining "
        "compliant with open-data licences. Data provenance is tracked from source to feature using lineage "
        "metadata stored in an Apache Atlas catalogue.",
        styles["body"]
    ))

    datasets = [
        ["Dataset", "Source", "Records", "Licence", "Primary Use"],
        ["UCI Online Retail II",       "UC Irvine ML Repo", "1.07M",    "CC BY 4.0",    "Transaction history"],
        ["M5 Competition Data",        "Kaggle / Walmart",  "58K series","CC BY 4.0",    "Hierarchical forecasting"],
        ["Google Trends (pytrends)",   "Google API",        "Dynamic",  "Free / ToS",   "Consumer intent signals"],
        ["World Bank Open Data",       "worldbank.org",     "~5K series","CC BY 4.0",    "Macro-economic context"],
        ["OpenWeather API (history)",  "openweathermap.org","5 years",  "Free tier",    "Weather seasonality"],
        ["Public Holidays (holidays)", "PyPI library",      "All years","MIT",          "Calendar features"],
    ]
    t = Table(datasets, colWidths=[3.5*cm, 3*cm, 2*cm, 2*cm, 5.5*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), ROYAL_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 4 — Public Datasets Used", styles["caption"]))

    elems.append(Paragraph("3.2 Data Preprocessing Pipeline", styles["h2"]))
    steps = [
        ("Step 1 — Ingestion",
         "Airflow DAGs pull daily incremental snapshots from each source into the Bronze layer of a "
         "Medallion architecture (Bronze → Silver → Gold). Raw files are stored in MinIO with SHA-256 checksums."),
        ("Step 2 — Validation",
         "Great Expectations validates schema conformity, null ratios (threshold: < 5%), value ranges, "
         "and referential integrity. Failed rows are quarantined with full audit trail."),
        ("Step 3 — Cleaning & Transformation",
         "Missing values are imputed using k-NN imputation for numerical and mode-fill for categorical "
         "variables. Outliers beyond 3.5 IQR are Winsorised. Returns (negative quantities) are netted."),
        ("Step 4 — Feature Engineering",
         "50+ features including lag variables (t−1 to t−28), rolling statistics (7-day, 28-day, 90-day), "
         "Fourier terms for seasonality, calendar dummy variables, and external signal embeddings."),
        ("Step 5 — Feature Store Materialisation",
         "Features are point-in-time joined and materialised into Feast online (Redis) and offline "
         "(BigQuery) stores, preventing any target leakage through temporal boundaries."),
    ]
    for title, body in steps:
        elems.append(Paragraph(f"<b>{title}:</b> {body}", styles["bullet"]))

    elems.append(Paragraph("3.3 Model Development Approach", styles["h2"]))
    elems.append(Paragraph(
        "The modelling strategy follows a structured tournament approach. Three model families are trained "
        "and evaluated in parallel before an ensemble champion is selected:",
        styles["body"]
    ))
    models = [
        ("<b>Baseline Models</b>",
         "Seasonal Naïve, Exponential Smoothing (ETS/Holt-Winters) — serve as the performance floor "
         "and statistical hypothesis test benchmark."),
        ("<b>Tree-Based Models</b>",
         "LightGBM and XGBoost — trained with Optuna hyperparameter optimisation (500 trials, TPE sampler). "
         "Fast inference, high accuracy, native SHAP support."),
        ("<b>Deep Learning Models</b>",
         "N-BEATS (neural basis expansion) and Temporal Fusion Transformer (TFT) — capture complex "
         "temporal dependencies and covariate relationships in long sequences."),
        ("<b>Ensemble / Stacking</b>",
         "A meta-learner (Ridge regression) combines predictions from all base models. Weighted blending "
         "guided by per-SKU validation performance."),
    ]
    for title, body in models:
        elems.append(Paragraph(f"{title}: {body}", styles["bullet"]))

    elems.append(Paragraph("3.4 Evaluation Techniques", styles["h2"]))
    elems.append(Paragraph(
        "A walk-forward (expanding window) cross-validation strategy is used to avoid data leakage and "
        "simulate real deployment conditions. The final 90-day period is reserved as a held-out test set "
        "and is never used during training or model selection.",
        styles["body"]
    ))

    metrics = [
        ["Metric",    "Formula",                          "Target"],
        ["MAE",       "Mean Absolute Error",              "≤ 260 units"],
        ["RMSE",      "Root Mean Squared Error",          "≤ 380 units"],
        ["MAPE",      "Mean Absolute Percentage Error",   "≤ 12%"],
        ["sMAPE",     "Symmetric MAPE",                   "≤ 11%"],
        ["Pinball",   "Quantile loss (p10, p50, p90)",    "Minimise"],
        ["Winkler",   "Prediction interval quality",      "Minimise"],
    ]
    t = Table(metrics, colWidths=[2.5*cm, 7*cm, 7*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), ACCENT_TEAL),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("GRID",          (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 5 — Evaluation Metrics", styles["caption"]))
    elems.append(PageBreak())
    return elems


# ──────────────────────── Section 4: Gantt Chart ─────────────────────────────
def build_timeline(styles):
    elems = []
    elems.append(Paragraph("4. Project Timeline & Milestones", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph(
        "The project is structured into six consecutive monthly sprints (two-week sub-sprints) with explicit "
        "phase gates requiring sign-off before proceeding. The Gantt chart below represents planned effort "
        "allocation across all workstreams for the full 26-week engagement.",
        styles["body"]
    ))

    # (phase, task_label, start_week, duration_weeks, color)
    tasks = [
        # Phase 1: Initiation (weeks 0–3)
        ("Init", "Project Kick-off & Charter",         0,  2, colors.HexColor("#3A86FF")),
        ("Init", "Stakeholder Alignment Workshops",    1,  2, colors.HexColor("#3A86FF")),
        ("Init", "Data Source Identification",         1,  3, colors.HexColor("#3A86FF")),
        # Phase 2: Data Engineering (weeks 3–9)
        ("Data", "Data Ingestion Pipeline Setup",      3,  4, colors.HexColor("#06B6D4")),
        ("Data", "Data Validation & Governance",       4,  3, colors.HexColor("#06B6D4")),
        ("Data", "Feature Engineering",                6,  4, colors.HexColor("#06B6D4")),
        ("Data", "Feature Store Materialisation",      8,  2, colors.HexColor("#06B6D4")),
        # Phase 3: Modelling (weeks 9–17)
        ("Model","Baseline Model Development",         9,  2, colors.HexColor("#8B5CF6")),
        ("Model","LightGBM / XGBoost Training",        10, 4, colors.HexColor("#8B5CF6")),
        ("Model","Deep Learning (N-BEATS / TFT)",      11, 5, colors.HexColor("#8B5CF6")),
        ("Model","Hyperparameter Optimisation",        13, 3, colors.HexColor("#8B5CF6")),
        ("Model","Ensemble / Stacking",                15, 2, colors.HexColor("#8B5CF6")),
        # Phase 4: Evaluation & Ethics (weeks 16–20)
        ("Eval", "Walk-Forward CV Evaluation",         16, 3, colors.HexColor("#10B981")),
        ("Eval", "Explainability (SHAP / LIME)",       17, 2, colors.HexColor("#10B981")),
        ("Eval", "Bias & Fairness Audit",              18, 2, colors.HexColor("#10B981")),
        ("Eval", "Model Card Preparation",             19, 1, colors.HexColor("#10B981")),
        # Phase 5: Deployment (weeks 19–24)
        ("Deploy","MLOps Pipeline (MLflow / CI-CD)",   19, 3, colors.HexColor("#F59E0B")),
        ("Deploy","API & Dashboard Development",        20, 4, colors.HexColor("#F59E0B")),
        ("Deploy","UAT & Stakeholder Validation",       22, 2, colors.HexColor("#F59E0B")),
        ("Deploy","Shadow Mode Production Deployment", 23, 2, colors.HexColor("#F59E0B")),
        # Phase 6: Monitoring (weeks 24–26)
        ("Mon",  "Drift Monitoring Setup",             24, 2, colors.HexColor("#EF4444")),
        ("Mon",  "Documentation & Handover",           24, 2, colors.HexColor("#EF4444")),
        ("Mon",  "Project Closure & Retrospective",    25, 1, colors.HexColor("#EF4444")),
    ]

    gantt = GanttChart(tasks, width=17*cm, row_height=0.60*cm)
    elems.append(gantt)
    elems.append(Paragraph("Figure 1 — Project Gantt Chart (26-week horizon, Jan–Jun 2026)", styles["caption"]))
    elems.append(Spacer(1, 0.3*cm))

    # Legend
    legend_data = [[
        Paragraph("<font color='white'><b> Phase 1: Initiation </b></font>",
                  ParagraphStyle("l", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
        Paragraph("<font color='white'><b> Phase 2: Data Engineering </b></font>",
                  ParagraphStyle("l", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
        Paragraph("<font color='white'><b> Phase 3: Modelling </b></font>",
                  ParagraphStyle("l", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
        Paragraph("<font color='white'><b> Phase 4: Evaluation </b></font>",
                  ParagraphStyle("l", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
        Paragraph("<font color='white'><b> Phase 5: Deployment </b></font>",
                  ParagraphStyle("l", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
        Paragraph("<font color='white'><b> Phase 6: Monitoring </b></font>",
                  ParagraphStyle("l", fontSize=8, textColor=WHITE, fontName="Helvetica-Bold")),
    ]]
    legend_colors = [
        colors.HexColor("#3A86FF"), colors.HexColor("#06B6D4"),
        colors.HexColor("#8B5CF6"), colors.HexColor("#10B981"),
        colors.HexColor("#F59E0B"), colors.HexColor("#EF4444"),
    ]
    legend = Table(legend_data, colWidths=[2.83*cm]*6)
    bg_cmds = [("BACKGROUND", (i,0), (i,0), legend_colors[i]) for i in range(6)]
    legend.setStyle(TableStyle([
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ] + bg_cmds))
    elems.append(legend)
    elems.append(Paragraph("Figure 1 Legend — Phase Colour Coding", styles["caption"]))

    elems.append(Paragraph("4.1 Key Milestones", styles["h2"]))
    milestones = [
        ["#",  "Milestone",                              "Week", "Gate Criteria"],
        ["M1", "Project Kick-off Complete",              "W2",   "Charter signed; all stakeholders onboarded"],
        ["M2", "Data Pipeline Operational",              "W7",   "All sources ingesting; validation passing 99%+"],
        ["M3", "Feature Store v1.0 Released",            "W10",  "Point-in-time features validated; no leakage"],
        ["M4", "Baseline Models Benchmarked",            "W11",  "MAPE of naïve baseline documented"],
        ["M5", "Champion Model Selected",                "W17",  "Ensemble MAPE ≤ 12%; sign-off by DS lead"],
        ["M6", "Ethics & Fairness Review Passed",        "W20",  "Model card approved by AI Ethics Board"],
        ["M7", "UAT Sign-off",                           "W24",  "≥ 85% stakeholder satisfaction score"],
        ["M8", "Production Go-Live (Shadow Mode)",       "W25",  "System stable; monitoring dashboards live"],
        ["M9", "Project Closure & Lessons Learned",      "W26",  "Final report delivered; retrospective held"],
    ]
    t = Table(milestones, colWidths=[1*cm, 5.5*cm, 1.5*cm, 9*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("ALIGN",         (0,2), (0,-1), "CENTER"),
        ("ALIGN",         (2,0), (2,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 6 — Project Milestones & Phase Gates", styles["caption"]))
    elems.append(PageBreak())
    return elems


# ──────────────── Section 5: Challenges & Risk Mitigation ────────────────────
def build_risks(styles):
    elems = []
    elems.append(Paragraph("5. Potential Challenges & Risk Mitigation", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph(
        "A structured Risk Register has been compiled using a 3×3 likelihood-impact scoring matrix. "
        "Risk owners are assigned at the project kick-off and reviewed at fortnightly sprint reviews. "
        "The register is maintained in the project's Confluence space with version history.",
        styles["body"]
    ))

    elems.append(build_risk_matrix())
    elems.append(Paragraph("Table 7 — Risk Register (Score = Likelihood × Impact, scale 1–3 each)", styles["caption"]))

    elems.append(Paragraph("5.1 Data Governance Framework", styles["h2"]))
    gov_items = [
        "<b>Data Classification:</b> All ingested datasets are classified as Public, Internal, or Sensitive "
        "using a four-tier taxonomy. Processing is restricted to approved compute environments.",
        "<b>Consent & Licensing:</b> Only CC BY, CC0, MIT, or equivalent open licences are used. A licence "
        "inventory is maintained and reviewed quarterly.",
        "<b>Retention & Deletion:</b> Raw data is retained for 24 months; derived features for 36 months. "
        "Automated lifecycle policies enforce deletion on schedule.",
        "<b>Access Control:</b> Role-based access control (RBAC) enforced via Kubernetes namespaces and "
        "BigQuery IAM policies. Least-privilege principle applied throughout.",
        "<b>Audit Logging:</b> All pipeline runs, model training jobs, and prediction requests are logged "
        "with timestamps, user IDs, and data hashes to an immutable audit trail.",
    ]
    for item in gov_items:
        elems.append(Paragraph(item, styles["bullet"]))

    elems.append(Paragraph("5.2 Ethical AI Considerations", styles["h2"]))
    elems.append(Paragraph(
        "The project team is committed to responsible AI development guided by the principles of the EU AI Act "
        "(2024), Google's AI Principles, and the Partnership on AI framework. The following practices are "
        "mandatory and audited at Milestone M6:",
        styles["body"]
    ))
    ethics = [
        "<b>Bias Detection:</b> Disparate Impact Analysis and Equalised Odds tests applied across demographic "
        "proxies (region, seasonality segments). Threshold: max 10% disparity tolerated.",
        "<b>Model Cards:</b> Standardised model card documents (Mitchell et al., 2019 format) published for "
        "every production model, covering intended use, limitations, and performance disaggregates.",
        "<b>Human-in-the-Loop:</b> All forecasts exceeding a ±40% deviation from the prior period trigger "
        "a human review flag before propagation to downstream systems.",
        "<b>Transparency Reporting:</b> Annual AI transparency report published to internal stakeholders "
        "summarising model decisions, errors, and retraining events.",
        "<b>Environmental Impact:</b> Training compute budgets are capped; carbon footprint estimated using "
        "CodeCarbon library and reported in the final project closure document.",
    ]
    for item in ethics:
        elems.append(Paragraph(item, styles["bullet"]))

    elems.append(PageBreak())
    return elems


# ──────────────────────── Section 6: Scalability ─────────────────────────────
def build_scalability(styles):
    elems = []
    elems.append(Paragraph("6. Scalability & Infrastructure Design", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph(
        "The architecture is designed for horizontal scalability from day one. The system must handle "
        "growth from the initial pilot (500 SKUs × 50 stores) to full enterprise deployment (50,000 SKUs × "
        "500 stores) without architectural re-engineering — a 1,000× scale increase in inference volume.",
        styles["body"]
    ))

    arch_data = [
        ["Component",       "Pilot Scale",           "Enterprise Scale",     "Scaling Mechanism"],
        ["Data Ingestion",  "Airflow (2 workers)",   "Airflow on Kubernetes","KubernetesExecutor + autoscaling"],
        ["Feature Store",   "Local Redis",           "Redis Cluster (6 nodes)","Redis Cluster sharding"],
        ["Model Training",  "Single GPU (A100)",     "Distributed (4× A100)","PyTorch DistributedDataParallel"],
        ["Inference API",   "2 FastAPI replicas",    "BentoML + K8s HPA",    "CPU/GPU horizontal pod autoscaler"],
        ["Data Warehouse",  "BigQuery on-demand",    "BigQuery Editions",     "Slot reservations + BI Engine"],
        ["Dashboard",       "Streamlit (1 instance)","Streamlit Cloud / GKE","Containerised, load-balanced"],
    ]
    t = Table(arch_data, colWidths=[3*cm, 3.5*cm, 4*cm, 6*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 8 — Scalability Design Matrix", styles["caption"]))

    elems.append(Paragraph("6.1 MLOps & Continuous Improvement", styles["h2"]))
    mlops = [
        "<b>Automated Retraining:</b> Evidently AI triggers retraining when Population Stability Index (PSI) "
        "exceeds 0.2 on key features, or when rolling 7-day MAPE degrades by more than 3 percentage points.",
        "<b>Model Registry Governance:</b> MLflow model registry enforces four stages: Staging → Validation → "
        "Champion → Archived. Promotion requires automated test suite passage and human approval.",
        "<b>A/B Shadow Testing:</b> New challenger models receive 10% of production traffic in shadow mode "
        "for 14 days before full promotion, enabling risk-free performance comparison.",
        "<b>Canary Deployments:</b> BentoML + Kubernetes enables gradual traffic shifting (5% → 25% → 100%) "
        "with automatic rollback on error rate threshold breach.",
    ]
    for item in mlops:
        elems.append(Paragraph(item, styles["bullet"]))

    elems.append(PageBreak())
    return elems


# ────────────────────── Section 7: Expected Outcomes ─────────────────────────
def build_outcomes(styles):
    elems = []
    elems.append(Paragraph("7. Expected Outcomes & Business Impact", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph("7.1 Quantitative Outcomes", styles["h2"]))

    outcomes_data = [
        ["Outcome",                         "Current State",  "6-Month Target", "12-Month Target"],
        ["Forecast MAPE",                   "~35%",           "≤ 12%",          "≤ 9%"],
        ["Forecast MAE (units)",            "~420",           "≤ 260",          "≤ 190"],
        ["Stockout Rate",                   "8.2%",           "≤ 4.5%",         "≤ 3.0%"],
        ["Overstock (excess inventory days)","18 days avg",   "≤ 12 days",      "≤ 9 days"],
        ["Forecasting Cycle Time",          "3 days (manual)","< 30 min (auto)","< 5 min (real-time)"],
        ["Demand Planner Productivity",     "Baseline",       "+25% efficiency","+ 45% efficiency"],
        ["Annual Inventory Cost Saving",    "—",              "~$1.2M est.",    "~$2.8M est."],
    ]
    t = Table(outcomes_data, colWidths=[5*cm, 2.8*cm, 2.8*cm, 3.4*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), SUCCESS),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, colors.HexColor("#F0FDF4")]),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 9 — Expected Quantitative Outcomes", styles["caption"]))

    elems.append(Paragraph("7.2 Qualitative Outcomes", styles["h2"]))
    qual = [
        "<b>Organisational AI Maturity:</b> The initiative advances the organisation from Level 1 (Ad-hoc) "
        "to Level 3 (Defined) on the AI Maturity Model, building reusable ML infrastructure and institutional "
        "knowledge transferable to future AI projects.",
        "<b>Data Culture:</b> Cross-functional data literacy workshops (embedded in the project) upskill "
        "supply-chain planners, creating a team that understands and trusts AI-driven recommendations.",
        "<b>Trust & Transparency:</b> Publication of model cards and explainability dashboards builds "
        "stakeholder confidence, reducing resistance to AI adoption in downstream planning cycles.",
        "<b>Regulatory Readiness:</b> Documentation produced (model cards, risk assessments, data governance "
        "policies) positions the organisation for compliance with forthcoming EU AI Act obligations.",
        "<b>Reusable ML Platform:</b> The Medallion data lake, feature store, MLflow registry, and MLOps "
        "pipelines are domain-agnostic and can accelerate time-to-value for subsequent ML initiatives.",
    ]
    for item in qual:
        elems.append(Paragraph(item, styles["bullet"]))

    elems.append(Paragraph("7.3 Statistical Validation Plan", styles["h2"]))
    elems.append(Paragraph(
        "Upon completion of the 90-day held-out evaluation, a Wilcoxon Signed-Rank test (non-parametric, "
        "suitable for paired forecast errors) will be applied at α = 0.05 to test H₁ vs H₀. Additionally, "
        "the Diebold-Mariano (DM) test will be used for pairwise comparison between candidate models. "
        "Results will be reported with 95% confidence intervals and corrected for multiple comparisons "
        "using the Benjamini-Hochberg procedure to control the False Discovery Rate (FDR < 0.05).",
        styles["body"]
    ))
    elems.append(PageBreak())
    return elems


# ────────────────────── Section 8: Budget & Team ─────────────────────────────
def build_budget(styles):
    elems = []
    elems.append(Paragraph("8. Budget Estimate & Team Structure", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph("8.1 Budget Breakdown", styles["h2"]))
    budget = [
        ["Category",                    "6-Month Estimate (USD)", "Notes"],
        ["Cloud Compute (GCP)",         "$18,000",   "Training (Vertex AI) + inference + BigQuery"],
        ["Data Engineering (Airflow)",  "$3,200",    "Managed Cloud Composer (dev+prod)"],
        ["Software Licences",           "$0",        "All open-source tooling; no licence cost"],
        ["External Data APIs",          "$1,500",    "OpenWeather paid tier; Google Cloud APIs"],
        ["Personnel (6 FTE, 6 months)", "$312,000",  "Blended rate ~$104K/year per FTE"],
        ["Training & Workshops",        "$4,000",    "Data literacy, MLOps, ethics training"],
        ["Contingency Reserve (10%)",   "$33,870",   "Risk buffer for scope changes"],
        ["<b>Total Project Cost</b>",   "<b>$372,570</b>","Excluding ongoing operational costs"],
    ]
    t = Table(budget, colWidths=[6*cm, 4*cm, 7*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BACKGROUND",    (0,-1), (-1,-1), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR",     (0,-1), (-1,-1), WHITE),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 10 — Project Budget Estimate", styles["caption"]))

    elems.append(Paragraph("8.2 Team Structure & RACI", styles["h2"]))
    team = [
        ["Role",                        "FTE", "Primary Responsibilities"],
        ["Project Manager",             "1.0", "Planning, stakeholder management, risk tracking, phase gates"],
        ["Lead Data Scientist",         "1.0", "Model design, evaluation framework, hypothesis testing"],
        ["Senior ML Engineer",          "1.0", "MLOps, CI/CD, model serving, drift monitoring"],
        ["Data Engineer",               "1.0", "Pipeline development, feature store, data governance"],
        ["Business Analyst",            "0.5", "Requirements, UAT co-ordination, dashboard spec"],
        ["AI Ethics & Compliance Lead", "0.5", "Bias audits, model cards, regulatory documentation"],
        ["<b>Total</b>",               "<b>5.0 FTE</b>",""],
    ]
    t = Table(team, colWidths=[5*cm, 1.5*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), ROYAL_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BACKGROUND",    (0,-1), (-1,-1), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR",     (0,-1), (-1,-1), WHITE),
        ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
        ("ALIGN",         (1,0), (1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    elems.append(t)
    elems.append(Paragraph("Table 11 — Team Structure", styles["caption"]))
    elems.append(PageBreak())
    return elems


# ──────────────────────── Conclusion & References ────────────────────────────
def build_conclusion(styles):
    elems = []
    elems.append(Paragraph("9. Conclusion", styles["h1"]))
    elems.append(divider())

    elems.append(Paragraph(
        "This project plan presents a rigorous, end-to-end blueprint for deploying a production-grade "
        "predictive analytics solution grounded in sound ML principles, ethical governance, and scalable "
        "engineering. The six-phase roadmap — spanning data engineering, model development, explainability, "
        "deployment, and continuous monitoring — is designed to deliver measurable business value within "
        "six months while laying the architectural foundation for enterprise-wide AI adoption.",
        styles["body"]
    ))
    elems.append(Paragraph(
        "The initiative is hypothesis-driven: success is defined in terms of statistically validated "
        "improvement over a seasonal naïve baseline, ensuring that claims of model efficacy are scientifically "
        "sound rather than anecdotal. The multi-source public dataset strategy demonstrates that significant "
        "value can be extracted from open data, reducing dependence on expensive proprietary data providers.",
        styles["body"]
    ))
    elems.append(Paragraph(
        "By embedding ethical review, bias auditing, and model card documentation as first-class deliverables "
        "— not afterthoughts — the project positions the organisation as a responsible AI practitioner. "
        "The MLOps framework ensures that the system remains accurate, fair, and reliable long after the "
        "initial launch, with automated drift detection and retraining pipelines sustaining model performance "
        "through evolving market conditions.",
        styles["body"]
    ))
    elems.append(Paragraph(
        "In summary, the Predictive Analytics AI Initiative represents a strategically significant investment "
        "with a projected ROI driven by inventory cost reduction, improved service levels, and the creation "
        "of a reusable ML platform. The plan is ambitious, grounded, and executable — and positions the "
        "organisation to realise the full transformative potential of artificial intelligence.",
        styles["body"]
    ))

    elems.append(Paragraph("10. References & Further Reading", styles["h1"]))
    elems.append(divider())

    refs = [
        "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. <i>KDD 2016</i>.",
        "Oreshkin, B. N., et al. (2020). N-BEATS: Neural basis expansion analysis. <i>ICLR 2020</i>.",
        "Lim, B., et al. (2021). Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. <i>International Journal of Forecasting</i>, 37(4), 1748–1764.",
        "Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. <i>NeurIPS 2017</i>.",
        "Mitchell, M., et al. (2019). Model cards for model reporting. <i>FAccT 2019</i>.",
        "Sculley, D., et al. (2015). Hidden technical debt in machine learning systems. <i>NeurIPS 2015</i>.",
        "Makridakis, S., et al. (2022). M5 accuracy competition: Results, findings, and conclusions. <i>International Journal of Forecasting</i>, 38(4).",
        "European Parliament (2024). EU Artificial Intelligence Act. Official Journal of the European Union.",
        "Google. (2023). Responsible AI Practices. https://ai.google/responsibilities/responsible-ai-practices/",
        "Feature Store for Machine Learning (Feast). https://feast.dev",
        "MLflow: An open source platform for the machine learning lifecycle. https://mlflow.org",
        "Evidently AI. (2024). Open-source ML observability platform. https://www.evidentlyai.com",
    ]
    for i, ref in enumerate(refs, 1):
        elems.append(Paragraph(f"[{i}] {ref}", ParagraphStyle(
            "ref", fontSize=8.5, fontName="Helvetica", textColor=DARK_GRAY,
            spaceAfter=4, leading=12, leftIndent=14, firstLineIndent=-14, alignment=TA_JUSTIFY
        )))

    return elems


# ──────────────────────────── Page Number Footer ──────────────────────────────
class NumberedPageCanvas:
    """Adds page number footer and header to every page."""
    def __init__(self, filename, **kwargs):
        from reportlab.pdfgen.canvas import Canvas
        self._doc_canvas = Canvas(filename, **kwargs)
        self._saved_page_states = []
        self._filename = filename

    def showPage(self):
        self._saved_page_states.append(dict(self._doc_canvas.__dict__))
        self._doc_canvas._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self._doc_canvas.__dict__.update(state)
            self._draw_footer(total)
            self._doc_canvas.showPage()
        self._doc_canvas.save()

    def _draw_footer(self, page_count):
        c = self._doc_canvas
        page_num = c._pageNumber
        w, h = A4

        # Footer bar
        c.setFillColor(NAVY)
        c.rect(0, 0, w, 22, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.setFont("Helvetica", 7.5)
        c.drawString(2*cm, 7, "Predictive Analytics AI Initiative — Project Plan")
        c.drawRightString(w - 2*cm, 7, f"Page {page_num} of {page_count}  |  CONFIDENTIAL")


def on_first_page(canvas, doc):
    pass  # Cover page — no footer drawn by doc template

def on_later_pages(canvas, doc):
    pass


# ──────────────────────────────── MAIN ───────────────────────────────────────
def generate_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2.2*cm,
        title="Predictive Analytics AI Initiative — Project Plan",
        author="AI Strategy & Data Science Team",
        subject="AI Project Plan",
        creator="Antigravity AI Planner",
    )

    styles = build_styles()
    story = []

    story += build_cover(styles)
    story += build_executive_summary(styles)
    story += build_objectives(styles)
    story += build_technology(styles)
    story += build_methodology(styles)
    story += build_timeline(styles)
    story += build_risks(styles)
    story += build_scalability(styles)
    story += build_outcomes(styles)
    story += build_budget(styles)
    story += build_conclusion(styles)

    # Build using the internal canvas for page numbers
    from reportlab.pdfgen.canvas import Canvas as _Canvas
    from reportlab.lib.pagesizes import A4 as _A4

    class _NumberedCanvas(_Canvas):
        def __init__(self, *args, **kwargs):
            _Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_page_footer(num_pages)
                _Canvas.showPage(self)
            _Canvas.save(self)

        def _draw_page_footer(self, page_count):
            w, h = A4
            page_num = self._pageNumber
            if page_num == 1:
                return  # No footer on cover
            self.setFillColor(NAVY)
            self.rect(0, 0, w, 22, fill=1, stroke=0)
            self.setFillColor(WHITE)
            self.setFont("Helvetica", 7.5)
            self.drawString(2*cm, 7, "Predictive Analytics AI Initiative — Comprehensive Project Plan")
            self.drawRightString(w - 2*cm, 7, f"Page {page_num} of {page_count}   |   CONFIDENTIAL")

            # Top thin accent bar
            self.setFillColor(STEEL_BLUE)
            self.rect(0, h - 4, w, 4, fill=1, stroke=0)

    doc.build(story, canvasmaker=_NumberedCanvas)
    print(f"[OK] PDF generated successfully: {output_path}")


if __name__ == "__main__":
    output = r"c:\Users\prate\Desktop\youva\AI_Project_Plan_Predictive_Analytics.pdf"
    generate_pdf(output)
