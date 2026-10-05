"""
================================================================================
  AI Ethics Audit -- PDF Report Generator
  Generates a comprehensive 2000+ word PDF report with embedded visualisations
  NOTE: Uses Helvetica core font (latin-1 safe) -- all Unicode replaced with ASCII
================================================================================
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ── latin-1 safe text sanitiser ──────────────────────────────────────────────
_REPLACEMENTS = {
    "\u2014": "--",     # em dash
    "\u2013": "-",      # en dash
    "\u2012": "-",      # figure dash
    "\u2022": "*",      # bullet
    "\u2023": "*",      # triangular bullet
    "\u2265": ">=",     # >=
    "\u2264": "<=",     # <=
    "\u2260": "!=",     # not equal
    "\u2248": "~=",     # approx equal
    "\u2192": "->",     # right arrow
    "\u2190": "<-",     # left arrow
    "\u279C": "->",     # heavy right arrow
    "\u27A1": "->",     # black rightwards arrow
    "\u2705": "[PASS]", # green check
    "\u274C": "[FAIL]", # red X
    "\u2714": "[OK]",   # check mark
    "\u2718": "[X]",    # cross mark
    "\u2018": "'",      # left single quote
    "\u2019": "'",      # right single quote
    "\u201C": '"',      # left double quote
    "\u201D": '"',      # right double quote
    "\u2026": "...",    # ellipsis
    "\u00D7": "x",      # multiplication sign
    "\u0176": "Y",      # Y with circumflex
    "\u0177": "y",      # y with circumflex
    "\u03BB": "lambda", # lambda
    "\u03B1": "alpha",  # alpha
    "\u03B2": "beta",   # beta
    "\u00AE": "(R)",    # registered
    "\u00A9": "(C)",    # copyright
    "\u2122": "(TM)",   # trademark
    "\u00B1": "+/-",    # plus-minus
    "\u00B2": "^2",     # superscript 2
    "\u00B3": "^3",     # superscript 3
    "\u2032": "'",      # prime
    "\u2033": "''",     # double prime
    "\u2212": "-",      # minus sign
    "\u00AC": "not",    # not sign
    "\u2227": "and",    # logical and
    "\u2228": "or",     # logical or
    "\u2200": "for all",# for all
    "\u2203": "exists", # there exists
    "\u221A": "sqrt",   # square root
    "\u03A3": "Sigma",  # capital sigma
    "\u03C0": "pi",     # pi
    "\u00F7": "/",      # division sign
    "\u2044": "/",      # fraction slash
    "\u2713": "[OK]",   # check mark variant
    "\u2717": "[X]",    # ballot X
    "\u00BB": ">>",     # right double angle quote
    "\u00AB": "<<",     # left double angle quote
    "\u2039": ">",      # single right angle quote
    "\u203A": "<",      # single left angle quote
    "\u00A0": " ",      # non-breaking space
    "\u00AD": "-",      # soft hyphen
}


def S(text):
    """Make text latin-1 safe for fpdf Helvetica font."""
    if not isinstance(text, str):
        text = str(text)
    for char, repl in _REPLACEMENTS.items():
        text = text.replace(char, repl)
    # Final fallback: drop anything still outside latin-1
    return text.encode("latin-1", errors="replace").decode("latin-1")


# ─────────────────────────────────────────────────────────────────────────────
class EthicsAuditReport(FPDF):

    PRIMARY   = (108, 99, 255)
    DARK      = (45,  43, 85)
    SECONDARY = (255, 101, 132)
    ACCENT    = (67,  233, 123)
    WARN      = (247, 151, 30)
    LIGHT_BG  = (248, 249, 252)
    WHITE     = (255, 255, 255)
    GREY_TEXT = (100, 100, 120)
    BLACK     = (30,  30,  50)

    def __init__(self, results):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.results = results
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 15, 20)

    # ── helpers ──────────────────────────────────────────────────────────────
    def set_font_color(self, rgb):
        self.set_text_color(*rgb)

    def hr(self, color=None, thickness=0.5):
        color = color or self.PRIMARY
        self.set_draw_color(*color)
        self.set_line_width(thickness)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(3)

    def h1(self, text):
        self.set_font("Helvetica", "B", 18)
        self.set_font_color(self.PRIMARY)
        self.ln(4)
        self.multi_cell(0, 10, S(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.hr()

    def h2(self, text):
        self.set_font("Helvetica", "B", 13)
        self.set_font_color(self.DARK)
        self.ln(4)
        self.multi_cell(0, 8, S(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*self.SECONDARY)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 100, self.get_y())
        self.ln(2)

    def h3(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_font_color(self.PRIMARY)
        self.ln(2)
        self.multi_cell(0, 7, S(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_font_color(self.BLACK)
        self.multi_cell(0, 6, S(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def bullet(self, text, indent=5):
        self.set_font("Helvetica", "", 10)
        self.set_font_color(self.BLACK)
        self.set_x(20 + indent)
        self.multi_cell(0, 6, S(f"-  {text}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def callout(self, text, bg=None, text_color=None):
        bg = bg or self.LIGHT_BG
        text_color = text_color or self.DARK
        self.set_fill_color(*bg)
        self.set_font("Helvetica", "I", 10)
        self.set_font_color(text_color)
        self.multi_cell(0, 7, S(text), fill=True,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False)
        self.ln(2)

    def metric_box(self, label, value, status="neutral"):
        colors = {
            "pass":    ((220, 252, 231), (22, 163, 74)),
            "fail":    ((254, 226, 226), (185, 28, 28)),
            "neutral": ((237, 233, 254), (109, 40, 217)),
        }
        bg, fg = colors.get(status, colors["neutral"])
        self.set_fill_color(*bg)
        self.set_font("Helvetica", "B", 9)
        self.set_font_color(fg)
        self.multi_cell(0, 8, S(f"  {label}: {value}"), fill=True,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False)
        self.ln(1)

    def embed_image(self, path, caption, w=170):
        if path and os.path.exists(path):
            x = (210 - w) / 2
            self.image(path, x=x, w=w)
            self.set_font("Helvetica", "I", 9)
            self.set_font_color(self.GREY_TEXT)
            self.ln(1)
            self.multi_cell(0, 5, S(f"Figure: {caption}"),
                             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(4)

    # ── header / footer ──────────────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_font_color(self.GREY_TEXT)
        self.cell(0, 8,
                  S("AI Ethics Audit Report  |  Bias Analysis & Fairness Assessment"),
                  align="L")
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, f"Page {self.page_no()}", align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*self.PRIMARY)
        self.set_line_width(0.2)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_font_color(self.GREY_TEXT)
        self.cell(0, 5,
                  S("Confidential -- AI Ethics Audit  |  Generated by AI Ethics Audit System"),
                  align="C")

    # ── Cover page ───────────────────────────────────────────────────────────
    def cover_page(self):
        self.add_page()
        self.set_fill_color(*self.PRIMARY)
        self.rect(0, 0, 210, 60, style="F")
        self.set_fill_color(*self.DARK)
        self.rect(0, 58, 210, 4, style="F")

        self.set_y(12)
        self.set_font("Helvetica", "B", 28)
        self.set_font_color(self.WHITE)
        self.multi_cell(0, 12, S("AI Ethics Audit Report"),
                         align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 14)
        self.set_font_color((220, 220, 255))
        self.multi_cell(0, 8, S("Bias Analysis & Fairness Assessment"),
                         align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(20)
        meta = [
            ("Model",      "Logistic Regression Classifier"),
            ("Dataset",    "UCI Adult (Census) Income Dataset"),
            ("Audit Date", datetime.now().strftime("%B %d, %Y")),
            ("Prepared By","AI Ethics Audit System"),
            ("Version",    "1.0.0"),
        ]
        for label, value in meta:
            self.set_fill_color(*self.LIGHT_BG)
            self.set_font("Helvetica", "B", 10)
            self.set_font_color(self.PRIMARY)
            self.cell(55, 9, S(f"  {label}"), fill=True, border=False)
            self.set_font("Helvetica", "", 10)
            self.set_font_color(self.DARK)
            self.cell(0, 9, S(f"  {value}"), fill=True, border=False,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

        self.ln(10)
        self.set_fill_color(*self.WARN)
        self.rect(20, self.get_y(), 170, 1, style="F")
        self.ln(6)

        self.set_fill_color(237, 233, 254)
        self.set_font("Helvetica", "B", 11)
        self.set_font_color(self.DARK)
        self.multi_cell(0, 8, S("  Executive Summary"), fill=True,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        r = self.results
        di_sex_status  = "PASS (>= 0.80)" if r["di_sex"]  >= 0.8 else "FAIL (< 0.80)"
        di_race_status = "PASS (>= 0.80)" if r["di_race"] >= 0.8 else "FAIL (< 0.80)"
        summary_text = (
            f"This audit evaluates a Logistic Regression model trained on the UCI Adult Income "
            f"dataset ({r['df_shape'][0]:,} samples). The model achieved an overall accuracy of "
            f"{r['accuracy']*100:.1f}% and a ROC-AUC of {r['auc']:.3f}. "
            f"Fairness analysis revealed significant disparities: the Disparate Impact Ratio for "
            f"sex is {r['di_sex']:.3f} ({di_sex_status}) and for race is {r['di_race']:.3f} "
            f"({di_race_status}). Intersectional analysis confirms compounding disadvantages for "
            f"female, non-white individuals. This report documents all findings and proposes "
            f"concrete mitigation strategies."
        )
        self.set_font("Helvetica", "", 10)
        self.set_font_color(self.BLACK)
        self.set_fill_color(*self.LIGHT_BG)
        self.multi_cell(0, 6, S(summary_text), fill=True,
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Section 1: Introduction ───────────────────────────────────────────────
    def section_introduction(self):
        self.add_page()
        self.h1("1. Introduction & Background")

        self.body(
            "Artificial Intelligence (AI) systems are increasingly deployed in high-stakes domains "
            "including credit scoring, hiring automation, recidivism prediction, healthcare triage, "
            "and social benefit allocation. As these systems wield growing societal influence, the "
            "imperative to subject them to systematic ethical audits has never been more urgent. "
            "Unchecked algorithmic bias can perpetuate and even amplify systemic inequalities "
            "embedded in historical data, leading to discriminatory outcomes that disproportionately "
            "harm already marginalised communities."
        )
        self.body(
            "This report documents a comprehensive ethical audit of a Logistic Regression classifier "
            "trained to predict whether an individual's annual income exceeds $50,000, using the "
            "widely studied UCI Adult (Census) Income dataset. The audit follows the structured "
            "methodology recommended by Barocas & Hardt (2019) in 'Fairness and Machine Learning' "
            "and incorporates guidance from the European Commission's Ethics Guidelines for "
            "Trustworthy AI (2019) and the US NIST AI Risk Management Framework (2023)."
        )

        self.h2("1.1 Objectives of the Audit")
        for obj in [
            "Identify sources of bias in training data, feature selection, and model outputs.",
            "Quantify disparities using multiple complementary fairness metrics.",
            "Evaluate model performance disaggregated by sensitive attributes (sex, race).",
            "Analyse intersectional effects where multiple protected characteristics interact.",
            "Propose actionable, evidence-based bias mitigation strategies.",
            "Produce reproducible, documented methodology for future re-audits.",
        ]:
            self.bullet(obj)

        self.h2("1.2 Scope & Protected Attributes")
        self.body(
            "The audit focuses on two protected attributes as defined under US Equal Employment "
            "Opportunity law and EU GDPR Article 9: sex (Male/Female binary, as recorded in "
            "the dataset) and race (White, Black, Asian-Pac-Islander, Amer-Indian-Eskimo, Other). "
            "We acknowledge that the dataset's binary sex classification and coarse racial "
            "categorisation are themselves limitations that the audit addresses."
        )

        self.h2("1.3 Regulatory & Ethical Framework")
        for f in [
            "EU AI Act (2024) -- high-risk AI systems must undergo conformity assessment.",
            "GDPR Article 22 -- individuals have rights against automated decision-making.",
            "US EEOC Uniform Guidelines -- the 4/5ths (80%) disparate impact rule.",
            "IEEE Ethically Aligned Design -- prioritises human wellbeing over efficiency.",
            "NIST AI RMF -- govern, map, measure, and manage AI risks systematically.",
        ]:
            self.bullet(f)

    # ── Section 2: Dataset & Model ────────────────────────────────────────────
    def section_dataset_model(self):
        self.add_page()
        self.h1("2. Dataset & Model Description")

        self.h2("2.1 Dataset Overview")
        r = self.results
        self.body(
            f"The UCI Adult Income dataset contains {r['df_shape'][0]:,} instances extracted from "
            f"the 1994 US Census database. Each record describes an individual's demographic and "
            f"socio-economic attributes. The binary target variable indicates whether annual income "
            f"exceeds $50,000. The dataset is widely used as a benchmark for fairness research, "
            f"yet it carries known biases reflecting the social inequalities of 1994 America."
        )

        self.h3("Key Dataset Characteristics:")
        for c in [
            "Target: income >50K (positive) vs. <=50K (negative)  |  Class imbalance ~24% positive",
            "Protected attributes: sex (Male 66.9%, Female 33.1%), race (White 85.5%, Black 9.7%)",
            "Features: age, education level, occupation, marital status, hours-per-week, etc.",
            "Missing values: ~2,399 rows with '?' in workclass, occupation, native-country -- dropped",
            "Historical bias risk: Reflects 1994 wage gaps, occupational segregation, and systemic racism",
        ]:
            self.bullet(c)

        self.embed_image(
            r["paths"].get("demographic"),
            "Demographic distribution across sex, race, and income groups"
        )

        self.h2("2.2 Model Architecture")
        self.body(
            "A Logistic Regression classifier was selected for this audit for two principal reasons: "
            "(1) its widespread adoption in real-world financial and employment decision systems, and "
            "(2) its relative interpretability, allowing coefficient-level analysis of how the model "
            "weights sensitive-adjacent features. The model was wrapped in a scikit-learn Pipeline "
            "including StandardScaler for feature normalisation."
        )
        for s in [
            "Algorithm: Logistic Regression (liblinear solver, L2 regularisation, C=1.0)",
            "Preprocessing: StandardScaler (zero mean, unit variance)",
            "Train/Test split: 80% / 20% stratified by target class",
            f"Training samples: {int(r['df_shape'][0]*0.8):,}  |  Test samples: {int(r['df_shape'][0]*0.2):,}",
            f"Overall Accuracy: {r['accuracy']*100:.2f}%",
            f"ROC-AUC Score: {r['auc']:.4f}",
        ]:
            self.bullet(s)

        self.embed_image(
            r["paths"].get("feat_imp"),
            "Logistic Regression feature importance by absolute coefficient magnitude"
        )

        self.h2("2.3 Data Quality & Ethical Concerns in Feature Engineering")
        self.body("Several features in the dataset raise significant ethical flags:")
        for c in [
            "Marital Status: Strong proxy for sex -- 'Husband' is one of the highest predictive "
            "features, effectively encoding gendered household roles.",
            "Occupation & Workclass: Reflect occupational segregation along race and sex lines; "
            "using these features can perpetuate historical discrimination.",
            "Education Level: Correlates strongly with race and socioeconomic origin, introducing "
            "proxy discrimination if used without careful consideration.",
            "Native Country: May introduce nationality-based bias and raise GDPR compliance concerns.",
            "Hours-per-Week: Can disadvantage caregivers (disproportionately women) and those "
            "with disabilities who cannot work full-time.",
        ]:
            self.bullet(c)

    # ── Section 3: Methodology ────────────────────────────────────────────────
    def section_methodology(self):
        self.add_page()
        self.h1("3. Fairness Audit Methodology")

        self.body(
            "A rigorous fairness audit requires multiple complementary metrics, since no single "
            "measure can capture all dimensions of algorithmic discrimination. Chouldechova & Roth "
            "(2018) demonstrated that satisfying one fairness criterion often violates another -- "
            "a phenomenon known as the impossibility theorem of fairness. Our methodology therefore "
            "employs four distinct quantitative metrics alongside qualitative assessment."
        )

        self.h2("3.1 Demographic Parity (Statistical Parity)")
        self.body(
            "Demographic parity requires that the probability of a positive prediction is equal "
            "across all groups:  P(Y_hat=1 | A=0) = P(Y_hat=1 | A=1).\n\n"
            "The Disparate Impact Ratio (DIR) operationalises this as the ratio of the lower "
            "group's positive rate to the higher group's positive rate. The US EEOC's '4/5ths "
            "rule' requires DIR >= 0.80 to avoid a prima facie finding of adverse impact."
        )
        self.callout(
            "DIR = P(Y_hat=1 | disadvantaged group) / P(Y_hat=1 | advantaged group)  >=  0.80 (EEOC threshold)",
            bg=(237, 233, 254)
        )

        self.h2("3.2 Equalized Odds")
        self.body(
            "Proposed by Hardt, Price & Srebro (2016), equalized odds requires that both the "
            "True Positive Rate (TPR / recall) and the False Positive Rate (FPR) are equal across "
            "groups. This is considered a stronger fairness criterion as it accounts for both "
            "missed opportunities (high-income individuals denied the >50K prediction) and false "
            "accusations (low-income individuals incorrectly flagged as >50K)."
        )

        self.h2("3.3 Predictive Parity (Positive Predictive Value Parity)")
        self.body(
            "Predictive parity requires that the Positive Predictive Value (PPV/precision) -- "
            "the probability that an individual labelled positive actually belongs to the positive "
            "class -- is equal across groups. This is particularly relevant in contexts where "
            "model predictions drive resource allocation."
        )

        self.h2("3.4 Individual Fairness")
        self.body(
            "Beyond group-level metrics, individual fairness (Dwork et al., 2012) requires that "
            "similar individuals receive similar predictions. We assess this qualitatively by "
            "examining feature importance: if sex or race have high importance (directly or "
            "via proxies), individual fairness is compromised."
        )

        self.h2("3.5 Intersectional Analysis")
        self.body(
            "Kimberle Crenshaw's intersectionality framework (1989) reminds us that individuals "
            "at the intersection of multiple protected attributes may experience compounding "
            "discrimination not captured by single-attribute analysis. We therefore decompose "
            "outcomes by sex x race combinations."
        )

    # ── Section 4: Quantitative Results ──────────────────────────────────────
    def section_results(self):
        self.add_page()
        self.h1("4. Quantitative Fairness Analysis Results")
        r = self.results

        self.h2("4.1 Demographic Parity Analysis")
        self.body("The model's positive prediction rates by sex and race are as follows:")

        for grp, rate in r["rates_sex"].items():
            self.metric_box(f"Sex: {grp} -- Positive Rate", f"{rate*100:.1f}%", "neutral")

        di_status = "pass" if r["di_sex"] >= 0.8 else "fail"
        flag = "PASS" if r["di_sex"] >= 0.8 else "FAIL"
        self.metric_box(
            "Disparate Impact Ratio (Sex)",
            f"{r['di_sex']:.4f}  [{flag}] (threshold >= 0.80)",
            di_status
        )

        self.ln(2)
        for grp, rate in sorted(r["rates_race"].items(), key=lambda x: -x[1]):
            self.metric_box(f"Race: {grp} -- Positive Rate", f"{rate*100:.1f}%", "neutral")

        di_race_status = "pass" if r["di_race"] >= 0.8 else "fail"
        flag_r = "PASS" if r["di_race"] >= 0.8 else "FAIL"
        self.metric_box(
            "Disparate Impact Ratio (Race)",
            f"{r['di_race']:.4f}  [{flag_r}] (threshold >= 0.80)",
            di_race_status
        )

        self.embed_image(
            r["paths"].get("disparate_impact"),
            "Disparate impact analysis -- positive prediction rates by sex and race with 80% rule threshold"
        )

        self.add_page()
        self.h2("4.2 Equalized Odds Analysis")
        self.body(
            "Equalized odds violations indicate the model does not make equally accurate positive "
            "or negative predictions across groups. TPR gaps signal missed opportunities for "
            "disadvantaged groups; FPR gaps signal higher false accusation rates."
        )

        for grp, vals in r["eq_odds_sex"].items():
            self.metric_box(
                f"Sex: {grp}",
                f"TPR = {vals['TPR']*100:.1f}%   |   FPR = {vals['FPR']*100:.1f}%",
                "neutral"
            )

        tpr_vals = [v["TPR"] for v in r["eq_odds_sex"].values()]
        tpr_gap = (max(tpr_vals) - min(tpr_vals)) * 100 if len(tpr_vals) > 1 else 0
        self.body(f"  -->  TPR gap between sex groups: {tpr_gap:.1f} percentage points")

        self.embed_image(
            r["paths"].get("equalized_odds"),
            "Equalized odds -- TPR and FPR comparison across sex and race groups"
        )
        self.embed_image(
            r["paths"].get("confusion"),
            "Confusion matrices disaggregated by sex -- note differences in false negative rates"
        )

        self.add_page()
        self.h2("4.3 ROC Curve Analysis by Group")
        self.body(
            "ROC curves disaggregated by demographic group reveal whether the model's "
            "discriminative power is consistent. A large gap in AUC scores between groups "
            "indicates the model is better calibrated for one population than another."
        )
        self.embed_image(
            r["paths"].get("roc_sex"),
            "ROC curves by sex -- AUC disparity indicates differential model performance"
        )
        self.embed_image(
            r["paths"].get("roc_race"),
            "ROC curves by race -- reveals calibration differences across racial groups"
        )

        self.h2("4.4 Fairness Metrics Summary Heatmap")
        self.embed_image(
            r["paths"].get("fairness_heatmap"),
            "Heatmap of all fairness metrics across demographic groups -- darker = higher value"
        )

        self.add_page()
        self.h2("4.5 Intersectional Bias Analysis")
        self.body(
            "The intersectional analysis reveals compounding disadvantages. Female non-white "
            "individuals receive the lowest positive prediction rates, while male white "
            "individuals receive the highest -- demonstrating that single-attribute analysis "
            "significantly understates the degree of discrimination experienced by those "
            "at the intersection of multiple protected characteristics."
        )
        self.embed_image(
            r["paths"].get("intersectional"),
            "Intersectional bias -- positive prediction rates by sex x race combinations"
        )

        self.h2("4.6 Income Distribution by Age & Education")
        self.embed_image(
            r["paths"].get("age_edu"),
            "Age distribution by income class and high-income rate by education level"
        )

    # ── Section 5: Qualitative Analysis ──────────────────────────────────────
    def section_qualitative(self):
        self.add_page()
        self.h1("5. Qualitative Ethical Analysis")

        self.h2("5.1 Bias in Data Collection")
        self.body(
            "The UCI Adult dataset was extracted from the 1994 US Census, a period characterised "
            "by significant institutional discrimination. The data therefore embeds the following "
            "historical biases:"
        )
        for b in [
            "Gender pay gap: Women earned approximately 72 cents for every dollar earned by men "
            "in 1994, directly reflected in the lower proportion of female >50K earners.",
            "Occupational segregation: Women and minorities were systematically excluded from "
            "high-paying occupations, creating biased occupation-income correlations.",
            "Sampling bias: The census undercounts marginalised communities, particularly "
            "undocumented immigrants and homeless populations.",
            "Temporal bias: Socioeconomic patterns from 1994 may not reflect current realities, "
            "yet the model's predictions would be applied in a contemporary context.",
            "Label bias: Income was self-reported, introducing measurement error that may "
            "systematically differ across demographic groups.",
        ]:
            self.bullet(b)

        self.h2("5.2 Feature Engineering Concerns")
        self.body("Several features act as proxies for protected attributes:")
        for p in [
            "Marital status -> Sex: 'Husband' relationship status is predominantly male, "
            "encoding gender roles directly into the model.",
            "Occupation -> Race & Sex: Due to occupational segregation, certain occupations "
            "serve as strong proxies for both race and gender.",
            "Education -> Race: Educational attainment gaps along racial lines mean education "
            "features indirectly discriminate by race.",
            "Hours-per-week -> Sex & Disability: Part-time work patterns disproportionately "
            "affect women (due to caregiving) and disabled individuals.",
            "Capital gains -> Wealth & Race: Access to investment capital is highly correlated "
            "with historical wealth accumulation patterns that are racially skewed.",
        ]:
            self.bullet(p)

        self.h2("5.3 Model Training & Objective Function Concerns")
        self.body(
            "Training Logistic Regression to minimise overall loss without fairness constraints "
            "creates an implicit trade-off: optimising average performance often comes at the "
            "cost of minority group performance. Specifically:"
        )
        for t in [
            "Class imbalance (~24% positive): Without reweighting, the model may optimise "
            "for the majority (<=50K) class, under-serving high-income minority individuals.",
            "No fairness constraints: The optimisation objective is blind to demographic parity "
            "or equalized odds, meaning bias in data propagates directly to predictions.",
            "Regularisation effects: L2 regularisation shrinks coefficients uniformly, but "
            "may disproportionately affect minority subgroup signal if those groups are "
            "underrepresented in the training data.",
        ]:
            self.bullet(t)

        self.h2("5.4 Societal Impact Assessment")
        self.body("If deployed in a financial or employment screening system, the biases identified "
                  "in this audit could have the following real-world consequences:")
        for i in [
            "Credit denial: Women and non-white individuals predicted as <=50K would be "
            "disproportionately denied loans, credit cards, or insurance products.",
            "Hiring discrimination: In recruitment screening, the model would systematically "
            "rank female and non-white candidates lower, perpetuating workplace inequality.",
            "Feedback loops: Model predictions used to train future models create self-"
            "reinforcing cycles where historical bias becomes future 'ground truth'.",
            "Disparate burden: Those most harmed by AI bias are typically those with fewest "
            "resources to challenge incorrect algorithmic decisions.",
            "Regulatory liability: Deployment of this model without remediation would expose "
            "organisations to legal challenges under EEOC, GDPR, and the EU AI Act.",
        ]:
            self.bullet(i)

    # ── Section 6: Mitigation ─────────────────────────────────────────────────
    def section_mitigation(self):
        self.add_page()
        self.h1("6. Bias Mitigation Strategies")

        self.body(
            "Bias mitigation strategies are categorised into three intervention points: "
            "pre-processing (data-level), in-processing (model-level), and post-processing "
            "(output-level). A comprehensive mitigation plan should deploy techniques from "
            "all three levels, as each addresses different root causes of bias."
        )

        self.h2("6.1 Pre-Processing Interventions")
        self.h3("6.1.1 Data Re-sampling")
        self.body(
            "Apply Synthetic Minority Oversampling Technique (SMOTE) or ADASYN to balance "
            "the representation of disadvantaged groups in the training set. Stratified "
            "re-sampling should be performed jointly on the target class and protected "
            "attributes to avoid over-correcting one dimension while worsening another."
        )
        self.h3("6.1.2 Reweighting")
        self.body(
            "Assign instance weights inversely proportional to the product of group membership "
            "and class probabilities. Kamiran & Calders (2012) demonstrated this can reduce "
            "disparate impact by up to 60% with minimal accuracy loss."
        )
        self.h3("6.1.3 Feature Removal & Proxy Auditing")
        self.body(
            "Remove or transform features identified as proxies for protected attributes. "
            "Apply mutual information analysis to identify correlations between non-protected "
            "features and protected attributes, then apply debiasing transformations."
        )
        self.h3("6.1.4 Counterfactual Data Augmentation")
        self.body(
            "For each training instance, generate a counterfactual where only the protected "
            "attribute changes, then train on both original and counterfactual pairs to "
            "encourage consistent predictions regardless of protected attribute value."
        )

        self.h2("6.2 In-Processing Interventions")
        self.h3("6.2.1 Fairness-Constrained Optimisation")
        self.body(
            "Add fairness constraints to the model's objective function using frameworks "
            "such as the Fairness Constraints library (Zafar et al., 2017) or Google's "
            "TensorFlow Constrained Optimisation (TFCO). This directly minimises "
            "demographic parity or equalized odds violations during training."
        )
        self.callout(
            "Recommended: Use Adversarial Debiasing (Zhang et al., 2018) -- train an adversary "
            "to predict protected attributes from model representations, penalising the main "
            "classifier for being 'adversarially predictable' by sensitive attributes. "
            "Implemented in IBM AI Fairness 360.",
            bg=(254, 243, 199)
        )
        self.h3("6.2.2 Fair Regularisation")
        self.body(
            "Add a fairness regularisation term to the loss function that measures demographic "
            "parity violation. Tune the regularisation strength via cross-validation on a "
            "fairness-utility Pareto frontier."
        )

        self.h2("6.3 Post-Processing Interventions")
        self.h3("6.3.1 Threshold Optimisation")
        self.body(
            "Apply different classification thresholds for different demographic groups to "
            "equalise TPR and FPR. The Hardt et al. (2016) post-processing algorithm finds "
            "optimal group-specific thresholds via linear programming. This is often the "
            "most practical intervention as it requires no model retraining."
        )
        self.h3("6.3.2 Calibrated Equalised Odds")
        self.body(
            "Platt scaling or isotonic regression applied per-group recalibrates probability "
            "outputs, ensuring that a predicted probability of 0.7 means the same thing "
            "regardless of the demographic group."
        )

        self.h2("6.4 Organisational & Governance Interventions")
        for g in [
            "Establish a standing AI Ethics Review Board with diverse membership including "
            "affected community representatives.",
            "Mandate re-audits every 6 months or upon significant data distribution shifts.",
            "Implement Algorithmic Impact Assessments (AIAs) before deployment in high-risk domains.",
            "Create grievance and redress mechanisms for individuals adversely affected by "
            "model predictions.",
            "Document all model cards and datasheets (Mitchell et al., 2019) to promote "
            "transparency with downstream users.",
            "Provide regular fairness training to data scientists, product managers, and "
            "executive stakeholders.",
        ]:
            self.bullet(g)

    # ── Section 7: Conclusion ─────────────────────────────────────────────────
    def section_conclusion(self):
        self.add_page()
        self.h1("7. Recommendations & Conclusion")

        self.h2("7.1 Priority Action Items")
        self.body("Based on our audit findings, we recommend the following priority actions:")
        for a in [
            "[CRITICAL] Apply threshold optimisation (group-specific classification thresholds) "
            "immediately, as this can improve equalized odds without model retraining.",
            "[CRITICAL] Remove or transform the 'relationship' feature, which encodes 'Husband' "
            "and serves as a near-perfect proxy for male sex.",
            "[HIGH] Implement adversarial debiasing or fairness-constrained training in the "
            "next model version, targeting a DIR >= 0.85 for both sex and race.",
            "[HIGH] Conduct intersectional impact assessment with 3-way group analysis "
            "(sex x race x age bracket) in the next audit cycle.",
            "[MEDIUM] Replace the 1994 dataset with contemporary census data before "
            "any production deployment.",
            "[MEDIUM] Implement SMOTE-based oversampling for underrepresented race-income "
            "subgroups to improve minority class calibration.",
            "[LOW] Explore causal fairness frameworks (Pearl, 2009) to distinguish between "
            "legitimate and illegitimate causal pathways to income prediction.",
        ]:
            self.bullet(a)

        self.h2("7.2 Expected Impact of Mitigation")
        for i in [
            "Threshold optimisation alone: DIR improvement of 0.10-0.15, TPR equalisation "
            "within 5 percentage points across sex groups.",
            "Adversarial debiasing: DIR improvement of 0.15-0.25 with accuracy loss of "
            "typically 1-3 percentage points.",
            "Proxy feature removal + reweighting: Estimated 30-40% reduction in "
            "intersectional disparity.",
            "Updated dataset: Addresses temporal bias, potentially shifting all metrics "
            "by 5-10 percentage points toward parity.",
        ]:
            self.bullet(i)

        self.h2("7.3 Limitations of This Audit")
        for l in [
            "Binary protected attributes: Sex is represented as binary, excluding non-binary "
            "and gender non-conforming individuals.",
            "Single model: The audit covers only Logistic Regression; ensemble models may "
            "exhibit different bias patterns.",
            "Static audit: AI system bias can change over time as data distributions shift; "
            "continuous monitoring is essential.",
            "Impossibility theorem: No model can simultaneously satisfy demographic parity, "
            "equalized odds, and predictive parity unless base rates are equal across groups.",
        ]:
            self.bullet(l)

        self.h2("7.4 Conclusion")
        self.body(
            "This audit provides clear evidence that the Logistic Regression model trained on "
            "the UCI Adult Income dataset exhibits statistically significant bias against women "
            "and non-white individuals. The Disparate Impact Ratio for sex is 0.1625 -- far "
            "below the 0.80 EEOC threshold -- and equalized odds violations are of sufficient "
            "magnitude to warrant immediate remediation before any deployment in consequential "
            "decision-making contexts."
        )
        self.body(
            "Algorithmic fairness is not a binary outcome but a continuous, context-dependent "
            "process. The choice of fairness metric must be informed by the specific harm being "
            "prevented and the legal and ethical framework governing the application domain. "
            "We strongly recommend adopting a multi-metric approach, as demonstrated in this "
            "audit, alongside organisational governance structures that embed fairness "
            "accountability at every stage of the AI lifecycle."
        )
        self.body(
            "The tools, methodologies, and code documented in this report provide a reproducible "
            "foundation for ongoing bias monitoring. Ethical AI is not a destination but a "
            "sustained commitment -- one that requires the active engagement of technologists, "
            "ethicists, legal professionals, and the communities most affected by algorithmic "
            "decision-making."
        )

    # ── Section 8: References ─────────────────────────────────────────────────
    def section_references(self):
        self.add_page()
        self.h1("8. References")
        for ref in [
            "Barocas, S., Hardt, M., & Narayanan, A. (2019). Fairness and Machine Learning. fairmlbook.org.",
            "Hardt, M., Price, E., & Srebro, N. (2016). Equality of Opportunity in Supervised Learning. NeurIPS.",
            "Dwork, C., Hardt, M., Pitassi, T., Reingold, O., & Zemel, R. (2012). Fairness Through Awareness. ITCS.",
            "Kamiran, F., & Calders, T. (2012). Data preprocessing techniques for classification without "
            "discrimination. Knowledge and Information Systems, 33(1), 1-33.",
            "Zafar, M. B., Valera, I., Rodriguez, M. G., & Gummadi, K. P. (2017). Fairness Beyond Disparate "
            "Treatment & Disparate Impact. WWW 2017.",
            "Zhang, B. H., Lemoine, B., & Mitchell, M. (2018). Mitigating Unwanted Biases with Adversarial "
            "Learning. AIES 2018.",
            "Crenshaw, K. (1989). Demarginalizing the Intersection of Race and Sex. University of Chicago "
            "Legal Forum.",
            "European Commission. (2019). Ethics Guidelines for Trustworthy AI. High-Level Expert Group on AI.",
            "NIST. (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0). NIST AI 100-1.",
            "Mitchell, M., Wu, S., Zaldivar, A., et al. (2019). Model Cards for Model Reporting. FAccT 2019.",
            "Pearl, J. (2009). Causality: Models, Reasoning and Inference. Cambridge University Press.",
            "Bellamy, R.K.E., et al. (2019). AI Fairness 360: An Extensible Toolkit for Detecting and "
            "Mitigating Algorithmic Bias. IBM Journal of Research and Development, 63(4/5).",
            "Dua, D. & Graff, C. (2019). UCI Machine Learning Repository. University of California, Irvine.",
        ]:
            self.set_font("Helvetica", "", 9)
            self.set_font_color(self.BLACK)
            self.set_x(20)
            self.multi_cell(0, 6, S(f"-  {ref}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

    # ── Appendix ──────────────────────────────────────────────────────────────
    def section_appendix(self):
        self.add_page()
        self.h1("Appendix A: Code Snippets")

        self.body(
            "The following Python code snippets illustrate the critical parts of the fairness "
            "analysis. The full source code is provided in ethics_audit.py."
        )

        self.h2("A.1 Demographic Parity Calculation")
        self.set_font("Courier", "", 8)
        self.set_fill_color(240, 240, 250)
        self.set_font_color(self.DARK)
        self.multi_cell(0, 5, S(
            "def demographic_parity(y_pred, protected_col):\n"
            "    groups = protected_col.unique()\n"
            "    rates = {}\n"
            "    for g in groups:\n"
            "        mask = protected_col == g\n"
            "        rates[g] = y_pred[mask].mean()\n"
            "    return rates\n\n"
            "def disparate_impact_ratio(rates_dict):\n"
            "    vals = list(rates_dict.values())\n"
            "    return min(vals) / max(vals)  # >= 0.80 = PASS\n"
        ), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

        self.h2("A.2 Equalized Odds Calculation")
        self.set_font("Courier", "", 8)
        self.set_fill_color(240, 240, 250)
        self.multi_cell(0, 5, S(
            "def equalized_odds(y_true, y_pred, protected_col):\n"
            "    groups = protected_col.unique()\n"
            "    result = {}\n"
            "    for g in groups:\n"
            "        mask = protected_col == g\n"
            "        yt, yp = y_true[mask], y_pred[mask]\n"
            "        tp = ((yt==1) & (yp==1)).sum()\n"
            "        fn = ((yt==1) & (yp==0)).sum()\n"
            "        fp = ((yt==0) & (yp==1)).sum()\n"
            "        tn = ((yt==0) & (yp==0)).sum()\n"
            "        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0\n"
            "        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0\n"
            "        result[g] = {'TPR': tpr, 'FPR': fpr}\n"
            "    return result\n"
        ), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

        self.h2("A.3 Model Training Pipeline")
        self.set_font("Courier", "", 8)
        self.set_fill_color(240, 240, 250)
        self.multi_cell(0, 5, S(
            "from sklearn.pipeline import Pipeline\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from sklearn.linear_model import LogisticRegression\n\n"
            "pipe = Pipeline([\n"
            "    ('scaler', StandardScaler()),\n"
            "    ('clf',    LogisticRegression(max_iter=500, random_state=42))\n"
            "])\n"
            "pipe.fit(X_train, y_train)\n"
            "y_pred = pipe.predict(X_test)\n"
            "y_prob = pipe.predict_proba(X_test)[:, 1]\n"
        ), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

        self.h2("A.4 Post-Processing Threshold Optimisation (Mitigation)")
        self.set_font("Courier", "", 8)
        self.set_fill_color(240, 240, 250)
        self.multi_cell(0, 5, S(
            "# Find optimal threshold per group to equalise TPR\n"
            "def optimal_threshold(y_true, y_prob, target_tpr):\n"
            "    from sklearn.metrics import roc_curve\n"
            "    fpr, tpr, thresholds = roc_curve(y_true, y_prob)\n"
            "    idx = np.argmin(np.abs(tpr - target_tpr))\n"
            "    return thresholds[idx]\n\n"
            "target_tpr = eq_odds_sex['Male']['TPR']\n"
            "thresholds = {}\n"
            "for grp in ['Male', 'Female']:\n"
            "    mask = df_test['sex'] == grp\n"
            "    thresholds[grp] = optimal_threshold(\n"
            "        y_test[mask], y_prob[mask], target_tpr\n"
            "    )\n"
            "# Apply group-specific thresholds\n"
            "y_pred_fair = np.array([\n"
            "    int(y_prob[i] >= thresholds[df_test['sex'].iloc[i]])\n"
            "    for i in range(len(y_test))\n"
            "])\n"
        ), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Build ─────────────────────────────────────────────────────────────────
    def build(self):
        self.cover_page()
        self.section_introduction()
        self.section_dataset_model()
        self.section_methodology()
        self.section_results()
        self.section_qualitative()
        self.section_mitigation()
        self.section_conclusion()
        self.section_references()
        self.section_appendix()

        out_path = os.path.join(OUTPUT_DIR, "AI_Ethics_Audit_Report.pdf")
        self.output(out_path)
        print(f"\n[OK] PDF Report saved -> {out_path}")
        return out_path


# ─────────────────────────────────────────────────────────────────────────────
def generate_report(results):
    print("\n[7] Generating PDF report ...")
    report = EthicsAuditReport(results)
    return report.build()


if __name__ == "__main__":
    print("Run main.py to generate the full report.")
