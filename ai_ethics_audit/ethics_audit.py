"""
================================================================================
  AI Ethics Audit: Bias Analysis & Fairness Assessment
  Model: Logistic Regression trained on UCI Adult (Census) Income Dataset
  Author: AI Ethics Audit System
================================================================================
"""

import warnings
warnings.filterwarnings("ignore")

import os
import sys
# Force UTF-8 output on Windows to avoid cp1252 encoding errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_auc_score, roc_curve, ConfusionMatrixDisplay
)
from sklearn.pipeline import Pipeline

# -- Output directory ----------------------------------------------------------
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -- Colour palette ------------------------------------------------------------
PALETTE = {
    "primary":   "#6C63FF",
    "secondary": "#FF6584",
    "accent":    "#43E97B",
    "warning":   "#F7971E",
    "dark":      "#2D2B55",
    "light":     "#F8F9FA",
    "male":      "#4A90E2",
    "female":    "#E24A8A",
    "white":     "#5B8DEF",
    "nonwhite":  "#EF875B",
}

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
})

# ==============================================================================
# 1.  LOAD & PREPARE DATA
# ==============================================================================

def load_and_prepare_data():
    """Load UCI Adult dataset via URL and prepare it for analysis."""
    print("[1] Loading UCI Adult Income dataset ...")
    col_names = [
        "age", "workclass", "fnlwgt", "education", "education_num",
        "marital_status", "occupation", "relationship", "race", "sex",
        "capital_gain", "capital_loss", "hours_per_week",
        "native_country", "income"
    ]
    url = (
        "https://archive.ics.uci.edu/ml/machine-learning-databases"
        "/adult/adult.data"
    )
    try:
        df = pd.read_csv(url, header=None, names=col_names,
                         na_values=" ?", skipinitialspace=True)
        print("    -> Dataset loaded from URL.")
    except Exception:
        print("    -> URL unavailable - generating representative synthetic data ...")
        np.random.seed(42)
        n = 32_561
        df = pd.DataFrame({
            "age":           np.clip(np.random.normal(38, 13, n).astype(int), 17, 90),
            "workclass":     np.random.choice(
                ["Private","Self-emp-not-inc","Local-gov","State-gov",
                 "Self-emp-inc","Federal-gov","Without-pay"],
                n, p=[.69,.08,.065,.04,.035,.03,.01]),
            "fnlwgt":        np.random.randint(12_285, 1_484_705, n),
            "education":     np.random.choice(
                ["HS-grad","Some-college","Bachelors","Masters",
                 "Assoc-acdm","11th","Doctorate","Prof-school",
                 "9th","7th-8th"],
                n, p=[.32,.22,.16,.08,.07,.05,.02,.02,.04,.02]),
            "education_num": np.random.randint(1, 16, n),
            "marital_status":np.random.choice(
                ["Married-civ-spouse","Never-married","Divorced",
                 "Separated","Widowed"],
                n, p=[.46,.33,.13,.05,.03]),
            "occupation":    np.random.choice(
                ["Prof-specialty","Craft-repair","Exec-managerial",
                 "Adm-clerical","Sales","Other-service",
                 "Machine-op-inspct","Transport-moving",
                 "Handlers-cleaners","Farming-fishing"],
                n, p=[.13,.13,.12,.11,.11,.10,.07,.05,.04,.04]),
            "relationship":  np.random.choice(
                ["Husband","Not-in-family","Own-child",
                 "Unmarried","Wife","Other-relative"],
                n, p=[.40,.26,.19,.10,.04,.01]),
            "race":          np.random.choice(
                ["White","Black","Asian-Pac-Islander",
                 "Amer-Indian-Eskimo","Other"],
                n, p=[.855,.097,.032,.01,.006]),
            "sex":           np.random.choice(["Male","Female"], n, p=[.67,.33]),
            "capital_gain":  np.where(np.random.rand(n) < .08,
                                      np.random.randint(2_000, 99_999, n), 0),
            "capital_loss":  np.where(np.random.rand(n) < .05,
                                      np.random.randint(200, 4_356, n), 0),
            "hours_per_week":np.clip(np.random.normal(40, 12, n).astype(int), 1, 99),
            "native_country":"United-States",
            "income":        None,
        })
        log_odds = (
            -3.5
            + 0.03  * df["age"]
            + 0.15  * df["education_num"]
            + 0.008 * df["hours_per_week"]
            + 0.7   * (df["sex"] == "Male").astype(float)
            + 0.5   * (df["race"] == "White").astype(float)
            + 1.2   * (df["marital_status"] == "Married-civ-spouse").astype(float)
            + 0.003 * df["capital_gain"]
        )
        prob_high = 1 / (1 + np.exp(-log_odds))
        df["income"] = np.where(np.random.rand(n) < prob_high, ">50K", "<=50K")

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["income"] = df["income"].str.strip().str.rstrip(".")
    df["income_binary"] = (df["income"] == ">50K").astype(int)
    print(f"    -> Dataset shape: {df.shape}")
    return df


