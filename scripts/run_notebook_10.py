"""Execute Notebook 10 top-to-bottom and save populated outputs and evaluation report."""

import json
from pathlib import Path
import nbformat
from nbclient import NotebookClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "10_end_to_end_evaluation.ipynb"
EVAL_REPORT_PATH = PROJECT_ROOT / "data" / "evaluation" / "phase1_evaluation_report.json"


def main():
    print(f"Reading notebook from: {NOTEBOOK_PATH}")
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    client = NotebookClient(
        nb,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOK_PATH.parent)}},
    )

    print("Executing Notebook 10...")
    client.execute()

    print(f"Writing executed notebook to: {NOTEBOOK_PATH}")
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    print("Notebook executed and saved successfully.")

    if EVAL_REPORT_PATH.exists():
        with open(EVAL_REPORT_PATH, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        print("\nSerialized Phase 1 Evaluation Report:")
        print(json.dumps(report_data, indent=2))
        assert report_data["all_acceptance_criteria_passed"] is True, "Evaluation report has failed criteria!"
        print("\nSUCCESS: All 10 acceptance criteria passed in evaluation report!")
    else:
        raise FileNotFoundError(f"Evaluation report not found at {EVAL_REPORT_PATH}")


if __name__ == "__main__":
    main()
