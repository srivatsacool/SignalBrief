"""
build_signalbrief_final_notebook.py
Assembles all sections into SignalBrief_Text_Analytics_Final.ipynb and executes
every cell top-to-bottom using nbconvert.preprocessors.ExecutePreprocessor.
"""

import sys
import os
import time
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

# Ensure scripts directory is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.signalbrief_builder.sections_part1 import build_sections_part1
from scripts.signalbrief_builder.sections_part2 import build_sections_part2
from scripts.signalbrief_builder.sections_part3 import build_sections_part3
from scripts.signalbrief_builder.sections_part4 import build_sections_part4

def build_and_execute_notebook():
    print("=" * 80)
    print("SIGNALBRIEF QTA 404 FINAL MASTER NOTEBOOK BUILDER")
    print("=" * 80)

    # 1. Gather all cells from modular sections
    print("\n[Stage 1/4] Assembling notebook cells from builder modules...")
    cells = []
    
    p1 = build_sections_part1()
    print(f"  * Part 1 (Sections 00-03): {len(p1)} cells")
    cells.extend(p1)
    
    p2 = build_sections_part2()
    print(f"  * Part 2 (Sections 04-07): {len(p2)} cells")
    cells.extend(p2)
    
    p3 = build_sections_part3()
    print(f"  * Part 3 (Sections 08-11): {len(p3)} cells")
    cells.extend(p3)
    
    p4 = build_sections_part4()
    print(f"  * Part 4 (Sections 12-16): {len(p4)} cells")
    cells.extend(p4)

    print(f"\nTotal Assembled Cells: {len(cells)}")
    code_cells = [c for c in cells if c['cell_type'] == 'code']
    md_cells = [c for c in cells if c['cell_type'] == 'markdown']
    print(f"  * Code Cells    : {len(code_cells)}")
    print(f"  * Markdown Cells: {len(md_cells)}")

    # 2. Create nbformat notebook object
    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata['kernelspec'] = {
        'display_name': 'Python 3 (ipykernel)',
        'language': 'python',
        'name': 'python3'
    }
    nb.metadata['language_info'] = {
        'codemirror_mode': {'name': 'ipython', 'version': 3},
        'file_extension': '.py',
        'mimetype': 'text/x-python',
        'name': 'python',
        'nbconvert_exporter': 'python',
        'pygments_lexer': 'ipython3',
        'version': '3.12.0'
    }

    target_nb_path = PROJECT_ROOT / "SignalBrief_Text_Analytics_Final.ipynb"
    print(f"\n[Stage 2/4] Saving raw notebook to: {target_nb_path.name}")
    with open(target_nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("  * Raw notebook saved successfully.")

    # 3. Execute all cells from top to bottom
    print(f"\n[Stage 3/4] Executing notebook top-to-bottom via ExecutePreprocessor...")
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    
    start_time = time.time()
    try:
        ep.preprocess(nb, {'metadata': {'path': str(PROJECT_ROOT)}})
        exec_duration = time.time() - start_time
        print(f"  * Execution completed successfully in {exec_duration:.2f} seconds!")
    except Exception as e:
        exec_duration = time.time() - start_time
        print(f"\n[ERROR] Execution failed after {exec_duration:.2f} seconds: {e}")
        # Save what was executed up to the error for debugging
        with open(target_nb_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        raise

    # 4. Save fully executed notebook
    print(f"\n[Stage 4/4] Writing fully executed notebook with all outputs and figures...")
    with open(target_nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    
    file_size_kb = target_nb_path.stat().st_size / 1024
    print(f"  * Executed notebook saved: {target_nb_path.name} ({file_size_kb:.1f} KB)")
    print("=" * 80)
    print("BUILD & EXECUTION COMPLETE: Notebook is presentation-ready!")
    print("=" * 80)

if __name__ == "__main__":
    build_and_execute_notebook()
