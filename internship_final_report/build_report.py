"""
build_report.py
===============
Generates a comprehensive 50-page AI Internship Final Report as DOCX + PDF.

Formatting:
- Font: Times New Roman throughout
- Headings: 16pt bold centered uppercase
- Subheadings: 14pt bold left
- Content: 12pt justified
- Line spacing: 1.5
- Margins: Left 3.5cm, Right 2cm, Top 3.5cm, Bottom 2cm
- Pagination: Roman numerals for front matter, Arabic from Chapter 1
- Includes: Table of Contents, List of Figures, List of Tables
"""

import os
import sys

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx2pdf import convert
import PyPDF2

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = r"c:\Users\prate\Desktop\youva"
REPORT_DIR = os.path.join(BASE_DIR, "internship_final_report")
os.makedirs(REPORT_DIR, exist_ok=True)

# Image directories
DP_DIR = os.path.join(BASE_DIR, "data processing")
ML_DIR = os.path.join(BASE_DIR, "ml_model_development", "results", "figures")
XAI_DIR = os.path.join(BASE_DIR, "explainable_ai")
DEPLOY_DIR = os.path.join(BASE_DIR, "ai_deployment_monitoring")
ETHICS_DIR = os.path.join(BASE_DIR, "ai_ethics_audit")

# Track figures and tables for List of Figures / List of Tables
figure_list = []  # (number, caption, page_placeholder)
table_list = []   # (number, caption, page_placeholder)
fig_counter = [0]
tbl_counter = [0]


# ── Helpers ───────────────────────────────────────────────────────────────────

def set_cell_font(cell, font_name='Times New Roman', font_size=12, bold=False):
    """Set font for all runs in a table cell."""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = bold


def add_page_number_field(paragraph):
    """Insert a PAGE field code into a paragraph."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = "PAGE"
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def setup_footer(section):
    """Add centered page number to footer."""
    footer = section.footer
    footer.is_linked_to_previous = False
    if footer.paragraphs:
        p = footer.paragraphs[0]
    else:
        p = footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.clear()
    add_page_number_field(p)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)


def set_section_page_numbering(section, fmt='decimal', start=None):
    """Set page numbering format for a section."""
    sectPr = section._sectPr
    # Remove existing pgNumType
    for child in sectPr.findall(qn('w:pgNumType')):
        sectPr.remove(child)
    pgNumType = OxmlElement('w:pgNumType')
    pgNumType.set(qn('w:fmt'), fmt)
    if start is not None:
        pgNumType.set(qn('w:start'), str(start))
    sectPr.append(pgNumType)


def add_heading_styled(doc, text, level=1):
    """Add a heading with Times New Roman font."""
    if level == 1:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(24)
        run = p.add_run(text.upper())
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        # Set the style for TOC recognition
        p.style = doc.styles['Heading 1']
        # Re-apply font after style
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(16)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0, 0, 0)
    elif level == 2:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        p.style = doc.styles['Heading 2']
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0, 0, 0)
    return p


def add_body(doc, text):
    """Add a justified body paragraph in Times New Roman 12pt."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    return p


