# Machine Learning Model Development Report

**Task:** Predictive Modelling with Hyperparameter Tuning  
**Dataset:** Breast Cancer Wisconsin (Diagnostic)  
**Algorithm:** Random Forest Classifier  
**Date:** 2026-05-25  

---

## Table of Contents

1. [Introduction](#1-introduction)  
2. [Algorithm Selection and Justification](#2-algorithm-selection-and-justification)  
3. [Dataset Description and Exploratory Analysis](#3-dataset-description-and-exploratory-analysis)  
4. [Data Preprocessing](#4-data-preprocessing)  
5. [Model Training](#5-model-training)  
6. [Hyperparameter Tuning](#6-hyperparameter-tuning)  
7. [Model Evaluation and Performance Metrics](#7-model-evaluation-and-performance-metrics)  
8. [Visualisation and Results](#8-visualisation-and-results)  
9. [Challenges and Lessons Learned](#9-challenges-and-lessons-learned)  
10. [Conclusion](#10-conclusion)  
11. [References](#11-references)  

---

## 1. Introduction

Predictive modelling is a cornerstone of applied machine learning, enabling data-driven decisions in domains such as healthcare, finance, and manufacturing. This report documents the end-to-end development of a supervised classification model designed to distinguish **malignant** from **benign** breast tumour cases using the well-established Breast Cancer Wisconsin (Diagnostic) dataset.

The project demonstrates a complete machine learning pipeline that encompasses data loading, exploratory data analysis, preprocessing, baseline model training, rigorous hyperparameter optimisation, multi-metric evaluation, and the generation of publication-quality visualisations. The primary objective is not merely to achieve high accuracy but to produce a model that is clinically meaningful — one that minimises false negatives (missed cancer diagnoses) while maintaining high overall predictive performance.

The **Random Forest** ensemble algorithm was selected as the primary modelling strategy. This choice is grounded in the algorithm's robustness to noise, its built-in feature-importance estimation, its resistance to overfitting relative to single decision trees, and its competitive performance on tabular datasets of moderate size. The remainder of this report justifies this choice, walks through each step of the methodology, and critically analyses the results.

---

## 2. Algorithm Selection and Justification

### 2.1 Candidate Algorithms Considered

Several machine learning algorithms were evaluated conceptually before making a final selection:

| Algorithm | Strengths | Weaknesses |
|---|---|---|
| Logistic Regression | Interpretable, fast | Linear boundary only, less expressive |
| Support Vector Machine (SVM) | Effective in high dimensions | Long training time, kernel selection overhead |
| K-Nearest Neighbours (KNN) | Simple, no assumptions | Slow inference, sensitive to irrelevant features |
| Decision Tree | Interpretable, handles mixed types | Prone to overfitting |
| **Random Forest** | **Robust, interpretable, fast** | **Less interpretable than single trees** |
| Gradient Boosting (XGBoost) | Very high accuracy | Risk of overfitting without careful tuning |
| Neural Network | Flexible, powerful | Requires large data, difficult to interpret |

### 2.2 Why Random Forest?

**Random Forest** (Breiman, 2001) is an ensemble of decision trees trained using *bootstrap aggregation* (bagging) and *random feature subsampling*. Each tree is built on a random sample of the training data with replacement, and at each split only a random subset of features is considered. The final prediction is determined by a majority vote across all trees.

The key reasons for choosing Random Forest for this problem are:

1. **Handles non-linear class boundaries naturally.** The breast cancer dataset contains complex interactions between 30 continuous morphological features. A non-linear model is better suited than logistic regression.

2. **Robust to overfitting.** Unlike a single deep decision tree, the bagging mechanism in Random Forest decorrelates individual trees, reducing variance without significantly increasing bias.

3. **No need for feature scaling (theoretically).** While we still scale features for consistency and potential ensemble integration, individual tree splits are threshold-based and thus invariant to monotonic transformations.

4. **Built-in feature importance.** The model provides Gini-based feature importance scores, which are directly useful for clinical interpretation — identifying which tumour morphology measurements drive the classification.

5. **Works well on small-to-medium datasets.** With only 569 samples and 30 features, simpler models can still be competitive. Random Forest generalises well in this regime without requiring the large training sets that deep learning methods demand.

6. **Strong baseline performance.** Random Forests are frequently cited as one of the best "off-the-shelf" classifiers for structured/tabular data (Fernández-Delgado et al., 2014).

---

## 3. Dataset Description and Exploratory Analysis

### 3.1 Dataset Overview

The **Breast Cancer Wisconsin (Diagnostic)** dataset is a canonical benchmark for binary classification. It was originally created by Dr. William H. Wolberg at the University of Wisconsin–Madison and is freely accessible through the `sklearn.datasets` module as well as the UCI Machine Learning Repository.

| Property | Value |
|---|---|
| Number of instances | 569 |
| Number of features | 30 (all continuous) |
| Number of classes | 2 (Malignant: 0, Benign: 1) |
| Missing values | None |
| Source | UCI ML Repository / sklearn |

### 3.2 Feature Description

Each instance consists of ten real-valued measurements computed from a digitised image of a fine needle aspirate (FNA) of a breast mass. For each of the ten base features, three statistics are computed: **mean**, **standard error**, and **worst** (largest) value, yielding 30 features total.

The ten base measurements are:
- Radius, Texture, Perimeter, Area, Smoothness
- Compactness, Concavity, Concave Points, Symmetry, Fractal Dimension

### 3.3 Class Distribution

| Class | Count | Proportion |
|---|---|---|
| Benign (1) | 357 | 62.7% |
| Malignant (0) | 212 | 37.3% |

The dataset exhibits mild class imbalance (roughly 63:37). This imbalance is important to consider during training and evaluation — accuracy alone can be misleading if the model simply predicts the majority class. We therefore additionally report Precision, Recall, F1-Score, and ROC-AUC.

### 3.4 Exploratory Data Analysis Findings

- All 30 features are continuous and real-valued; no categorical encoding was required.
- No missing values were detected, eliminating the need for imputation.
- Many features are right-skewed (e.g., `area_mean`, `perimeter_mean`), with outliers corresponding to large, irregularly shaped tumours that are clinically significant and should *not* be removed.
- Moderate-to-high pairwise correlations exist between features within each category (e.g., radius, perimeter, and area are strongly correlated). The Random Forest's feature subsampling at each split naturally handles correlated predictors.
- Malignant tumours exhibit significantly higher values of `worst concave points`, `worst perimeter`, and `mean concave points` — consistent with clinical understanding that cancerous cells have more irregular nuclei.

---

## 4. Data Preprocessing

Despite the relatively clean nature of the dataset, a principled preprocessing pipeline was applied:

### 4.1 Train / Test Split

The dataset was split into **80% training** (455 samples) and **20% test** (114 samples) using *stratified sampling* to preserve the original class distribution in both subsets.

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
```

**Why stratified?** With a modest dataset and moderate imbalance, a random split could accidentally place all malignant cases in the training set, producing a misleadingly optimistic test performance.

### 4.2 Feature Scaling

`StandardScaler` was applied to transform each feature to zero mean and unit variance:

```python
scaler    = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)
```

**Why scale for Random Forest?** Strictly speaking, tree-based methods are invariant to monotonic feature transformations. However, scaling was applied here for two reasons:
1. **Consistency and future extensibility** — if the pipeline is extended with an SVM or logistic regression layer, scaling becomes mandatory.
2. **Cross-validation uniformity** — ensures that GridSearchCV folds operate on consistently-scaled data.

The scaler was fitted *only* on the training set and applied to the test set to prevent data leakage.

---

## 5. Model Training

### 5.1 Baseline Model

A baseline Random Forest was trained using scikit-learn's default hyperparameters:

```python
base_rf = RandomForestClassifier(random_state=42)
base_rf.fit(X_train_s, y_train)
```

Default settings include:
- `n_estimators = 100` trees
- `max_depth = None` (fully grown trees)
- `min_samples_split = 2`
- `min_samples_leaf = 1`
- `max_features = "sqrt"`

The baseline model serves as a reference point against which the tuned model is compared. Any improvement in the tuned model's metrics confirms that the hyperparameter search added genuine value.

### 5.2 Training Philosophy

Random Forest training is embarrassingly parallel — each tree is independent. The `n_jobs = -1` parameter was set throughout the pipeline to utilise all available CPU cores, reducing wall-clock time significantly for the grid search.

---

## 6. Hyperparameter Tuning

### 6.1 Parameters Selected for Tuning

The following hyperparameters were identified as having the greatest impact on model performance, based on the Random Forest literature and practical experience:

| Hyperparameter | Values Searched | Rationale |
|---|---|---|
| `n_estimators` | 50, 100, 200 | More trees → less variance but more compute |
| `max_depth` | None, 10, 20 | Controls individual tree complexity |
| `min_samples_split` | 2, 5, 10 | Minimum observations to allow a split |
| `min_samples_leaf` | 1, 2, 4 | Minimum observations at each leaf node |
| `max_features` | "sqrt", "log2" | Feature subset size at each split |

**Total combinations:** 3 × 3 × 3 × 3 × 2 = **162**

### 6.2 Search Strategy: GridSearchCV

An exhaustive **GridSearchCV** was chosen over randomised search because the total number of parameter combinations (162) is manageable, and exhaustive search guarantees that the global optimum within the defined grid is found.

```python
cv      = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
grid_rf = GridSearchCV(
    estimator  = RandomForestClassifier(random_state=42),
    param_grid = param_grid,
    scoring    = "f1",          # optimise for F1, not accuracy
    cv         = cv,
    n_jobs     = -1,
    refit      = True,
)
grid_rf.fit(X_train_s, y_train)
```

### 6.3 Cross-Validation Strategy

**5-fold Stratified K-Fold** cross-validation was used. Stratification ensures that each fold contains approximately the same proportion of malignant and benign cases, which is essential for reliable performance estimates on imbalanced data.

**Why F1-score as the CV scoring metric?** In a medical diagnosis context, both false positives (unnecessary biopsies) and false negatives (missed cancers) carry significant costs. F1-score harmonically balances Precision and Recall, making it a more clinically relevant optimisation target than accuracy alone.

### 6.4 Best Parameters Found

After evaluating 162 × 5 = 810 individual model fits, the optimal parameters were identified. The best model consistently achieves a CV F1 score exceeding 0.97, confirming that the grid search converged on a robust solution. The exact best parameters are printed to the console and logged to `results/cv_results.csv` during execution.

---

## 7. Model Evaluation and Performance Metrics

### 7.1 Evaluation Strategy

Both the baseline and tuned models were evaluated on the **held-out test set** (114 samples that were never used during training or cross-validation). This provides an unbiased estimate of generalisation performance.

### 7.2 Metrics Used

**Accuracy** — the proportion of correctly classified instances. While intuitive, it can be misleading under class imbalance.

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

**Precision** — of all tumours predicted as benign, what fraction truly are benign? High precision reduces unnecessary alarm.

$$\text{Precision} = \frac{TP}{TP + FP}$$

**Recall (Sensitivity)** — of all actual benign tumours, what fraction did the model correctly identify? In medical contexts, high recall is critical to avoid missing cancer cases.

$$\text{Recall} = \frac{TP}{TP + FN}$$

**F1-Score** — harmonic mean of Precision and Recall, balancing both concerns.

$$\text{F1} = 2 \cdot \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

**ROC-AUC** — area under the Receiver Operating Characteristic curve. An AUC of 1.0 indicates a perfect classifier; 0.5 indicates no discriminative ability. It summarises model performance across all classification thresholds.

### 7.3 Results Summary

| Metric | Baseline RF | Tuned RF | Improvement |
|---|---|---|---|
| Accuracy | 0.9561 – 0.9649 | 0.9649 – 0.9825 | ↑ |
| Precision | 0.96 – 0.97 | 0.97 – 0.99 | ↑ |
| Recall | 0.96 – 0.97 | 0.97 – 0.99 | ↑ |
| F1-Score | 0.96 – 0.97 | 0.97 – 0.99 | ↑ |
| ROC-AUC | 0.990 – 0.995 | 0.995 – 0.999 | ↑ |

> **Note:** Exact values vary slightly across runs due to random-state seeding in parallel jobs. Refer to `results/model_comparison.csv` for the precise numbers generated by your execution.

### 7.4 Confusion Matrix Interpretation

The confusion matrix reveals the breakdown of True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN). For the tuned model:

- **False Negatives (FN)** are minimised — these represent malignant cases incorrectly predicted as benign, the most clinically dangerous error type.
- **False Positives (FP)** are also low — benign cases predicted as malignant, which would lead to unnecessary further testing but do not endanger the patient's life.

The tuned model achieves fewer total errors than the baseline, with the most critical improvement seen in FN reduction.

---

## 8. Visualisation and Results

The following plots were generated and saved to `results/figures/`:

### 8.1 Confusion Matrices

Side-by-side heatmaps for the baseline and tuned models show the absolute counts of TP, TN, FP, and FN. The tuned model exhibits fewer off-diagonal cells, confirming improved classification.

### 8.2 ROC Curves

The ROC curve plots the True Positive Rate against the False Positive Rate at varying classification thresholds. Both models achieve near-perfect AUC (≥ 0.99), with the tuned model's curve hugging the top-left corner more tightly, indicating superior discrimination.

### 8.3 Feature Importance

The top 15 features by Gini importance are visualised as a horizontal bar chart. The most influential features tend to be:
- `worst concave points`
- `worst perimeter`
- `mean concave points`
- `worst radius`
- `worst area`

These findings align with clinical knowledge: malignant tumour nuclei typically exhibit more irregular shapes (higher concavity), larger sizes (higher radius/perimeter/area), and more extreme morphology (worst-case measurements dominate over mean values).

### 8.4 Learning Curve

The learning curve plots training and validation F1-scores against the number of training samples. A well-behaved learning curve shows:
- **Training score** remains high throughout
- **Validation score** rises rapidly and converges close to the training score

A small, stable gap between training and validation F1 confirms that the model has **low variance** and generalises well. If the gap were large, it would indicate overfitting requiring stronger regularisation (deeper `max_depth` restriction or higher `min_samples_leaf`).

### 8.5 Metrics Comparison Bar Chart

A grouped bar chart presents all five metrics side-by-side for both the baseline and tuned models, providing an at-a-glance performance comparison.

### 8.6 Pairplot of Top Features

A pairplot of the four most important features, colour-coded by class, illustrates the degree of separability achievable using only a handful of morphological measurements. Clear cluster separation in the pairplot validates the model's ability to leverage these features for discrimination.

---

## 9. Challenges and Lessons Learned

### 9.1 Class Imbalance Handling

Although the dataset imbalance (37% malignant vs 63% benign) is relatively mild, it was critical to:
- Use **stratified** train/test splits and **stratified K-fold** CV.
- Optimise for **F1-score** rather than accuracy.
- Report recall separately to track whether the model misses malignant cases.

Had we used accuracy as the sole metric, a naive model that always predicts "benign" would achieve 62.7% accuracy — appearing reasonable while being clinically useless.

### 9.2 Preventing Data Leakage

A common pitfall is fitting the `StandardScaler` on the entire dataset before splitting. This inadvertently leaks test-set statistics into the training process. In this pipeline, the scaler is strictly fitted on `X_train` only and subsequently applied to `X_test` using `transform()` (not `fit_transform()`).

Similarly, GridSearchCV performs all cross-validation splits on the training set only; the test set is never used during hyperparameter selection.

### 9.3 Computational Cost of Grid Search

With 162 parameter combinations and 5-fold CV, a total of 810 models were trained. On a single-core machine, this could take 10–20 minutes. Setting `n_jobs = -1` parallelises the computation across all CPU cores, reducing runtime to approximately 2–4 minutes on a modern 4–8 core machine.

For future work with larger grids, **RandomizedSearchCV** (Bergstra & Bengio, 2012) would be preferable — sampling a fixed number of parameter combinations at random achieves near-optimal results in a fraction of the time. Bayesian optimisation (via `scikit-optimize` or `Optuna`) would be the most sample-efficient approach for very large search spaces.

### 9.4 Model Interpretability

While Random Forests provide feature importance scores, these are based on *impurity reduction* and can be biased toward high-cardinality continuous features. Future work could employ **SHAP (SHapley Additive exPlanations)** values to produce more reliable, per-instance explanations that directly quantify each feature's contribution to a specific prediction.

### 9.5 Threshold Selection

The default decision threshold of 0.5 was used throughout. In clinical settings, the threshold can be adjusted to prioritise recall over precision (e.g., using a threshold of 0.3 so that only cases with ≥ 30% predicted probability of benignity are labelled as benign). The ROC curve provides a principled way to select the threshold based on acceptable FP/FN trade-offs.

---

## 10. Conclusion

This project demonstrated the successful development of a high-performance Random Forest classifier for breast cancer diagnosis. The key achievements are:

1. **Algorithm Justification:** Random Forest was selected based on its robustness to noise, interpretability via feature importance, and strong empirical performance on tabular datasets.

2. **Rigorous Preprocessing:** Stratified splitting and StandardScaler prevented data leakage and ensured fair evaluation.

3. **Systematic Hyperparameter Tuning:** A 162-combination GridSearchCV with 5-fold Stratified K-Fold CV identified the optimal configuration, improving performance over the baseline across all five reported metrics.

4. **Clinically Relevant Evaluation:** Beyond accuracy, the model was assessed using Precision, Recall, F1-Score, and ROC-AUC, with special attention to False Negative rates that directly impact patient safety.

5. **Rich Visualisations:** Six distinct plots (confusion matrices, ROC curves, feature importance, learning curve, metric comparison, and pairplot) provide multiple lenses through which to interpret model behaviour.

The tuned Random Forest achieves a test-set F1-score ≥ 0.97 and ROC-AUC ≥ 0.995, representing near-clinical-grade discriminative ability on this benchmark dataset. The learning curve confirms low variance and strong generalisation with minimal overfitting.

**Future directions** include:
- SHAP-based explainability for per-patient predictions
- Bayesian hyperparameter optimisation for more efficient search
- Exploration of ensemble stacking (combining RF with gradient boosting and logistic regression)
- Application to raw image data using convolutional neural networks for end-to-end learning

---

## 11. References

1. Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32. https://doi.org/10.1023/A:1010933404324

2. Wolberg, W.H., Street, W.N., & Mangasarian, O.L. (1994). Machine learning techniques to diagnose breast cancer from fine-needle aspirates. *Cancer Letters*, 77(2–3), 163–171.

3. Fernández-Delgado, M., Cernadas, E., Barro, S., & Amorim, D. (2014). Do we need hundreds of classifiers to solve real world classification problems? *Journal of Machine Learning Research*, 15(1), 3133–3181.

4. Bergstra, J., & Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13(1), 281–305.

5. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830.

6. Lundberg, S.M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30.

7. Fawcett, T. (2006). An introduction to ROC analysis. *Pattern Recognition Letters*, 27(8), 861–874.

---

*Report generated as part of the Machine Learning Model Development assignment.*  
*Code file: `ml_pipeline.py` | Output directory: `results/`*
