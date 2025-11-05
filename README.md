[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/<your-username>/StructureLineage/blob/main/StructureLineage_Quickstart.ipynb)

# StructureLineage Prototype
Lightweight prototype for StructureLineage: schema dependency extraction (SQL + Notebooks)

## Requirements
- Python 3.9+
- Recommended: create virtualenv and install requirements.txt

Windows quick setup (PowerShell):
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Run demo
```powershell
python examples\quick_demo.py
```
The demo will generate a synthetic project under `examples/demo_project`, process it, and write a JSON SDG to `examples/demo_project/sdg.json`.

## Notes
- The prototype uses sqlglot for SQL parsing, nbformat for notebook parsing, DuckDB for optional dynamic probing,
  NetworkX for an in-memory graph and SQLite for optional persistence (simple wrapper).
- Do NOT run code cloned from untrusted repos. Dynamic probing will only run on local/synthetic data created by the generator.
