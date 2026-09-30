"""
test_cells_syntax.py
Compiles all code cells across sections to verify syntax validity before execution.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from qta404_builder.sections_part1 import build_sections_part1
from qta404_builder.sections_part2 import build_sections_part2
from qta404_builder.sections_part3 import build_sections_part3
from qta404_builder.sections_part4 import build_sections_part4

cells = build_sections_part1() + build_sections_part2() + build_sections_part3() + build_sections_part4()
code_cells = [c for c in cells if c.cell_type == 'code']

print(f"Total code cells to check: {len(code_cells)}")
errors = []

for idx, c in enumerate(code_cells):
    try:
        compile(c.source, f"Cell_{idx+1}", 'exec')
    except Exception as e:
        errors.append((idx + 1, e, c.source))

if errors:
    print(f"❌ Found {len(errors)} syntax errors:")
    for cell_num, err, src in errors:
        print(f"\n--- Cell #{cell_num} Error: {err} ---")
        lines = src.splitlines()
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line}")
else:
    print("✅ ALL CODE CELLS COMPILED WITH ZERO SYNTAX ERRORS!")
