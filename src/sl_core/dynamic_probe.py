
import duckdb
import logging

log = logging.getLogger(__name__)

def probe_cooccurrence_from_query(sql_query: str, left_col: str, right_col: str, limit: int = 1000):
    try:
        con = duckdb.connect(database=':memory:')
        q = f"SELECT {left_col} as left_col, {right_col} as right_col FROM ({sql_query}) as sub LIMIT {limit}"
        df = con.execute(q).fetchdf()
        if df.empty:
            return 0.0
        left = df['left_col']
        right = df['right_col']
        set_right = set(right.dropna().unique())
        matches = left.dropna().apply(lambda v: v in set_right).sum()
        return float(matches) / max(1, len(left))
    except Exception as e:
        log.error("DuckDB probe failed: %s", e)
        return None
