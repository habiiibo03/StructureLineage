
from src.tools.gen_synthetic import gen_project
from src.sl_core.build_sdg import process_workspace
import os

def run_demo():
    out = os.path.join('examples', 'demo_project')
    gen_project(out, n_tables=4, cols_range=(3,5), n_views=4)
    store = process_workspace(out, sqlite_db=os.path.join(out, 'sdg.sqlite3'))
    store.persist_json(os.path.join(out, 'sdg.json'))
    print("Demo complete. SDG written to", os.path.join(out, 'sdg.json'))

if __name__ == '__main__':
    run_demo()
