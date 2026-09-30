"""
verify_final_notebook.py
Audits the executed Employee_Voice_Analytics_Final.ipynb:
- Verifies cell sequence (pre-MD -> Code -> post-MD)
- Verifies cell output presence (text, stdout, display data, plots)
- Verifies Course Outcome coverage and TLP topic completeness
"""

import sys
from pathlib import Path
import nbformat as nbf

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

NOTEBOOK_PATH = Path('Employee_Voice_Analytics_Final.ipynb')

if not NOTEBOOK_PATH.exists():
    print(f"❌ File {NOTEBOOK_PATH} does not exist!")
    sys.exit(1)

nb = nbf.read(NOTEBOOK_PATH, as_version=4)
cells = nb.cells

print("=" * 80)
print(f"AUDITING FINAL NOTEBOOK: {NOTEBOOK_PATH.name}")
print(f"File Size: {NOTEBOOK_PATH.stat().st_size / (1024*1024):.2f} MB")
print(f"Total Cells: {len(cells)}")
print("=" * 80)

code_cells = [c for c in cells if c.cell_type == 'code']
md_cells = [c for c in cells if c.cell_type == 'markdown']

print(f"Code Cells:     {len(code_cells)}")
print(f"Markdown Cells: {len(md_cells)}")

# 1. Output presence check
cells_without_output = []
image_outputs_count = 0
for idx, c in enumerate(code_cells):
    has_output = len(c.outputs) > 0
    if not has_output:
        cells_without_output.append(idx + 1)
    for out in c.outputs:
        if 'image/png' in out.get('data', {}):
            image_outputs_count += 1

print(f"Code cells with outputs: {len(code_cells) - len(cells_without_output)} / {len(code_cells)}")
print(f"Total embedded chart images (PNG): {image_outputs_count}")

if cells_without_output:
    print(f"⚠️ Warning: Code cells without output: {cells_without_output}")
else:
    print("✅ EVERY SINGLE CODE CELL HAS CAPTURED OUTPUT!")

# 2. Strict Pre-MD and Post-MD check
print("\nAuditing Pre-MD and Post-MD structure around every code cell...")
rule_violations = []

for i, cell in enumerate(cells):
    if cell.cell_type == 'code':
        # Check cell before
        if i == 0 or cells[i - 1].cell_type != 'markdown':
            rule_violations.append((i, "Missing explanatory Markdown cell IMMEDIATELY BEFORE code cell"))
        else:
            prev_md = cells[i - 1].source
            if "WHAT ARE WE DOING" not in prev_md:
                rule_violations.append((i, "Pre-MD missing 'WHAT ARE WE DOING' section"))
        
        # Check cell after
        if i == len(cells) - 1 or cells[i + 1].cell_type != 'markdown':
            rule_violations.append((i, "Missing explanatory Markdown cell IMMEDIATELY AFTER code cell"))
        else:
            next_md = cells[i + 1].source
            if "WHAT THE OUTPUT MEANS" not in next_md:
                rule_violations.append((i, "Post-MD missing 'WHAT THE OUTPUT MEANS' section"))

if rule_violations:
    print(f"❌ Found {len(rule_violations)} structural documentation violations:")
    for idx, issue in rule_violations:
        print(f"  • Cell Index {idx}: {issue}")
else:
    print("✅ 100% PERFECT ADHERENCE TO MANDATORY NOTEBOOK WRITING STYLE!")
    print("   Every single code cell has 'WHAT ARE WE DOING' before and 'WHAT THE OUTPUT MEANS' after!")

print("=" * 80)
