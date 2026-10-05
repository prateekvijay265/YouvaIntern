<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=250&section=header&text=AI%20Internship%20Portfolio&fontSize=70&fontAlignY=35&animation=twinkling&fontColor=ffffff" width="100%" />

  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=26&pause=1000&color=2ecc71&center=true&vCenter=true&width=800&lines=End-to-End+Machine+Learning+Lifecycle;Data+Processing+%26+Feature+Engineering;Model+Development+%26+Tuning;Explainable+AI+(XAI)+%26+Interpretability;AI+Ethics+%26+Bias+Auditing;Model+Deployment+%26+Monitoring" alt="Typing SVG" />
  </a>
</div>

<p align="center">
  <em>A comprehensive portfolio showcasing projects undertaken during my AI & Data Science Internship. The repository covers the complete lifecycle of AI development, from raw data processing to production deployment, with a strong focus on ethics and interpretability.</em>
</p>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## 📑 Table of Contents

- [📊 Project 1: Data Processing & EDA](#-project-1-data-processing--eda)
- [🧠 Project 2: ML Model Development](#-project-2-ml-model-development)
- [🔍 Project 3: Explainable AI (XAI)](#-project-3-explainable-ai-xai)
- [⚖️ Project 4: AI Ethics Audit](#️-project-4-ai-ethics-audit)
- [🚀 Project 5: AI Deployment & Monitoring](#-project-5-ai-deployment--monitoring)
- [📁 Final Internship Reports](#-final-internship-reports)

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## 📊 Project 1: Data Processing & EDA
**Directory:** [`data processing/`](./data\ processing/)

### 📝 Overview
Data quality is the foundation of robust machine learning. This phase focused on building a rigorous data preprocessing pipeline to clean, explore, and transform raw data into a model-ready format.

### 🛠️ Key Highlights
- **Exploratory Data Analysis (EDA):** Visualizing distributions, correlation matrices, and identifying underlying patterns.
- **Handling Missing Data:** Implementing advanced imputation techniques to handle sparse features reliably.
- **Outlier Detection:** Analyzing feature spread and treating outliers to ensure statistical robustness (visualized via Boxplots).
- **Feature Engineering & Scaling:** Standardizing features and evaluating scaling comparisons for distance-based and gradient-based algorithms.

### 🖼️ Visual Insights
> Includes `correlation_matrix.png`, `missing_data_analysis.png`, `feature_importance.png`, `outlier_boxplots.png`, and `scaling_comparison.png`.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## 🧠 Project 2: ML Model Development
**Directory:** [`ml_model_development/`](./ml_model_development/)

### 📝 Overview
Developed a predictive classification model using the **Breast Cancer Wisconsin (Diagnostic)** dataset to accurately distinguish between benign and malignant tumors. The goal was to maximize recall (minimizing false negatives) while retaining high overall accuracy.

### 🛠️ Key Highlights
- **Algorithm Used:** Random Forest Classifier (Robust, interpretable, and resistant to overfitting).
- **Hyperparameter Tuning:** Conducted exhaustive 5-fold `GridSearchCV` over 162 parameter combinations.
- **Pipeline:** Automated pipeline (`ml_pipeline.py`) incorporating stratified 80/20 train-test splits and `StandardScaler` transformations.
- **Evaluation:** Rigorous performance benchmarking generating confusion matrices, ROC curves, learning curves, and precise metric comparisons.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## 🔍 Project 3: Explainable AI (XAI)
**Directory:** [`explainable_ai/`](./explainable_ai/)

### 📝 Overview
AI shouldn't be a black box, especially in healthcare. This project focused on integrating Explainable AI (XAI) techniques to provide both global and local interpretability for the Breast Cancer diagnostic model.

### 🛠️ Key Highlights
- **SHAP (SHapley Additive exPlanations):**
  - *Global Interpretability:* Generating SHAP summary and dependence plots to understand overall feature impacts across the dataset.
  - *Local Interpretability:* Utilizing SHAP waterfall plots for specific single-prediction rationales.
- **LIME (Local Interpretable Model-agnostic Explanations):** 
  - Providing human-readable explanations for individual predictions to build clinical trust (analyzed both benign and malignant cases).
- **Outputs:** Comprehensive visual suite (`fig3_shap_summary.png`, `fig6_lime_benign.png`, etc.) and a dedicated `XAI_Report.pdf`.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## ⚖️ Project 4: AI Ethics Audit
**Directory:** [`ai_ethics_audit/`](./ai_ethics_audit/)

### 📝 Overview
An exhaustive audit to evaluate fairness and uncover hidden biases within machine learning models across sensitive demographic attributes like Race, Sex, Age, and Education.

### 🛠️ Key Highlights
- **Fairness Metrics Evaluated:** 
  - Disparate Impact
  - Equalized Odds
  - Intersectional Bias Analysis
- **Deep Dive Visualizations:**
  - Demographic distribution overviews.
  - Sub-group ROC curves (`fig5_roc_race.png`, `fig5_roc_sex.png`).
  - Comprehensive fairness heatmaps (`fig6_fairness_heatmap.png`).
- **Reporting:** Generated a robust ethical audit report outlining mitigation strategies and bias discovery (`AI_Ethics_Audit_Report.pdf`).

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## 🚀 Project 5: AI Deployment & Monitoring
**Directory:** [`ai_deployment_monitoring/`](./ai_deployment_monitoring/)

### 📝 Overview
Transitioning a model from a notebook to a robust production environment. This proof-of-concept deployed an Iris Species Classifier utilizing modern DevOps and MLOps practices.

### 🛠️ Key Highlights
- **Tech Stack:** FastAPI (Python), Uvicorn, and Docker.
- **API Architecture:**
  - `/predict` & `/predict/batch`: High-performance inference endpoints.
  - `/health`: Liveness & readiness probes.
  - `/metrics`: Thread-safe, in-process operational metrics store (latency, request counts, error rates).
- **Containerization:** Multi-stage `Dockerfile` with non-root security and a complete `docker-compose.yml` orchestrating resource limits and volumes.
- **Monitoring:** Structured JSON logging (console + rotating files) for downstream log aggregation.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%">

## 📁 Final Internship Reports
**Directories:** [`internship_final_report/`](./internship_final_report/) & [`report/`](./report/)

- Contains the overarching `Final_Internship_Report.pdf/docx` detailing the entire internship journey, key learnings, and professional growth.
- Includes presentation decks (`Internship_Presentation_Deployed.pptx`) used for stakeholder review and end-of-internship defense.
- Multiple programmatic report builders (`build_report.py`, `build_ppt.py`) that automated documentation generation.

<br>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" width="100%" />
</div>
