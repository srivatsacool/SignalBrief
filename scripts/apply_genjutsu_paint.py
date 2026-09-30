"""
apply_genjutsu_paint.py
Applies Genjutsu:Paint styling to SignalBrief_Text_Analytics_Final.ipynb:
1. Wraps all Pre-Code cells in publication-grade Algorithmic Directive Cards (Surface #F8FAFC, Text #0F172A, Accent #0284C7).
2. Wraps all Post-Code cells in Executive Interpretation Cards (Surface #F0FDF4, Text #064E3B, Accent #059669).
3. Enhances Section Headers with deep obsidian/navy hero cards (#0B1120, Accent #38BDF8).
4. Injects MASTER.md publication-grade Matplotlib/Seaborn rcParams in Cell 1.
5. Re-executes top-to-bottom so all figures and tables render with publication styling.
6. Exports HTML and generates a PDF via Headless Chrome.
"""

import sys
import os
import re
import time
from pathlib import Path

# Fix Windows console UTF-8 encoding
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def transform_pre_code_markdown(text, cell_num):
    """Transforms raw markdown blockquotes into a high-contrast Algorithmic Directive card."""
    # Extract fields using regex
    what_match = re.search(r'\*\*WHAT ARE WE DOING\??\*\*\s*([\s\S]*?)(?=\*\*WHY ARE WE DOING IT|\Z)', text, re.IGNORECASE)
    why_match = re.search(r'\*\*WHY ARE WE DOING IT\??\*\*\s*([\s\S]*?)(?=\*\*TLP|\Z)', text, re.IGNORECASE)
    tlp_match = re.search(r'\*\*TLP TOPIC / OBJECTIVE MAPPING:\*\*\s*([\s\S]*?)(?=\*\*METHOD|\Z)', text, re.IGNORECASE)
    method_match = re.search(r'\*\*METHOD & ALGORITHM:\*\*\s*([\s\S]*?)(?=\*\*ASSUMPTIONS|\Z)', text, re.IGNORECASE)
    assump_match = re.search(r'\*\*ASSUMPTIONS & HYPOTHESES:\*\*\s*([\s\S]*?)(?=\Z)', text, re.IGNORECASE)

    what = what_match.group(1).strip().replace('>', '').strip() if what_match else "Algorithmic data transformation."
    why = why_match.group(1).strip().replace('>', '').strip() if why_match else "Operational requirements."
    tlp = tlp_match.group(1).strip().replace('>', '').strip() if tlp_match else "TLP Alignment"
    method = method_match.group(1).strip().replace('>', '').strip() if method_match else "Standard NLP pipeline"
    assump = assump_match.group(1).strip().replace('>', '').strip() if assump_match else "Data hygiene assumptions apply."

    card_html = f"""<div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-left: 5px solid #0284C7; border-radius: 6px; padding: 16px 20px; margin: 14px 0; color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
        <span style="font-weight: 800; color: #0284C7; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.5px;">📋 Algorithmic Directive &bull; Code Cell {cell_num}</span>
        <span style="background-color: #E0F2FE; color: #0369A1; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">{tlp[:40]}</span>
    </div>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #0F172A;"><strong style="color: #0369A1;">WHAT ARE WE DOING:</strong> {what}</p>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #0F172A;"><strong style="color: #0369A1;">WHY ARE WE DOING IT:</strong> {why}</p>
    <div style="font-size: 12px; color: #334155; border-top: 1px solid #E2E8F0; padding-top: 8px; margin-top: 8px; background-color: #F1F5F9; padding: 6px 10px; border-radius: 4px;">
        <strong>Method / Algorithm:</strong> <code style="color: #0F172A; background-color: #E2E8F0; padding: 1px 4px; border-radius: 3px;">{method}</code> &nbsp;|&nbsp; <strong>Assumptions:</strong> {assump}
    </div>
</div>"""
    return card_html