# ==============================================================================
# 2.  FAIRNESS METRICS
# ==============================================================================

def demographic_parity(y_pred, protected_col, positive_label=1):
    """P(Y_hat=1 | A=a) for each group a."""
    groups = protected_col.unique()
    rates = {}
    for g in groups:
        mask = protected_col == g
        rates[g] = y_pred[mask].mean()
    return rates


def equalized_odds(y_true, y_pred, protected_col):
    """TPR and FPR per group."""
    groups = protected_col.unique()
    result = {}
    for g in groups:
        mask = protected_col == g
        yt, yp = y_true[mask], y_pred[mask]
        tp = ((yt == 1) & (yp == 1)).sum()
        fn = ((yt == 1) & (yp == 0)).sum()
        fp = ((yt == 0) & (yp == 1)).sum()
        tn = ((yt == 0) & (yp == 0)).sum()
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        result[g] = {"TPR": tpr, "FPR": fpr}
    return result


def disparate_impact_ratio(rates_dict):
    """min_group_rate / max_group_rate (>= 0.8 passes the 80% rule)."""
    vals = list(rates_dict.values())
    return min(vals) / max(vals) if max(vals) > 0 else None


def predictive_parity(y_true, y_pred, protected_col):
    """Precision (PPV) per group."""
    groups = protected_col.unique()
    result = {}
    for g in groups:
        mask = protected_col == g
        yt, yp = y_true[mask], y_pred[mask]
        result[g] = float((yt[yp == 1]).mean()) if yp.sum() > 0 else 0.0
    return result


# ==============================================================================
# 3.  TRAIN MODEL
# ==============================================================================

def encode_and_split(df):
    cat_cols = ["workclass","education","marital_status","occupation",
                "relationship","race","sex","native_country"]
    df_enc = df.copy()
    for c in cat_cols:
        if c in df_enc.columns:
            df_enc[c] = LabelEncoder().fit_transform(df_enc[c].astype(str))

    feature_cols = ["age","workclass","fnlwgt","education","education_num",
                    "marital_status","occupation","relationship","race","sex",
                    "capital_gain","capital_loss","hours_per_week"]
    feature_cols = [c for c in feature_cols if c in df_enc.columns]

    X = df_enc[feature_cols]
    y = df_enc["income_binary"]
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_model(X_train, y_train):
    print("[2] Training Logistic Regression model ...")
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    LogisticRegression(max_iter=500, random_state=42))
    ])
    pipe.fit(X_train, y_train)
    return pipe


# ==============================================================================
# 4.  VISUALISATIONS
# ==============================================================================

def save(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"    -> Saved: {name}")
    return path


