# src/sl_core/parser_sql.py
from sqlglot import parse, parse_one, exp
from typing import List, Dict, Tuple, Optional
import logging

log = logging.getLogger(__name__)

def parse_sql_statements(sql_text: str):
    """
    Parse SQL text into sqlglot Expression ASTs.
    Returns list of Expression nodes (one per top-level statement).
    """
    try:
        asts = parse(sql_text)
        return asts
    except Exception as e:
        log.warning("sqlglot.parse failed, trying parse_one: %s", e)
        try:
            one = parse_one(sql_text)
            return [one] if one is not None else []
        except Exception as e2:
            log.error("Failed to parse SQL: %s", e2)
            return []

def extract_create_selects(ast):
    """
    Given an AST, find CREATE VIEW / CREATE TABLE AS / INSERT ... SELECT constructs.
    Returns list of (output_name, select_ast)
    """
    out = []
    if ast is None:
        return out

    for node in ast.walk():
        # CREATE TABLE ... AS SELECT / CREATE VIEW ... AS SELECT
        if isinstance(node, exp.Create):
            target = None
            try:
                # node.this is the table identifier expression
                if hasattr(node, "this") and node.this is not None:
                    target = getattr(node.this, "name", None) or node.this.sql()
            except Exception:
                target = None
            # The create node may contain an expression (select) as node.expression
            if hasattr(node, "expression") and node.expression is not None:
                select_ast = node.expression
                out.append((target, select_ast))
        # INSERT INTO ... SELECT ...
        if isinstance(node, exp.Insert):
            target = None
            try:
                if hasattr(node, "this") and node.this is not None:
                    target = getattr(node.this, "name", None) or node.this.sql()
            except Exception:
                target = None
            select_ast = getattr(node, "expression", None)
            if select_ast is not None:
                out.append((target, select_ast))
        # VIEW definitions might also appear as exp.View depending on dialect; handle generically
        if isinstance(node, exp.View):
            target = None
            try:
                target = getattr(node, "this", None)
                if target is not None:
                    target = getattr(target, "name", None) or target.sql()
            except Exception:
                target = None
            select_ast = getattr(node, "expression", None)
            if select_ast is not None:
                out.append((target, select_ast))
    return out

def resolve_table_refs(select_ast) -> List[Tuple[str, Optional[str]]]:
    """
    Return table references used in select AST as a list of (table_name, alias)
    """
    refs = []
    if select_ast is None:
        return refs
    for table in select_ast.find_all(exp.Table):
        # sqlglot Table nodes have 'this' or 'name' attributes depending on structure
        try:
            table_name = getattr(table, "name", None) or table.sql()
        except Exception:
            table_name = table.sql()
        alias = None
        parent = getattr(table, "parent", None)
        if parent is not None and isinstance(parent, exp.Alias):
            alias = parent.alias_or_name
        refs.append((table_name, alias))
    return refs

def map_output_to_input_columns(select_ast, catalog: Optional[Dict[str, List[str]]] = None) -> Dict[str, List[str]]:
    """
    Walk the select AST expressions to map output column names -> input columns.
    Returns dict: out_col -> list of input references like 'table.col' or just 'col' if ambiguous.
    If SELECT * is encountered, and catalog is provided, it will expand into concrete columns.
    """
    mapping = {}
    if select_ast is None:
        return mapping

    # Get projection expressions (Select.expressions)
    try:
        select_list = list(select_ast.expressions)
    except Exception:
        # fallback: scan children for projection-like nodes
        select_list = [n for n in select_ast.find_all(exp.Expression)][:50]

    for expr in select_list:
        # Determine output name (alias or expression SQL)
        try:
            out_name = expr.alias_or_name or expr.sql()
        except Exception:
            out_name = expr.sql() if hasattr(expr, "sql") else str(expr)

        inputs = []
        # If expression contains Column nodes, collect them
        columns = list(expr.find_all(exp.Column))
        if columns:
            for ident in columns:
                # ident may have parts: table, column
                try:
                    table = getattr(ident, "table", None)
                except Exception:
                    table = None
                col = getattr(ident, "name", None) or ident.sql()
                if table:
                    inputs.append(f"{table}.{col}")
                else:
                    inputs.append(col)
        else:
            # handle star expansion: if expression includes Star nodes, expand
            stars = list(expr.find_all(exp.Star))
            if stars:
                # If catalog provided, attempt to expand using available tables in FROM clause
                from_tables = [t for t in select_ast.find_all(exp.Table)]
                if catalog and from_tables:
                    # Expand * across referenced tables using their catalog columns if available
                    for t in from_tables:
                        tname = getattr(t, "name", None) or t.sql()
                        cols = catalog.get(tname, [])
                        for c in cols:
                            inputs.append(f"{tname}.{c}")
                else:
                    # fallback: leave wildcard marker
                    inputs.append("*")
        # Deduplicate while preserving order
        seen = []
        for x in inputs:
            if x not in seen:
                seen.append(x)
        mapping[out_name] = seen
    return mapping
