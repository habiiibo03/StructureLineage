
from src.sl_core.parser_sql import parse_sql_statements, extract_create_selects, map_output_to_input_columns

def test_create_view_simple():
    sql = "CREATE VIEW v AS SELECT a.id AS id, b.name AS name FROM a JOIN b ON a.id=b.aid;"
    asts = parse_sql_statements(sql)
    assert len(asts) >= 1
    pairs = []
    for ast in asts:
        pairs.extend(extract_create_selects(ast))
    assert len(pairs) == 1
    out, select_ast = pairs[0]
    mapping = map_output_to_input_columns(select_ast)
    # mapping keys might be 'id' and 'name' or alias forms
    assert any('id' in k.lower() for k in mapping.keys())
