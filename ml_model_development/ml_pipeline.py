# -*- coding: utf-8 -*-
"""
=============================================================================
  Machine Learning Pipeline: Random Forest Classifier
  Dataset   : Breast Cancer Wisconsin (Diagnostic) – sklearn built-in
  Author    : ML Model Development Project
  Date      : 2026-05-25
=============================================================================

Pipeline overview
-----------------
1. Data Loading & Exploration
2. Preprocessing (scaling, train/test split)
3. Baseline Model Training
4. Hyperparameter Tuning (GridSearchCV)
5. Model Evaluation (Accuracy, Precision, Recall, F1, ROC-AUC)
6. Visualisations (Confusion Matrix, ROC Curve, Feature Importance, Learning Curve)
7. Results summary saved to results/
"""

# ---------------------------------------------------------------------------
# 0. Imports
# ---------------------------------------------------------------------------
import os
import sys
import warnings

# Force UTF-8 output so Unicode chars print correctly on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # non-interactive backend – safe for scripts
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets       import load_breast_cancer
from sklearn.model_selection import (
    train_test_split, GridSearchCV, StratifiedKFold, learning_curve
)
from sklearn.preprocessing  import StandardScaler
from sklearn.ensemble       import RandomForestClassifier
from sklearn.metrics        import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, roc_curve,
    confusion_matrix, classification_report
)
from sklearn.pipeline       import Pipeline

warnings.filterwarnings("ignore")
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Create output directories
os.makedirs("results/figures", exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Data Loading & Exploration
# ---------------------------------------------------------------------------
print("=" * 70)
print("STEP 1 – Data Loading & Exploration")
print("=" * 70)

# Load the Breast Cancer Wisconsin dataset
data   = load_breast_cancer()
X      = pd.DataFrame(data.data, columns=data.feature_names)
y      = pd.Series(data.target, name="target")          # 0 = malignant, 1 = benign

print(f"\nDataset shape   : {X.shape}")
print(f"Feature count   : {X.shape[1]}")
print(f"Classes         : {data.target_names.tolist()}  ->  {dict(zip([0,1], data.target_names))}") 
print(f"Class balance   :\n{y.value_counts().rename({0:'malignant', 1:'benign'}).to_string()}")
print(f"\nMissing values  : {X.isnull().sum().sum()}")
print(f"\nDescriptive statistics (first 6 features):")
print(X.iloc[:, :6].describe().round(3).to_string())

# Save dataset summary
summary_df = X.describe().T
summary_df.to_csv("results/dataset_summary.csv")
print("[OK] dataset_summary.csv saved.")

# ---------------------------------------------------------------------------
# 2. Preprocessing
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 2 – Preprocessing")
print("=" * 70)

# Stratified split to preserve class ratio
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
)

print(f"\nTraining samples : {X_train.shape[0]}")
print(f"Test samples     : {X_test.shape[0]}")
print(f"Train class dist : {y_train.value_counts().to_dict()}")
print(f"Test  class dist : {y_test.value_counts().to_dict()}")

# StandardScaler – zero mean, unit variance
scaler  = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)
print("[OK] Features scaled with StandardScaler.")

# ---------------------------------------------------------------------------
# 3. Baseline Model Training
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 3 – Baseline Random Forest (default hyperparameters)")
print("=" * 70)

base_rf = RandomForestClassifier(random_state=RANDOM_STATE)
base_rf.fit(X_train_s, y_train)

y_pred_base = base_rf.predict(X_test_s)
y_prob_base = base_rf.predict_proba(X_test_s)[:, 1]

def evaluate(y_true, y_pred, y_prob, label="Model"):
    """Print and return a dict of evaluation metrics."""
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec  = recall_score(y_true, y_pred)
    f1   = f1_score(y_true, y_pred)
    auc  = roc_auc_score(y_true, y_prob)
    print(f"\n--- {label} ---")
    print(f"  Accuracy  : {acc:.4f}")
    print(f"  Precision : {prec:.4f}")
    print(f"  Recall    : {rec:.4f}")
    print(f"  F1-Score  : {f1:.4f}")
    print(f"  ROC-AUC   : {auc:.4f}")
    return dict(model=label, accuracy=acc, precision=prec,
                recall=rec, f1=f1, roc_auc=auc)

baseline_metrics = evaluate(y_test, y_pred_base, y_prob_base, "Baseline RF")

