
import os, glob, datetime, logging
from src.sl_core.parser_sql import parse_sql_statements, extract_create_selects, map_output_to_input_columns
from src.sl_core.parser_notebook import extract_cells_from_notebook
from src.sl_core.map_columns import name_similarity
from src.sl_core.graph_store import SDGStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def process_workspace(path_root: str, catalog=None, sqlite_db: str = None):
    store = SDGStore(sqlite_db)
    artifacts = []
    for ext in ('*.sql', '*.ipynb', '*.py', '*.json'):
        artifacts.extend(glob.glob(os.path.join(path_root, '**', ext), recursive=True))
    ts = datetime.datetime.utcnow().isoformat()
    for art in sorted(set(artifacts)):
        try:
            if art.endswith('.sql'):
                sql_text = open(art, encoding='utf-8', errors='ignore').read()
                asts = parse_sql_statements(sql_text)
                for ast in asts:
                    pairs = extract_create_selects(ast)
                    for out_name, select_ast in pairs:
                        colmap = map_output_to_input_columns(select_ast, catalog)
                        for out_col, in_cols in colmap.items():
                            for in_col in in_cols:
                                sim = name_similarity(out_col, in_col.split('.')[-1] if '.' in in_col else in_col)
                                score = sim
                                src = in_col if isinstance(in_col, str) else str(in_col)
                                tgt = f"{out_name}.{out_col}" if out_name else out_col
                                store.add_edge(src, tgt, score, artifact_id=art, timestamp=ts)
            elif art.endswith('.ipynb'):
                cells = extract_cells_from_notebook(art)
                for cell in cells:
                    if cell['type'] == 'sql':
                        sql_text = cell['content']
                        asts = parse_sql_statements(sql_text)
                        for ast in asts:
                            pairs = extract_create_selects(ast)
                            for out_name, select_ast in pairs:
                                colmap = map_output_to_input_columns(select_ast, catalog)
                                for out_col, in_cols in colmap.items():
                                    for in_col in in_cols:
                                        sim = name_similarity(out_col, in_col.split('.')[-1] if '.' in in_col else in_col)
                                        score = 0.6 * sim + 0.4 * 0.0
                                        src = in_col if isinstance(in_col, str) else str(in_col)
                                        tgt = f"{out_name}.{out_col}" if out_name else out_col
                                        store.add_edge(src, tgt, score, artifact_id=art, timestamp=ts)
                    else:
                        pass
            else:
                pass
        except Exception as e:
            log.error("Error processing artifact %s: %s", art, e)
    return store
