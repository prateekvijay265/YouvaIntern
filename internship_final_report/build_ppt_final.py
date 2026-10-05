"""
build_ppt_final.py
==================
10-slide AI Internship presentation — handcrafted design.

Design language (inspired by the LOCALOOM reference):
  • Warm, light background with bold geometric ribbon accents
  • Angled parallelogram shapes layered for depth
  • Large images framed inside colored panels
  • Human, conversational text — not generic AI bullet points
  • Tech-savvy color palette: deep indigo / electric teal / warm amber / slate
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE   = r"c:\Users\prate\Desktop\youva"
OUT    = os.path.join(BASE, "internship_final_report")
IMG_DP = os.path.join(BASE, "data processing")
IMG_ML = os.path.join(BASE, "ml_model_development", "results", "figures")
IMG_XAI = os.path.join(BASE, "explainable_ai")
IMG_ETH = os.path.join(BASE, "ai_ethics_audit")
os.makedirs(OUT, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = RGBColor(0xF8, 0xFA, 0xFC)   # barely-there blue-white
PANEL    = RGBColor(0x0F, 0x24, 0x4E)   # deep indigo (like dark navy card)
TEAL     = RGBColor(0x00, 0xB4, 0xD8)   # electric teal
AMBER    = RGBColor(0xF5, 0xA6, 0x23)   # warm amber / gold
CORAL    = RGBColor(0xEF, 0x47, 0x6F)   # vivid coral-pink
MINT     = RGBColor(0x38, 0xB2, 0xAC)   # muted mint-teal
SLATE    = RGBColor(0x47, 0x55, 0x69)   # dark slate for body text
HEADING  = RGBColor(0x0F, 0x24, 0x4E)   # same deep indigo for headings
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY    = RGBColor(0xCB, 0xD5, 0xE1)   # light gray for accents
DGRAY    = RGBColor(0x1E, 0x29, 0x3B)   # very dark gray
OFFWHITE = RGBColor(0xF1, 0xF5, 0xF9)

SW = Inches(13.333)
SH = Inches(7.5)

# ── Primitive helpers ─────────────────────────────────────────────────────────

def _bg(slide, c=BG):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = c

def _rect(slide, l, t, w, h, c, radius=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                l, t, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = c
    sh.line.fill.background()
    if radius: sh.adjustments[0] = radius
    return sh

def _para(slide, l, t, w, h, c, adj=0.25):
    sh = slide.shapes.add_shape(MSO_SHAPE.PARALLELOGRAM, l, t, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = c
    sh.line.fill.background()
    sh.adjustments[0] = adj
    return sh

def _txt(slide, l, t, w, h, text, sz=18, c=HEADING, bold=False, align=PP_ALIGN.LEFT, font='Segoe UI'):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(sz); p.font.color.rgb = c
    p.font.bold = bold; p.font.name = font; p.alignment = align
    return tb

def _bullets(slide, l, t, w, h, items, sz=15, c=SLATE, spacing=Pt(10), font='Segoe UI'):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    for i, txt in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = txt; p.font.size = Pt(sz); p.font.color.rgb = c
        p.font.name = font; p.space_after = spacing
    return tb

def _img(slide, path, l, t, width=None, height=None):
    if not os.path.exists(path): return False
    kw = {}
    if width: kw['width'] = width
    if height: kw['height'] = height
    slide.shapes.add_picture(path, l, t, **kw)
    return True

def _circle(slide, l, t, d, c):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, l, t, d, d)
    sh.fill.solid(); sh.fill.fore_color.rgb = c
    sh.line.fill.background()
    return sh

def _line(slide, l, t, w, c, thickness=Pt(4)):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, thickness)
    sh.fill.solid(); sh.fill.fore_color.rgb = c
    sh.line.fill.background()
    return sh

# ── Ribbon generators (faithful to reference) ────────────────────────────────

def ribbons_title(s):
    """Title slide: big angular panels on right, crossing ribbons bottom-left."""
    _bg(s)
    # Right-side angular panel stack (image backdrop area)
    _para(s, Inches(7.2), Inches(-1), Inches(8), Inches(10), LGRAY, 0.15)
    _para(s, Inches(7.8), Inches(-0.5), Inches(7.5), Inches(9), OFFWHITE, 0.15)
    # Crossing ribbons — bottom left
    _para(s, Inches(-2), Inches(5.2), Inches(9), Inches(1.3), TEAL, 0.25)
    _para(s, Inches(-0.5), Inches(5.9), Inches(8), Inches(1.1), PANEL, 0.25)
    # Thin accent bar top
    _line(s, Inches(1), Inches(1.2), Inches(4.5), AMBER)

def ribbons_A(s):
    """Layout A: top-right accent + left mid-ribbon + bottom bar."""
    _bg(s)
    _para(s, Inches(8.5), Inches(-0.8), Inches(6), Inches(1.8), TEAL, 0.3)
    _para(s, Inches(-1.5), Inches(3.2), Inches(3.5), Inches(1.0), PANEL, 0.3)
    _rect(s, Inches(0), Inches(6.8), Inches(13.333), Inches(0.7), PANEL)

def ribbons_B(s):
    """Layout B: left vertical dark strip + bottom ribbon."""
    _bg(s)
    _para(s, Inches(-1), Inches(-1), Inches(2.2), Inches(10), PANEL, 0.08)
    _para(s, Inches(-0.5), Inches(-1), Inches(1.8), Inches(10), RGBColor(0x14, 0x30, 0x60), 0.08)
    _para(s, Inches(0.5), Inches(5.5), Inches(14), Inches(1.2), TEAL, 0.15)
    _para(s, Inches(1.5), Inches(6.1), Inches(13), Inches(0.9), PANEL, 0.15)

def ribbons_C(s):
    """Layout C: right image column + top accent."""
    _bg(s)
    _rect(s, Inches(7.8), Inches(0), Inches(5.6), Inches(7.5), OFFWHITE)
    _para(s, Inches(7.3), Inches(-0.5), Inches(1), Inches(8.5), TEAL, 0.5)
    _rect(s, Inches(0), Inches(0), Inches(13.333), Inches(0.15), AMBER)
    _rect(s, Inches(0), Inches(7.35), Inches(13.333), Inches(0.15), PANEL)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def build():
    print("=" * 55)
    print("  BUILDING FINAL PRESENTATION (v3)")
    print("=" * 55)

    prs = Presentation()
    prs.slide_width = SW; prs.slide_height = SH
    BL = prs.slide_layouts[6]

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 1 — TITLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[1/10] Title …")
    s = prs.slides.add_slide(BL); ribbons_title(s)

    _txt(s, Inches(1), Inches(1.6), Inches(6), Inches(2),
         "AI INTERNSHIP", 46, HEADING, True)
    _txt(s, Inches(1), Inches(2.8), Inches(6), Inches(1.2),
         "PROJECT REPORT", 46, HEADING, True)
    _line(s, Inches(1), Inches(4.2), Inches(3), AMBER)
    _txt(s, Inches(1), Inches(4.5), Inches(5), Inches(0.5),
         "A 6-Week Deep Dive into AI — From Planning to Production",
         16, SLATE)
    # Right side info
    _txt(s, Inches(9), Inches(2.5), Inches(3.5), Inches(0.8),
         "Presented By:", 14, SLATE, align=PP_ALIGN.RIGHT)
    _txt(s, Inches(9), Inches(3.0), Inches(3.5), Inches(0.8),
         "Prateek Vijay", 22, HEADING, True, PP_ALIGN.RIGHT)
    _txt(s, Inches(9), Inches(3.8), Inches(3.5), Inches(0.5),
         "May – June 2026", 16, TEAL, True, PP_ALIGN.RIGHT)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 2 — WHAT THIS INTERNSHIP COVERED
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[2/10] Overview …")
    s = prs.slides.add_slide(BL); ribbons_A(s)

    _txt(s, Inches(0.8), Inches(0.5), Inches(8), Inches(0.8),
         "WHAT THIS INTERNSHIP COVERED", 34, HEADING, True)
    _line(s, Inches(0.8), Inches(1.3), Inches(2.5), TEAL)

    _txt(s, Inches(0.8), Inches(1.6), Inches(7), Inches(0.6),
         "Six weeks. Six real projects. One complete AI lifecycle.",
         18, TEAL, True)

    # Week cards — 3 columns × 2 rows with colored left border
    weeks_data = [
        ("01", "Project Planning",     "Scoped a healthcare\npredictive analytics system",  TEAL),
        ("02", "Data Preprocessing",   "Cleaned the Titanic dataset;\nbuilt a reusable pipeline",  MINT),
        ("03", "Model Building",       "Tuned a Random Forest on\n569 breast-cancer samples",  AMBER),
        ("04", "Explainable AI",       "Made the model transparent\nwith SHAP & LIME",  CORAL),
        ("05", "Deployment",           "Shipped a FastAPI service\ninside Docker — scored 95!",  TEAL),
        ("06", "Ethics & Fairness",    "Audited 32k records for\nbias across sex & race",  PANEL),
    ]
    for i, (num, title, desc, color) in enumerate(weeks_data):
        col = i % 3; row = i // 3
        x = Inches(0.8 + col * 4.0)
        y = Inches(2.5 + row * 2.1)
        # Card background
        _rect(s, x, y, Inches(3.6), Inches(1.8), WHITE, radius=0.03)
        # Color stripe on left edge
        _rect(s, x, y, Pt(6), Inches(1.8), color)
        # Week number
        _txt(s, x + Inches(0.2), y + Inches(0.1), Inches(0.6), Inches(0.5),
             num, 28, color, True)
        # Title
        _txt(s, x + Inches(0.8), y + Inches(0.1), Inches(2.5), Inches(0.5),
             title, 14, HEADING, True)
        # Description
        _txt(s, x + Inches(0.8), y + Inches(0.6), Inches(2.5), Inches(1.0),
             desc, 11, SLATE)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 3 — WEEK 1: PLANNING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[3/10] Week 1 …")
    s = prs.slides.add_slide(BL); ribbons_B(s)

    _txt(s, Inches(2), Inches(0.6), Inches(5), Inches(0.4),
         "WEEK 1", 14, TEAL, True)
    _txt(s, Inches(2), Inches(1.0), Inches(9), Inches(0.8),
         "PROJECT PLANNING & DOCUMENTATION", 30, HEADING, True)
    _line(s, Inches(2), Inches(1.8), Inches(2), AMBER)

    _txt(s, Inches(2), Inches(2.2), Inches(9), Inches(0.6),
         "I started by asking the right question: \"What if we could predict patient "
         "readmission risk before discharge?\" That framing shaped every decision that followed.",
         15, SLATE)

    _txt(s, Inches(2), Inches(3.2), Inches(4.5), Inches(0.4),
         "WHAT I DELIVERED", 16, TEAL, True)
    _bullets(s, Inches(2), Inches(3.7), Inches(4.5), Inches(2.5), [
        "•  A full project plan targeting healthcare readmissions",
        "•  Hypothesis: clinical + demographic features can predict\n   30-day readmission with AUC > 0.80",
        "•  Tech stack rationale (Python, scikit-learn, pandas)",
        "•  Risk register with concrete mitigation steps",
    ], 13, SLATE)

    _txt(s, Inches(7.5), Inches(3.2), Inches(4.5), Inches(0.4),
         "WHAT I LEARNED", 16, CORAL, True)
    _bullets(s, Inches(7.5), Inches(3.7), Inches(4.5), Inches(2.5), [
        "•  Documentation depth matters — evaluator wanted\n   more on ethics and data governance",
        "•  A good hypothesis drives the entire project scope",
        "•  Planning isn't just paperwork — it saves weeks later",
    ], 13, SLATE)

    # Score badge
    badge = _rect(s, Inches(11), Inches(1.0), Inches(1.3), Inches(0.6), AMBER, 0.15)
    tf = badge.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; p.text = "65 / 100"
    p.font.size = Pt(14); p.font.color.rgb = WHITE; p.font.bold = True
    p.font.name = 'Segoe UI'; p.alignment = PP_ALIGN.CENTER

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 4 — WEEK 2: DATA PREPROCESSING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[4/10] Week 2 …")
    s = prs.slides.add_slide(BL); ribbons_C(s)

    _txt(s, Inches(0.8), Inches(0.4), Inches(5), Inches(0.4),
         "WEEK 2", 14, TEAL, True)
    _txt(s, Inches(0.8), Inches(0.8), Inches(6.5), Inches(0.8),
         "DATA PREPROCESSING", 34, HEADING, True)
    _line(s, Inches(0.8), Inches(1.6), Inches(2), AMBER)

    _txt(s, Inches(0.8), Inches(1.9), Inches(6), Inches(0.8),
         "The Titanic dataset has 891 passengers and a deliberate mess of missing data — "
         "exactly the kind of real-world chaos you need to learn to handle properly.",
         14, SLATE)

    _txt(s, Inches(0.8), Inches(2.9), Inches(6), Inches(0.4),
         "KEY TECHNIQUES", 16, TEAL, True)
    _bullets(s, Inches(0.8), Inches(3.4), Inches(6), Inches(3.5), [
        "•  KNN Imputation for Age — smarter than plugging in the mean",
        "•  IQR method with Winsorization to tame fare outliers\n   without throwing away data",
        "•  Engineered FamilySize, IsAlone, Title — features that\n   actually explain who survived",
        "•  Wrapped everything in a sklearn Pipeline so it\n   reproduces perfectly on new data",
    ], 13, SLATE)

    # Score badge
    badge = _rect(s, Inches(5.5), Inches(0.4), Inches(1.3), Inches(0.6), MINT, 0.15)
    tf = badge.text_frame; p = tf.paragraphs[0]; p.text = "85 / 100"
    p.font.size = Pt(14); p.font.color.rgb = WHITE; p.font.bold = True
    p.font.name = 'Segoe UI'; p.alignment = PP_ALIGN.CENTER

    # Right image panel
    _img(s, os.path.join(IMG_DP, "correlation_matrix.png"),
         Inches(8.0), Inches(0.5), width=Inches(4.8))
    _img(s, os.path.join(IMG_DP, "feature_importance.png"),
         Inches(8.0), Inches(4.0), width=Inches(4.8))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 5 — WEEK 3: MODEL BUILDING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[5/10] Week 3 …")
    s = prs.slides.add_slide(BL); ribbons_B(s)

    _txt(s, Inches(2), Inches(0.6), Inches(5), Inches(0.4),
         "WEEK 3", 14, TEAL, True)
    _txt(s, Inches(2), Inches(1.0), Inches(9), Inches(0.8),
         "BUILDING & TUNING THE MODEL", 30, HEADING, True)
    _line(s, Inches(2), Inches(1.8), Inches(2), AMBER)

    _txt(s, Inches(2), Inches(2.2), Inches(5), Inches(0.6),
         "I trained a Random Forest on the Breast Cancer Wisconsin dataset — 569 samples, "
         "30 features computed from cell-nucleus images. The goal: distinguish malignant from benign.",
         14, SLATE)

    # Stats row with colored circles
    stats = [("162", "Parameter\nCombinations", TEAL),
             ("810", "Total\nCV Fits", AMBER),
             ("0.99", "Best\nF1-Score", MINT),
             ("0.999", "Best\nROC-AUC", CORAL)]
    for i, (val, label, color) in enumerate(stats):
        cx = Inches(2.3 + i * 2.3)
        _circle(s, cx, Inches(3.3), Inches(1.1), color)
        tf = slide_circle_txt = _txt(s, cx, Inches(3.5), Inches(1.1), Inches(0.6),
             val, 20, WHITE, True, PP_ALIGN.CENTER)
        _txt(s, cx - Inches(0.2), Inches(4.5), Inches(1.5), Inches(0.6),
             label, 10, SLATE, False, PP_ALIGN.CENTER)

    # Images
    _img(s, os.path.join(IMG_ML, "roc_curves.png"),
         Inches(7.5), Inches(0.8), width=Inches(5))
    _img(s, os.path.join(IMG_ML, "confusion_matrices.png"),
         Inches(7.5), Inches(3.8), width=Inches(5))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 6 — WEEK 4: EXPLAINABLE AI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[6/10] Week 4 …")
    s = prs.slides.add_slide(BL); ribbons_C(s)

    _txt(s, Inches(0.8), Inches(0.4), Inches(5), Inches(0.4),
         "WEEK 4", 14, TEAL, True)
    _txt(s, Inches(0.8), Inches(0.8), Inches(6.5), Inches(0.8),
         "EXPLAINABLE AI", 34, HEADING, True)
    _line(s, Inches(0.8), Inches(1.6), Inches(2), AMBER)

    _txt(s, Inches(0.8), Inches(1.9), Inches(6), Inches(0.8),
         "\"Why did the model say malignant?\" If you can't answer that, "
         "a doctor has no reason to trust your prediction. This week was about earning that trust.",
         14, SLATE)

    # SHAP card
    _rect(s, Inches(0.8), Inches(3.0), Inches(6), Inches(1.6), PANEL, 0.03)
    _txt(s, Inches(1.1), Inches(3.15), Inches(5.5), Inches(0.4),
         "SHAP — Global & Local Explanations", 15, TEAL, True)
    _txt(s, Inches(1.1), Inches(3.6), Inches(5.5), Inches(1.0),
         "Used TreeExplainer for global feature rankings. The beeswarm plot "
         "showed worst concave points and worst perimeter as the top drivers — "
         "which aligns with what oncologists already know about cell shape irregularity.",
         12, WHITE)

    # LIME card
    _rect(s, Inches(0.8), Inches(4.9), Inches(6), Inches(1.6), PANEL, 0.03)
    _txt(s, Inches(1.1), Inches(5.05), Inches(5.5), Inches(0.4),
         "LIME — Case-by-Case Transparency", 15, AMBER, True)
    _txt(s, Inches(1.1), Inches(5.5), Inches(5.5), Inches(1.0),
         "Generated local explanations for individual predictions — one benign, one malignant. "
         "Each explanation shows exactly which measurements pushed the decision and by how much.",
         12, WHITE)

    # Right image panel
    _img(s, os.path.join(IMG_XAI, "fig3_shap_summary.png"),
         Inches(8.0), Inches(0.4), width=Inches(4.8))
    _img(s, os.path.join(IMG_XAI, "fig6_lime_benign.png"),
         Inches(8.0), Inches(4.0), width=Inches(4.8))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 7 — WEEK 5 pt.1: DEPLOYMENT ARCHITECTURE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[7/10] Week 5 — Architecture …")
    s = prs.slides.add_slide(BL); ribbons_A(s)

    _txt(s, Inches(0.8), Inches(0.4), Inches(5), Inches(0.4),
         "WEEK 5  ★  SCORED 95/100", 14, AMBER, True)
    _txt(s, Inches(0.8), Inches(0.8), Inches(10), Inches(0.8),
         "DEPLOYMENT & MONITORING", 34, HEADING, True)
    _line(s, Inches(0.8), Inches(1.6), Inches(3), AMBER)

    _txt(s, Inches(0.8), Inches(1.9), Inches(11), Inches(0.6),
         "This was the big one. I didn't just train a model — I shipped it as a real service "
         "that handles requests, logs everything, monitors itself, and restarts automatically "
         "if something breaks.", 14, SLATE)

    # Architecture cards in a row
    cards = [
        ("FastAPI", "7 REST endpoints with\nPydantic validation,\nSwagger docs, CORS", TEAL),
        ("Docker", "Multi-stage build,\nnon-root user, 512 MB\nmemory limit, healthcheck", PANEL),
        ("Monitoring", "Thread-safe metrics:\nlatency P95, error rate,\nper-class distributions", AMBER),
        ("Logging", "Structured JSON logs,\nrotating files (10 MB × 5),\nconsole + file handlers", CORAL),
    ]
    for i, (title, desc, color) in enumerate(cards):
        x = Inches(0.8 + i * 3.1)
        _rect(s, x, Inches(2.8), Inches(2.8), Inches(2.8), WHITE, 0.03)
        _rect(s, x, Inches(2.8), Inches(2.8), Inches(0.6), color, 0.03)
        _txt(s, x + Inches(0.15), Inches(2.9), Inches(2.5), Inches(0.5),
             title, 16, WHITE, True, PP_ALIGN.CENTER)
        _txt(s, x + Inches(0.15), Inches(3.6), Inches(2.5), Inches(1.8),
             desc, 12, SLATE, False, PP_ALIGN.CENTER)

    # API endpoint table card
    _rect(s, Inches(0.8), Inches(5.8), Inches(11.7), Inches(0.8), PANEL, 0.02)
    _txt(s, Inches(1.0), Inches(5.9), Inches(11), Inches(0.6),
         "GET /health   •   GET /metrics   •   GET /model/info   •   "
         "POST /predict   •   POST /predict/batch   •   GET /docs   •   GET /redoc",
         12, LGRAY, False, PP_ALIGN.CENTER, 'Consolas')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 8 — WEEK 5 pt.2: HOW IT WORKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[8/10] Week 5 — Deep Dive …")
    s = prs.slides.add_slide(BL); ribbons_C(s)

    _txt(s, Inches(0.8), Inches(0.4), Inches(5), Inches(0.4),
         "WEEK 5  —  UNDER THE HOOD", 14, TEAL, True)
    _txt(s, Inches(0.8), Inches(0.8), Inches(6.5), Inches(0.8),
         "HOW IT ACTUALLY WORKS", 30, HEADING, True)
    _line(s, Inches(0.8), Inches(1.6), Inches(2), AMBER)

    # Docker card
    _rect(s, Inches(0.8), Inches(2.0), Inches(6.2), Inches(2.0), PANEL, 0.03)
    _txt(s, Inches(1.1), Inches(2.1), Inches(5.5), Inches(0.4),
         "Containerization", 16, TEAL, True)
    _txt(s, Inches(1.1), Inches(2.6), Inches(5.5), Inches(1.2),
         "The Dockerfile uses a two-stage build — gcc and pip in the builder, only "
         "the compiled packages in runtime. Runs as a non-root user (appuser) for security. "
         "Docker Compose sets CPU/memory limits and auto-restarts on failure.",
         12, WHITE)

    # Testing card
    _rect(s, Inches(0.8), Inches(4.3), Inches(6.2), Inches(2.0), PANEL, 0.03)
    _txt(s, Inches(1.1), Inches(4.4), Inches(5.5), Inches(0.4),
         "15 Automated Tests", 16, AMBER, True)
    _txt(s, Inches(1.1), Inches(4.9), Inches(5.5), Inches(1.2),
         "The pytest suite covers every endpoint: health checks return the right payload, "
         "predictions classify known setosa and virginica samples correctly, invalid inputs "
         "trigger 422 errors, batch endpoints reject empty lists, and metrics accumulate properly.",
         12, WHITE)

    # Right image panel — sample request/response
    _rect(s, Inches(8.0), Inches(0.8), Inches(4.8), Inches(5.5), WHITE, 0.03)
    _txt(s, Inches(8.3), Inches(1.0), Inches(4.2), Inches(0.4),
         "Sample Request → Response", 14, HEADING, True)
    _txt(s, Inches(8.3), Inches(1.6), Inches(4.2), Inches(0.3),
         "POST /predict", 12, TEAL, True, font='Consolas')
    _txt(s, Inches(8.3), Inches(2.0), Inches(4.2), Inches(1.5),
         '{\n  "sepal_length": 5.1,\n  "sepal_width": 3.5,\n'
         '  "petal_length": 1.4,\n  "petal_width": 0.2\n}',
         11, SLATE, font='Consolas')
    _txt(s, Inches(8.3), Inches(3.6), Inches(4.2), Inches(0.3),
         "→ Response", 12, AMBER, True, font='Consolas')
    _txt(s, Inches(8.3), Inches(4.0), Inches(4.2), Inches(2.0),
         '{\n  "prediction": 0,\n  "class_name": "setosa",\n'
         '  "confidence": 1.0,\n  "probabilities": {\n'
         '    "setosa": 1.0,\n    "versicolor": 0.0,\n'
         '    "virginica": 0.0\n  }\n}',
         11, SLATE, font='Consolas')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 9 — WEEK 6: ETHICS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[9/10] Week 6 …")
    s = prs.slides.add_slide(BL); ribbons_B(s)

    _txt(s, Inches(2), Inches(0.6), Inches(5), Inches(0.4),
         "WEEK 6", 14, TEAL, True)
    _txt(s, Inches(2), Inches(1.0), Inches(9), Inches(0.8),
         "AI ETHICS & BIAS AUDIT", 30, HEADING, True)
    _line(s, Inches(2), Inches(1.8), Inches(2), CORAL)

    _txt(s, Inches(2), Inches(2.2), Inches(5.5), Inches(0.6),
         "I audited a Logistic Regression model trained on the UCI Adult Income dataset — "
         "32,561 records with sensitive attributes like sex and race. "
         "The question: does this model treat everyone fairly?",
         14, SLATE)

    # Findings cards
    _rect(s, Inches(2), Inches(3.2), Inches(5.5), Inches(1.5), PANEL, 0.03)
    _txt(s, Inches(2.3), Inches(3.3), Inches(5), Inches(0.3),
         "WHAT THE AUDIT FOUND", 14, CORAL, True)
    _txt(s, Inches(2.3), Inches(3.7), Inches(5), Inches(1.0),
         "• Disparate Impact by sex fell below the legal 80% threshold\n"
         "• TPR for high-income females was significantly lower than for males\n"
         "• Non-White females had the lowest positive prediction rates of any group",
         12, WHITE)

    # Remediation card
    _rect(s, Inches(2), Inches(4.9), Inches(5.5), Inches(1.2), WHITE, 0.03)
    _rect(s, Inches(2), Inches(4.9), Inches(5.5), Pt(5), CORAL)
    _txt(s, Inches(2.3), Inches(5.1), Inches(5), Inches(0.3),
         "PROPOSED FIXES", 14, CORAL, True)
    _txt(s, Inches(2.3), Inches(5.5), Inches(5), Inches(0.6),
         "Resample training data  •  Adversarial debiasing  •  Per-group threshold tuning",
         12, SLATE)

    # Images on right
    _img(s, os.path.join(IMG_ETH, "fig2_disparate_impact.png"),
         Inches(8), Inches(0.8), width=Inches(4.5))
    _img(s, os.path.join(IMG_ETH, "fig9_intersectional_bias.png"),
         Inches(8), Inches(4.2), width=Inches(4.5))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SLIDE 10 — TAKEAWAYS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("[10/10] Conclusion …")
    s = prs.slides.add_slide(BL); ribbons_title(s)

    _txt(s, Inches(1), Inches(0.8), Inches(6), Inches(0.4),
         "WRAPPING UP", 14, TEAL, True)
    _txt(s, Inches(1), Inches(1.2), Inches(6), Inches(0.8),
         "KEY TAKEAWAYS", 36, HEADING, True)
    _line(s, Inches(1), Inches(2.1), Inches(3), AMBER)

    # Three takeaway cards
    takeaways = [
        ("Ship it, don't just train it",
         "The deployment week scored highest (95!) because it proved "
         "the model works in production — not just in a notebook.",
         TEAL),
        ("If you can't explain it, don't deploy it",
         "SHAP and LIME turned a black-box into something a clinician "
         "can actually review and trust.",
         AMBER),
        ("Fairness isn't optional",
         "The ethics audit caught real bias — females and minorities "
         "were systematically disadvantaged by the model.",
         CORAL),
    ]
    for i, (title, desc, color) in enumerate(takeaways):
        y = Inches(2.5 + i * 1.5)
        _circle(s, Inches(1), y + Inches(0.05), Inches(0.5), color)
        _txt(s, Inches(1.1), y + Inches(0.1), Inches(0.5), Inches(0.4),
             str(i + 1), 16, WHITE, True, PP_ALIGN.CENTER)
        _txt(s, Inches(1.8), y, Inches(5), Inches(0.4),
             title, 16, HEADING, True)
        _txt(s, Inches(1.8), y + Inches(0.4), Inches(5), Inches(0.8),
             desc, 12, SLATE)

    # Score summary
    _txt(s, Inches(9), Inches(1.5), Inches(3.5), Inches(0.4),
         "SCORES", 16, HEADING, True, PP_ALIGN.CENTER)
    scores = [("W1", "65", LGRAY), ("W2", "85", MINT), ("W3", "45", LGRAY),
              ("W4", "55", LGRAY), ("W5", "95", TEAL), ("W6", "70", LGRAY)]
    for i, (wk, sc, col) in enumerate(scores):
        row = i % 3; column = i // 3
        x = Inches(9.3 + column * 1.5)
        y = Inches(2.1 + row * 1.3)
        _circle(s, x, y, Inches(1.0), col)
        _txt(s, x, y + Inches(0.15), Inches(1.0), Inches(0.4),
             sc, 22, WHITE, True, PP_ALIGN.CENTER)
        _txt(s, x, y + Inches(0.5), Inches(1.0), Inches(0.4),
             wk, 10, WHITE, False, PP_ALIGN.CENTER)

    _txt(s, Inches(9), Inches(5.8), Inches(3.5), Inches(0.6),
         "Thank You!", 28, HEADING, True, PP_ALIGN.CENTER)

    # ── SAVE ──────────────────────────────────────────────────────────────────
    out_path = os.path.join(OUT, "Internship_Presentation_Final.pptx")
    prs.save(out_path)
    print(f"\n[OK] Saved -> {out_path}")
    print(f"   Slides: {len(prs.slides)}")
    print("=" * 55)

if __name__ == "__main__":
    build()