# -- 4a. Dataset demographic overview ------------------------------------------
def plot_demographic_overview(df):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Dataset Demographic Overview", fontsize=15, fontweight="bold", y=1.02)

    sex_counts = df["sex"].value_counts()
    axes[0].bar(sex_counts.index, sex_counts.values,
                color=[PALETTE["male"], PALETTE["female"]], edgecolor="white", linewidth=1.5)
    axes[0].set_title("Sex Distribution")
    axes[0].set_ylabel("Count")
    for i, v in enumerate(sex_counts.values):
        axes[0].text(i, v + 150, f"{v:,}", ha="center", fontweight="bold")

    race_counts = df["race"].value_counts()
    colors_race = [PALETTE["white"] if r == "White" else PALETTE["nonwhite"]
                   for r in race_counts.index]
    axes[1].barh(race_counts.index, race_counts.values, color=colors_race,
                 edgecolor="white", linewidth=1)
    axes[1].set_title("Race Distribution")
    axes[1].set_xlabel("Count")

    cross = df.groupby(["sex", "income"]).size().unstack(fill_value=0)
    cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100
    x = np.arange(len(cross_pct))
    width = 0.35
    bars1 = axes[2].bar(x - width/2, cross_pct["<=50K"],
                         width, label="<=50K", color=PALETTE["secondary"], alpha=0.85)
    bars2 = axes[2].bar(x + width/2, cross_pct[">50K"],
                         width, label=">50K", color=PALETTE["accent"], alpha=0.85)
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(cross_pct.index)
    axes[2].set_title("Income Distribution by Sex (%)")
    axes[2].set_ylabel("Percentage (%)")
    axes[2].legend()
    for bar in bars2:
        axes[2].text(bar.get_x() + bar.get_width()/2,
                      bar.get_height() + 0.5,
                      f"{bar.get_height():.1f}%", ha="center", fontsize=9)

    fig.tight_layout()
    return save(fig, "fig1_demographic_overview.png")


# -- 4b. Disparate impact ------------------------------------------------------
def plot_disparate_impact(rates_sex, rates_race):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Disparate Impact Analysis - Positive Prediction Rates",
                 fontsize=14, fontweight="bold")

    keys_s = list(rates_sex.keys())
    vals_s = [rates_sex[k] * 100 for k in keys_s]
    colors_s = [PALETTE["male"] if k == "Male" else PALETTE["female"] for k in keys_s]
    bars = axes[0].bar(keys_s, vals_s, color=colors_s, width=0.5, edgecolor="white")
    axes[0].axhline(y=max(vals_s) * 0.8, color=PALETTE["warning"],
                    linestyle="--", linewidth=2, label="80% Rule Threshold")
    axes[0].set_title("Positive Prediction Rate by Sex")
    axes[0].set_ylabel("P(Y_hat=1) %")
    axes[0].set_ylim(0, max(vals_s) * 1.3)
    axes[0].legend()
    for bar, v in zip(bars, vals_s):
        axes[0].text(bar.get_x() + bar.get_width()/2,
                      bar.get_height() + 0.5, f"{v:.1f}%", ha="center", fontweight="bold")

    top_races = dict(sorted(rates_race.items(), key=lambda x: -x[1])[:5])
    keys_r = list(top_races.keys())
    vals_r = [top_races[k] * 100 for k in keys_r]
    colors_r = [PALETTE["white"] if k == "White" else PALETTE["nonwhite"] for k in keys_r]
    bars2 = axes[1].bar(keys_r, vals_r, color=colors_r, width=0.5, edgecolor="white")
    axes[1].axhline(y=max(vals_r) * 0.8, color=PALETTE["warning"],
                    linestyle="--", linewidth=2, label="80% Rule Threshold")
    axes[1].set_title("Positive Prediction Rate by Race (Top 5)")
    axes[1].set_ylabel("P(Y_hat=1) %")
    axes[1].set_ylim(0, max(vals_r) * 1.35)
    axes[1].tick_params(axis="x", rotation=15)
    axes[1].legend()
    for bar, v in zip(bars2, vals_r):
        axes[1].text(bar.get_x() + bar.get_width()/2,
                      bar.get_height() + 0.3, f"{v:.1f}%", ha="center", fontsize=9)

    fig.tight_layout()
    return save(fig, "fig2_disparate_impact.png")


# -- 4c. Equalized Odds --------------------------------------------------------
def plot_equalized_odds(eq_odds_sex, eq_odds_race):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Equalized Odds - TPR & FPR per Group",
                 fontsize=14, fontweight="bold")

    for ax, eq_odds, title in zip(
        axes, [eq_odds_sex, eq_odds_race], ["Sex", "Race"]
    ):
        groups = list(eq_odds.keys())
        tprs = [eq_odds[g]["TPR"] * 100 for g in groups]
        fprs = [eq_odds[g]["FPR"] * 100 for g in groups]
        x = np.arange(len(groups))
        w = 0.35
        ax.bar(x - w/2, tprs, w, label="TPR (Recall)",
               color=PALETTE["primary"], alpha=0.85, edgecolor="white")
        ax.bar(x + w/2, fprs, w, label="FPR",
               color=PALETTE["secondary"], alpha=0.85, edgecolor="white")
        ax.set_xticks(x)
        ax.set_xticklabels(groups, rotation=15, ha="right")
        ax.set_title(f"Equalized Odds by {title}")
        ax.set_ylabel("Rate (%)")
        ax.legend()
        ax.set_ylim(0, max(tprs + fprs) * 1.25)

    fig.tight_layout()
    return save(fig, "fig3_equalized_odds.png")


