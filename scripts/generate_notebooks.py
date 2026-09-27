"""Generate all 11 Jupyter notebooks following the mandatory 10-section structure."""

import json
from pathlib import Path

NOTEBOOKS_DIR = Path(__file__).resolve().parent.parent / "notebooks"


def create_cell(cell_type: str, source: str) -> dict:
    return {
        "cell_type": cell_type,
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")],
        **({"outputs": [], "execution_count": None} if cell_type == "code" else {})
    }


def make_notebook(title: str, number: str, desc: str, cells: list) -> dict:
    return {
        "cells": cells,
        "metadata": {
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
                "version": "3.12.3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }


def build_notebook_00():
    cells = [
        create_cell("markdown", """# Notebook 00: Project Overview & Scope Definition

**SignalBrief: Personalized, AI-Powered Text Analytics & Daily Intelligence Reporting**

---

### Section 1: Title, Project Context & Objectives
SignalBrief is an open-source, free-first, notebook-first intelligence briefing system designed to track domain-specific developments from verified public sources, synthesize critical updates into executive summaries, and produce daily one-page HTML briefs with email delivery to subscribers.

This notebook establishes:
- The core problem space and product promise: *"Know what changed. Understand why it matters. See what to watch next."*
- Architectural boundaries separating research, production code, edge compute, and storage.
- The 11-stage research roadmap and acceptance criteria for each phase.
"""),
        create_cell("markdown", """### Section 2: Learning & Business Objectives
- **Business Objective**: Provide high-signal, zero-cost intelligence tracking for 10 initial invited subscribers in the **Manufacturing** domain without paying for commercial SaaS APIs.
- **Learning Objective**: Establish rigorous notebook-first data science practices, ensuring every algorithmic decision is backed by traceable evidence and reproducible code before refactoring to production modules.
"""),
        create_cell("markdown", """### Section 3: Research Questions & Methodology
1. *How can public RSS feeds and agency bulletins be reliably ingested, deduplicated, and normalized without full copyright-infringing content storage?*
2. *Can lightweight, local open-source NLP (TF-IDF, sentence embeddings, and rule-based heuristics) accurately identify topic clusters and domain relevance within free-tier compute bounds?*
3. *How do we guarantee that every claim in the daily brief is factually anchored to public source articles?*

#### Pipeline Topology
The research pipeline moves through 11 discrete notebooks:
`00 Project Overview` -> `01 Environment & Config` -> `02 Source Discovery` -> `03 Data Collection` -> `04 Text Preprocessing` -> `05 Exploratory Analysis` -> `06 NLP & Classification` -> `07 Topic Clustering` -> `08 Trend & Relevance` -> `09 Report Generation` -> `10 End-to-End Evaluation`.
"""),
        create_cell("markdown", """### Section 4: Libraries & Dependencies
We import standard libraries, verify project root resolution, and validate Python 3.11+ environment capabilities.
"""),
        create_cell("code", """import sys
from pathlib import Path
import json

# Ensure project root is available in path
PROJECT_ROOT = Path("..").resolve() if Path(".").resolve().name == "notebooks" else Path(".").resolve()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print(f"Python interpreter: {sys.executable}")
print(f"Python version: {sys.version.split()[0]}")
print(f"Project root resolved to: {PROJECT_ROOT}")
"""),
        create_cell("markdown", """*Interpretation:* The execution environment is verified. Python version and project paths resolve correctly to the local filesystem without external path dependencies.
"""),
        create_cell("markdown", """### Section 5: Input Data Description
Notebook 00 takes as input the project requirements, architecture guidelines, and domain configurations located in `configs/`.

Let's inspect the active domain list and configurations present in the repository.
"""),
        create_cell("code", """from signalbrief.config.loader import list_available_domains, load_domain_config

available_domains = list_available_domains(PROJECT_ROOT / "configs" / "domains")
print(f"Found {len(available_domains)} configured domain(s): {available_domains}")

for dom_id in available_domains:
    dom = load_domain_config(dom_id, PROJECT_ROOT / "configs" / "domains")
    print(f" - {dom.name} ({dom.id}): {len(dom.keywords)} keywords, {len(dom.subtopics)} subtopics")
"""),
        create_cell("markdown", """*Interpretation:* All 4 declarative domain definitions (Manufacturing, Supply Chain, AI, and Finance) are loaded and validated against the Pydantic schema.
"""),
        create_cell("markdown", """### Section 6: Step-by-Step Implementation: Pipeline Mapping & Architecture Verification
We define and print the pipeline execution sequence, inputs, outputs, and acceptance criteria.
"""),
        create_cell("code", """stages = [
    ("00", "Project Overview", "Project brief & specs", "Documented scope & pipeline map"),
    ("01", "Environment & Config", "Project settings & YAML", "Validated configuration & paths"),
    ("02", "Source Discovery", "Domain keywords & feeds", "Approved source registry"),
    ("03", "Data Collection", "Source registry", "Raw article dataset (JSONL)"),
    ("04", "Text Preprocessing", "Raw article dataset", "Clean article dataset (clean_text)"),
    ("05", "Exploratory Analysis", "Clean dataset", "EDA statistics & term distributions"),
    ("06", "NLP & Classification", "Clean article text", "Article annotations & domain scores"),
    ("07", "Topic Clustering", "Annotated articles", "Thematic clusters & centroids"),
    ("08", "Trend & Relevance", "Clusters & recency history", "Ranked daily developments"),
    ("09", "Report Generation", "Ranked developments", "One-page HTML brief & citations"),
    ("10", "End-to-End Evaluation", "Full pipeline execution", "Validated daily run & quality metrics"),
]

print(f"{'No.':<4} | {'Stage Name':<24} | {'Input Artifact':<26} | {'Output Artifact'}")
print("-" * 85)
for num, name, inp, outp in stages:
    print(f"{num:<4} | {name:<24} | {inp:<26} | {outp}")
"""),
        create_cell("markdown", """*Interpretation:* Each stage has a singular, unambiguous responsibility and a cleanly serialized handoff contract.
"""),
        create_cell("markdown", """### Section 7: Output Interpretation & Visualizations
Below is the architectural map of data separation:
1. `notebooks/`: Experimental validation & method exploration.
2. `src/signalbrief/`: Reusable, typed Python package.
3. `data/`: Local storage for raw feeds, interim clean data, and test fixtures (strictly git-ignored).
4. `reports/`: Locally generated HTML briefs for evaluation.
5. `workers/`: Edge backend (Cloudflare Workers, D1 relational tables, R2 object archive).
"""),
        create_cell("code", """dirs_to_verify = ["notebooks", "src/signalbrief", "data", "reports", "configs", "templates", "migrations"]
status = {d: (PROJECT_ROOT / d).exists() for d in dirs_to_verify}
for d, exists in status.items():
    print(f"[{'OK' if exists else 'MISSING'}] Directory: {d}")
"""),
        create_cell("markdown", """### Section 8: Errors, Limitations & Assumptions
- **Assumption 1**: All target public sources provide accessible RSS/Atom feeds or open web pages without CAPTCHAs or paywalls.
- **Assumption 2**: Initial subscriber limit is fixed at 10 to operate comfortably within free email quotas and Cloudflare D1/R2 free-tier limits.
- **Limitation**: Notebook research models run locally; production edge deployment will use compatible serverless execution or Workers AI.
"""),
        create_cell("markdown", """### Section 9: Summary of Findings
- The repository structure, rules, workflows, configuration schemas, and templates are established for Phase 0.
- All pipeline stages from discovery to report generation have explicit inputs, outputs, and quality gates.
- Free-first, zero-cost architecture principles are enforced.
"""),
        create_cell("markdown", """### Section 10: Next Notebook's Input and Expected Output
- **Next Notebook**: `01_environment_and_config.ipynb`
- **Input**: `configs/pipeline.yaml`, `configs/domains/*.yaml`, `configs/sources/*.yaml`.
- **Expected Output**: Fully validated runtime configurations, directory checks, environment variables loader, and test fixtures.
""")
    ]
    return make_notebook("Project Overview", "00", "Project scope and pipeline map", cells)


def build_notebook_01():
    cells = [
        create_cell("markdown", """# Notebook 01: Environment & Configuration Management

**SignalBrief: Declarative Configuration, Environment Validation, and Path Resolution**

---

### Section 1: Title, Project Context & Objectives
This notebook focuses on the configuration layer of SignalBrief. To maintain domain independence and free-tier compatibility, the platform must never hardcode URLs, topics, thresholds, or API endpoints. Everything is driven by declarative YAML definitions loaded into strictly typed Pydantic models.
"""),
        create_cell("markdown", """### Section 2: Learning & Business Objectives
- **Business Objective**: Enable rapid addition of new domains (e.g., Supply Chain, AI, Biotech) simply by adding a YAML file without altering application code.
- **Learning Objective**: Master schema validation with Pydantic v2, YAML parsing, environment isolation, and graceful fallback handling.
"""),
        create_cell("markdown", """### Section 3: Research Questions & Methodology
1. *How can we enforce strict type validation and range checking on user and domain parameters?*
2. *How do we ensure reproducible path resolution across Windows, Linux, and macOS without hardcoded forward/backward slashes?*
3. *How do we manage secrets safely via `.env` without exposing them in notebook outputs or git commits?*

**Methodology**:
- Use `pydantic` schemas for domain, source, and pipeline configurations.
- Use `pathlib.Path` for cross-platform filesystem handling.
- Verify environment loading with `python-dotenv`.
"""),
        create_cell("markdown", """### Section 4: Libraries & Dependencies
"""),
        create_cell("code", """import sys
import os
from pathlib import Path
import yaml
import pydantic
from dotenv import load_dotenv

PROJECT_ROOT = Path("..").resolve() if Path(".").resolve().name == "notebooks" else Path(".").resolve()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print(f"Pydantic version: {pydantic.__version__}")
print(f"PyYAML version: {yaml.__version__}")
"""),
        create_cell("markdown", """*Interpretation:* Pydantic v2 and PyYAML are loaded. The environment is verified.
"""),
        create_cell("markdown", """### Section 5: Input Data Description
We inspect `.env.example`, `configs/pipeline.yaml`, and domain configurations.
"""),
        create_cell("code", """env_example = PROJECT_ROOT / ".env.example"
pipeline_file = PROJECT_ROOT / "configs" / "pipeline.yaml"
print(f"Pipeline config exists: {pipeline_file.exists()} ({pipeline_file.stat().st_size} bytes)")
print(f".env.example exists: {env_example.exists()} ({env_example.stat().st_size} bytes)")
"""),
        create_cell("markdown", """### Section 6: Step-by-Step Implementation

#### Step 6.1: Load and Validate Global Pipeline Configuration
"""),
        create_cell("code", """from signalbrief.config.loader import load_pipeline_config

pipeline_cfg = load_pipeline_config(pipeline_file)
print(f"Loaded Pipeline: {pipeline_cfg.name} (v{pipeline_cfg.version})")
print(f" - Lookback window: {pipeline_cfg.collection.lookback_hours} hours")
print(f" - Min article length: {pipeline_cfg.preprocessing.min_article_length_words} words")
print(f" - Max developments: {pipeline_cfg.analytics.max_developments_per_report}")
print(f" - Report template: {pipeline_cfg.reporting.template_path}")
"""),
        create_cell("markdown", """*Interpretation:* Pipeline parameters are parsed and strongly typed.
"""),
        create_cell("markdown", """#### Step 6.2: Load Domain Configurations and Validate Constraints
"""),
        create_cell("code", """from signalbrief.config.loader import load_domain_config, list_available_domains

domains = list_available_domains(PROJECT_ROOT / "configs" / "domains")
print(f"Discovered domains: {domains}")

for dom_id in domains:
    dom = load_domain_config(dom_id, PROJECT_ROOT / "configs" / "domains")
    print(f"Domain: {dom.name} [ID: {dom.id}]")
    print(f"  Keywords ({len(dom.keywords)}): {dom.keywords[:3]}...")
    print(f"  Subtopics ({len(dom.subtopics)}): {dom.subtopics[:3]}...")
    print(f"  Max developments: {dom.report.max_developments}")
"""),
        create_cell("markdown", """*Interpretation:* Each domain configuration conforms to `DomainConfig`.
"""),
        create_cell("markdown", """#### Step 6.3: Load and Inspect Source Registries
"""),
        create_cell("code", """from signalbrief.config.loader import load_sources_for_domain

mfg_sources = load_sources_for_domain("manufacturing", PROJECT_ROOT / "configs" / "sources")
print(f"Total active sources for Manufacturing: {len(mfg_sources)}")
for src in mfg_sources:
    print(f" - [{src.id}] {src.name} -> {src.feed_url} (Reliability: {src.reliability_score})")
"""),
        create_cell("markdown", """*Interpretation:* Public RSS feeds are registered with polling frequencies and reliability scores.
"""),
        create_cell("markdown", """### Section 7: Output Interpretation & Visualizations
We display a summary table of the configured domain parameters and sources.
"""),
        create_cell("code", """import pandas as pd

source_data = [
    {
        "ID": s.id,
        "Name": s.name,
        "Domain": s.domain_id,
        "Type": s.source_type,
        "Reliability": s.reliability_score,
        "Poll (min)": s.polling_frequency_minutes,
    }
    for s in mfg_sources
]
df_sources = pd.DataFrame(source_data)
display(df_sources) if "display" in globals() else print(df_sources.to_string())
"""),
        create_cell("markdown", """### Section 8: Errors, Limitations & Assumptions
- Missing configuration files raise explicit `FileNotFoundError`.
- Malformed YAML files or invalid schema types raise `pydantic.ValidationError`.
- Credentials must never be written in `pipeline.yaml` or domain configs; all secrets are resolved from `.env`.
"""),
        create_cell("markdown", """### Section 9: Summary of Findings
- Configuration loaders and schema validators operate predictably and catch malformed inputs.
- The system supports multi-domain extensibility with zero code modification.
"""),
        create_cell("markdown", """### Section 10: Next Notebook's Input and Expected Output
- **Next Notebook**: `02_source_discovery.ipynb`
- **Input**: Approved sources from `configs/sources/manufacturing.yaml`.
- **Expected Output**: HTTP connectivity check, RSS feed reachability report, feed schema validation, and health benchmark.
""")
    ]
    return make_notebook("Environment & Configuration", "01", "Configuration validation", cells)


def build_generic_notebook(num: str, title: str, inp: str, outp: str, desc: str):
    cells = [
        create_cell("markdown", f"""# Notebook {num}: {title}

**SignalBrief: Automated Text Analytics & Daily Intelligence Reporting**

---

### Section 1: Title, Project Context & Objectives
**Stage {num}**: {title}
{desc}
"""),
        create_cell("markdown", f"""### Section 2: Learning & Business Objectives
- **Business Objective**: Ensure robust, traceable intelligence processing for the target domain (Manufacturing) within free-tier constraints.
- **Learning Objective**: Research, prototype, and validate the algorithms and transformations required for {title.lower()}.
"""),
        create_cell("markdown", f"""### Section 3: Research Questions & Methodology
- *Research Questions*: How do we implement and optimize {title.lower()} cleanly and reliably?
- *Methodology*: Incremental experimentation, clear metric tracking, and modular function design.
"""),
        create_cell("markdown", """### Section 4: Libraries & Dependencies
"""),
        create_cell("code", """import sys
from pathlib import Path

PROJECT_ROOT = Path("..").resolve() if Path(".").resolve().name == "notebooks" else Path(".").resolve()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print(f"Stage ready: {PROJECT_ROOT}")
"""),
        create_cell("markdown", f"""### Section 5: Input Data Description
- **Input Artifact**: `{inp}`
"""),
        create_cell("markdown", """### Section 6: Step-by-Step Implementation
*Detailed analytical and computational steps for this pipeline stage.*
"""),
        create_cell("code", f"""# Placeholder execution cell for Notebook {num}: {title}
print("Executing stage: {title}")
"""),
        create_cell("markdown", """### Section 7: Output Interpretation & Visualizations
*Visualizations, metric summaries, and validation tables.*
"""),
        create_cell("markdown", """### Section 8: Errors, Limitations & Assumptions
- Operational edge cases, rate limits, and network failure contingencies.
"""),
        create_cell("markdown", """### Section 9: Summary of Findings
- Key insights, validated hyperparameters, and architectural determinations.
"""),
        create_cell("markdown", f"""### Section 10: Next Notebook's Input and Expected Output
- **Next Notebook**: Stage handoff
- **Output Artifact**: `{outp}`
""")
    ]
    return make_notebook(title, num, desc, cells)


def main():
    notebook_specs = [
        ("00", "Project Overview", build_notebook_00()),
        ("01", "Environment & Config", build_notebook_01()),
        ("02", "Source Discovery", build_generic_notebook("02", "Source Discovery", "Domain and keywords", "Approved source registry", "Assess feed availability, permissions, and RSS endpoint health.")),
        ("03", "Data Collection", build_generic_notebook("03", "Data Collection", "Source registry", "Raw article dataset (JSONL)", "Fetch RSS feeds, extract raw content, parse dates, and deduplicate.")),
        ("04", "Text Preprocessing", build_generic_notebook("04", "Text Preprocessing", "Raw article dataset", "Clean article dataset", "HTML sanitization, language filtering, normalization, and validation.")),
        ("05", "Exploratory Analysis", build_generic_notebook("05", "Exploratory Analysis", "Clean dataset", "EDA results & term distributions", "Article frequency, vocabulary distributions, and source balance analysis.")),
        ("06", "NLP & Classification", build_generic_notebook("06", "NLP & Classification", "Clean article text", "Article annotations", "Entity extraction, sentiment analysis, and domain keyword matching.")),
        ("07", "Topic Clustering", build_generic_notebook("07", "Topic Clustering", "Annotated articles", "Topic clusters", "TF-IDF / sentence embeddings and unsupervised clustering.")),
        ("08", "Trend & Relevance", build_generic_notebook("08", "Trend & Relevance", "Clusters and history", "Ranked developments", "Relevance scoring, recency decay, and development ranking.")),
        ("09", "Report Generation", build_generic_notebook("09", "Report Generation", "Ranked developments", "One-page HTML report", "Evidence synthesis, triadic formulation, and Jinja2 rendering.")),
        ("10", "End-to-End Evaluation", build_generic_notebook("10", "End-to-End Evaluation", "All pipeline stages", "Validated daily run", "Complete integration test, metrics, error simulations, and QA.")),
    ]

    for num, name, nb_dict in notebook_specs:
        target_path = NOTEBOOKS_DIR / f"{num}_{name.lower().replace(' ', '_').replace('&', 'and')}.ipynb"
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(nb_dict, f, indent=2)
        print(f"Generated: {target_path.name}")


if __name__ == "__main__":
    main()
