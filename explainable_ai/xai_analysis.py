"""
=============================================================================
Explainable AI (XAI) Analysis
=============================================================================
Dataset     : Breast Cancer Wisconsin (Diagnostic) - scikit-learn built-in
Model       : Random Forest Classifier + Gradient Boosting Classifier
XAI Methods : SHAP, LIME, Permutation Feature Importance, Partial Dependence
Author      : XAI Assignment
=============================================================================
"""

# ── Core Imports ──────────────────────────────────────────────────────────────
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless backend for saving figures
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (RandomForestClassifier,
                               GradientBoostingClassifier)
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, ConfusionMatrixDisplay)
from sklearn.inspection import permutation_importance, PartialDependenceDisplay
import shap
import lime
import lime.lime_tabular

warnings.filterwarnings("ignore")

# ── Global Style ──────────────────────────────────────────────────────────────
PALETTE   = ["#6C63FF", "#FF6584", "#43B89C", "#F5A623", "#E74C3C"]
BG_COLOR  = "#0D1117"
GRID_COLOR = "#21262D"
TEXT_COLOR = "#E6EDF3"
ACCENT    = "#6C63FF"

plt.rcParams.update({
    "figure.facecolor":  BG_COLOR,
    "axes.facecolor":    "#161B22",
    "axes.edgecolor":    GRID_COLOR,
    "axes.labelcolor":   TEXT_COLOR,
    "xtick.color":       TEXT_COLOR,
    "ytick.color":       TEXT_COLOR,
    "text.color":        TEXT_COLOR,
    "grid.color":        GRID_COLOR,
    "grid.alpha":        0.4,
    "axes.grid":         True,
    "font.family":       "DejaVu Sans",
    "font.size":         10,
})

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def savefig(name, dpi=150):
    path = os.path.join(OUT_DIR, name)
    plt.savefig(path, dpi=dpi, bbox_inches="tight",
                facecolor=BG_COLOR, edgecolor="none")
    plt.close("all")
    print(f"  [OK] Saved: {path}")
    return path


# =============================================================================
# 1. DATA LOADING & PREPROCESSING
# =============================================================================
print("\n[1/7] Loading dataset...")
data   = load_breast_cancer()
X      = pd.DataFrame(data.data, columns=data.feature_names)
y      = pd.Series(data.target, name="target")   # 0=malignant, 1=benign

print(f"      Shape: {X.shape}  |  Classes: {dict(zip(data.target_names, np.bincount(y)))}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

scaler   = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

X_train_s = pd.DataFrame(X_train_s, columns=X.columns)
X_test_s  = pd.DataFrame(X_test_s,  columns=X.columns)


# =============================================================================
# 2. MODEL TRAINING
# =============================================================================
print("\n[2/7] Training models...")
rf  = RandomForestClassifier(n_estimators=200, max_depth=6,
                              random_state=42, n_jobs=-1)
gb  = GradientBoostingClassifier(n_estimators=200, max_depth=4,
                                  learning_rate=0.05, random_state=42)

rf.fit(X_train_s, y_train)
gb.fit(X_train_s, y_train)

for name, mdl in [("Random Forest", rf), ("Gradient Boosting", gb)]:
    cv  = cross_val_score(mdl, X_train_s, y_train, cv=5, scoring="roc_auc")
    auc = roc_auc_score(y_test, mdl.predict_proba(X_test_s)[:, 1])
    print(f"      {name}  |  CV AUC: {cv.mean():.4f} ± {cv.std():.4f}  |  Test AUC: {auc:.4f}")


# =============================================================================
# 3. FIGURE 1 – Dataset Overview
# =============================================================================
print("\n[3/7] Figure 1 - Dataset overview...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Breast Cancer Dataset Overview", fontsize=14,
             color=TEXT_COLOR, weight="bold", y=1.02)

# Class distribution
ax = axes[0]
counts = y.value_counts()
bars = ax.bar(data.target_names, counts.values,
              color=[PALETTE[1], PALETTE[0]], edgecolor="none", width=0.5)
for bar, v in zip(bars, counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            str(v), ha="center", color=TEXT_COLOR, fontsize=11)
ax.set_title("Class Distribution", color=TEXT_COLOR, weight="bold")
ax.set_ylabel("Count", color=TEXT_COLOR)

# Feature correlation heatmap (top 10 features)
ax = axes[1]
top10 = X.columns[:10]
corr  = X[top10].corr()
cmap  = LinearSegmentedColormap.from_list("xai", ["#FF6584", "#0D1117", "#6C63FF"])
im    = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(10)); ax.set_yticks(range(10))
ax.set_xticklabels([c.replace(" ", "\n") for c in top10], fontsize=6)
ax.set_yticklabels(top10, fontsize=6)
ax.set_title("Feature Correlation (top 10)", color=TEXT_COLOR, weight="bold")
plt.colorbar(im, ax=ax, shrink=0.8)

