# Notebook Development Workflow

This workflow guides the step-by-step authoring and execution of SignalBrief research notebooks (00 through 10).

## 10 Mandatory Sections per Notebook

Every notebook in `notebooks/` must strictly implement the following 10 sections:

1. **Title, Project Context & Objectives**: Clear scope, rationale, and alignment with the SignalBrief mission.
2. **Learning & Business Objectives**: What analytical or technical goal this notebook achieves.
3. **Research Questions & Methodology**: Specific hypotheses, analytical algorithms, and methods applied.
4. **Libraries & Dependencies**: Clean import cell with verified package versions and determinism seeds where relevant.
5. **Input Data Description**: File formats, schemas, expected row counts, data sources, and sanity checks.
6. **Step-by-Step Implementation**:
   - Every significant code cell must have Markdown before it explaining *why* the method is used and *what* it does.
   - Every significant code cell must have Markdown after it explaining *how to interpret* the output.
   - Keep cells focused; avoid giant monolithic blocks.
7. **Output Interpretation & Visualizations**: Charts, tables, or metric distributions with explicit textual analysis.
8. **Errors, Limitations & Assumptions**: Known caveats, edge cases, quota bounds, or failure modes.
9. **Summary of Findings**: Bulleted summary of validated findings and decisions made.
10. **Next Notebook's Input and Expected Output**: Clean handoff contract to the subsequent notebook stage.

## Execution Quality Checklist

- [ ] Execute top-to-bottom sequentially (`Restart Kernel and Run All Cells`).
- [ ] No unhandled exceptions or broken output streams.
- [ ] No API keys, credentials, or private personal data printed in cell outputs.
- [ ] Synthetic or mock data is explicitly annotated with `[SYNTHETIC DATA]`.
- [ ] Output artifacts (e.g. clean JSON, figures, HTML previews) are written to their respective `data/` or `reports/` paths.
- [ ] Notebook file is saved with rendered outputs for full reproducibility.
