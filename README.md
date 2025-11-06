# 🧩 StructureLineage

StructureLineage is a framework for generating synthetic pipelines, building Schema Dependency Graphs (SDGs), and evaluating lineage mappings with precision/recall metrics.

**Author:** Habib Maicha

---

## 🚀 Quickstart in Google Colab

Run the full pipeline interactively with one click:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/habiiibo03/StructureLineage/blob/main/StructureLineage_Quickstart.ipynb)

The Quickstart notebook demonstrates how to:
1. Clone the StructureLineage repo  
2. Generate a synthetic project  
3. Build the Schema Dependency Graph (SDG)  
4. Evaluate precision/recall against ground truth  
5. ✅ Auto-verify pipeline success  
6. 📊 Visualize the SDG (tables vs views)

---

## 📊 Example SDG Visualization

Here’s a simplified layered view of tables (blue) and views (green):

![Schema Dependency Graph](examples/sdg_clean.png)

---

## ⚙️ Requirements

- Python 3.9+
- `sqlglot`, `duckdb`, `networkx`, `pandas`, `pytest`

Install dependencies:
```bash
pip install -r requirements.txt
```
---
## 🖥️ Getting Started Locally

Clone the repository and run the pipeline on your machine:
```bash 
git clone https://github.com/habiiibo03/StructureLineage.git cd StructureLineage pip install -r 
```
requirements.txt Generate a synthetic project:
```bash
python -m src.tools.gen_synthetic examples/local_project --n_tables 3 --n_views 3
```
Build the Schema Dependency Graph:
```bash
python -m src.sl_core.build_sdg examples/local_project 
```
Evaluate results:
```bash
pytest
```
---

## 🧪 Testing
Run unit tests with:
```bash 
pytest 
```
---