
from sqlglot import parse, parse_one, exp
from typing import List, Dict, Tuple, Optional
import logging
import re

log = logging.getLogger(__name__)

def parse_sql_statements(sql_text: str):
    """Parse SQL text into sqlglot expressions (ASTs). Returns list of Expression nodes."""
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
    """Given an AST, find CREATE VIEW / CREATE TABLE AS / INSERT ... SELECT constructs.
    Returns list of (output_name, select_ast)"""
    out = []
    if ast is None:
        return out
    for node in ast.walk():
        if isinstance(node, exp.Create):
            target = None
            try:
                target = node.this.name if node.this is not None else None
            except Exception:
                target = None
            if hasattr(node, 'expression') and node.expression is not None:
                select_ast = node.expression
                out.append((target, select_ast))
        if isinstance(node, exp.Insert):
            try:
                target = node.this.name if node.this is not None else None
            except Exception:
                target = None
            select_ast = node.expression
            out.append((target, select_ast))
    return out

def resolve_table_refs(select_ast) -> List[Tuple[str, Optional[str]]]:
    """Return table references used in select AST as a list of (table_name, alias)"""
    refs = []
    if select_ast is None:
        return refs
    for table in select_ast.find_all(exp.Table):
        table_name = table.name or table.sql()
        alias = None
        parent = getattr(table, 'parent', None)
        if parent is not None and isinstance(parent, exp.Alias):
            alias = parent.alias_or_name
        refs.append((table_name, alias))
    return refs

def map_output_to_input_columns(select_ast, catalog=None) -> Dict[str, List[str]]:
    """Walk the select AST expressions to map output column names -> input columns
    Returns dict: out_col -> list of (table.col) strings"""
    mapping = {}
    if select_ast is None:
        return mapping
    select_list = []
    try:
        select_list = list(select_ast.expressions)
    except Exception:
        select_list = [node for node in select_ast.find_all(exp.Expression)][:10]

    for expr in select_list:
        out_name = None
        try:
            out_name = expr.alias_or_name or expr.sql()
        except Exception:
            out_name = expr.sql() if hasattr(expr, 'sql') else str(expr)
        inputs = []
        for ident in expr.find_all(exp.Column):
            table = None
            try:
                table = ident.table
            except Exception:
                table = None
            col = ident.name if hasattr(ident, 'name') else ident.sql()
            if table:
                inputs.append(f"{table}.{col}")
            else:
                inputs.append(col)
        if any(isinstance(node, exp.Star) for node in expr.find_all(exp.Star)):
            inputs.append("*")
        mapping[out_name] = list(dict.fromkeys(inputs))
    return mapping
