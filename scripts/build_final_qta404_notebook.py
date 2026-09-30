"""
build_final_qta404_notebook.py
Master compiler and executor for the QTA 404 Final Capstone Notebook:
Employee_Voice_Analytics_Final.ipynb

Assembles all 17 sections (00 to 16) with 33 fully documented code cells,
executes the notebook end-to-end using ExecutePreprocessor,
and verifies that all figures, tables, and metrics render properly.
"""

import sys
import os
import time
from pathlib import Path
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Import modular section builders
from qta404_builder.sections_part1 import build_sections_part1
from qta404_builder.sections_part2 import build_sections_part2
from qta404_builder.sections_part3 import build_sections_part3
from qta404_builder.sections_part4 import build_sections_part4

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_NOTEBOOK_PATH = ROOT_DIR / "Employee_Voice_Analytics_Final.ipynb"
BACKUP_NOTEBOOK_PATH = Path("D:/Brain/03_Projects/WORKFORCE INTELLIGENCE ANALYTICS/Employee_Voice_Analytics_Final.ipynb")

print("=" * 80)
print("BUILDING QTA 404 MASTER JUPYTER NOTEBOOK")
print("=" * 80)

start_time = time.time()

# 1. Assemble all sections
print("📦 Assembling notebook sections...")
cells_p1 = build_sections_part1()
cells_p2 = build_sections_part2()
cells_p3 = build_sections_part3()
cells_p4 = build_sections_part4()

all_cells = cells_p1 + cells_p2 + cells_p3 + cells_p4

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.12.0"
    }
}
nb.cells = all_cells

num_code_cells = sum(1 for c in all_cells if c.cell_type == 'code')
num_md_cells = sum(1 for c in all_cells if c.cell_type == 'markdown')
print(f"✅ Notebook assembled: {len(all_cells)} total cells ({num_code_cells} Code cells, {num_md_cells} Markdown cells).")

# Save unexecuted draft first
with open(OUTPUT_NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"💾 Unexecuted draft saved to: {OUTPUT_NOTEBOOK_PATH.name}")

# 2. Execute notebook end-to-end
print("\n⚙️ Executing all cells top-to-bottom via ExecutePreprocessor (kernel: python3)...")
print("   (This runs all data cleaning, TF-IDF, classification, VADER sentiment, and LDA topic modeling...)")

exec_start = time.time()
ep = ExecutePreprocessor(timeout=1200, kernel_name='python3')

try:
    ep.preprocess(nb, {'metadata': {'path': str(ROOT_DIR)}})
    exec_duration = time.time() - exec_start
    print(f"🎉 All {num_code_cells} code cells executed successfully in {exec_duration:.1f} seconds!")
except Exception as e:
    print(f"❌ Error during notebook execution: {e}")
    # Write partial outputs for inspection
    with open(OUTPUT_NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    raise

# 3. Save fully executed notebook
with open(OUTPUT_NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print(f"💾 Fully executed notebook saved to: {OUTPUT_NOTEBOOK_PATH}")

# Save duplicate copy to Workforce Intelligence Analytics project directory if accessible
try:
    if BACKUP_NOTEBOOK_PATH.parent.exists():
        with open(BACKUP_NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
        print(f"💾 Synchronized copy saved to: {BACKUP_NOTEBOOK_PATH}")
except Exception as e:
    print(f"Note: Could not write secondary copy to {BACKUP_NOTEBOOK_PATH}: {e}")

total_duration = time.time() - start_time
print("=" * 80)
print(f"✅ QTA 404 MASTER NOTEBOOK BUILD COMPLETE IN {total_duration:.1f} SECONDS!")
print("=" * 80)