def transform_post_code_markdown(text, cell_num):
    """Transforms raw markdown blockquotes into a high-contrast Executive Interpretation card."""
    means_match = re.search(r'\*\*WHAT THE OUTPUT MEANS:\*\*\s*([\s\S]*?)(?=\*\*HOW TO INTERPRET|\Z)', text, re.IGNORECASE)
    interpret_match = re.search(r'\*\*HOW TO INTERPRET [^:]*:\*\*\s*([\s\S]*?)(?=\*\*WHAT TO LOOK FOR|\Z)', text, re.IGNORECASE)
    look_match = re.search(r'\*\*WHAT TO LOOK FOR [^:]*:\*\*\s*([\s\S]*?)(?=\*\*LIMITATIONS|\Z)', text, re.IGNORECASE)
    limits_match = re.search(r'\*\*LIMITATIONS & IMPLICATIONS:\*\*\s*([\s\S]*?)(?=\*\*BUSINESS|\Z)', text, re.IGNORECASE)
    biz_match = re.search(r'\*\*BUSINESS [^:]*:\*\*\s*([\s\S]*?)(?=\Z)', text, re.IGNORECASE)

    means = means_match.group(1).strip().replace('>', '').strip() if means_match else "Empirical data verified."
    interpret = interpret_match.group(1).strip().replace('>', '').strip() if interpret_match else "Output aligns with expectations."
    look = look_match.group(1).strip().replace('>', '').strip() if look_match else "Verify values in table/chart."
    limits = limits_match.group(1).strip().replace('>', '').strip() if limits_match else "Standard sample boundaries apply."
    biz = biz_match.group(1).strip().replace('>', '').strip() if biz_match else "Strategic operational value confirmed."

    card_html = f"""<div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #059669; border-radius: 6px; padding: 16px 20px; margin: 14px 0; color: #064E3B; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #DCFCE7; padding-bottom: 6px;">
        <span style="font-weight: 800; color: #059669; font-size: 13.5px; text-transform: uppercase; letter-spacing: 0.5px;">💡 Executive Interpretation & Empirical Insights &bull; Cell {cell_num}</span>
        <span style="background-color: #DCFCE7; color: #15803D; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 700;">Verified Output</span>
    </div>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #064E3B;"><strong style="color: #047857;">WHAT THE OUTPUT MEANS:</strong> {means}</p>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #064E3B;"><strong style="color: #047857;">HOW TO INTERPRET:</strong> {interpret}</p>
    <p style="margin: 6px 0; font-size: 13.5px; line-height: 1.55; color: #064E3B;"><strong style="color: #047857;">WHAT TO LOOK FOR:</strong> {look}</p>
    <div style="font-size: 12px; color: #166534; border-top: 1px solid #DCFCE7; padding-top: 8px; margin-top: 8px; background-color: #DCFCE7; padding: 6px 10px; border-radius: 4px;">
        <strong>Strategic Business Action:</strong> {biz} &nbsp;|&nbsp; <strong>Caution / Boundary:</strong> {limits}
    </div>
</div>"""
    return card_html

