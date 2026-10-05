"""
build_ppt.py
============
Generates a 10-slide professional PowerPoint presentation summarizing
the 6-week AI Internship, with embedded project images and a modern design.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = r"c:\Users\prate\Desktop\youva"
REPORT_DIR = os.path.join(BASE_DIR, "internship_final_report")
DP_DIR = os.path.join(BASE_DIR, "data processing")
ML_DIR = os.path.join(BASE_DIR, "ml_model_development", "results", "figures")
XAI_DIR = os.path.join(BASE_DIR, "explainable_ai")
DEPLOY_DIR = os.path.join(BASE_DIR, "ai_deployment_monitoring")
ETHICS_DIR = os.path.join(BASE_DIR, "ai_ethics_audit")

# ── Color Palette ─────────────────────────────────────────────────────────────
BG_DARK    = RGBColor(0x0D, 0x11, 0x17)   # #0D1117
BG_CARD    = RGBColor(0x16, 0x1B, 0x22)   # #161B22
ACCENT     = RGBColor(0x6C, 0x63, 0xFF)   # #6C63FF purple
ACCENT2    = RGBColor(0x43, 0xE9, 0x7B)   # #43E97B green
ACCENT3    = RGBColor(0xFF, 0x65, 0x84)   # #FF6584 pink
ACCENT4    = RGBColor(0xF5, 0xA6, 0x23)   # #F5A623 amber
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xA0, 0xA8, 0xB8)
MID_GRAY   = RGBColor(0x6E, 0x76, 0x81)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def set_slide_bg(slide, color=BG_DARK):
    """Set solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, fill_color, corner_radius=None):
    """Add a rounded rectangle shape."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    if corner_radius:
        shape.adjustments[0] = corner_radius
    return shape


def add_textbox(slide, left, top, width, height, text, font_size=18,
                color=WHITE, bold=False, alignment=PP_ALIGN.LEFT,
                font_name='Calibri'):
    """Add a text box with specified formatting."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_bullet_frame(slide, left, top, width, height, items, font_size=16,
                     color=LIGHT_GRAY, bullet_color=ACCENT):
    """Add a text frame with bulleted items."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = 'Calibri'
        p.space_after = Pt(8)
        p.level = 0
    return txBox


def add_accent_line(slide, left, top, width, color=ACCENT):
    """Add a thin accent line."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, Pt(3)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_image_safe(slide, path, left, top, width=None, height=None):
    """Add image if it exists."""
    if os.path.exists(path):
        kwargs = {}
        if width:
            kwargs['width'] = width
        if height:
            kwargs['height'] = height
        slide.shapes.add_picture(path, left, top, **kwargs)
        return True
    return False


