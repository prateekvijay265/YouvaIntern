# ML Model Development – Random Forest Classifier

## Project Structure

```
ml_model_development/
├── ml_pipeline.py        ← Main code file (complete ML pipeline)
├── report.md             ← Detailed written report (1500+ words)
├── requirements.txt      ← Python package dependencies
├── README.md             ← This file
└── results/              ← Auto-created when pipeline runs
    ├── dataset_summary.csv
    ├── cv_results.csv
    ├── model_comparison.csv
    └── figures/
        ├── confusion_matrices.png
        ├── roc_curves.png
        ├── feature_importance.png
        ├── learning_curve.png
        ├── metrics_comparison.png
        └── pairplot_top4.png
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the pipeline
python ml_pipeline.py
```

## What the Pipeline Does

1. **Loads** the Breast Cancer Wisconsin dataset (569 samples, 30 features)  
2. **Explores** the data (shape, class distribution, missing values)  
3. **Preprocesses** (stratified 80/20 split + StandardScaler)  
4. **Trains** a baseline Random Forest with default hyperparameters  
5. **Tunes** hyperparameters with 5-fold GridSearchCV (162 combinations)  
6. **Evaluates** both models on the held-out test set  
7. **Saves** 6 visualisation figures and 3 CSV result files  

## Expected Runtime

- ~2–4 minutes on a modern multi-core machine (parallelised with `n_jobs=-1`)

## Deliverables

| File | Description |
|---|---|
| `ml_pipeline.py` | Complete, commented Python code |
| `report.md` | Detailed report (>1500 words, convert to PDF using Pandoc or Word) |