# Distribution of a key feature
ax = axes[2]
for cls, lbl, col in zip([0, 1], data.target_names, PALETTE[1::-1]):
    ax.hist(X["mean radius"][y == cls], bins=25, alpha=0.7,
            label=lbl, color=col, edgecolor="none")
ax.set_title("Mean Radius Distribution", color=TEXT_COLOR, weight="bold")
ax.set_xlabel("Mean Radius", color=TEXT_COLOR)
ax.set_ylabel("Frequency", color=TEXT_COLOR)
ax.legend(facecolor="#161B22", edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)

plt.tight_layout()
savefig("fig1_dataset_overview.png")


# =============================================================================
# 4. FIGURE 2 – Built-in & Permutation Feature Importance
# =============================================================================
print("\n[4/7] Figure 2 - Feature importance...")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Feature Importance Analysis – Random Forest", fontsize=14,
             color=TEXT_COLOR, weight="bold")

# 4a. Built-in (MDI) importance
imp_df = pd.DataFrame({"feature": X.columns,
                        "importance": rf.feature_importances_}) \
           .sort_values("importance", ascending=True).tail(15)

ax = axes[0]
colors_bar = [PALETTE[0] if v > imp_df["importance"].median() else PALETTE[2]
              for v in imp_df["importance"]]
ax.barh(imp_df["feature"], imp_df["importance"],
        color=colors_bar, edgecolor="none")
ax.set_xlabel("Mean Decrease in Impurity (MDI)", color=TEXT_COLOR)
ax.set_title("Built-in Feature Importance (Top 15)", color=TEXT_COLOR, weight="bold")

# 4b. Permutation importance
perm = permutation_importance(rf, X_test_s, y_test,
                               n_repeats=20, random_state=42, n_jobs=-1)
perm_df = pd.DataFrame({"feature": X.columns,
                         "mean": perm.importances_mean,
                         "std":  perm.importances_std}) \
            .sort_values("mean", ascending=True).tail(15)

ax = axes[1]
ax.barh(perm_df["feature"], perm_df["mean"],
        xerr=perm_df["std"], color=PALETTE[3],
        edgecolor="none", capsize=3, ecolor="#888")
ax.set_xlabel("Decrease in AUC Score", color=TEXT_COLOR)
ax.set_title("Permutation Feature Importance (Top 15)", color=TEXT_COLOR, weight="bold")

plt.tight_layout()
savefig("fig2_feature_importance.png")


# =============================================================================
# 5. FIGURE 3-5 - SHAP Analysis
# =============================================================================
print("\n[5/7] Figure 3-5 - SHAP analysis...")

explainer_rf = shap.TreeExplainer(rf)
shap_vals_rf = explainer_rf.shap_values(X_test_s)

# Handle both old (list) and new (3D ndarray) SHAP API for binary classification
if isinstance(shap_vals_rf, list):
    sv_benign = shap_vals_rf[1]   # old API: list[class0, class1]
elif isinstance(shap_vals_rf, np.ndarray) and shap_vals_rf.ndim == 3:
    sv_benign = shap_vals_rf[:, :, 1]   # new API: (n_samples, n_features, n_classes)
else:
    sv_benign = shap_vals_rf  # fallback for single-output

print(f"      SHAP values shape: {np.array(sv_benign).shape}")

# Fig 3 - SHAP Summary (beeswarm)
print("      -> SHAP summary plot...")
plt.figure(figsize=(10, 8), facecolor=BG_COLOR)
shap.summary_plot(sv_benign, X_test_s, show=False,
                  color_bar=True, plot_size=None)
plt.title("SHAP Summary Plot - Random Forest (Benign class)",
          color=TEXT_COLOR, fontsize=13, weight="bold", pad=12)
plt.gca().set_facecolor("#161B22")
plt.gcf().set_facecolor(BG_COLOR)
plt.tight_layout()
savefig("fig3_shap_summary.png")

