"""
build_ppt_v4.py
===============
10-slide AI Internship presentation — pixel-precise layout.

Design fixes from v3:
  - NO overlapping elements — shapes are edge accents only
  - Images sized properly in dedicated zones
  - Content fills slides — no dead space
  - Clean grid: left text / right images, or full-width
  - Distinctive, non-generic cards with color coding per week
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = r"c:\Users\prate\Desktop\youva"
OUT    = os.path.join(BASE, "internship_final_report")
IMG_DP = os.path.join(BASE, "data processing")
IMG_ML = os.path.join(BASE, "ml_model_development", "results", "figures")
IMG_XAI = os.path.join(BASE, "explainable_ai")
IMG_ETH = os.path.join(BASE, "ai_ethics_audit")

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY     = RGBColor(0x0F, 0x24, 0x4E)
TEAL     = RGBColor(0x00, 0xB4, 0xD8)
AMBER    = RGBColor(0xF5, 0xA6, 0x23)
CORAL    = RGBColor(0xEF, 0x47, 0x6F)
MINT     = RGBColor(0x2D, 0xD4, 0xBF)
SLATE    = RGBColor(0x47, 0x55, 0x69)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE = RGBColor(0xF1, 0xF5, 0xF9)
LGRAY    = RGBColor(0xE2, 0xE8, 0xF0)
CREAM    = RGBColor(0xFA, 0xFA, 0xF5)

SW = Inches(13.333)
SH = Inches(7.5)

# ── Helpers ───────────────────────────────────────────────────────────────────

def bg(slide, c=CREAM):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = c

def rect(slide, l, t, w, h, c, r=None):
    sh = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE, l, t, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = c
    sh.line.fill.background()
    if r: sh.adjustments[0] = r
    return sh

def txt(slide, l, t, w, h, text, sz=18, c=NAVY, bold=False, align=PP_ALIGN.LEFT, font='Segoe UI'):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(sz); p.font.color.rgb = c
    p.font.bold = bold; p.font.name = font; p.alignment = align
    return tb

def multi_txt(slide, l, t, w, h, lines, sz=14, c=SLATE, bold_first=False, font='Segoe UI'):
    """Multiple paragraphs in one textbox."""
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(sz); p.font.color.rgb = c
        p.font.name = font; p.space_after = Pt(6)
        if bold_first and i == 0: p.font.bold = True
    return tb

def img(slide, path, l, t, width=None, height=None):
    if not os.path.exists(path): return False
    kw = {}
    if width: kw['width'] = width
    if height: kw['height'] = height
    slide.shapes.add_picture(path, l, t, **kw)
    return True

def bar(slide, l, t, w, c, thick=Pt(4)):
    """Thin horizontal accent bar."""
    return rect(slide, l, t, w, thick, c)

def stripe(slide, l, t, w, h, c):
    """Vertical or horizontal stripe."""
    return rect(slide, l, t, w, h, c)

def badge(slide, l, t, text, c=AMBER, w=Inches(1.4), h=Inches(0.5)):
    """Score badge with rounded corners."""
    sh = rect(slide, l, t, w, h, c, r=0.2)
    tf = sh.text_frame; p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(14); p.font.color.rgb = WHITE
    p.font.bold = True; p.font.name = 'Segoe UI'; p.alignment = PP_ALIGN.CENTER
    return sh


# ══════════════════════════════════════════════════════════════════════════════
def build():
    print("BUILDING PRESENTATION v4")
    print("=" * 40)

    prs = Presentation()
    prs.slide_width = SW; prs.slide_height = SH
    BL = prs.slide_layouts[6]

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 1: TITLE
    # Layout: Left 55% text on cream | Right 45% navy panel
    # ──────────────────────────────────────────────────────────────────────────
    print("[1/10] Title")
    s = prs.slides.add_slide(BL); bg(s)

    # Right navy panel
    rect(s, Inches(7.5), Inches(0), Inches(5.833), SH, NAVY)
    # Teal accent stripe on right panel
    stripe(s, Inches(7.5), Inches(2.5), Pt(6), Inches(2.5), TEAL)

    # Left side content
    bar(s, Inches(1), Inches(1.5), Inches(2.5), TEAL, Pt(5))
    txt(s, Inches(1), Inches(1.8), Inches(5.5), Inches(1.2),
        "AI INTERNSHIP", 48, NAVY, True)
    txt(s, Inches(1), Inches(3.0), Inches(5.5), Inches(1),
        "PROJECT REPORT", 48, NAVY, True)
    bar(s, Inches(1), Inches(4.2), Inches(3), AMBER, Pt(4))
    txt(s, Inches(1), Inches(4.6), Inches(5.5), Inches(0.5),
        "A 6-Week Deep Dive into AI", 20, TEAL, True)
    txt(s, Inches(1), Inches(5.1), Inches(5.5), Inches(0.5),
        "From Planning to Production", 20, SLATE)

    # Right panel content
    txt(s, Inches(8.2), Inches(2.8), Inches(4.5), Inches(0.5),
        "Presented By", 14, LGRAY, align=PP_ALIGN.LEFT)
    txt(s, Inches(8.2), Inches(3.2), Inches(4.5), Inches(0.6),
        "Prateek Vijay", 28, WHITE, True)
    bar(s, Inches(8.2), Inches(3.9), Inches(2), TEAL, Pt(3))
    txt(s, Inches(8.2), Inches(4.2), Inches(4.5), Inches(0.5),
        "May - June 2026", 16, LGRAY)
    txt(s, Inches(8.2), Inches(4.7), Inches(4.5), Inches(0.5),
        "AI/ML Internship Program", 14, TEAL)

    # Bottom accent
    stripe(s, Inches(0), Inches(7.0), Inches(7.5), Inches(0.5), NAVY)
    stripe(s, Inches(0), Inches(6.85), Inches(4), Inches(0.15), TEAL)

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 2: OVERVIEW
    # Layout: Top header | 6 cards in 3x2 grid
    # ──────────────────────────────────────────────────────────────────────────
    print("[2/10] Overview")
    s = prs.slides.add_slide(BL); bg(s)

    # Top bar
    stripe(s, Inches(0), Inches(0), SW, Inches(0.1), TEAL)

    txt(s, Inches(0.8), Inches(0.4), Inches(8), Inches(0.7),
        "WHAT THIS INTERNSHIP COVERED", 32, NAVY, True)
    bar(s, Inches(0.8), Inches(1.1), Inches(2.5), TEAL, Pt(4))
    txt(s, Inches(0.8), Inches(1.3), Inches(10), Inches(0.5),
        "Six weeks. Six real projects. One complete AI lifecycle.", 17, TEAL, True)

    weeks = [
        ("01", "Project Planning",     "Scoped a healthcare predictive analytics\nsystem with risk assessment & timelines",  TEAL,  "65/100"),
        ("02", "Data Preprocessing",   "Cleaned the Titanic dataset with KNN\nimputation & built a reusable pipeline",      MINT,  "85/100"),
        ("03", "Model Building",       "Tuned a Random Forest across 162\ncombinations on breast cancer data",              AMBER, "45/100"),
        ("04", "Explainable AI",       "Made the model transparent with\nSHAP & LIME interpretability",                     CORAL, "55/100"),
        ("05", "Deployment",           "Shipped a FastAPI + Docker service\nwith monitoring & 15 automated tests",           TEAL,  "95/100"),
        ("06", "Ethics & Bias",        "Audited 32k records for fairness\nacross sex & race dimensions",                    NAVY,  "70/100"),
    ]

    for i, (num, title, desc, color, score) in enumerate(weeks):
        col = i % 3; row = i // 3
        x = Inches(0.6 + col * 4.1)
        y = Inches(2.0 + row * 2.6)

        # Card
        rect(s, x, y, Inches(3.8), Inches(2.3), WHITE, r=0.02)
        # Color top edge
        rect(s, x, y, Inches(3.8), Pt(5), color)
        # Number circle
        circle = rect(s, x + Inches(0.2), y + Inches(0.3), Inches(0.6), Inches(0.6), color, r=0.5)
        tf = circle.text_frame; p = tf.paragraphs[0]
        p.text = num; p.font.size = Pt(16); p.font.color.rgb = WHITE
        p.font.bold = True; p.font.name = 'Segoe UI'; p.alignment = PP_ALIGN.CENTER

        # Title
        txt(s, x + Inches(1.0), y + Inches(0.3), Inches(2.5), Inches(0.5),
            title, 15, NAVY, True)
        # Description
        txt(s, x + Inches(0.2), y + Inches(0.9), Inches(3.3), Inches(0.9),
            desc, 11, SLATE)
        # Score badge
        badge(s, x + Inches(2.2), y + Inches(1.7), score, color, Inches(1.3), Inches(0.4))

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 3: WEEK 1 — PLANNING
    # Layout: Full width content (no images for this week)
    # ──────────────────────────────────────────────────────────────────────────
    print("[3/10] Week 1")
    s = prs.slides.add_slide(BL); bg(s)

    # Left accent stripe
    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, TEAL)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(3), Inches(0.4),
        "WEEK 1", 14, TEAL, True)
    badge(s, Inches(11.5), Inches(0.4), "65 / 100", AMBER)
    txt(s, Inches(0.8), Inches(0.8), Inches(10), Inches(0.7),
        "PROJECT PLANNING & DOCUMENTATION", 30, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2), AMBER, Pt(4))

    txt(s, Inches(0.8), Inches(1.8), Inches(11.5), Inches(0.8),
        "I started by asking the right question: \"What if we could predict patient "
        "readmission risk before discharge?\" That single hypothesis shaped every "
        "decision that followed -- from dataset selection to model evaluation criteria.",
        15, SLATE)

    # Two cards side by side
    # Left card - What I Delivered
    rect(s, Inches(0.8), Inches(3.0), Inches(5.7), Inches(4.0), WHITE, r=0.02)
    rect(s, Inches(0.8), Inches(3.0), Inches(5.7), Pt(5), TEAL)
    txt(s, Inches(1.1), Inches(3.2), Inches(5), Inches(0.4),
        "WHAT I DELIVERED", 16, TEAL, True)
    multi_txt(s, Inches(1.1), Inches(3.8), Inches(5.2), Inches(3.0), [
        "  A full project plan targeting healthcare readmissions",
        "  Hypothesis: clinical + demographic features can",
        "  predict 30-day readmission with AUC > 0.80",
        "  Tech stack rationale -- Python, scikit-learn, pandas",
        "  Risk register covering data quality, overfitting,",
        "  compute constraints, and patient privacy",
        "  Project timeline with phased milestones",
    ], 13, SLATE)

    # Right card - Lessons
    rect(s, Inches(6.8), Inches(3.0), Inches(5.7), Inches(4.0), WHITE, r=0.02)
    rect(s, Inches(6.8), Inches(3.0), Inches(5.7), Pt(5), CORAL)
    txt(s, Inches(7.1), Inches(3.2), Inches(5), Inches(0.4),
        "WHAT I LEARNED", 16, CORAL, True)
    multi_txt(s, Inches(7.1), Inches(3.8), Inches(5.2), Inches(3.0), [
        "  Documentation depth matters -- the evaluator",
        "  wanted more on ethics and data governance",
        "  A good hypothesis drives the entire project scope;",
        "  without it, everything else is unfocused",
        "  Planning isn't just paperwork -- it saves weeks",
        "  of rework later in the project lifecycle",
        "  Score deducted for insufficient word count",
    ], 13, SLATE)

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 4: WEEK 2 — PREPROCESSING
    # Layout: Left 50% text | Right 50% stacked images
    # ──────────────────────────────────────────────────────────────────────────
    print("[4/10] Week 2")
    s = prs.slides.add_slide(BL); bg(s)

    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, MINT)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(3), Inches(0.4),
        "WEEK 2", 14, MINT, True)
    badge(s, Inches(5.8), Inches(0.4), "85 / 100", MINT)
    txt(s, Inches(0.8), Inches(0.8), Inches(6), Inches(0.7),
        "DATA PREPROCESSING", 30, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2), AMBER, Pt(4))

    txt(s, Inches(0.8), Inches(1.8), Inches(5.8), Inches(0.7),
        "The Titanic dataset has 891 passengers and a deliberate "
        "mess of missing data -- exactly the real-world chaos "
        "you need to learn to handle.",
        14, SLATE)

    rect(s, Inches(0.8), Inches(2.8), Inches(5.8), Inches(4.2), WHITE, r=0.02)
    rect(s, Inches(0.8), Inches(2.8), Inches(5.8), Pt(5), MINT)
    txt(s, Inches(1.1), Inches(3.0), Inches(5), Inches(0.4),
        "KEY TECHNIQUES", 15, MINT, True)
    multi_txt(s, Inches(1.1), Inches(3.5), Inches(5.2), Inches(3.0), [
        "  KNN Imputation for Age -- smarter than just",
        "  plugging in the mean; it uses feature similarity",
        "",
        "  IQR method with Winsorization -- tamed fare",
        "  outliers without throwing away valuable data",
        "",
        "  Engineered FamilySize, IsAlone, Title, FareBin",
        "  -- features that actually explain who survived",
        "",
        "  Wrapped everything in a sklearn Pipeline for",
        "  perfect reproducibility on new data",
    ], 12, SLATE)

    # Right side: two stacked images
    img(s, os.path.join(IMG_DP, "correlation_matrix.png"),
        Inches(7.0), Inches(0.4), width=Inches(5.8))
    img(s, os.path.join(IMG_DP, "feature_importance.png"),
        Inches(7.0), Inches(3.9), width=Inches(5.8))

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 5: WEEK 3 — MODEL BUILDING
    # Layout: Left 50% text + stats | Right 50% stacked images
    # ──────────────────────────────────────────────────────────────────────────
    print("[5/10] Week 3")
    s = prs.slides.add_slide(BL); bg(s)

    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, AMBER)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(3), Inches(0.4),
        "WEEK 3", 14, AMBER, True)
    badge(s, Inches(5.8), Inches(0.4), "45 / 100", RGBColor(0x94,0xA3,0xB8))
    txt(s, Inches(0.8), Inches(0.8), Inches(6), Inches(0.7),
        "BUILDING & TUNING THE MODEL", 28, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2), AMBER, Pt(4))

    txt(s, Inches(0.8), Inches(1.8), Inches(5.8), Inches(0.8),
        "Trained a Random Forest on the Breast Cancer Wisconsin "
        "dataset -- 569 samples, 30 features from cell-nucleus "
        "images. Goal: distinguish malignant from benign.",
        14, SLATE)

    # Stat boxes in a 2x2 grid
    stats = [
        ("162",   "Hyperparameter\nCombinations", TEAL),
        ("810",   "Total CV\nFits", AMBER),
        ("0.99",  "Best\nF1-Score", MINT),
        ("0.999", "Best\nROC-AUC", CORAL),
    ]
    for i, (val, label, color) in enumerate(stats):
        col = i % 2; row = i // 2
        x = Inches(0.8 + col * 3.0)
        y = Inches(3.0 + row * 2.0)
        rect(s, x, y, Inches(2.7), Inches(1.7), WHITE, r=0.02)
        rect(s, x, y, Inches(2.7), Pt(5), color)
        txt(s, x + Inches(0.2), y + Inches(0.3), Inches(2.3), Inches(0.6),
            val, 28, color, True, PP_ALIGN.CENTER)
        txt(s, x + Inches(0.2), y + Inches(1.0), Inches(2.3), Inches(0.5),
            label, 11, SLATE, False, PP_ALIGN.CENTER)

    # Right side: stacked images
    img(s, os.path.join(IMG_ML, "roc_curves.png"),
        Inches(7.0), Inches(0.4), width=Inches(5.8))
    img(s, os.path.join(IMG_ML, "confusion_matrices.png"),
        Inches(7.0), Inches(3.9), width=Inches(5.8))

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 6: WEEK 4 — EXPLAINABLE AI
    # Layout: Left 50% text in dark cards | Right 50% stacked images
    # ──────────────────────────────────────────────────────────────────────────
    print("[6/10] Week 4")
    s = prs.slides.add_slide(BL); bg(s)

    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, CORAL)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(3), Inches(0.4),
        "WEEK 4", 14, CORAL, True)
    badge(s, Inches(5.8), Inches(0.4), "55 / 100", RGBColor(0x94,0xA3,0xB8))
    txt(s, Inches(0.8), Inches(0.8), Inches(6), Inches(0.7),
        "EXPLAINABLE AI", 30, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2), AMBER, Pt(4))

    txt(s, Inches(0.8), Inches(1.8), Inches(5.8), Inches(0.6),
        "\"Why did the model say malignant?\" If you can't "
        "answer that, no doctor will trust your prediction.",
        14, SLATE)

    # SHAP card (dark)
    rect(s, Inches(0.8), Inches(2.7), Inches(5.8), Inches(2.0), NAVY, r=0.02)
    txt(s, Inches(1.1), Inches(2.9), Inches(5.2), Inches(0.4),
        "SHAP -- Global & Local Explanations", 15, TEAL, True)
    txt(s, Inches(1.1), Inches(3.4), Inches(5.2), Inches(1.2),
        "Used TreeExplainer for global feature rankings. "
        "The beeswarm plot showed worst concave points and "
        "worst perimeter as top drivers -- aligning with "
        "what oncologists know about cell shape irregularity.",
        12, LGRAY)

    # LIME card (dark)
    rect(s, Inches(0.8), Inches(5.0), Inches(5.8), Inches(2.0), NAVY, r=0.02)
    txt(s, Inches(1.1), Inches(5.2), Inches(5.2), Inches(0.4),
        "LIME -- Case-by-Case Transparency", 15, AMBER, True)
    txt(s, Inches(1.1), Inches(5.7), Inches(5.2), Inches(1.2),
        "Generated local explanations for individual predictions. "
        "Each shows exactly which measurements pushed the "
        "decision and by how much -- one benign case, one malignant.",
        12, LGRAY)

    # Right side: stacked images
    img(s, os.path.join(IMG_XAI, "fig3_shap_summary.png"),
        Inches(7.0), Inches(0.4), width=Inches(5.8))
    img(s, os.path.join(IMG_XAI, "fig6_lime_benign.png"),
        Inches(7.0), Inches(3.9), width=Inches(5.8))

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 7: WEEK 5 pt.1 — DEPLOYMENT ARCHITECTURE
    # Layout: Full width with 4 architecture cards
    # ──────────────────────────────────────────────────────────────────────────
    print("[7/10] Week 5 - Architecture")
    s = prs.slides.add_slide(BL); bg(s)

    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, TEAL)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(6), Inches(0.4),
        "WEEK 5  --  HIGHEST SCORE", 14, TEAL, True)
    badge(s, Inches(11.5), Inches(0.4), "95 / 100", TEAL)
    txt(s, Inches(0.8), Inches(0.8), Inches(10), Inches(0.7),
        "DEPLOYMENT & MONITORING", 30, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(3), AMBER, Pt(4))

    txt(s, Inches(0.8), Inches(1.8), Inches(11.5), Inches(0.7),
        "This was the big one. I didn't just train a model -- I shipped it as a real service "
        "that handles requests, logs everything, monitors itself, and restarts if something breaks.",
        14, SLATE)

    # 4 architecture cards
    cards = [
        ("FastAPI",     "7 REST endpoints\nPydantic validation\nSwagger docs, CORS\nRequest-ID middleware", TEAL),
        ("Docker",      "Multi-stage build\nNon-root user (appuser)\n512 MB memory limit\nAuto-restart policy",  NAVY),
        ("Monitoring",  "Thread-safe metrics\nLatency P95 tracking\nError rate per-class\nRolling 1000 window",  AMBER),
        ("Testing",     "15 pytest tests\nAll endpoints covered\nEdge case validation\nMetric accumulation",    CORAL),
    ]
    for i, (title, desc, color) in enumerate(cards):
        x = Inches(0.6 + i * 3.15)
        # Card
        rect(s, x, Inches(2.8), Inches(2.9), Inches(3.0), WHITE, r=0.02)
        # Colored header bar
        rect(s, x, Inches(2.8), Inches(2.9), Inches(0.7), color, r=0.02)
        txt(s, x + Inches(0.15), Inches(2.9), Inches(2.6), Inches(0.5),
            title, 17, WHITE, True, PP_ALIGN.CENTER)
        # Content
        txt(s, x + Inches(0.2), Inches(3.7), Inches(2.5), Inches(2.0),
            desc, 12, SLATE)

    # API endpoint bar at bottom
    rect(s, Inches(0.6), Inches(6.1), Inches(12.1), Inches(1.0), NAVY, r=0.02)
    txt(s, Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.4),
        "API ENDPOINTS", 12, TEAL, True, PP_ALIGN.LEFT)
    txt(s, Inches(0.8), Inches(6.55), Inches(11.7), Inches(0.4),
        "GET /health    GET /metrics    GET /model/info    "
        "POST /predict    POST /predict/batch    GET /docs    GET /redoc",
        12, LGRAY, False, PP_ALIGN.CENTER, 'Consolas')

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 8: WEEK 5 pt.2 — UNDER THE HOOD
    # Layout: Left 50% dark cards | Right 50% code sample
    # ──────────────────────────────────────────────────────────────────────────
    print("[8/10] Week 5 - Deep Dive")
    s = prs.slides.add_slide(BL); bg(s)

    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, TEAL)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(6), Inches(0.4),
        "WEEK 5  --  UNDER THE HOOD", 14, TEAL, True)
    txt(s, Inches(0.8), Inches(0.8), Inches(10), Inches(0.7),
        "HOW IT ACTUALLY WORKS", 28, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2), AMBER, Pt(4))

    # Docker card
    rect(s, Inches(0.8), Inches(1.9), Inches(5.8), Inches(2.4), NAVY, r=0.02)
    txt(s, Inches(1.1), Inches(2.1), Inches(5.2), Inches(0.4),
        "Containerization", 16, TEAL, True)
    txt(s, Inches(1.1), Inches(2.6), Inches(5.2), Inches(1.5),
        "Two-stage Dockerfile -- gcc and pip in the builder, "
        "only compiled packages in runtime. Runs as non-root "
        "user (appuser) for security. Docker Compose sets "
        "CPU/memory limits and auto-restarts on failure. "
        "Healthcheck pings /health every 30 seconds.",
        12, LGRAY)

    # Logging card
    rect(s, Inches(0.8), Inches(4.6), Inches(5.8), Inches(2.5), NAVY, r=0.02)
    txt(s, Inches(1.1), Inches(4.8), Inches(5.2), Inches(0.4),
        "Structured Logging", 16, AMBER, True)
    txt(s, Inches(1.1), Inches(5.3), Inches(5.2), Inches(1.5),
        "Every request gets a UUID. Every log entry is structured "
        "JSON with timestamp, service name, level, and custom "
        "fields. Rotating file handler caps at 10 MB with "
        "5 backups -- logs persist but don't fill the disk.",
        12, LGRAY)

    # Right: request/response code sample
    rect(s, Inches(7.0), Inches(1.9), Inches(5.8), Inches(5.2), WHITE, r=0.02)
    rect(s, Inches(7.0), Inches(1.9), Inches(5.8), Pt(5), TEAL)
    txt(s, Inches(7.3), Inches(2.1), Inches(5.2), Inches(0.4),
        "Sample: POST /predict", 14, TEAL, True)

    txt(s, Inches(7.3), Inches(2.6), Inches(5.2), Inches(0.3),
        "Request:", 12, NAVY, True)
    txt(s, Inches(7.3), Inches(3.0), Inches(5.2), Inches(1.2),
        '{\n'
        '  "sepal_length": 5.1,\n'
        '  "sepal_width": 3.5,\n'
        '  "petal_length": 1.4,\n'
        '  "petal_width": 0.2\n'
        '}',
        11, SLATE, font='Consolas')

    txt(s, Inches(7.3), Inches(4.4), Inches(5.2), Inches(0.3),
        "Response:", 12, NAVY, True)
    txt(s, Inches(7.3), Inches(4.8), Inches(5.2), Inches(2.0),
        '{\n'
        '  "prediction": 0,\n'
        '  "class_name": "setosa",\n'
        '  "confidence": 1.0,\n'
        '  "probabilities": {\n'
        '    "setosa": 1.0,\n'
        '    "versicolor": 0.0,\n'
        '    "virginica": 0.0\n'
        '  }\n'
        '}',
        11, SLATE, font='Consolas')

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 9: WEEK 6 — ETHICS
    # Layout: Left 50% text | Right 50% stacked images
    # ──────────────────────────────────────────────────────────────────────────
    print("[9/10] Week 6")
    s = prs.slides.add_slide(BL); bg(s)

    stripe(s, Inches(0), Inches(0), Inches(0.15), SH, CORAL)
    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(3), Inches(0.4),
        "WEEK 6", 14, CORAL, True)
    badge(s, Inches(5.8), Inches(0.4), "70 / 100", CORAL)
    txt(s, Inches(0.8), Inches(0.8), Inches(6), Inches(0.7),
        "AI ETHICS & BIAS AUDIT", 30, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2), AMBER, Pt(4))

    txt(s, Inches(0.8), Inches(1.8), Inches(5.8), Inches(0.7),
        "Audited a Logistic Regression model on the UCI Adult "
        "Income dataset -- 32,561 records with sensitive "
        "attributes. Does this model treat everyone fairly?",
        14, SLATE)

    # Findings card
    rect(s, Inches(0.8), Inches(2.8), Inches(5.8), Inches(2.0), NAVY, r=0.02)
    txt(s, Inches(1.1), Inches(3.0), Inches(5.2), Inches(0.3),
        "WHAT THE AUDIT FOUND", 14, CORAL, True)
    multi_txt(s, Inches(1.1), Inches(3.4), Inches(5.2), Inches(1.2), [
        "  Disparate Impact by sex fell below the legal 80% threshold",
        "  TPR for high-income females was much lower than for males",
        "  Non-White females had the lowest positive prediction rates",
    ], 12, LGRAY)

    # Remediation card
    rect(s, Inches(0.8), Inches(5.1), Inches(5.8), Inches(1.9), WHITE, r=0.02)
    rect(s, Inches(0.8), Inches(5.1), Inches(5.8), Pt(5), CORAL)
    txt(s, Inches(1.1), Inches(5.3), Inches(5.2), Inches(0.3),
        "PROPOSED FIXES", 14, CORAL, True)
    multi_txt(s, Inches(1.1), Inches(5.7), Inches(5.2), Inches(1.0), [
        "  Resample training data to equalize representation",
        "  Apply adversarial debiasing during training",
        "  Tune classification thresholds per demographic group",
    ], 12, SLATE)

    # Right side: stacked images
    img(s, os.path.join(IMG_ETH, "fig2_disparate_impact.png"),
        Inches(7.0), Inches(0.4), width=Inches(5.8))
    img(s, os.path.join(IMG_ETH, "fig9_intersectional_bias.png"),
        Inches(7.0), Inches(3.9), width=Inches(5.8))

    # ──────────────────────────────────────────────────────────────────────────
    # SLIDE 10: CONCLUSION
    # Layout: Left 55% takeaways | Right 45% navy panel with scores
    # ──────────────────────────────────────────────────────────────────────────
    print("[10/10] Conclusion")
    s = prs.slides.add_slide(BL); bg(s)

    # Right navy panel (mirrors title slide)
    rect(s, Inches(7.8), Inches(0), Inches(5.533), SH, NAVY)
    stripe(s, Inches(7.8), Inches(2.0), Pt(5), Inches(3), TEAL)

    stripe(s, Inches(0), Inches(0), SW, Inches(0.08), NAVY)

    txt(s, Inches(0.8), Inches(0.4), Inches(6), Inches(0.4),
        "WRAPPING UP", 14, TEAL, True)
    txt(s, Inches(0.8), Inches(0.8), Inches(6.5), Inches(0.7),
        "KEY TAKEAWAYS", 32, NAVY, True)
    bar(s, Inches(0.8), Inches(1.5), Inches(2.5), AMBER, Pt(4))

    # Three takeaway cards
    takeaways = [
        ("Ship it, don't just train it",
         "The deployment week scored 95 because it proved "
         "the model works in production -- not just in a notebook. "
         "A model that can't serve requests has zero value.", TEAL),
        ("If you can't explain it, don't deploy it",
         "SHAP and LIME turned a black-box into something a "
         "clinician can actually review. Transparency builds "
         "the trust that adoption requires.", AMBER),
        ("Fairness isn't optional",
         "The ethics audit caught real bias -- females and "
         "minorities were systematically disadvantaged. "
         "You have to check before you ship.", CORAL),
    ]
    for i, (title, desc, color) in enumerate(takeaways):
        y = Inches(2.0 + i * 1.7)
        rect(s, Inches(0.8), y, Inches(6.5), Inches(1.4), WHITE, r=0.02)
        rect(s, Inches(0.8), y, Pt(6), Inches(1.4), color)
        # Number
        n = rect(s, Inches(1.1), y + Inches(0.25), Inches(0.5), Inches(0.5), color, r=0.5)
        tf = n.text_frame; p = tf.paragraphs[0]
        p.text = str(i + 1); p.font.size = Pt(16); p.font.color.rgb = WHITE
        p.font.bold = True; p.font.name = 'Segoe UI'; p.alignment = PP_ALIGN.CENTER
        txt(s, Inches(1.8), y + Inches(0.15), Inches(5.2), Inches(0.4),
            title, 15, NAVY, True)
        txt(s, Inches(1.8), y + Inches(0.55), Inches(5.2), Inches(0.8),
            desc, 11, SLATE)

    # Right panel: scores
    txt(s, Inches(8.5), Inches(2.2), Inches(3.8), Inches(0.5),
        "SCORES", 18, WHITE, True, PP_ALIGN.CENTER)
    bar(s, Inches(9.3), Inches(2.7), Inches(2.2), TEAL, Pt(3))

    scores = [("Week 1", "65", LGRAY), ("Week 2", "85", MINT),
              ("Week 3", "45", LGRAY), ("Week 4", "55", LGRAY),
              ("Week 5", "95", TEAL),  ("Week 6", "70", LGRAY)]
    for i, (wk, sc, col) in enumerate(scores):
        y = Inches(3.0 + i * 0.65)
        rect(s, Inches(8.5), y, Inches(3.8), Inches(0.5), col, r=0.1)
        txt(s, Inches(8.7), y + Inches(0.05), Inches(1.5), Inches(0.4),
            wk, 12, NAVY if col != TEAL else WHITE, True)
        txt(s, Inches(11.0), y + Inches(0.05), Inches(1.0), Inches(0.4),
            sc, 14, NAVY if col != TEAL else WHITE, True, PP_ALIGN.RIGHT)

    # Thank you
    txt(s, Inches(8.5), Inches(6.2), Inches(3.8), Inches(0.7),
        "Thank You!", 28, WHITE, True, PP_ALIGN.CENTER)

    # ── SAVE ──────────────────────────────────────────────────────────────────
    path = os.path.join(OUT, "Internship_Presentation_v4.pptx")
    prs.save(path)
    print(f"\n[OK] Saved -> {path}")
    print(f"    Slides: {len(prs.slides)}")
    print("=" * 40)

if __name__ == "__main__":
    build()