def add_code_block(doc, code_text, title=None):
    """Add a code block with monospace font."""
    if title:
        add_heading_styled(doc, title, level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    # Limit code length to keep report manageable
    lines = code_text.strip().split('\n')
    if len(lines) > 60:
        display_code = '\n'.join(lines[:55]) + '\n\n    ... [truncated for brevity] ...\n'
    else:
        display_code = code_text.strip()
    run = p.add_run(display_code)
    run.font.name = 'Courier New'
    run.font.size = Pt(8)
    return p


def add_figure(doc, image_path, caption):
    """Add an image with a numbered caption."""
    if not os.path.exists(image_path):
        add_body(doc, f"[Image not found: {os.path.basename(image_path)}]")
        return
    fig_counter[0] += 1
    num = fig_counter[0]
    figure_list.append((num, caption))
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(image_path, width=Cm(14))
    
    cap_p = doc.add_paragraph()
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_p.paragraph_format.space_after = Pt(12)
    cap_run = cap_p.add_run(f"Figure {num}: {caption}")
    cap_run.font.name = 'Times New Roman'
    cap_run.font.size = Pt(10)
    cap_run.font.italic = True


def add_table_with_caption(doc, headers, rows, caption):
    """Add a table with a numbered caption."""
    tbl_counter[0] += 1
    num = tbl_counter[0]
    table_list.append((num, caption))
    
    cap_p = doc.add_paragraph()
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_p.paragraph_format.space_before = Pt(12)
    cap_run = cap_p.add_run(f"Table {num}: {caption}")
    cap_run.font.name = 'Times New Roman'
    cap_run.font.size = Pt(10)
    cap_run.font.italic = True
    
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    
    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        set_cell_font(cell, bold=True, font_size=11)
    
    # Data rows
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            set_cell_font(cell, font_size=11)
    
    doc.add_paragraph()  # spacing


def add_toc_field(doc):
    """Insert a Word TOC field."""
    p = doc.add_paragraph()
    run = p.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-2" \\h \\z \\u'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def read_file(path):
    """Read a text file safely."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"


# ══════════════════════════════════════════════════════════════════════════════
# MAIN REPORT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_report():
    print("=" * 60)
    print("  GENERATING COMPREHENSIVE INTERNSHIP REPORT")
    print("=" * 60)
    
    doc = Document()
    
    # ── Configure default styles ──────────────────────────────────────────
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    h1 = doc.styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    h2 = doc.styles['Heading 2']
    h2.font.name = 'Times New Roman'
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # ── Set margins ───────────────────────────────────────────────────────
    for section in doc.sections:
        section.left_margin = Cm(3.5)
        section.right_margin = Cm(2.0)
        section.top_margin = Cm(3.5)
        section.bottom_margin = Cm(2.0)
    
    # Set Roman numeral pagination for front matter
    set_section_page_numbering(doc.sections[0], fmt='lowerRoman', start=1)
    setup_footer(doc.sections[0])
    
    # ══════════════════════════════════════════════════════════════════════
    # FRONT MATTER
    # ══════════════════════════════════════════════════════════════════════
    print("[1/10] Front matter...")
    
    # ── Cover Page ────────────────────────────────────────────────────────
    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("COMPREHENSIVE AI INTERNSHIP\nPROJECT REPORT")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(24)
    run.font.bold = True
    
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Submitted in Partial Fulfillment of the Requirement\nfor the AI/ML Internship Program")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Submitted By:\n[Student Name]\n\nUnder the Guidance of:\n[Supervisor Name]")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Duration: May 2026 – June 2026\n(6-Week Intensive AI Internship)")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    
    doc.add_page_break()
    
    # ── Declaration ───────────────────────────────────────────────────────
    add_heading_styled(doc, "Declaration", level=1)
    add_body(doc, "I hereby declare that this internship report titled \"Comprehensive AI Internship Project Report\" is a record of the original work carried out by me during the 6-week AI/ML internship program. The content presented in this report has not been submitted to any other institution or university for the award of any degree, diploma, or certificate.")
    add_body(doc, "All the code, analyses, visualizations, and documentation contained in this report are my own work, developed during the course of the internship. Where external sources, libraries, or datasets have been used, appropriate references and citations have been provided.")
    add_body(doc, "I understand that any misrepresentation or plagiarism will result in the cancellation of this report and may lead to disciplinary action.")
    doc.add_paragraph()
    add_body(doc, "Date: _______________")
    add_body(doc, "Place: _______________")
    add_body(doc, "Signature: _______________")
    doc.add_page_break()
    
    # ── Certificate ───────────────────────────────────────────────────────
    add_heading_styled(doc, "Certificate", level=1)
    add_body(doc, "This is to certify that the internship report titled \"Comprehensive AI Internship Project Report\" submitted by [Student Name] is a bonafide record of work carried out during the 6-week AI/ML internship program under the supervision and guidance provided.")
    add_body(doc, "The work presented in this report demonstrates competence in artificial intelligence concepts including project planning, data preprocessing, machine learning model development, explainable AI, deployment practices, and ethical auditing of AI systems.")
    doc.add_paragraph()
    add_body(doc, "Supervisor Signature: _______________")
    add_body(doc, "Date: _______________")
    doc.add_page_break()
    
    # ── Acknowledgement ───────────────────────────────────────────────────
    add_heading_styled(doc, "Acknowledgement", level=1)
    add_body(doc, "I would like to express my sincere gratitude to all those who have contributed to the successful completion of this internship project. First and foremost, I am deeply thankful to my internship supervisor for providing invaluable guidance, constant encouragement, and constructive feedback throughout the duration of this program.")
    add_body(doc, "I would also like to acknowledge the open-source community for maintaining the datasets and tools that formed the foundation of this work, including the UCI Machine Learning Repository, scikit-learn, FastAPI, Docker, SHAP, and LIME libraries. The availability of these high-quality resources made it possible to implement production-grade solutions within the internship timeline.")
    add_body(doc, "Finally, I extend my thanks to my peers and colleagues who provided support, discussed ideas, and helped me overcome challenges encountered during the various phases of this project.")
    doc.add_page_break()
    
    # ── Abstract ──────────────────────────────────────────────────────────
    add_heading_styled(doc, "Abstract", level=1)
    add_body(doc, "This comprehensive report documents the progression, execution, and outcomes of a 6-week intensive Artificial Intelligence (AI) internship program. The internship was structured to simulate the complete lifecycle of an AI project, spanning from initial planning and feasibility assessment through to production deployment and ethical auditing.")
    add_body(doc, "Week 1 focused on developing a detailed AI project plan for a predictive analytics initiative, covering objectives, hypothesis formulation, technology selection, methodology, risk assessment, and timeline planning. Week 2 involved designing and implementing a comprehensive data preprocessing and feature engineering pipeline using the Titanic dataset, including missing value imputation via KNN, outlier detection using the IQR method with winsorization, and the creation of domain-specific engineered features.")
    add_body(doc, "Week 3 addressed building and hyperparameter tuning of a Random Forest Classifier on the Breast Cancer Wisconsin dataset, utilizing GridSearchCV with 162 parameter combinations across 5-fold stratified cross-validation to optimize F1-score. Week 4 introduced Explainable AI techniques, applying SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) to interpret model predictions and enhance transparency.")
    add_body(doc, "The most substantial deliverable was produced in Week 5, which involved the end-to-end deployment of an AI model as a production-ready REST API using FastAPI, containerized with Docker, and equipped with structured JSON logging, health check endpoints, thread-safe metrics monitoring, and a comprehensive test suite of 15 pytest tests. This project scored 95/100 in evaluation.")
    add_body(doc, "Week 6 concluded the internship with an AI Ethics and Bias Audit, performing disparate impact analysis, equalized odds assessment, and intersectional bias evaluation on the UCI Adult Income dataset using a Logistic Regression classifier. The audit identified biases across sex and race dimensions and proposed concrete remediation strategies including re-sampling, adversarial debiasing, and threshold adjustment.")
    add_body(doc, "Keywords: Artificial Intelligence, Machine Learning, Predictive Analytics, Data Preprocessing, Feature Engineering, Hyperparameter Tuning, Explainable AI, SHAP, LIME, Model Deployment, FastAPI, Docker, Monitoring, AI Ethics, Bias Analysis, Fairness Assessment")
    doc.add_page_break()
    
    # ── Table of Contents ─────────────────────────────────────────────────
    add_heading_styled(doc, "Table of Contents", level=1)
    add_toc_field(doc)
    add_body(doc, "(Note: To populate the Table of Contents with page numbers, open this file in Microsoft Word, press Ctrl+A to select all, then press F9 to update fields.)")
    doc.add_page_break()
    
    # ── List of Figures (placeholder - will be populated at end) ──────────
    add_heading_styled(doc, "List of Figures", level=1)
    lof_placeholder = doc.add_paragraph()  # We'll come back to fill this
    doc.add_page_break()
    
    # ── List of Tables (placeholder - will be populated at end) ───────────
    add_heading_styled(doc, "List of Tables", level=1)
    lot_placeholder = doc.add_paragraph()
    doc.add_page_break()
    
    # ── List of Abbreviations ─────────────────────────────────────────────
    add_heading_styled(doc, "List of Abbreviations", level=1)
    abbreviations = [
        ("AI", "Artificial Intelligence"),
        ("ML", "Machine Learning"),
        ("XAI", "Explainable Artificial Intelligence"),
        ("SHAP", "SHapley Additive exPlanations"),
        ("LIME", "Local Interpretable Model-agnostic Explanations"),
        ("API", "Application Programming Interface"),
        ("REST", "Representational State Transfer"),
        ("CSV", "Comma-Separated Values"),
        ("EDA", "Exploratory Data Analysis"),
        ("KNN", "K-Nearest Neighbours"),
        ("IQR", "Interquartile Range"),
        ("ROC", "Receiver Operating Characteristic"),
        ("AUC", "Area Under the Curve"),
        ("CV", "Cross-Validation"),
        ("FPR", "False Positive Rate"),
        ("TPR", "True Positive Rate"),
        ("PPV", "Positive Predictive Value"),
        ("CORS", "Cross-Origin Resource Sharing"),
        ("JSON", "JavaScript Object Notation"),
        ("CI/CD", "Continuous Integration / Continuous Deployment"),
    ]
    table = doc.add_table(rows=1 + len(abbreviations), cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = "Abbreviation"
    table.rows[0].cells[1].text = "Full Form"
    set_cell_font(table.rows[0].cells[0], bold=True)
    set_cell_font(table.rows[0].cells[1], bold=True)
    for i, (abbr, full) in enumerate(abbreviations):
        table.rows[i + 1].cells[0].text = abbr
        table.rows[i + 1].cells[1].text = full
        set_cell_font(table.rows[i + 1].cells[0])
        set_cell_font(table.rows[i + 1].cells[1])
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # NEW SECTION: Switch to Arabic numerals starting from page 1
    # ══════════════════════════════════════════════════════════════════════
    new_section = doc.add_section()
    new_section.left_margin = Cm(3.5)
    new_section.right_margin = Cm(2.0)
    new_section.top_margin = Cm(3.5)
    new_section.bottom_margin = Cm(2.0)
    set_section_page_numbering(new_section, fmt='decimal', start=1)
    setup_footer(new_section)
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 1: INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════
    print("[2/10] Chapter 1: Introduction...")
    add_heading_styled(doc, "Chapter 1: Introduction", level=1)
    
    add_heading_styled(doc, "1.1 Background", level=2)
    add_body(doc, "Artificial Intelligence has emerged as one of the most transformative technologies of the 21st century, reshaping industries ranging from healthcare and finance to transportation and entertainment. The ability to extract insights from data, automate decision-making, and build intelligent systems has become a core competency sought across virtually every sector of the modern economy. However, the journey from understanding AI concepts in an academic setting to applying them in real-world scenarios requires hands-on experience with the full lifecycle of AI projects — from initial ideation and planning through to deployment, monitoring, and ethical governance.")
    add_body(doc, "This internship was designed as a 6-week intensive program to bridge exactly this gap. Each week presented a distinct challenge that mapped to a critical phase of the AI project lifecycle, progressively building skills and culminating in a fully deployed, production-ready AI service.")
    
    add_heading_styled(doc, "1.2 Internship Overview", level=2)
    add_body(doc, "The internship consisted of six sequential tasks, each building upon the previous week's work:")
    
    add_table_with_caption(doc,
        ["Week", "Task", "Focus Area", "Score"],
        [
            ["1", "AI Project Planning & Documentation", "Planning, Feasibility, Gantt Charts", "65/100"],
            ["2", "Data Preprocessing & Feature Engineering", "EDA, Cleaning, Feature Extraction", "85/100"],
            ["3", "Building and Tuning an AI Model", "Random Forest, GridSearchCV, Evaluation", "45/100"],
            ["4", "Explainable AI & Model Interpretability", "SHAP, LIME, Feature Importance", "55/100"],
            ["5", "Deployment & Monitoring of AI Service", "FastAPI, Docker, Logging, Monitoring", "95/100"],
            ["6", "AI Ethics, Bias Analysis & Fairness", "Disparate Impact, Equalized Odds, Bias Mitigation", "70/100"],
        ],
        "Summary of Weekly Internship Tasks and Evaluation Scores"
    )
    
    add_heading_styled(doc, "1.3 Objectives", level=2)
    add_body(doc, "The primary objectives of this internship were to: (1) Develop a thorough understanding of the AI project lifecycle from ideation to deployment. (2) Gain practical experience with industry-standard tools and frameworks including scikit-learn, FastAPI, Docker, SHAP, and LIME. (3) Build reproducible, well-documented data science pipelines. (4) Deploy a machine learning model as a containerized REST API with monitoring capabilities. (5) Understand and apply ethical AI principles including bias detection and fairness assessment.")
    
    add_heading_styled(doc, "1.4 Report Structure", level=2)
    add_body(doc, "This report is organized into eight chapters. Chapter 1 provides the introduction and internship overview. Chapters 2 through 7 document each weekly task in detail, with special emphasis on Chapter 6 (Deployment and Monitoring) which represents the most substantial and highest-scoring deliverable. Chapter 8 presents conclusions and recommendations for future work. The report includes all relevant code snippets, visualizations, and analysis outputs generated during the internship.")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 2: AI PROJECT PLANNING (WEEK 1)
    # ══════════════════════════════════════════════════════════════════════
    print("[3/10] Chapter 2: AI Project Planning...")
    add_heading_styled(doc, "Chapter 2: AI Project Planning and Documentation", level=1)
    
    add_heading_styled(doc, "2.1 Task Description", level=2)
    add_body(doc, "The first week required developing a detailed project plan for an AI initiative focused on predictive analytics using publicly available datasets. The objective was to simulate the process of ideation, planning, and feasibility assessment for a real-world AI project. The deliverable was a comprehensive PDF document covering project objectives, hypothesis formulation, technology selection, methodology, risk assessment, and a project timeline.")
    
    add_heading_styled(doc, "2.2 Project Objectives Defined", level=2)
    add_body(doc, "The planned project aimed to build a predictive analytics system for healthcare outcomes, specifically predicting patient readmission risk using publicly available clinical datasets. The key objectives included: (1) collecting and integrating relevant healthcare datasets, (2) performing thorough exploratory data analysis, (3) engineering clinically meaningful features, (4) training and validating multiple predictive models, and (5) evaluating model performance using both statistical and clinical metrics.")
    
    add_heading_styled(doc, "2.3 Technology Stack Selection", level=2)
    add_body(doc, "The project plan specified the following technology stack: Python 3.11 as the primary programming language, pandas and NumPy for data manipulation, scikit-learn for machine learning algorithms, matplotlib and seaborn for visualization, Jupyter Notebooks for interactive development, and Git for version control. The rationale for each technology choice was documented with consideration for scalability, community support, and integration capability.")
    
    add_table_with_caption(doc,
        ["Component", "Technology", "Justification"],
        [
            ["Language", "Python 3.11", "Industry standard for AI/ML, extensive library ecosystem"],
            ["Data Processing", "pandas, NumPy", "Efficient tabular data operations, vectorized computation"],
            ["ML Framework", "scikit-learn", "Comprehensive algorithms, consistent API, well-documented"],
            ["Visualization", "matplotlib, seaborn", "Publication-quality plots, statistical visualization"],
            ["Version Control", "Git", "Industry standard, collaboration, reproducibility"],
        ],
        "Technology Stack for the Proposed AI Project"
    )
    
    add_heading_styled(doc, "2.4 Risk Assessment and Mitigation", level=2)
    add_body(doc, "The project plan identified several key risks: data quality issues including missing values and class imbalance, model overfitting due to limited training data, computational resource constraints, and ethical concerns around patient data privacy. For each risk, mitigation strategies were proposed, including robust preprocessing pipelines, cross-validation techniques, cloud computing resources, and strict adherence to data anonymization protocols.")
    
    add_heading_styled(doc, "2.5 Evaluator Feedback and Reflection", level=2)
    add_body(doc, "The submission received a score of 65/100. The evaluator noted that while the plan outlined detailed project objectives, data sources, methodology, timeline, risk mitigation measures, and expected outcomes, it lacked an explicit hypothesis formulation, a full exploration of ethical considerations, scalability issues, and a deep discussion on data governance. The submitted text was significantly shorter than the required 2000 words. This feedback highlighted the importance of thoroughness and depth in project documentation, a lesson that informed subsequent weeks' work.")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 3: DATA PREPROCESSING (WEEK 2)
    # ══════════════════════════════════════════════════════════════════════
    print("[4/10] Chapter 3: Data Preprocessing...")
    add_heading_styled(doc, "Chapter 3: Data Preprocessing and Feature Engineering", level=1)
    
    add_heading_styled(doc, "3.1 Task Description", level=2)
    add_body(doc, "The second week focused on designing and implementing a comprehensive data preprocessing and feature engineering pipeline. The task required selecting a publicly available dataset, performing data cleaning, handling missing values, normalization, categorical encoding, and outlier detection. Additionally, the plan covered feature extraction and engineering with clear rationale for each decision. The deliverable was a well-documented Jupyter Notebook with code, explanatory notes, and visualizations.")
    
    add_heading_styled(doc, "3.2 Dataset Selection: Titanic", level=2)
    add_body(doc, "The Titanic dataset from Kaggle was selected for this task. It is a well-known dataset for binary classification containing passenger information including age, sex, passenger class, fare, number of siblings/spouses (SibSp), number of parents/children (Parch), port of embarkation, and survival status. The dataset contains 891 training samples with a mix of numerical and categorical features, along with deliberate missing values in the Age, Cabin, and Embarked columns — making it ideal for demonstrating preprocessing techniques.")
    
    add_heading_styled(doc, "3.3 Exploratory Data Analysis", level=2)
    add_body(doc, "The exploratory data analysis phase revealed several key insights about the Titanic dataset. The survival rate was approximately 38.4%, indicating moderate class imbalance. Age had 177 missing values (19.9%), Cabin had 687 missing values (77.1%), and Embarked had 2 missing values. The distribution of fares was heavily right-skewed, with outliers corresponding to luxury cabin bookings. Strong correlations were observed between passenger class and fare, and between survival and features such as sex, passenger class, and fare.")
    
    add_figure(doc, os.path.join(DP_DIR, "missing_data_analysis.png"), "Missing Data Analysis showing patterns and percentages of missing values across features")
    add_figure(doc, os.path.join(DP_DIR, "eda_distributions.png"), "Exploratory Data Analysis showing distributions of key features")
    add_figure(doc, os.path.join(DP_DIR, "correlation_matrix.png"), "Correlation Matrix showing pairwise relationships between numerical features")
    
    add_heading_styled(doc, "3.4 Data Cleaning and Imputation", level=2)
    add_body(doc, "Missing value imputation was performed using KNN (K-Nearest Neighbours) imputation for the Age column, which leverages the relationships between features to produce more accurate imputed values compared to simple mean or median imputation. The Cabin column was dropped due to its extremely high missing rate (77.1%), and the two missing Embarked values were imputed with the mode. Duplicate rows were checked and removed where found.")
    
    add_figure(doc, os.path.join(DP_DIR, "age_imputation.png"), "Age Imputation Results comparing distributions before and after KNN imputation")
    
    add_heading_styled(doc, "3.5 Outlier Detection and Treatment", level=2)
    add_body(doc, "Outlier detection was performed using the Interquartile Range (IQR) method. Instead of removing outliers entirely (which could discard valuable high-fare passengers), winsorization was applied — capping extreme values at the 1st and 99th percentiles. This approach preserves the information content while reducing the influence of extreme values on model training.")
    
    add_figure(doc, os.path.join(DP_DIR, "outlier_boxplots.png"), "Box plots showing outlier distributions for numerical features before and after treatment")
    
    add_heading_styled(doc, "3.6 Feature Engineering", level=2)
    add_body(doc, "Several domain-specific features were engineered to capture patterns not directly available in the raw data. These included: FamilySize (SibSp + Parch + 1), IsAlone (binary flag for solo travelers), Title (extracted from the Name column using regex), FareBin (discretized fare ranges), and AgeBin (age group categories). The Title feature proved particularly valuable, capturing social status information (Mr, Mrs, Miss, Master, etc.) that correlated strongly with survival.")
    
    add_figure(doc, os.path.join(DP_DIR, "feature_engineering_insights.png"), "Feature Engineering Insights showing the impact of engineered features on the target variable")
    add_figure(doc, os.path.join(DP_DIR, "feature_importance.png"), "Feature Importance ranking showing the relative predictive power of original and engineered features")
    add_figure(doc, os.path.join(DP_DIR, "scaling_comparison.png"), "Comparison of different scaling methods (StandardScaler, MinMaxScaler, RobustScaler) on feature distributions")
    
    add_heading_styled(doc, "3.7 Pipeline Assembly and Validation", level=2)
    add_body(doc, "All preprocessing steps were assembled into a reproducible scikit-learn Pipeline object, ensuring that the same transformations could be applied consistently to new data. The pipeline included: (1) KNN imputation, (2) outlier winsorization, (3) feature engineering, (4) categorical encoding (one-hot encoding for nominal features, ordinal encoding for ordered features), and (5) StandardScaler normalization. The pipeline was validated by applying it to a held-out validation set and confirming that no data leakage occurred.")
    
    add_heading_styled(doc, "3.8 Evaluator Feedback", level=2)
    add_body(doc, "This submission received a score of 85/100, the second-highest score of the internship. The evaluator praised the strong understanding of the preprocessing workflow, the detailed explanations of KNN imputation, IQR method with winsorization, and the creation of multiple domain-specific features. The inclusion of a reproducible sklearn pipeline was noted as demonstrating attention to best practices. Points were deducted for the submission being a high-level summary rather than a fully executable notebook with inline code comments.")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 4: ML MODEL BUILDING (WEEK 3) 
    # ══════════════════════════════════════════════════════════════════════
    print("[5/10] Chapter 4: ML Model Building...")
    add_heading_styled(doc, "Chapter 4: Building and Tuning an AI Model", level=1)
    
    add_heading_styled(doc, "4.1 Task Description", level=2)
    add_body(doc, "The third week required choosing a machine learning algorithm to solve a predictive problem, implementing a complete training pipeline, performing hyperparameter tuning, and documenting the methodology with performance metrics. Two deliverables were expected: a working code file and a detailed report of at least 1500 words.")
    
    add_heading_styled(doc, "4.2 Algorithm Selection: Random Forest", level=2)
    add_body(doc, "The Random Forest ensemble algorithm (Breiman, 2001) was selected as the primary modelling strategy for the Breast Cancer Wisconsin (Diagnostic) dataset. This choice was grounded in the algorithm's robustness to noise, built-in feature-importance estimation via Gini impurity, resistance to overfitting relative to single decision trees, and competitive performance on tabular datasets of moderate size. The Random Forest constructs multiple decision trees using bootstrap aggregation (bagging) and random feature subsampling, with the final prediction determined by majority vote across all trees.")
    
    add_table_with_caption(doc,
        ["Algorithm", "Strengths", "Weaknesses"],
        [
            ["Logistic Regression", "Interpretable, fast", "Linear boundary only"],
            ["SVM", "Effective in high dimensions", "Long training time, kernel selection"],
            ["KNN", "Simple, no assumptions", "Slow inference, sensitive to noise"],
            ["Decision Tree", "Interpretable, handles mixed types", "Prone to overfitting"],
            ["Random Forest", "Robust, interpretable, fast", "Less interpretable than single trees"],
            ["XGBoost", "Very high accuracy", "Risk of overfitting without careful tuning"],
            ["Neural Network", "Flexible, powerful", "Requires large data, hard to interpret"],
        ],
        "Comparison of Candidate Machine Learning Algorithms"
    )
    
    add_heading_styled(doc, "4.3 Dataset: Breast Cancer Wisconsin", level=2)
    add_body(doc, "The Breast Cancer Wisconsin (Diagnostic) dataset consists of 569 instances with 30 continuous features computed from digitized images of fine needle aspirates (FNA) of breast masses. The ten base measurements (radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, symmetry, and fractal dimension) are each represented by three statistics: mean, standard error, and worst (largest) value. The binary classification task distinguishes malignant (37.3%) from benign (62.7%) tumours.")
    
    add_heading_styled(doc, "4.4 Hyperparameter Tuning with GridSearchCV", level=2)
    add_body(doc, "An exhaustive GridSearchCV was performed over 162 parameter combinations (3 × 3 × 3 × 3 × 2) using 5-fold Stratified K-Fold cross-validation. The hyperparameters tuned were: n_estimators (50, 100, 200), max_depth (None, 10, 20), min_samples_split (2, 5, 10), min_samples_leaf (1, 2, 4), and max_features ('sqrt', 'log2'). F1-score was chosen as the optimization metric because in a medical diagnosis context, both false positives and false negatives carry significant costs.")
    
    add_table_with_caption(doc,
        ["Metric", "Baseline RF", "Tuned RF", "Improvement"],
        [
            ["Accuracy", "0.9561 – 0.9649", "0.9649 – 0.9825", "↑"],
            ["Precision", "0.96 – 0.97", "0.97 – 0.99", "↑"],
            ["Recall", "0.96 – 0.97", "0.97 – 0.99", "↑"],
            ["F1-Score", "0.96 – 0.97", "0.97 – 0.99", "↑"],
            ["ROC-AUC", "0.990 – 0.995", "0.995 – 0.999", "↑"],
        ],
        "Model Performance Comparison: Baseline vs. Tuned Random Forest"
    )
    
    add_figure(doc, os.path.join(ML_DIR, "metrics_comparison.png"), "Grouped bar chart comparing all five metrics between baseline and tuned Random Forest models")
    add_figure(doc, os.path.join(ML_DIR, "confusion_matrices.png"), "Side-by-side confusion matrices for baseline and tuned models showing TP, TN, FP, and FN counts")
    add_figure(doc, os.path.join(ML_DIR, "feature_importance.png"), "Top 15 features ranked by Gini importance from the tuned Random Forest model")
    add_figure(doc, os.path.join(ML_DIR, "learning_curve.png"), "Learning curve showing training and validation F1-scores against number of training samples")
    add_figure(doc, os.path.join(ML_DIR, "roc_curves.png"), "ROC curves for baseline and tuned models with AUC values")
    
    add_heading_styled(doc, "4.5 Evaluator Feedback", level=2)
    add_body(doc, "This submission received a score of 45/100. The evaluator noted that while the submission demonstrated a reasonable understanding of the ML pipeline, it lacked the two explicitly required deliverables (a code file and a detailed PDF report of at least 1500 words). The submitted text was a summary narrative without accompanying executable code. This feedback underscored the critical importance of meeting deliverable specifications precisely.")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 5: EXPLAINABLE AI (WEEK 4)
    # ══════════════════════════════════════════════════════════════════════
    print("[6/10] Chapter 5: Explainable AI...")
    add_heading_styled(doc, "Chapter 5: Explainable AI and Model Interpretability", level=1)
    
    add_heading_styled(doc, "5.1 Task Description", level=2)
    add_body(doc, "The fourth week focused on implementing techniques for Explainable AI (XAI) to interpret model predictions. The task required integrating one or more model interpretation techniques such as SHAP or LIME, working on a publicly available dataset, creating visualizations of interpretation results, and compiling a comprehensive report of at least 2000 words discussing real-world applications of these techniques.")
    
    add_heading_styled(doc, "5.2 Models Under Analysis", level=2)
    add_body(doc, "Two models were trained on the Breast Cancer Wisconsin dataset for XAI analysis: a Random Forest Classifier (200 trees, max_depth=6) and a Gradient Boosting Classifier (200 trees, max_depth=4, learning_rate=0.05). Both models achieved high test AUC scores, making them suitable candidates for interpretability analysis. The Random Forest was selected as the primary model for SHAP and LIME explanations due to its ensemble nature and built-in feature importance capabilities.")
    
    add_heading_styled(doc, "5.3 SHAP Analysis", level=2)
    add_body(doc, "SHAP (SHapley Additive exPlanations) values were computed using the TreeExplainer optimized for tree-based models. The SHAP summary plot (beeswarm plot) revealed the global feature importance rankings and the direction of each feature's impact on predictions. The most influential features for predicting benign tumours were: worst concave points, mean concave points, worst perimeter, and worst radius — aligning with clinical understanding that malignant cells exhibit more irregular shapes and larger sizes.")
    add_body(doc, "The SHAP dependence plot for the most important feature revealed non-linear relationships between feature values and SHAP values, with interaction effects from correlated features. The waterfall plot for individual predictions provided a transparent breakdown of how each feature contributed to a specific prediction, enabling clinicians to understand exactly why the model classified a particular sample as malignant or benign.")
    
    add_figure(doc, os.path.join(XAI_DIR, "fig1_dataset_overview.png"), "Breast Cancer Dataset Overview: class distribution, feature correlations, and mean radius distribution")
    add_figure(doc, os.path.join(XAI_DIR, "fig2_feature_importance.png"), "Feature Importance Analysis comparing built-in MDI importance with permutation importance")
    add_figure(doc, os.path.join(XAI_DIR, "fig3_shap_summary.png"), "SHAP Summary (Beeswarm) Plot showing global feature importance and impact direction")
    add_figure(doc, os.path.join(XAI_DIR, "fig5_shap_dependence.png"), "SHAP Dependence Plot for the most important feature showing interaction effects")
    add_figure(doc, os.path.join(XAI_DIR, "fig5b_shap_waterfall.png"), "SHAP Waterfall Plot for a single malignant prediction showing per-feature contributions")
    
    add_heading_styled(doc, "5.4 LIME Analysis", level=2)
    add_body(doc, "LIME (Local Interpretable Model-agnostic Explanations) was applied to generate local explanations for individual predictions. Unlike SHAP which provides mathematically grounded global explanations, LIME creates interpretable surrogate models around individual data points. Two representative instances were analyzed: a high-confidence benign prediction and a high-confidence malignant prediction. The LIME explanations highlighted different feature combinations for each case, providing complementary insights to the SHAP analysis.")
    
    add_figure(doc, os.path.join(XAI_DIR, "fig6_lime_benign.png"), "LIME Explanation for a Benign prediction showing feature weights and prediction probabilities")
    add_figure(doc, os.path.join(XAI_DIR, "fig7_lime_malignant.png"), "LIME Explanation for a Malignant prediction showing feature weights toward the malignant class")
    add_figure(doc, os.path.join(XAI_DIR, "fig8_confusion_matrix.png"), "Confusion matrices for Random Forest and Gradient Boosting models on the test set")
    
    add_heading_styled(doc, "5.5 Evaluator Feedback", level=2)
    add_body(doc, "This submission received a score of 55/100. The evaluator acknowledged the correct selection of XAI techniques and their application but noted the submission fell short of the required 2000-word comprehensive report. The submission lacked detailed visualizations as embedded outputs and a thorough discussion of real-world implications, trust, and accountability aspects.")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 6: DEPLOYMENT AND MONITORING (WEEK 5) — HEAVIEST WEIGHT
    # ══════════════════════════════════════════════════════════════════════
    print("[7/10] Chapter 6: Deployment and Monitoring (HEAVY)...")
    add_heading_styled(doc, "Chapter 6: Deployment and Monitoring of an AI Service", level=1)
    
    add_heading_styled(doc, "6.1 Task Description", level=2)
    add_body(doc, "The fifth week represented the culmination of the internship's technical arc, requiring the creation of a proof-of-concept deployment of an AI model using containerization (Docker) and a simple API (Flask or FastAPI) to serve predictions. The project also required implementing logging and monitoring techniques to track usage statistics, model performance metrics, and error logs. The deliverable included a comprehensive deployment documentation of at least 1500 words and a working code repository. This task received the highest score of the internship at 95/100.")
    
    add_heading_styled(doc, "6.2 System Architecture", level=2)
    add_body(doc, "The deployment architecture follows a layered design pattern separating concerns across distinct modules. The FastAPI framework serves as the web layer, handling HTTP request routing, validation, and response serialization. The model layer encapsulates the machine learning model (a RandomForestClassifier trained on the Iris dataset), loading it once at startup and caching it as a module-level singleton to avoid repeated disk I/O. The monitoring layer provides a thread-safe in-process metrics store that tracks request counts, latencies, error rates, and per-class prediction distributions. The logging layer implements structured JSON logging with both console and rotating file handlers.")
    
    add_table_with_caption(doc,
        ["Method", "Endpoint", "Description"],
        [
            ["GET", "/health", "Liveness and readiness probe"],
            ["GET", "/metrics", "Operational metrics snapshot"],
            ["GET", "/model/info", "Model training metadata"],
            ["POST", "/predict", "Single-sample Iris prediction"],
            ["POST", "/predict/batch", "Batch prediction (1-256 samples)"],
            ["GET", "/docs", "Interactive Swagger UI (auto-generated)"],
            ["GET", "/redoc", "ReDoc API documentation (auto-generated)"],
        ],
        "API Endpoint Reference for the Iris Prediction Service"
    )
    
    add_heading_styled(doc, "6.3 Model Training and Serialization", level=2)
    add_body(doc, "The model was trained using scikit-learn's RandomForestClassifier with 100 estimators on the UCI Iris dataset (150 samples, 4 features, 3 classes). The training script (train_and_save.py) performs stratified train/test splitting, trains the classifier, evaluates it with accuracy and cross-validation metrics, and persists both the model (as a joblib file) and metadata (as a JSON file containing model type, accuracy, feature names, target names, and confusion matrix). This separation of training from serving ensures reproducibility and allows independent model updates.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "model", "train_and_save.py")), "6.3.1 Model Training Script (train_and_save.py)")
    
    add_heading_styled(doc, "6.4 FastAPI Application", level=2)
    add_body(doc, "The main application (main.py) is the central orchestration point. It configures the FastAPI instance with proper metadata (title, description, version), sets up CORS middleware for cross-origin requests, implements request-ID middleware that assigns a UUID to every incoming request for traceability, and registers a global exception handler that captures unhandled errors with full stack traces. The lifespan context manager ensures the model is loaded into memory at startup and cleaned up at shutdown.")
    add_body(doc, "The prediction endpoints accept Pydantic-validated payloads, extract features, invoke the model, record metrics, and return structured JSON responses with predicted class, confidence score, and per-class probabilities. The batch endpoint supports up to 256 samples in a single request, enabling efficient bulk inference.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "app", "main.py")), "6.4.1 FastAPI Application (main.py)")
    
    add_heading_styled(doc, "6.5 Model Loading and Prediction Interface", level=2)
    add_body(doc, "The model module (model.py) implements a clean separation between model I/O and prediction logic. The model is loaded from a joblib file at startup and cached as a module-level singleton. The predict_single function accepts a list of four floats, runs inference, and returns a dictionary with the predicted class index, human-readable class name, confidence (probability of the predicted class), and a full probability distribution across all three species.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "app", "model.py")), "6.5.1 Model Loading Module (model.py)")
    
    add_heading_styled(doc, "6.6 Request/Response Schemas", level=2)
    add_body(doc, "All API inputs and outputs are validated using Pydantic models defined in schemas.py. The IrisFeatures model enforces non-negative float constraints on all four measurements. The BatchIrisFeatures model accepts a list of 1-256 IrisFeatures samples. Response models (PredictionResponse, BatchPredictionResponse, HealthResponse, MetricsResponse) ensure consistent, type-safe API contracts.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "app", "schemas.py")), "6.6.1 Pydantic Schemas (schemas.py)")
    
    add_heading_styled(doc, "6.7 Thread-Safe Monitoring", level=2)
    add_body(doc, "The monitoring module implements a MetricsStore class that is thread-safe through the use of threading.Lock. It tracks total requests, successful predictions, failed requests, per-class prediction counts, and a rolling window of the last 1000 request latencies. The snapshot method computes derived metrics including average latency, P95 latency (using numpy percentile), error rate percentage, and uptime. This data is exposed through the /metrics endpoint, enabling Prometheus-style scraping or Grafana dashboarding.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "app", "monitoring.py")), "6.7.1 Thread-Safe Metrics Store (monitoring.py)")
    
    add_heading_styled(doc, "6.8 Structured JSON Logging", level=2)
    add_body(doc, "The logging configuration uses the python-json-logger library to produce structured JSON log entries. Each log entry includes a timestamp, logger name, log level, message, and a fixed 'service' field. Two handlers are configured: a console handler (StreamHandler to stdout) for real-time monitoring, and a rotating file handler (RotatingFileHandler) that creates files up to 10 MB with 5 backups. This ensures log persistence without unbounded disk growth. The structured format enables easy parsing by log aggregation systems like the ELK stack or Splunk.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "app", "logger_config.py")), "6.8.1 Structured JSON Logger Configuration (logger_config.py)")
    
    add_heading_styled(doc, "6.9 Docker Containerization", level=2)
    add_body(doc, "The Dockerfile uses a multi-stage build to minimize the final image size. The builder stage installs gcc and compiles Python dependencies, while the runtime stage copies only the installed packages and application source. A non-root user (appuser:appgroup) is created for security. The HEALTHCHECK directive configures Docker Engine to probe the /health endpoint every 30 seconds with a 10-second timeout and 15-second startup grace period. The default command launches uvicorn with a single worker.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "Dockerfile")), "6.9.1 Multi-Stage Dockerfile")
    
    add_heading_styled(doc, "6.10 Docker Compose Orchestration", level=2)
    add_body(doc, "The docker-compose.yml file defines the service configuration including port mapping (8000:8000), environment variables (LOG_LEVEL, LOG_DIR), volume mounting for log persistence, health check parameters, restart policy (unless-stopped), and resource limits (1 CPU, 512 MB memory limit with 0.25 CPU, 128 MB reservation). These settings reflect production-grade container orchestration practices.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "docker-compose.yml")), "6.10.1 Docker Compose Configuration")
    
    add_heading_styled(doc, "6.11 Automated Testing", level=2)
    add_body(doc, "A comprehensive pytest test suite with 15 tests validates all API endpoints. The tests cover: health endpoint (status 200, correct payload fields), model info endpoint (metadata fields), single prediction (correct species classification for known samples, validation of invalid payloads and negative values), batch prediction (correct count, empty list rejection), and metrics endpoint (field presence, metric accumulation after predictions). The test suite uses FastAPI's TestClient for synchronous testing without requiring a running server.")
    
    add_code_block(doc, read_file(os.path.join(DEPLOY_DIR, "tests", "test_api.py")), "6.11.1 Automated Test Suite (test_api.py)")
    
    add_heading_styled(doc, "6.12 Significance of Deployment Practices", level=2)
    add_body(doc, "Developing an accurate machine learning model is only the first step in delivering value from artificial intelligence. The model must be packaged, deployed, and maintained in an environment where real users or downstream systems can consume its predictions reliably, safely, and at scale. Industry research consistently shows that the majority of ML projects fail to move from prototype to production. The barriers are rarely algorithmic — they are operational: poor reproducibility, lack of monitoring, inadequate error handling, and the absence of systematic deployment pipelines.")
    add_body(doc, "Containerisation with Docker eliminates the 'it works on my machine' syndrome by bundling the entire runtime into a single immutable image. RESTful APIs constructed using FastAPI allow seamless integration with downstream applications and microservices. Monitoring systems track both system-level metrics (CPU, memory) and model-level metrics (prediction latency, data drift, concept drift). Structured JSON logging provides audit trails for debugging and performance tuning.")
    add_body(doc, "Health check endpoints (/health) enable orchestrators like Kubernetes to autonomously manage container lifecycle — restarting unhealthy instances, performing rolling updates, and scaling horizontally. The /metrics endpoint allows Prometheus to scrape operational data for real-time Grafana dashboards, enabling proactive alerting on performance degradation or error rate spikes.")
    
    add_heading_styled(doc, "6.13 Evaluator Feedback", level=2)
    add_body(doc, "This submission received the highest score of the internship at 95/100. The evaluator praised the clear and detailed understanding of the task requirements, the comprehensive API design with multiple endpoints, the robust logging and monitoring strategies, the mention of automated testing with 15 pytest tests, and the detailed configuration explanations. The slight deduction was due to the submission being a conceptual summary rather than an actual zipped repository with the full code and documentation, though the evaluator noted the submission was 'highly detailed and meets the assignment criteria almost perfectly.'")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 7: AI ETHICS (WEEK 6)
    # ══════════════════════════════════════════════════════════════════════
    print("[8/10] Chapter 7: AI Ethics...")
    add_heading_styled(doc, "Chapter 7: AI Ethics, Bias Analysis, and Fairness Assessment", level=1)
    
    add_heading_styled(doc, "7.1 Task Description", level=2)
    add_body(doc, "The sixth and final week focused on evaluating the ethical dimensions of AI models with emphasis on bias analysis and fairness assessment. The task required selecting an AI model, performing an in-depth ethical audit including disparate impact analysis, fairness metrics (demographic parity, equalized odds), and proposing remediation strategies. The deliverable was a comprehensive PDF report of at least 2000 words with visualizations and documented recommendations for bias mitigation.")
    
    add_heading_styled(doc, "7.2 Dataset and Model Selection", level=2)
    add_body(doc, "The UCI Adult (Census) Income dataset was selected for this ethical audit. It contains 32,561 records with demographic attributes including age, workclass, education, marital status, occupation, race, sex, and income level (binary: <=50K or >50K). A Logistic Regression classifier was trained within a scikit-learn Pipeline (StandardScaler + LogisticRegression with max_iter=500) using an 80/20 stratified train/test split. This dataset is widely used in fairness research because it contains well-documented biases along race and sex dimensions.")
    
    add_heading_styled(doc, "7.3 Fairness Metrics Implemented", level=2)
    add_body(doc, "Four fairness metrics were implemented and computed across both sex and race dimensions:")
    add_body(doc, "Demographic Parity: Measures whether the positive prediction rate P(Ŷ=1|A=a) is equal across groups. Violations indicate that certain groups receive favorable predictions at higher rates than others, regardless of their actual outcomes.")
    add_body(doc, "Disparate Impact Ratio: Computed as min_group_rate / max_group_rate. A ratio below 0.8 (the '80% rule' from US employment law) indicates adverse impact against the disadvantaged group.")
    add_body(doc, "Equalized Odds: Measures whether TPR (True Positive Rate) and FPR (False Positive Rate) are equal across groups. Violations mean the model's error rates differ by demographic group.")
    add_body(doc, "Predictive Parity: Measures whether Precision (Positive Predictive Value) is equal across groups. This ensures that when the model predicts a positive outcome, it is equally accurate for all groups.")
    
    add_heading_styled(doc, "7.4 Bias Findings", level=2)
    add_body(doc, "The audit revealed significant disparities. The disparate impact ratio by sex fell below the 0.8 threshold, indicating adverse impact against females in high-income predictions. Males received positive predictions at substantially higher rates than females. By race, White individuals received higher positive prediction rates than non-White groups, with some racial minorities showing disparate impact ratios well below 0.8.")
    add_body(doc, "The equalized odds analysis showed that TPR (recall) for the high-income class was significantly lower for females compared to males, meaning the model was more likely to miss genuinely high-income females. The intersectional analysis (combining race and sex) revealed compounding disadvantages for non-White females, who had the lowest positive prediction rates of any demographic intersection.")
    
    add_figure(doc, os.path.join(ETHICS_DIR, "fig1_demographic_overview.png"), "Dataset Demographic Overview: sex distribution, race distribution, and income by sex")
    add_figure(doc, os.path.join(ETHICS_DIR, "fig2_disparate_impact.png"), "Disparate Impact Analysis showing positive prediction rates by sex and race with 80% rule threshold")
    add_figure(doc, os.path.join(ETHICS_DIR, "fig3_equalized_odds.png"), "Equalized Odds assessment showing TPR and FPR disparities across sex and race groups")
    add_figure(doc, os.path.join(ETHICS_DIR, "fig4_confusion_matrices.png"), "Confusion Matrices by sex showing differential error patterns between Male and Female groups")
    add_figure(doc, os.path.join(ETHICS_DIR, "fig6_fairness_heatmap.png"), "Fairness Metrics Summary Heatmap showing all metrics across all demographic groups")
    add_figure(doc, os.path.join(ETHICS_DIR, "fig8_feature_importance.png"), "Logistic Regression Feature Importance showing which features have the highest absolute coefficients")
    add_figure(doc, os.path.join(ETHICS_DIR, "fig9_intersectional_bias.png"), "Intersectional Bias Analysis showing positive prediction rates across Race × Sex combinations")
    
    add_heading_styled(doc, "7.5 Proposed Remediation Strategies", level=2)
    add_body(doc, "Based on the audit findings, the following remediation strategies were proposed: (1) Pre-processing interventions: Re-sampling or re-weighting training data to equalize representation across demographic groups, removing or decorrelating sensitive attributes from feature sets. (2) In-processing interventions: Applying adversarial debiasing during model training, incorporating fairness constraints into the optimization objective. (3) Post-processing interventions: Adjusting classification thresholds per group to equalize TPR/FPR, applying calibration techniques to ensure predictive parity. (4) Organizational practices: Establishing regular bias audits as part of the ML lifecycle, creating diverse development teams, implementing bias impact assessments before deployment.")
    
    add_heading_styled(doc, "7.6 Evaluator Feedback", level=2)
    add_body(doc, "This submission received a score of 70/100. The evaluator acknowledged the solid understanding of bias analysis by reporting specific fairness metrics and identifying potential sources of bias, along with proposing multiple remediation strategies. However, the response was deemed too succinct compared to the required 2000-word minimum, lacking a step-by-step methodology, in-depth literature review, and detailed explanation of visualization methods.")
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════════════
    # CHAPTER 8: CONCLUSION
    # ══════════════════════════════════════════════════════════════════════
    print("[9/10] Chapter 8: Conclusion...")
    add_heading_styled(doc, "Chapter 8: Conclusion and Future Work", level=1)
    
    add_heading_styled(doc, "8.1 Summary of Achievements", level=2)
    add_body(doc, "This internship provided a comprehensive, end-to-end perspective on the lifecycle of artificial intelligence systems. Over six weeks, the following was accomplished:")
    add_body(doc, "Week 1 established the foundational project planning skills required for any AI initiative, covering feasibility analysis, technology selection, and risk assessment. Week 2 demonstrated rigorous data preprocessing expertise, achieving an 85/100 evaluation score through KNN imputation, IQR-based outlier handling, and domain-specific feature engineering on the Titanic dataset.")
    add_body(doc, "Week 3 applied machine learning model development practices including algorithm selection, GridSearchCV hyperparameter tuning with 162 combinations and 5-fold stratified cross-validation, achieving near-perfect classification performance (F1 ≥ 0.97, AUC ≥ 0.995) on the Breast Cancer Wisconsin dataset. Week 4 extended this work with Explainable AI techniques (SHAP and LIME), providing both global and local model interpretations.")
    add_body(doc, "The pinnacle of the internship was Week 5, which produced a production-grade deployment of an AI model as a containerized REST API. The system featured FastAPI with 7 endpoints, Docker multi-stage builds, structured JSON logging, thread-safe metrics monitoring, and 15 automated pytest tests — earning the highest evaluation score of 95/100. Week 6 concluded with a critical AI Ethics audit that quantified and visualized biases across sex and race dimensions.")
    
    add_heading_styled(doc, "8.2 Key Lessons Learned", level=2)
    add_body(doc, "Several critical lessons emerged from this internship: (1) Deliverable specifications must be met precisely — multiple submissions lost significant points for being summaries rather than complete, executable deliverables meeting word count requirements. (2) Deployment engineering is as important as model accuracy — the deployment task earned the highest score because it demonstrated real-world software engineering practices. (3) Ethical considerations must be integrated early in the AI lifecycle, not treated as an afterthought. (4) Reproducibility through pipelines, containers, and version control is essential for production AI.")
    
    add_heading_styled(doc, "8.3 Future Work", level=2)
    add_body(doc, "Several directions for future work were identified: (1) Implementing CI/CD pipelines using GitHub Actions or Jenkins to automate testing and deployment workflows. (2) Integrating model registries like MLflow for versioned model management and experiment tracking. (3) Deploying to managed cloud environments such as AWS SageMaker, Azure ML, or Google Cloud AI Platform. (4) Implementing automated retraining loops triggered by data drift detection. (5) Extending the ethics audit framework to support continuous fairness monitoring in production. (6) Exploring advanced XAI techniques such as Counterfactual Explanations and Attention mechanisms for deep learning models.")
    
    add_heading_styled(doc, "8.4 References", level=2)
    references = [
        "[1] Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5–32.",
        "[2] Wolberg, W.H., Street, W.N., & Mangasarian, O.L. (1994). Machine learning techniques to diagnose breast cancer from fine-needle aspirates. Cancer Letters, 77(2–3), 163–171.",
        "[3] Fernández-Delgado, M., Cernadas, E., Barro, S., & Amorim, D. (2014). Do we need hundreds of classifiers to solve real world classification problems? JMLR, 15(1), 3133–3181.",
        "[4] Lundberg, S.M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. NIPS, 30.",
        "[5] Ribeiro, M.T., Singh, S., & Guestrin, C. (2016). Why should I trust you? Explaining the predictions of any classifier. KDD 2016.",
        "[6] FastAPI Documentation. https://fastapi.tiangolo.com/",
        "[7] Docker Documentation. https://docs.docker.com/",
        "[8] Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. JMLR, 12, 2825–2830.",
        "[9] Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization. JMLR, 13(1), 281–305.",
        "[10] Fawcett, T. (2006). An introduction to ROC analysis. Pattern Recognition Letters, 27(8), 861–874.",
        "[11] Barocas, S., Hardt, M., & Narayanan, A. (2019). Fairness and Machine Learning. fairmlbook.org.",
        "[12] Mehrabi, N., et al. (2021). A survey on bias and fairness in machine learning. ACM Computing Surveys, 54(6).",
    ]
    for ref in references:
        add_body(doc, ref)
    
    # ══════════════════════════════════════════════════════════════════════
    # POPULATE LIST OF FIGURES AND LIST OF TABLES
    # ══════════════════════════════════════════════════════════════════════
    print("[10/10] Populating List of Figures and Tables...")
    
    # Clear and populate List of Figures
    lof_placeholder.clear()
    for num, caption in figure_list:
        run = lof_placeholder.add_run(f"Figure {num}: {caption}\n")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
    
    # Clear and populate List of Tables
    lot_placeholder.clear()
    for num, caption in table_list:
        run = lot_placeholder.add_run(f"Table {num}: {caption}\n")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
    
    # ══════════════════════════════════════════════════════════════════════
    # SAVE AND CONVERT
    # ══════════════════════════════════════════════════════════════════════
    docx_path = os.path.join(REPORT_DIR, "Final_Internship_Report.docx")
    doc.save(docx_path)
    print(f"\n[OK] DOCX saved: {docx_path}")
    
    pdf_path = os.path.join(REPORT_DIR, "Final_Internship_Report.pdf")
    print("Converting to PDF via MS Word COM...")
    try:
        convert(docx_path, pdf_path)
        print(f"[OK] PDF saved: {pdf_path}")
    except Exception as e:
        print(f"[ERROR] PDF conversion failed: {e}")
        print("You can open the DOCX in Word and Save As PDF manually.")
    
    # Count pages
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            print(f"\n[RESULT] Total pages: {len(reader.pages)}")
    except Exception:
        pass
    
    print("\n" + "=" * 60)
    print("  REPORT GENERATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    generate_report()
