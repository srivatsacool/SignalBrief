#!/usr/bin/env python3
"""Environment and setup validation script for SignalBrief Phase 0."""

import sys
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

def main():
    print("=" * 60)
    print("SignalBrief Phase 0 Environment & Integrity Validator")
    print("=" * 60)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # 1. Python version check
    py_ver = sys.version_info
    print(f"Python version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver < (3, 11):
        print("ERROR: Python 3.11 or greater is required.")
        sys.exit(1)
    print("[OK] Python version is compatible (>= 3.11)")

    # 2. Check essential directories
    required_dirs = [
        ".antigravity/rules",
        ".antigravity/workflows",
        ".github/workflows",
        "notebooks",
        "src/signalbrief",
        "web",
        "workers",
        "templates/reports",
        "templates/emails",
        "configs/domains",
        "configs/sources",
        "data/raw",
        "data/interim",
        "data/processed",
        "data/evaluation",
        "data/samples",
        "reports/generated",
        "reports/previews",
        "tests/unit",
        "migrations",
        "docs",
    ]
    for d in required_dirs:
        p = REPO_ROOT / d
        if not p.is_dir():
            print(f"ERROR: Missing directory: {d}")
            sys.exit(1)
    print(f"[OK] All {len(required_dirs)} core directories exist.")

    # 3. Check critical files
    required_files = [
        ".gitignore",
        "LICENSE",
        "README.md",
        "CONTRIBUTING.md",
        ".env.example",
        "pyproject.toml",
        "requirements.txt",
        "wrangler.toml",
        ".antigravity/rules/project_rules.md",
        ".antigravity/rules/notebook_rules.md",
        ".antigravity/rules/coding_rules.md",
        ".antigravity/rules/deployment_rules.md",
        "configs/pipeline.yaml",
        "configs/domains/manufacturing.yaml",
        "configs/sources/manufacturing.yaml",
        "migrations/0001_initial_schema.sql",
        "templates/reports/daily_report.html.jinja2",
    ]
    for f in required_files:
        p = REPO_ROOT / f
        if not p.is_file():
            print(f"ERROR: Missing file: {f}")
            sys.exit(1)
    print(f"[OK] All {len(required_files)} foundation files exist.")

    # 4. Test Configuration Loading
    try:
        from signalbrief.config.loader import (
            list_available_domains,
            load_domain_config,
            load_pipeline_config,
            load_sources_for_domain,
        )

        pipeline_cfg = load_pipeline_config()
        print(f"[OK] Pipeline config loaded: {pipeline_cfg.name} (v{pipeline_cfg.version})")

        domains = list_available_domains()
        print(f"[OK] Available domains detected: {domains}")
        assert "manufacturing" in domains

        mfg_cfg = load_domain_config("manufacturing")
        print(f"[OK] Manufacturing domain loaded: {len(mfg_cfg.keywords)} keywords, {len(mfg_cfg.subtopics)} subtopics")

        sources = load_sources_for_domain("manufacturing")
        print(f"[OK] Manufacturing sources loaded: {len(sources)} active sources")
    except Exception as e:
        print(f"ERROR loading configuration: {e}")
        sys.exit(1)

    print("=" * 60)
    print("ALL PHASE 0 INTEGRITY CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
