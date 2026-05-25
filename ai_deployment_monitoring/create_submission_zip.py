"""
create_submission_zip.py
------------------------
Packages the ai_deployment_monitoring project into a zip archive
for submission, excluding __pycache__, .pyc files, and large binaries.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ZIP = os.path.join(BASE_DIR, "..", "ai_deployment_submission.zip")

EXCLUDE_PATTERNS = {
    "__pycache__",
    ".pyc",
    ".pyo",
    ".git",
    ".DS_Store",
    "ai_deployment_submission.zip",
}


def should_exclude(path: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat in path:
            return True
    return False


def create_zip():
    output_path = os.path.abspath(OUTPUT_ZIP)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Skip excluded directories in-place
            dirs[:] = [d for d in dirs if not should_exclude(d)]
            for file in files:
                filepath = os.path.join(root, file)
                if should_exclude(filepath):
                    continue
                arcname = os.path.relpath(filepath, os.path.dirname(BASE_DIR))
                zf.write(filepath, arcname)
                print(f"  + {arcname}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n[OK] Zip created -> {output_path}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    create_zip()