# Fig 4 - SHAP Bar (global importance)
print("      -> SHAP global importance...")
plt.figure(figsize=(10, 6), facecolor=BG_COLOR)
shap.summary_plot(sv_benign, X_test_s, plot_type="bar", show=False)
plt.title("SHAP Global Feature Importance - Random Forest",
          color=TEXT_COLOR, fontsize=13, weight="bold", pad=12)
plt.gca().set_facecolor("#161B22")
plt.gcf().set_facecolor(BG_COLOR)
plt.tight_layout()
savefig("fig4_shap_global.png")

# Fig 5 - SHAP Dependence Plot (top feature)
# sv_benign is now guaranteed 2D: (n_samples, n_features)
sv_2d = np.array(sv_benign)  # ensure numpy array
top_feat = X.columns[np.abs(sv_2d).mean(axis=0).argmax()]
print(f"      -> SHAP dependence plot (feature: {top_feat})...")
plt.figure(figsize=(9, 6), facecolor=BG_COLOR)
shap.dependence_plot(top_feat, sv_2d, X_test_s,
                     interaction_index="auto", show=False,
                     dot_size=30, alpha=0.7)
plt.title(f"SHAP Dependence Plot: {top_feat}",
          color=TEXT_COLOR, fontsize=13, weight="bold", pad=12)
plt.gca().set_facecolor("#161B22")
plt.gcf().set_facecolor(BG_COLOR)
plt.tight_layout()
savefig("fig5_shap_dependence.png")

# Fig 5b - SHAP Waterfall for single prediction
print("      -> SHAP waterfall (single instance)...")
try:
    # Use the shap.Explanation object approach (newer API)
    exp_obj = shap.TreeExplainer(rf)(X_test_s)
    mal_idx = np.where(rf.predict(X_test_s) == 0)[0][0]
    plt.figure(figsize=(10, 6), facecolor=BG_COLOR)
    # Handle 3D Explanation objects
    if exp_obj.values.ndim == 3:
        exp_slice = shap.Explanation(
            values=exp_obj.values[mal_idx, :, 1],
            base_values=exp_obj.base_values[mal_idx, 1],
            data=exp_obj.data[mal_idx],
            feature_names=list(X.columns)
        )
    else:
        exp_slice = exp_obj[mal_idx]
    shap.plots.waterfall(exp_slice, max_display=12, show=False)
except Exception as e:
    print(f"      Waterfall via Explanation failed ({e}), using force_plot fallback...")
    mal_idx = np.where(rf.predict(X_test_s) == 0)[0][0]
    plt.figure(figsize=(10, 6), facecolor=BG_COLOR)
    ax = plt.gca()
    # Manual waterfall-style bar chart as fallback
    feat_shap = sv_2d[mal_idx]
    top_idx   = np.argsort(np.abs(feat_shap))[-12:]
    top_names = [X.columns[i] for i in top_idx]
    top_vals  = feat_shap[top_idx]
    bar_colors = [PALETTE[0] if v > 0 else PALETTE[1] for v in top_vals]
    ax.barh(top_names, top_vals, color=bar_colors, edgecolor="none")
    ax.axvline(0, color=TEXT_COLOR, linewidth=0.8, alpha=0.5)
    ax.set_xlabel("SHAP value (impact on prediction)", color=TEXT_COLOR)

plt.title("SHAP Waterfall Plot - Predicted Malignant Instance",
          color=TEXT_COLOR, fontsize=12, weight="bold")
plt.gcf().set_facecolor(BG_COLOR)
plt.gca().set_facecolor("#161B22")
plt.tight_layout()
savefig("fig5b_shap_waterfall.png")



# =============================================================================
# 6. FIGURE 6-7 – LIME Analysis
# =============================================================================
print("\n[6/7] Figure 6-7 - LIME analysis...")

lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    X_train_s.values,
    feature_names=list(X.columns),
    class_names=list(data.target_names),
    mode="classification",
    discretize_continuous=True,
    random_state=42
)

def lime_explain_instance(idx, title_suffix=""):
    """Return LIME explanation for test instance idx."""
    exp = lime_explainer.explain_instance(
        X_test_s.values[idx],
        rf.predict_proba,
        num_features=12,
        top_labels=1
    )
    return exp