# ---------------------------------------------------------------------------
# 4. Hyperparameter Tuning (GridSearchCV)
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 4 – Hyperparameter Tuning with GridSearchCV")
print("=" * 70)

param_grid = {
    "n_estimators"      : [50, 100, 200],
    "max_depth"         : [None, 10, 20],
    "min_samples_split" : [2, 5, 10],
    "min_samples_leaf"  : [1, 2, 4],
    "max_features"      : ["sqrt", "log2"],
}

total_combos = (
    len(param_grid["n_estimators"])
    * len(param_grid["max_depth"])
    * len(param_grid["min_samples_split"])
    * len(param_grid["min_samples_leaf"])
    * len(param_grid["max_features"])
)
print(f"\nTotal parameter combinations to evaluate : {total_combos}")
print("Running 5-fold Stratified CV … (this may take ~2–3 min)")

cv      = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
grid_rf = GridSearchCV(
    estimator  = RandomForestClassifier(random_state=RANDOM_STATE),
    param_grid = param_grid,
    scoring    = "f1",
    cv         = cv,
    n_jobs     = -1,
    verbose    = 1,
    refit      = True,
)
grid_rf.fit(X_train_s, y_train)

print(f"\n[✓] Best CV F1-Score : {grid_rf.best_score_:.4f}")
print(f"    Best Parameters  :\n")
for k, v in grid_rf.best_params_.items():
    print(f"      {k:25s}: {v}")

# Save CV results
cv_results_df = pd.DataFrame(grid_rf.cv_results_)
cv_results_df.to_csv("results/cv_results.csv", index=False)
print("[OK] cv_results.csv saved.")

# ---------------------------------------------------------------------------
# 5. Model Evaluation – Tuned Model
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 5 – Evaluating Tuned Model on Held-Out Test Set")
print("=" * 70)

best_rf     = grid_rf.best_estimator_
y_pred_best = best_rf.predict(X_test_s)
y_prob_best = best_rf.predict_proba(X_test_s)[:, 1]

tuned_metrics = evaluate(y_test, y_pred_best, y_prob_best, "Tuned RF")

print("\n--- Detailed Classification Report ---")
print(classification_report(y_test, y_pred_best,
                             target_names=data.target_names))

# Comparison table
comparison = pd.DataFrame([baseline_metrics, tuned_metrics]).set_index("model")
comparison.to_csv("results/model_comparison.csv")
print("\n--- Baseline vs Tuned Comparison ---")
print(comparison.round(4).to_string())
print("[OK] model_comparison.csv saved.")

# ---------------------------------------------------------------------------
# 6. Visualisations
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 6 – Generating Visualisations")
print("=" * 70)

sns.set_theme(style="whitegrid", palette="deep")
FIG_SIZE = (8, 6)

# ── 6a. Confusion Matrix ──────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, y_pred, title in zip(
    axes,
    [y_pred_base, y_pred_best],
    ["Baseline Random Forest", "Tuned Random Forest"],
):
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=data.target_names,
        yticklabels=data.target_names,
        ax=ax
    )
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")

plt.suptitle("Confusion Matrices – Baseline vs Tuned", fontsize=15, y=1.02)
plt.tight_layout()
plt.savefig("results/figures/confusion_matrices.png", dpi=150, bbox_inches="tight")
plt.close()
print("[OK] confusion_matrices.png saved.")