# -- 4d. Confusion matrices ----------------------------------------------------
def plot_confusion_matrices(df_test, y_pred, protected_col="sex"):
    groups = df_test[protected_col].unique()
    fig, axes = plt.subplots(1, len(groups), figsize=(6 * len(groups), 5))
    fig.suptitle(f"Confusion Matrices by {protected_col.title()}",
                 fontsize=14, fontweight="bold")
    if len(groups) == 1:
        axes = [axes]

    for ax, grp in zip(axes, groups):
        mask = df_test[protected_col] == grp
        yt = df_test.loc[mask, "income_binary"]
        yp = y_pred[mask]
        cm = confusion_matrix(yt, yp)
        disp = ConfusionMatrixDisplay(cm, display_labels=["<=50K", ">50K"])
        disp.plot(ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(f"{protected_col.title()} = {grp}", fontsize=12, fontweight="bold")

    fig.tight_layout()
    return save(fig, "fig4_confusion_matrices.png")


# -- 4e. ROC curves by group ---------------------------------------------------
def plot_roc_by_group(df_test, y_prob, protected_col="sex"):
    groups = df_test[protected_col].unique()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0,1],[0,1], "k--", alpha=0.4, label="Random")

    color_cycle = [PALETTE["primary"], PALETTE["secondary"],
                   PALETTE["accent"], PALETTE["warning"],
                   "#A29BFE", "#FD79A8"]
    for i, grp in enumerate(groups):
        mask = df_test[protected_col] == grp
        yt   = df_test.loc[mask, "income_binary"]
        yp   = y_prob[mask]
        if yt.nunique() < 2:
            continue
        fpr, tpr, _ = roc_curve(yt, yp)
        auc = roc_auc_score(yt, yp)
        ax.plot(fpr, tpr, linewidth=2.5,
                color=color_cycle[i % len(color_cycle)],
                label=f"{grp}  (AUC = {auc:.3f})")

    ax.set_title(f"ROC Curves by {protected_col.title()}", fontsize=14, fontweight="bold")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    ax.fill_between([0,1],[0,1], alpha=0.05, color="grey")
    fig.tight_layout()
    return save(fig, f"fig5_roc_{protected_col}.png")


# -- 4f. Fairness heatmap ------------------------------------------------------
def plot_fairness_summary(metrics_df):
    fig, ax = plt.subplots(figsize=(10, 5))
    cmap = sns.diverging_palette(10, 133, as_cmap=True)
    sns.heatmap(metrics_df, annot=True, fmt=".3f", cmap=cmap,
                center=0.5, linewidths=0.5, ax=ax,
                cbar_kws={"label": "Metric Value"})
    ax.set_title("Fairness Metrics Summary Heatmap", fontsize=14, fontweight="bold")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Group")
    fig.tight_layout()
    return save(fig, "fig6_fairness_heatmap.png")


