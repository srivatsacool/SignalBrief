"""
verify_signalbrief_notebook.py
Audits and verifies SignalBrief_Text_Analytics_Final.ipynb:
1. Validates nbformat structure.
2. Checks that every code cell has outputs and no errors.
3. Verifies mandatory pre-code and post-code Markdown documentation.
4. Produces an audit summary report.
"""

import sys
from pathlib import Path
import nbformat

def verify_notebook():
    nb_path = Path("SignalBrief_Text_Analytics_Final.ipynb")
    if not nb_path.exists():
        print(f"[ERROR] Notebook file not found: {nb_path}")
        sys.exit(1)

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    cells = nb.cells
    total_cells = len(cells)
    code_cells = [c for c in cells if c.cell_type == 'code']
    md_cells = [c for c in cells if c.cell_type == 'markdown']

    print("=" * 80)
    print(f"AUDIT REPORT FOR: {nb_path.name}")
    print("=" * 80)
    print(f"Total Notebook Cells : {total_cells}")
    print(f"Code Cells           : {len(code_cells)}")
    print(f"Markdown Cells       : {len(md_cells)}")
    print(f"Notebook File Size   : {nb_path.stat().st_size / 1024:.1f} KB")
    print("-" * 80)

    # Check code cells
    errors = 0
    missing_outputs = 0
    missing_pre_md = 0
    missing_post_md = 0

    for idx, cell in enumerate(cells):
        if cell.cell_type == 'code':
            # 1. Output check
            if not cell.outputs:
                print(f"[WARN] Cell {idx} has NO outputs!")
                missing_outputs += 1
            for out in cell.outputs:
                if out.get('output_type') == 'error':
                    print(f"[ERROR] Cell {idx} produced an execution error: {out.get('ename')}: {out.get('evalue')}")
                    errors += 1

            # 2. Preceding markdown check
            if idx == 0 or cells[idx - 1].cell_type != 'markdown':
                print(f"[WARN] Cell {idx} is NOT preceded by a Markdown cell!")
                missing_pre_md += 1
            else:
                pre_text = cells[idx - 1].source
                if "WHAT ARE WE DOING" not in pre_text and "Code Cell" not in pre_text:
                    print(f"[WARN] Cell {idx} preceding Markdown does not contain standard pre-explanation headers!")

            # 3. Following markdown check
            if idx == total_cells - 1 or cells[idx + 1].cell_type != 'markdown':
                print(f"[WARN] Cell {idx} is NOT followed by a Markdown cell!")
                missing_post_md += 1
            else:
                post_text = cells[idx + 1].source
                if "WHAT THE OUTPUT MEANS" not in post_text and "Interpretation" not in post_text:
                    print(f"[WARN] Cell {idx} following Markdown does not contain standard post-explanation headers!")

    print("\n" + "=" * 80)
    print("AUDIT SUMMARY:")
    print("=" * 80)
    print(f"Total Code Execution Errors : {errors}")
    print(f"Missing Outputs             : {missing_outputs}")
    print(f"Missing Pre-Code Markdown   : {missing_pre_md}")
    print(f"Missing Post-Code Markdown  : {missing_post_md}")
    print("=" * 80)

    if errors == 0 and missing_outputs == 0 and missing_pre_md == 0 and missing_post_md == 0:
        print("[SUCCESS] Notebook passes 100% of academic and structural compliance standards!")
        sys.exit(0)
    else:
        print("[WARNING] Compliance issues detected. Please review warnings above.")
        sys.exit(1)

if __name__ == "__main__":
    verify_notebook()