# ── 6b. ROC Curves ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=FIG_SIZE)
for y_prob, label, color in [
    (y_prob_base, "Baseline RF", "#5B8DB8"),
    (y_prob_best, "Tuned RF",    "#E07B54"),
]:
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc_val     = roc_auc_score(y_test, y_prob)
    ax.plot(fpr, tpr, label=f"{label}  (AUC = {auc_val:.4f})", linewidth=2, color=color)

ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Classifier")
ax.fill_between(fpr, tpr, alpha=0.08, color="#E07B54")
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.set_title("ROC Curves – Baseline vs Tuned Random Forest", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig("results/figures/roc_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("[OK] roc_curves.png saved.")

# ── 6c. Feature Importance (Top 15) ───────────────────────────────────────
importances    = best_rf.feature_importances_
feat_imp_df    = (
    pd.DataFrame({"feature": data.feature_names, "importance": importances})
    .sort_values("importance", ascending=False)
    .head(15)
)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(
    feat_imp_df["feature"][::-1],
    feat_imp_df["importance"][::-1],
    color=sns.color_palette("Blues_r", 15),
    edgecolor="white",
)
ax.set_xlabel("Feature Importance (Gini Impurity Reduction)", fontsize=12)
ax.set_title("Top 15 Feature Importances – Tuned Random Forest", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("results/figures/feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("[OK] feature_importance.png saved.")

# ── 6d. Learning Curve ─────────────────────────────────────────────────────
train_sizes, train_scores, val_scores = learning_curve(
    best_rf, X_train_s, y_train,
    train_sizes=np.linspace(0.1, 1.0, 10),
    cv=5, scoring="f1", n_jobs=-1
)
train_mean = train_scores.mean(axis=1)
train_std  = train_scores.std(axis=1)
val_mean   = val_scores.mean(axis=1)
val_std    = val_scores.std(axis=1)

fig, ax = plt.subplots(figsize=FIG_SIZE)
ax.plot(train_sizes, train_mean, "o-", color="#5B8DB8", label="Training F1")
ax.fill_between(train_sizes,
                train_mean - train_std,
                train_mean + train_std,
                alpha=0.15, color="#5B8DB8")
ax.plot(train_sizes, val_mean, "s-", color="#E07B54", label="Validation F1")
ax.fill_between(train_sizes,
                val_mean - val_std,
                val_mean + val_std,
                alpha=0.15, color="#E07B54")
ax.set_xlabel("Training Set Size", fontsize=12)
ax.set_ylabel("F1-Score", fontsize=12)
ax.set_title("Learning Curve – Tuned Random Forest", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.set_ylim([0.85, 1.02])
plt.tight_layout()
plt.savefig("results/figures/learning_curve.png", dpi=150, bbox_inches="tight")
plt.close()
print("[OK] learning_curve.png saved.")

# ── 6e. Metrics Bar Chart ─────────────────────────────────────────────────
metrics_labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
baseline_vals  = [baseline_metrics[k] for k in ["accuracy","precision","recall","f1","roc_auc"]]
tuned_vals     = [tuned_metrics[k]    for k in ["accuracy","precision","recall","f1","roc_auc"]]

x   = np.arange(len(metrics_labels))
w   = 0.35
fig, ax = plt.subplots(figsize=(10, 5))
b1  = ax.bar(x - w/2, baseline_vals, w, label="Baseline RF", color="#5B8DB8", alpha=0.85, edgecolor="white")
b2  = ax.bar(x + w/2, tuned_vals,    w, label="Tuned RF",    color="#E07B54", alpha=0.85, edgecolor="white")
ax.set_xticks(x)
ax.set_xticklabels(metrics_labels, fontsize=12)
ax.set_ylabel("Score", fontsize=12)
ax.set_ylim([0.90, 1.01])
ax.set_title("Metric Comparison – Baseline vs Tuned Random Forest", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.bar_label(b1, fmt="%.4f", padding=3, fontsize=9)
ax.bar_label(b2, fmt="%.4f", padding=3, fontsize=9)
plt.tight_layout()
plt.savefig("results/figures/metrics_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("[OK] metrics_comparison.png saved.")

# ── 6f. Pairplot of top 4 features ────────────────────────────────────────
top4  = feat_imp_df["feature"].values[:4].tolist()
plot_df = X[top4].copy()
plot_df["target"] = y.map({0: "Malignant", 1: "Benign"})
pair_fig = sns.pairplot(plot_df, hue="target",
                        palette={"Malignant": "#E07B54", "Benign": "#5B8DB8"},
                        plot_kws={"alpha": 0.5, "s": 30})
pair_fig.fig.suptitle("Pairplot – Top 4 Important Features", y=1.02, fontsize=13, fontweight="bold")
pair_fig.savefig("results/figures/pairplot_top4.png", dpi=150, bbox_inches="tight")
plt.close()
print("[OK] pairplot_top4.png saved.")

# ---------------------------------------------------------------------------
# 7. Final Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STEP 7 – Final Summary")
print("=" * 70)

print("\nAll results saved to the 'results/' directory.")
print("\nBest Hyperparameters Found:")
for k, v in grid_rf.best_params_.items():
    print(f"  {k:25s}: {v}")

print("\nFinal Model Performance on Test Set:")
for metric, val in tuned_metrics.items():
    if metric != "model":
        print(f"  {metric.capitalize():12s}: {val:.4f}")

print("[OK] Pipeline completed successfully!\n")