# -- 4g. Age & Education -------------------------------------------------------
def plot_age_education_income(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for income_val, color in [("<=50K", PALETTE["secondary"]), (">50K", PALETTE["accent"])]:
        subset = df[df["income"] == income_val]["age"]
        axes[0].hist(subset, bins=30, alpha=0.6, color=color,
                     label=income_val, edgecolor="white", density=True)
    axes[0].set_title("Age Distribution by Income Group")
    axes[0].set_xlabel("Age")
    axes[0].set_ylabel("Density")
    axes[0].legend()

    edu_order = (
        df[df["income"] == ">50K"]
        .groupby("education").size()
        .div(df.groupby("education").size())
        .sort_values(ascending=False)
        .index.tolist()
    )
    edu_rates = (
        df[df["income"] == ">50K"]
        .groupby("education").size()
        .div(df.groupby("education").size())
        .reindex(edu_order) * 100
    )
    axes[1].barh(edu_rates.index, edu_rates.values,
                 color=PALETTE["primary"], edgecolor="white")
    axes[1].axvline(x=25, color=PALETTE["warning"], linestyle="--",
                    linewidth=2, label="25% Reference")
    axes[1].set_title("High Income Rate (>50K) by Education Level")
    axes[1].set_xlabel("% with Income >50K")
    axes[1].legend()

    fig.tight_layout()
    return save(fig, "fig7_age_education_income.png")


# -- 4h. Feature importance ----------------------------------------------------
def plot_feature_importance(model, feature_names):
    try:
        coefs = model.named_steps["clf"].coef_[0]
    except Exception:
        return None
    importance = pd.Series(np.abs(coefs), index=feature_names).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [PALETTE["secondary"] if v > importance.median() else PALETTE["primary"]
              for v in importance]
    importance.plot(kind="barh", ax=ax, color=colors, edgecolor="white")
    ax.set_title("Logistic Regression Feature Importance (|Coefficient|)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Absolute Coefficient Value")
    high_patch = mpatches.Patch(color=PALETTE["secondary"], label="High Importance")
    low_patch  = mpatches.Patch(color=PALETTE["primary"],   label="Lower Importance")
    ax.legend(handles=[high_patch, low_patch])
    fig.tight_layout()
    return save(fig, "fig8_feature_importance.png")


# -- 4i. Intersectional bias ---------------------------------------------------
def plot_intersectional_bias(df_test, y_pred):
    df_temp = df_test[["sex", "race", "income_binary"]].copy()
    df_temp["predicted"] = y_pred
    df_temp["race_grp"] = df_temp["race"].apply(
        lambda r: "White" if r == "White" else "Non-White"
    )
    cross = df_temp.groupby(["sex", "race_grp"])["predicted"].mean() * 100
    cross_df = cross.unstack()

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(cross_df.index))
    w = 0.35
    colors_r = [PALETTE["white"], PALETTE["nonwhite"]]
    for i, col in enumerate(cross_df.columns):
        offset = (i - 0.5) * w
        bars = ax.bar(x + offset, cross_df[col], w,
                      label=col, color=colors_r[i], edgecolor="white", alpha=0.9)
        for bar, val in zip(bars, cross_df[col]):
            ax.text(bar.get_x() + bar.get_width()/2,
                     bar.get_height() + 0.5,
                     f"{val:.1f}%", ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(cross_df.index)
    ax.set_title("Intersectional Bias: Positive Prediction Rate (Race x Sex)",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("% Predicted High Income (>50K)")
    ax.legend(title="Race Group")
    ax.set_ylim(0, cross_df.values.max() * 1.3)
    fig.tight_layout()
    return save(fig, "fig9_intersectional_bias.png")


# ==============================================================================
# 5.  MAIN AUDIT PIPELINE
# ==============================================================================

def run_audit():
    print("\n" + "="*70)
    print("  AI ETHICS AUDIT - Starting Full Pipeline")
    print("="*70 + "\n")

    df = load_and_prepare_data()

    X_train, X_test, y_train, y_test = encode_and_split(df)
    model = train_model(X_train, y_train)

    print("[3] Evaluating model ...")
    y_pred  = model.predict(X_test)
    y_prob  = model.predict_proba(X_test)[:, 1]
    acc     = accuracy_score(y_test, y_pred)
    auc     = roc_auc_score(y_test, y_prob)
    print(f"    -> Accuracy : {acc:.4f}")
    print(f"    -> ROC-AUC  : {auc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["<=50K", ">50K"]))

    df_test = df.loc[X_test.index].copy()
    df_test["income_binary"] = y_test.values
    df_test["y_pred"]  = y_pred
    df_test["y_prob"]  = y_prob

    print("[4] Computing fairness metrics ...")

    rates_sex  = demographic_parity(pd.Series(y_pred, index=X_test.index), df_test["sex"])
    rates_race = demographic_parity(pd.Series(y_pred, index=X_test.index), df_test["race"])
    eq_odds_sex  = equalized_odds(y_test.values, y_pred, df_test["sex"].reset_index(drop=True))
    eq_odds_race = equalized_odds(y_test.values, y_pred, df_test["race"].reset_index(drop=True))
    ppv_sex  = predictive_parity(y_test.values, y_pred, df_test["sex"].reset_index(drop=True))
    ppv_race = predictive_parity(y_test.values, y_pred, df_test["race"].reset_index(drop=True))

    di_sex  = disparate_impact_ratio(rates_sex)
    di_race = disparate_impact_ratio(rates_race)

    print("\n  -- Demographic Parity (Sex) --")
    for k, v in rates_sex.items():
        print(f"     {k}: {v:.4f} ({v*100:.1f}%)")
    status_sex = "PASS (>=0.8)" if di_sex >= 0.8 else "FAIL (<0.8)"
    print(f"  Disparate Impact Ratio (Sex): {di_sex:.4f}  [{status_sex}]")

    print("\n  -- Demographic Parity (Race) --")
    for k, v in sorted(rates_race.items(), key=lambda x: -x[1]):
        print(f"     {k}: {v:.4f} ({v*100:.1f}%)")
    status_race = "PASS (>=0.8)" if di_race >= 0.8 else "FAIL (<0.8)"
    print(f"  Disparate Impact Ratio (Race): {di_race:.4f}  [{status_race}]")

    print("\n  -- Equalized Odds (Sex) --")
    for k, v in eq_odds_sex.items():
        print(f"     {k}: TPR={v['TPR']:.3f}  FPR={v['FPR']:.3f}")

    print("\n  -- Predictive Parity (Sex PPV) --")
    for k, v in ppv_sex.items():
        print(f"     {k}: PPV={v:.3f}")

    # Build metrics summary DataFrame
    metrics_rows = {}
    for grp in ["Male", "Female"]:
        if grp in rates_sex:
            metrics_rows[f"Sex:{grp}"] = {
                "Dem. Parity": rates_sex.get(grp, 0),
                "TPR":         eq_odds_sex.get(grp, {}).get("TPR", 0),
                "FPR":         eq_odds_sex.get(grp, {}).get("FPR", 0),
                "PPV":         ppv_sex.get(grp, 0),
            }
    for grp in df_test["race"].unique():
        metrics_rows[f"Race:{grp}"] = {
            "Dem. Parity": rates_race.get(grp, 0),
            "TPR":         (eq_odds_race.get(grp) or {}).get("TPR", 0),
            "FPR":         (eq_odds_race.get(grp) or {}).get("FPR", 0),
            "PPV":         ppv_race.get(grp, 0),
        }
    metrics_df = pd.DataFrame(metrics_rows).T

    print("\n[5] Generating visualisations ...")
    paths = {}
    paths["demographic"]      = plot_demographic_overview(df)
    paths["disparate_impact"] = plot_disparate_impact(rates_sex, rates_race)
    paths["equalized_odds"]   = plot_equalized_odds(eq_odds_sex, eq_odds_race)
    paths["confusion"]        = plot_confusion_matrices(df_test, y_pred, "sex")
    paths["roc_sex"]          = plot_roc_by_group(df_test, y_prob, "sex")
    paths["roc_race"]         = plot_roc_by_group(df_test, y_prob, "race")
    paths["fairness_heatmap"] = plot_fairness_summary(metrics_df)
    paths["age_edu"]          = plot_age_education_income(df)
    feat_cols = ["age","workclass","fnlwgt","education","education_num",
                 "marital_status","occupation","relationship","race","sex",
                 "capital_gain","capital_loss","hours_per_week"]
    feat_cols = [c for c in feat_cols if c in X_train.columns]
    paths["feat_imp"]         = plot_feature_importance(model, feat_cols)
    paths["intersectional"]   = plot_intersectional_bias(df_test, y_pred)

    csv_path = os.path.join(OUTPUT_DIR, "fairness_metrics_summary.csv")
    metrics_df.to_csv(csv_path)
    print(f"\n[6] Fairness metrics saved -> {csv_path}")

    results = {
        "accuracy": acc, "auc": auc,
        "di_sex": di_sex, "di_race": di_race,
        "rates_sex": rates_sex, "rates_race": rates_race,
        "eq_odds_sex": eq_odds_sex, "eq_odds_race": eq_odds_race,
        "ppv_sex": ppv_sex, "ppv_race": ppv_race,
        "metrics_df": metrics_df,
        "paths": paths,
        "df_shape": df.shape,
    }
    print("\n[OK] Analysis complete. Proceeding to PDF report generation ...\n")
    return results


if __name__ == "__main__":
    run_audit()