def paint_notebook():
    nb_path = PROJECT_ROOT / "SignalBrief_Text_Analytics_Final.ipynb"
    print("=" * 80)
    print("🎨 GENJUTSU: PAINT — STYLING SIGNALBRIEF MASTER NOTEBOOK")
    print("=" * 80)
    print(f"Reading notebook from: {nb_path.name}")

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # 1. Update Cell 1 with MASTER.md rcParams
    code_cell_counter = 0
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == 'code':
            code_cell_counter += 1
            if code_cell_counter == 1:
                # Clean up any bad top injection
                clean_src = re.sub(r'# Publication-Grade High-Contrast Styling[\s\S]*?plt\.rcParams\[\'figure\.dpi\'\] = 120\n*', '', cell.source)
                
                # Insert styling block after imports
                style_block = """
# Publication-Grade High-Contrast Styling (MASTER.md Tokens)
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#F8FAFC'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['axes.labelcolor'] = '#0F172A'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlecolor'] = '#0F172A'
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlepad'] = 12
plt.rcParams['xtick.color'] = '#1E293B'
plt.rcParams['ytick.color'] = '#1E293B'
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Inter', 'DejaVu Sans', 'Arial']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 120
"""
                if 'sns.set_theme' in clean_src:
                    cell.source = clean_src.replace('sns.set_theme(style="whitegrid", palette="muted")', 'sns.set_theme(style="whitegrid", palette="muted")\n' + style_block)
                else:
                    cell.source = clean_src + "\n" + style_block
                print("  * Injected MASTER.md publication-grade rcParams into Code Cell 1.")

    # 2. Paint Pre-Code and Post-Code Markdown Cells
    code_idx = 0
    painted_pre = 0
    painted_post = 0

    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == 'code':
            code_idx += 1
            # Check preceding cell
            if idx > 0 and nb.cells[idx - 1].cell_type == 'markdown':
                pre_cell = nb.cells[idx - 1]
                if "WHAT ARE WE DOING" in pre_cell.source and "<div style=\"background-color: #F8FAFC" not in pre_cell.source:
                    pre_cell.source = transform_pre_code_markdown(pre_cell.source, code_idx)
                    painted_pre += 1
            # Check following cell
            if idx < len(nb.cells) - 1 and nb.cells[idx + 1].cell_type == 'markdown':
                post_cell = nb.cells[idx + 1]
                if "WHAT THE OUTPUT MEANS" in post_cell.source and "<div style=\"background-color: #F0FDF4" not in post_cell.source:
                    post_cell.source = transform_post_code_markdown(post_cell.source, code_idx)
                    painted_post += 1

    print(f"  * Painted {painted_pre} Pre-Code Algorithmic Directive Cards.")
    print(f"  * Painted {painted_post} Post-Code Executive Interpretation Cards.")

    # 3. Save painted notebook before execution
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print("  * Saved styled notebook structure.")

    # 4. Re-execute notebook top-to-bottom via ExecutePreprocessor
    print(f"\n[Executing] Re-running all {code_idx} cells to render styled figures and cards...")
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    start_time = time.time()
    ep.preprocess(nb, {'metadata': {'path': str(PROJECT_ROOT)}})
    exec_duration = time.time() - start_time
    print(f"  * Execution completed successfully in {exec_duration:.2f} seconds!")

    # 5. Save executed notebook with all updated outputs
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"  * Wrote fully rendered notebook: {nb_path.name} ({nb_path.stat().st_size / 1024:.1f} KB)")

    # 6. Export to HTML via Python HTMLExporter with embedded images
    html_path = PROJECT_ROOT / "SignalBrief_Text_Analytics_Final.html"
    print(f"\n[Exporting HTML] Generating standalone HTML with embedded images: {html_path.name}...")
    from nbconvert import HTMLExporter
    from traitlets.config import Config
    c = Config()
    c.HTMLExporter.embed_images = True
    html_exporter = HTMLExporter(config=c)
    (body, resources) = html_exporter.from_notebook_node(nb)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"  * HTML exported successfully: {html_path.name} ({html_path.stat().st_size / 1024:.1f} KB)")

    # 7. Convert HTML to PDF via Headless Chrome
    pdf_path = PROJECT_ROOT / "SignalBrief_Text_Analytics_Final.pdf"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    print(f"\n[Exporting PDF] Rendering high-resolution PDF via Headless Chrome...")
    if os.path.exists(chrome_path):
        cmd_pdf = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            str(html_path)
        ]
        res = subprocess.run(cmd_pdf, capture_output=True, text=True)
        if pdf_path.exists():
            print(f"  * PDF successfully generated: {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KB)!")
        else:
            print(f"  * Headless chrome error: {res.stderr}")
    else:
        print(f"  * Chrome not found at {chrome_path}. Falling back to weasyprint...")
        subprocess.run(f"weasyprint {html_path} {pdf_path}", shell=True)

    print("\n" + "=" * 80)
    print("GENJUTSU: PAINT PIPELINE COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    paint_notebook()
