"""
================================================================================
  AI Ethics Audit - Main Entry Point
  Run this file to execute the full audit pipeline and generate the PDF report
================================================================================
"""

import sys
import os

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("\n" + "="*70)
    print("  AI ETHICS AUDIT - Full Pipeline Runner")
    print("  Model: Logistic Regression | Dataset: UCI Adult Income")
    print("="*70 + "\n")

    # Step 1: Run the audit analysis
    from ethics_audit import run_audit
    results = run_audit()

    # Step 2: Generate PDF report
    from generate_report import generate_report
    pdf_path = generate_report(results)

    print("\n" + "="*70)
    print("  [DONE] AUDIT COMPLETE")
    print(f"  [PDF]  Report  : {pdf_path}")
    print(f"  [PNG]  Figures : {os.path.dirname(pdf_path)}")
    print(f"  [CSV]  Metrics : {os.path.join(os.path.dirname(pdf_path), 'fairness_metrics_summary.csv')}")
    print("="*70 + "\n")

    return pdf_path


if __name__ == "__main__":
    main()