# Fig 6 – LIME explanation for a Benign prediction
ben_idx = np.where(rf.predict(X_test_s) == 1)[0][2]
exp_ben  = lime_explain_instance(ben_idx)

fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_COLOR)
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor("#161B22")

feat_vals = exp_ben.as_list(label=1)
feats  = [f[0] for f in feat_vals]
values = [f[1] for f in feat_vals]
colors = [PALETTE[0] if v > 0 else PALETTE[1] for v in values]
y_pos  = range(len(feats))

ax.barh(y_pos, values, color=colors, edgecolor="none", height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(feats, fontsize=8)
ax.axvline(0, color=TEXT_COLOR, linewidth=0.8, alpha=0.5)
ax.set_xlabel("LIME Weight (positive = Benign)", color=TEXT_COLOR)
ax.set_title(f"LIME Explanation – Benign Prediction (instance #{ben_idx})",
             color=TEXT_COLOR, fontsize=12, weight="bold")

# Prediction probabilities annotation
probs = rf.predict_proba(X_test_s.iloc[[ben_idx]])[0]
ax.text(0.99, 0.02,
        f"P(Malignant)={probs[0]:.3f}\nP(Benign)={probs[1]:.3f}",
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=10, color=PALETTE[2],
        bbox=dict(facecolor="#161B22", edgecolor=ACCENT, boxstyle="round,pad=0.4"))

plt.tight_layout()
savefig("fig6_lime_benign.png")

# Fig 7 - LIME explanation for a Malignant prediction
mal_idx2 = np.where(rf.predict(X_test_s) == 0)[0][1]
exp_mal   = lime_explain_instance(mal_idx2)

fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_COLOR)
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor("#161B22")

# Use the top predicted label (may be 0 for malignant instance)
mal_label = exp_mal.top_labels[0]
feat_vals = exp_mal.as_list(label=mal_label)
feats  = [f[0] for f in feat_vals]
values = [f[1] for f in feat_vals]
# Flip sign if label is malignant (0) so positive = toward malignant
if mal_label == 0:
    values = [-v for v in values]
colors = [PALETTE[1] if v > 0 else PALETTE[0] for v in values]
y_pos  = range(len(feats))

ax.barh(y_pos, values, color=colors, edgecolor="none", height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(feats, fontsize=8)
ax.axvline(0, color=TEXT_COLOR, linewidth=0.8, alpha=0.5)
ax.set_xlabel("LIME Weight (positive = toward Malignant)", color=TEXT_COLOR)
ax.set_title(f"LIME Explanation - Malignant Prediction (instance #{mal_idx2})",
             color=TEXT_COLOR, fontsize=12, weight="bold")

probs = rf.predict_proba(X_test_s.iloc[[mal_idx2]])[0]
ax.text(0.99, 0.02,
        f"P(Malignant)={probs[0]:.3f}\nP(Benign)={probs[1]:.3f}",
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=10, color=PALETTE[1],
        bbox=dict(facecolor="#161B22", edgecolor=PALETTE[1], boxstyle="round,pad=0.4"))

plt.tight_layout()
savefig("fig7_lime_malignant.png")



# =============================================================================
# 7. FIGURE 8 – Confusion Matrix & Model Performance Summary
# =============================================================================
print("\n[7/7] Figure 8 - Performance summary...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Model Performance Summary", fontsize=14,
             color=TEXT_COLOR, weight="bold")

for ax, (name, mdl) in zip(axes, [("Random Forest", rf),
                                    ("Gradient Boosting", gb)]):
    cm  = confusion_matrix(y_test, mdl.predict(X_test_s))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                  display_labels=data.target_names)
    cmap_cm = LinearSegmentedColormap.from_list("cm", ["#0D1117", ACCENT])
    disp.plot(ax=ax, cmap=cmap_cm, colorbar=False)
    ax.set_title(name, color=TEXT_COLOR, weight="bold")
    ax.set_facecolor("#161B22")
    for text in ax.texts:
        text.set_color(TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)

plt.tight_layout()
savefig("fig8_confusion_matrix.png")

print("\n" + "="*60)
print("  ALL FIGURES SAVED SUCCESSFULLY")
print("="*60)

# Print final metrics table
print("\n-- Classification Reports --")
for name, mdl in [("Random Forest", rf), ("Gradient Boosting", gb)]:
    print(f"\n{name}:")
    print(classification_report(y_test, mdl.predict(X_test_s),
                                 target_names=data.target_names))