def add_score_badge(slide, left, top, score, label, color=ACCENT):
    """Add a circular score badge."""
    # Background circle
    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, left, top, Inches(1.2), Inches(1.2)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    
    # Score text
    tf = shape.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = str(score)
    p.font.size = Pt(22)
    p.font.color.rgb = WHITE
    p.font.bold = True
    p.font.name = 'Calibri'
    p.alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].space_before = Pt(8)
    
    # Label below
    add_textbox(slide, left - Inches(0.2), top + Inches(1.3),
                Inches(1.6), Inches(0.4), label,
                font_size=10, color=LIGHT_GRAY, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════════════════
# SLIDE GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_ppt():
    print("=" * 50)
    print("  GENERATING PRESENTATION")
    print("=" * 50)
    
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank_layout = prs.slide_layouts[6]  # blank layout
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 1: TITLE
    # ══════════════════════════════════════════════════════════════════════
    print("[1/10] Title slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    # Decorative shapes
    add_shape(slide, Inches(-0.5), Inches(-0.5), Inches(5), Inches(8.5),
              RGBColor(0x6C, 0x63, 0xFF), corner_radius=0.05)
    add_shape(slide, Inches(-0.3), Inches(-0.3), Inches(4.6), Inches(8.2),
              BG_DARK, corner_radius=0.05)
    
    # Accent line
    add_accent_line(slide, Inches(1), Inches(2.5), Inches(2.5), ACCENT)
    
    # Title text
    add_textbox(slide, Inches(5), Inches(1.2), Inches(7.5), Inches(1.5),
                "COMPREHENSIVE", font_size=20, color=ACCENT, bold=True)
    add_textbox(slide, Inches(5), Inches(1.8), Inches(7.5), Inches(1.5),
                "AI INTERNSHIP", font_size=48, color=WHITE, bold=True)
    add_textbox(slide, Inches(5), Inches(3.0), Inches(7.5), Inches(1),
                "PROJECT REPORT", font_size=48, color=WHITE, bold=True)
    
    add_accent_line(slide, Inches(5), Inches(4.3), Inches(3), ACCENT)
    
    add_textbox(slide, Inches(5), Inches(4.7), Inches(7), Inches(0.5),
                "6-Week Intensive AI/ML Internship Program",
                font_size=18, color=LIGHT_GRAY)
    add_textbox(slide, Inches(5), Inches(5.3), Inches(7), Inches(0.5),
                "Duration: May 2026 – June 2026",
                font_size=14, color=MID_GRAY)
    
    # Left side bullets
    left_items = ["Planning", "Preprocessing", "Model Building",
                  "Explainability", "Deployment", "Ethics"]
    for i, item in enumerate(left_items):
        add_textbox(slide, Inches(0.8), Inches(3.2 + i * 0.55),
                    Inches(3), Inches(0.5),
                    f"▸  {item}", font_size=14, color=LIGHT_GRAY)
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 2: OVERVIEW / AGENDA
    # ══════════════════════════════════════════════════════════════════════
    print("[2/10] Overview slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.8),
                "INTERNSHIP OVERVIEW", font_size=32, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.2), Inches(2.5), ACCENT)
    
    # Week cards - 2 rows of 3
    weeks = [
        ("WEEK 1", "AI Project Planning\n& Documentation", "65/100", ACCENT),
        ("WEEK 2", "Data Preprocessing\n& Feature Engineering", "85/100", ACCENT2),
        ("WEEK 3", "ML Model Building\n& Tuning", "45/100", ACCENT3),
        ("WEEK 4", "Explainable AI\n& Interpretability", "55/100", ACCENT4),
        ("WEEK 5", "Deployment &\nMonitoring", "95/100", ACCENT),
        ("WEEK 6", "AI Ethics &\nBias Analysis", "70/100", ACCENT2),
    ]
    
    for i, (week, desc, score, color) in enumerate(weeks):
        col = i % 3
        row = i // 3
        left = Inches(0.8 + col * 4.1)
        top = Inches(1.8 + row * 2.8)
        
        card = add_shape(slide, left, top, Inches(3.7), Inches(2.4), BG_CARD, 0.03)
        
        # Top color bar
        bar = add_shape(slide, left, top, Inches(3.7), Pt(4), color)
        
        add_textbox(slide, left + Inches(0.3), top + Inches(0.2),
                    Inches(3), Inches(0.4), week,
                    font_size=12, color=color, bold=True)
        add_textbox(slide, left + Inches(0.3), top + Inches(0.6),
                    Inches(2.4), Inches(1), desc,
                    font_size=15, color=WHITE)
        
        # Score badge
        score_shape = add_shape(slide, left + Inches(2.5), top + Inches(1.6),
                                Inches(1), Inches(0.5), color, 0.1)
        tf = score_shape.text_frame
        p = tf.paragraphs[0]
        p.text = score
        p.font.size = Pt(16)
        p.font.color.rgb = WHITE
        p.font.bold = True
        p.font.name = 'Calibri'
        p.alignment = PP_ALIGN.CENTER
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 3: WEEK 1 - PROJECT PLANNING
    # ══════════════════════════════════════════════════════════════════════
    print("[3/10] Week 1 slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 1", font_size=14, color=ACCENT, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "AI Project Planning & Documentation", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(2), ACCENT)
    
    # Content cards
    card1 = add_shape(slide, Inches(0.8), Inches(2.0), Inches(5.5), Inches(4.5), BG_CARD, 0.02)
    add_textbox(slide, Inches(1.1), Inches(2.2), Inches(5), Inches(0.5),
                "📋  Deliverables", font_size=18, color=ACCENT, bold=True)
    add_bullet_frame(slide, Inches(1.1), Inches(2.8), Inches(5), Inches(3.5),
        [
            "▸  Detailed project plan for healthcare predictive analytics",
            "▸  Hypothesis formulation & feasibility assessment",
            "▸  Technology stack selection (Python, scikit-learn, pandas)",
            "▸  Risk assessment with mitigation strategies",
            "▸  Project timeline with milestone tracking",
            "▸  Data governance & ethical considerations",
        ], font_size=14)
    
    card2 = add_shape(slide, Inches(6.8), Inches(2.0), Inches(5.5), Inches(4.5), BG_CARD, 0.02)
    add_textbox(slide, Inches(7.1), Inches(2.2), Inches(5), Inches(0.5),
                "💡  Key Takeaways", font_size=18, color=ACCENT2, bold=True)
    add_bullet_frame(slide, Inches(7.1), Inches(2.8), Inches(5), Inches(3.5),
        [
            "▸  Simulated real-world AI project ideation process",
            "▸  Documented methodology for data collection & analysis",
            "▸  Identified scalability challenges for production",
            "▸  Learned importance of thorough documentation",
            "▸  Feedback: needed deeper ethical exploration",
            "▸  Score: 65/100 — room for improvement in depth",
        ], font_size=14)
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 4: WEEK 2 - DATA PREPROCESSING
    # ══════════════════════════════════════════════════════════════════════
    print("[4/10] Week 2 slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 2", font_size=14, color=ACCENT2, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "Data Preprocessing & Feature Engineering", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(2), ACCENT2)
    
    # Left content
    add_textbox(slide, Inches(0.8), Inches(1.9), Inches(5.5), Inches(0.4),
                "Titanic Dataset  •  891 samples  •  Score: 85/100",
                font_size=14, color=ACCENT2, bold=True)
    add_bullet_frame(slide, Inches(0.8), Inches(2.5), Inches(5.5), Inches(4.5),
        [
            "▸  KNN Imputation for missing Age values (19.9%)",
            "▸  IQR-based outlier detection with Winsorization",
            "▸  Engineered features: FamilySize, IsAlone, Title, FareBin",
            "▸  One-hot encoding for categorical variables",
            "▸  StandardScaler normalization pipeline",
            "▸  Reproducible sklearn Pipeline assembly",
        ], font_size=15)
    
    # Right side - images
    img1 = os.path.join(DP_DIR, "correlation_matrix.png")
    img2 = os.path.join(DP_DIR, "feature_importance.png")
    add_image_safe(slide, img1, Inches(6.8), Inches(1.8), width=Inches(5.8))
    add_image_safe(slide, img2, Inches(6.8), Inches(4.5), width=Inches(5.8))
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 5: WEEK 3 - ML MODEL
    # ══════════════════════════════════════════════════════════════════════
    print("[5/10] Week 3 slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 3", font_size=14, color=ACCENT3, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "Building & Tuning an AI Model", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(2), ACCENT3)
    
    # Key metrics card
    card = add_shape(slide, Inches(0.8), Inches(1.9), Inches(5.5), Inches(2.5), BG_CARD, 0.02)
    add_textbox(slide, Inches(1.1), Inches(2.1), Inches(5), Inches(0.4),
                "Breast Cancer Wisconsin  •  Random Forest  •  GridSearchCV",
                font_size=13, color=ACCENT3, bold=True)
    add_bullet_frame(slide, Inches(1.1), Inches(2.6), Inches(5), Inches(1.7),
        [
            "▸  162 hyperparameter combinations × 5-fold CV = 810 fits",
            "▸  Optimized for F1-score (clinically relevant)",
            "▸  Tuned F1: ≥ 0.97  |  AUC: ≥ 0.995",
        ], font_size=14)
    
    # Results table card
    card2 = add_shape(slide, Inches(0.8), Inches(4.7), Inches(5.5), Inches(2.3), BG_CARD, 0.02)
    add_textbox(slide, Inches(1.1), Inches(4.9), Inches(5), Inches(0.4),
                "Performance Comparison", font_size=14, color=WHITE, bold=True)
    metrics_text = (
        "Metric          Baseline      Tuned         Change\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Accuracy        0.96           0.98           ↑\n"
        "Precision       0.96           0.98           ↑\n"
        "Recall           0.96           0.98           ↑\n"
        "F1-Score        0.97           0.99           ↑\n"
        "ROC-AUC        0.99           0.999         ↑"
    )
    add_textbox(slide, Inches(1.1), Inches(5.3), Inches(5), Inches(1.5),
                metrics_text, font_size=10, color=LIGHT_GRAY, font_name='Consolas')
    
    # Images
    img1 = os.path.join(ML_DIR, "confusion_matrices.png")
    img2 = os.path.join(ML_DIR, "roc_curves.png")
    add_image_safe(slide, img1, Inches(6.8), Inches(1.8), width=Inches(5.8))
    add_image_safe(slide, img2, Inches(6.8), Inches(4.5), width=Inches(5.8))
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 6: WEEK 4 - EXPLAINABLE AI
    # ══════════════════════════════════════════════════════════════════════
    print("[6/10] Week 4 slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 4", font_size=14, color=ACCENT4, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "Explainable AI & Model Interpretability", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(2), ACCENT4)
    
    # SHAP card
    add_textbox(slide, Inches(0.8), Inches(1.9), Inches(5.5), Inches(0.4),
                "🔍  SHAP (SHapley Additive exPlanations)", font_size=16, color=ACCENT4, bold=True)
    add_bullet_frame(slide, Inches(0.8), Inches(2.4), Inches(5.5), Inches(1.5),
        [
            "▸  TreeExplainer for global feature importance",
            "▸  Beeswarm plots showing feature impact direction",
            "▸  Waterfall plots for individual prediction breakdown",
        ], font_size=14)
    
    # LIME card
    add_textbox(slide, Inches(0.8), Inches(4.0), Inches(5.5), Inches(0.4),
                "🔍  LIME (Local Interpretable Explanations)", font_size=16, color=ACCENT4, bold=True)
    add_bullet_frame(slide, Inches(0.8), Inches(4.5), Inches(5.5), Inches(1.5),
        [
            "▸  Local surrogate models for individual predictions",
            "▸  Benign & Malignant case explanations",
            "▸  Complementary to SHAP for clinical trust",
        ], font_size=14)
    
    # Images
    img1 = os.path.join(XAI_DIR, "fig3_shap_summary.png")
    img2 = os.path.join(XAI_DIR, "fig6_lime_benign.png")
    add_image_safe(slide, img1, Inches(6.8), Inches(1.8), width=Inches(5.8))
    add_image_safe(slide, img2, Inches(6.8), Inches(4.5), width=Inches(5.8))
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 7: WEEK 5 - DEPLOYMENT (Part 1: Architecture)
    # ══════════════════════════════════════════════════════════════════════
    print("[7/10] Week 5 slide (Architecture)...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    # Gold accent for the top-scoring week
    GOLD = RGBColor(0xFF, 0xD7, 0x00)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 5  ★  HIGHEST SCORE: 95/100", font_size=14, color=GOLD, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "AI Model Deployment & Monitoring", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(3), GOLD)
    
    # Architecture card
    card = add_shape(slide, Inches(0.8), Inches(1.9), Inches(6), Inches(5.0), BG_CARD, 0.02)
    add_textbox(slide, Inches(1.1), Inches(2.1), Inches(5.5), Inches(0.4),
                "🏗️  System Architecture", font_size=18, color=GOLD, bold=True)
    
    # Architecture components
    components = [
        ("FastAPI", "7 REST endpoints, Pydantic validation,\nSwagger UI, CORS, request-ID middleware", ACCENT),
        ("Docker", "Multi-stage build, non-root user,\nhealthcheck, compose with resource limits", ACCENT2),
        ("Monitoring", "Thread-safe MetricsStore, latency P95,\nerror rates, per-class distributions", ACCENT4),
        ("Logging", "Structured JSON (python-json-logger),\nrotating files (10 MB × 5 backups)", ACCENT3),
        ("Testing", "15 pytest tests covering all endpoints,\nvalidation, edge cases, accumulation", RGBColor(0xA2, 0x9B, 0xFE)),
    ]
    
    for i, (name, desc, color) in enumerate(components):
        y = Inches(2.7 + i * 0.8)
        # Colored dot
        dot = add_shape(slide, Inches(1.2), y + Pt(2), Pt(10), Pt(10), color)
        add_textbox(slide, Inches(1.5), y - Pt(2), Inches(1.5), Inches(0.4),
                    name, font_size=14, color=color, bold=True)
        add_textbox(slide, Inches(3.0), y - Pt(2), Inches(3.5), Inches(0.6),
                    desc, font_size=10, color=LIGHT_GRAY)
    
    # API endpoints card
    card2 = add_shape(slide, Inches(7.2), Inches(1.9), Inches(5.3), Inches(5.0), BG_CARD, 0.02)
    add_textbox(slide, Inches(7.5), Inches(2.1), Inches(5), Inches(0.4),
                "🌐  API Endpoints", font_size=18, color=GOLD, bold=True)
    
    endpoints_text = (
        "GET   /health         Liveness probe\n"
        "GET   /metrics        Operational metrics\n"
        "GET   /model/info     Model metadata\n"
        "POST  /predict        Single prediction\n"
        "POST  /predict/batch  Batch (1-256)\n"
        "GET   /docs           Swagger UI\n"
        "GET   /redoc          ReDoc docs"
    )
    add_textbox(slide, Inches(7.5), Inches(2.7), Inches(4.8), Inches(2.5),
                endpoints_text, font_size=12, color=LIGHT_GRAY, font_name='Consolas')
    
    # Sample response
    add_textbox(slide, Inches(7.5), Inches(5.0), Inches(4.8), Inches(0.3),
                "Sample /predict Response:", font_size=11, color=ACCENT, bold=True)
    sample = '{"prediction": 0, "class_name": "setosa",\n "confidence": 1.0, "probabilities":\n {"setosa": 1.0, "versicolor": 0.0,\n  "virginica": 0.0}}'
    add_textbox(slide, Inches(7.5), Inches(5.4), Inches(4.8), Inches(1.4),
                sample, font_size=10, color=ACCENT2, font_name='Consolas')
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 8: WEEK 5 - DEPLOYMENT (Part 2: Code Highlights)
    # ══════════════════════════════════════════════════════════════════════
    print("[8/10] Week 5 slide (Docker & Code)...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 5  ★  DEPLOYMENT DEEP DIVE", font_size=14, color=GOLD, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "Docker, Monitoring & Testing", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(3), GOLD)
    
    # Dockerfile card
    card1 = add_shape(slide, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.0), BG_CARD, 0.02)
    add_textbox(slide, Inches(1.1), Inches(2.1), Inches(5), Inches(0.4),
                "🐳  Dockerfile (Multi-stage Build)", font_size=14, color=ACCENT, bold=True)
    dockerfile_code = (
        "FROM python:3.11-slim AS builder\n"
        "WORKDIR /build\n"
        "COPY requirements.txt .\n"
        "RUN pip install --prefix=/install ...\n"
        "\n"
        "FROM python:3.11-slim AS runtime\n"
        "RUN groupadd appgroup && \\\n"
        "    useradd --gid appgroup appuser\n"
        "COPY --from=builder /install /usr/local\n"
        "COPY app/ ./app/\n"
        "USER appuser\n"
        "EXPOSE 8000\n"
        "HEALTHCHECK --interval=30s ...\n"
        'CMD ["uvicorn", "app.main:app",\n'
        '     "--host", "0.0.0.0", "--port", "8000"]'
    )
    add_textbox(slide, Inches(1.1), Inches(2.6), Inches(5.3), Inches(3.5),
                dockerfile_code, font_size=10, color=ACCENT2, font_name='Consolas')
    
    # Monitoring card
    card2 = add_shape(slide, Inches(7.0), Inches(1.9), Inches(5.5), Inches(2.3), BG_CARD, 0.02)
    add_textbox(slide, Inches(7.3), Inches(2.1), Inches(5), Inches(0.4),
                "📊  Metrics Tracked", font_size=14, color=ACCENT4, bold=True)
    add_bullet_frame(slide, Inches(7.3), Inches(2.6), Inches(5), Inches(1.5),
        [
            "▸  Total requests / success / failures",
            "▸  Avg latency & P95 latency (ms)",
            "▸  Error rate % & per-class distribution",
            "▸  Rolling window: last 1000 samples",
        ], font_size=12)
    
    # Testing card
    card3 = add_shape(slide, Inches(7.0), Inches(4.5), Inches(5.5), Inches(2.4), BG_CARD, 0.02)
    add_textbox(slide, Inches(7.3), Inches(4.7), Inches(5), Inches(0.4),
                "🧪  Test Suite: 15 pytest Tests", font_size=14, color=ACCENT3, bold=True)
    add_bullet_frame(slide, Inches(7.3), Inches(5.2), Inches(5), Inches(1.5),
        [
            "▸  Health: status 200, correct payload fields",
            "▸  Predict: setosa/virginica, validation, negatives",
            "▸  Batch: correct count, empty list rejection",
            "▸  Metrics: field presence, accumulation",
        ], font_size=12)
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 9: WEEK 6 - AI ETHICS
    # ══════════════════════════════════════════════════════════════════════
    print("[9/10] Week 6 slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.3), Inches(5), Inches(0.6),
                "WEEK 6", font_size=14, color=ACCENT2, bold=True)
    add_textbox(slide, Inches(0.8), Inches(0.7), Inches(10), Inches(0.8),
                "AI Ethics, Bias Analysis & Fairness", font_size=30, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.5), Inches(2), ACCENT2)
    
    # Left content
    add_textbox(slide, Inches(0.8), Inches(1.9), Inches(5.5), Inches(0.4),
                "UCI Adult Census  •  Logistic Regression  •  32,561 records",
                font_size=13, color=ACCENT2, bold=True)
    
    add_textbox(slide, Inches(0.8), Inches(2.5), Inches(5.5), Inches(0.4),
                "Fairness Metrics Evaluated:", font_size=15, color=WHITE, bold=True)
    add_bullet_frame(slide, Inches(0.8), Inches(3.0), Inches(5.5), Inches(2.0),
        [
            "▸  Demographic Parity — equal prediction rates",
            "▸  Disparate Impact Ratio — 80% rule (FAIL for sex)",
            "▸  Equalized Odds — TPR/FPR by group",
            "▸  Predictive Parity — precision across groups",
            "▸  Intersectional Bias — Race × Sex analysis",
        ], font_size=14)
    
    add_textbox(slide, Inches(0.8), Inches(5.2), Inches(5.5), Inches(0.4),
                "Remediation Strategies:", font_size=15, color=WHITE, bold=True)
    add_bullet_frame(slide, Inches(0.8), Inches(5.7), Inches(5.5), Inches(1.5),
        [
            "▸  Re-sampling / re-weighting training data",
            "▸  Adversarial debiasing & fairness constraints",
            "▸  Per-group threshold adjustment",
        ], font_size=14)
    
    # Right side - images
    img1 = os.path.join(ETHICS_DIR, "fig2_disparate_impact.png")
    img2 = os.path.join(ETHICS_DIR, "fig6_fairness_heatmap.png")
    add_image_safe(slide, img1, Inches(6.8), Inches(1.8), width=Inches(5.8))
    add_image_safe(slide, img2, Inches(6.8), Inches(4.5), width=Inches(5.8))
    
    # ══════════════════════════════════════════════════════════════════════
    # SLIDE 10: CONCLUSION & THANK YOU
    # ══════════════════════════════════════════════════════════════════════
    print("[10/10] Conclusion slide...")
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide)
    
    add_textbox(slide, Inches(0.8), Inches(0.4), Inches(10), Inches(0.8),
                "KEY TAKEAWAYS & CONCLUSION", font_size=32, color=WHITE, bold=True)
    add_accent_line(slide, Inches(0.8), Inches(1.2), Inches(3), ACCENT)
    
    # Score summary with badges
    add_textbox(slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.4),
                "Evaluation Scores Across 6 Weeks",
                font_size=16, color=LIGHT_GRAY, bold=True)
    
    scores = [
        ("W1\nPlanning", 65, ACCENT),
        ("W2\nData", 85, ACCENT2),
        ("W3\nModel", 45, ACCENT3),
        ("W4\nXAI", 55, ACCENT4),
        ("W5\nDeploy", 95, GOLD),
        ("W6\nEthics", 70, ACCENT2),
    ]
    for i, (label, score, color) in enumerate(scores):
        left = Inches(0.8 + i * 2.0)
        add_score_badge(slide, left, Inches(2.1), score, label, color)
    
    # Key learnings
    card = add_shape(slide, Inches(0.8), Inches(4.2), Inches(11.5), Inches(2.8), BG_CARD, 0.02)
    add_textbox(slide, Inches(1.2), Inches(4.4), Inches(5), Inches(0.4),
                "🎯  Key Lessons Learned", font_size=18, color=ACCENT, bold=True)
    
    add_bullet_frame(slide, Inches(1.2), Inches(5.0), Inches(5), Inches(2.0),
        [
            "▸  Deployment engineering > model accuracy alone",
            "▸  Deliverable specs must be met precisely",
            "▸  Ethics must be integrated early, not as afterthought",
        ], font_size=14)
    
    add_textbox(slide, Inches(7.0), Inches(4.4), Inches(5), Inches(0.4),
                "🚀  Future Directions", font_size=18, color=ACCENT2, bold=True)
    
    add_bullet_frame(slide, Inches(7.0), Inches(5.0), Inches(5), Inches(2.0),
        [
            "▸  CI/CD pipelines with GitHub Actions",
            "▸  MLflow model registry & experiment tracking",
            "▸  Cloud deployment (AWS / Azure / GCP)",
        ], font_size=14)
    
    # ══════════════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════════════
    pptx_path = os.path.join(REPORT_DIR, "Internship_Presentation.pptx")
    prs.save(pptx_path)
    print(f"\n[OK] Presentation saved: {pptx_path}")
    print(f"     Total slides: {len(prs.slides)}")
    print("\n" + "=" * 50)
    print("  PRESENTATION COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    generate_ppt()
