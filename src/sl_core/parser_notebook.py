
import nbformat
import re
from typing import List, Dict
import logging

log = logging.getLogger(__name__)

SQL_CELL_MAGIC = re.compile(r'^\s*%sql|^\s*%%sql', re.IGNORECASE)
SQL_API_CALL = re.compile(r'(spark\.sql|pd\.read_sql|conn\.execute|cursor\.execute)\s*\(\s*[rR]?[\'\"](.+?)[\'\"]\s*\)', re.S)

def extract_cells_from_notebook(nb_path: str):
    nb = nbformat.read(nb_path, as_version=4)
    cells = []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        source = cell.source or ''
        if SQL_CELL_MAGIC.search(source):
            lines = [line for line in source.splitlines() if not line.strip().startswith('%sql') and not line.strip().startswith('%%sql')]
            sql_text = "\n".join(lines).strip()
            cells.append({'type': 'sql', 'content': sql_text, 'cell_index': i})
            continue
        m = SQL_API_CALL.search(source)
        if m:
            sql_text = m.group(2)
            cells.append({'type': 'sql', 'content': sql_text, 'cell_index': i})
            continue
        if '.select(' in source or '.join(' in source or 'read_csv(' in source or 'read_table(' in source:
            cells.append({'type': 'df', 'content': source, 'cell_index': i})
            continue
    return cells
