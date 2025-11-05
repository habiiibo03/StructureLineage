import os, random, json
from pathlib import Path

COMMON_KEYS = ["customer_id", "order_id", "product_id", "user_id", "date_id"]
COMMON_ATTRS = ["amount", "quantity", "price", "status", "region", "country"]

def generate_table_sql(name, columns, path):
    cols_def = ",\n  ".join([f"{c} INTEGER" for c in columns])
    sql = f"CREATE TABLE {name} (\n  {cols_def}\n);\n\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sql)

def generate_view_sql(view_name, mapping, path):
    select_list = []
    for out_col, (t, c) in mapping.items():
        select_list.append(f"{t}.{c} AS {out_col}")
    select_sql = ",\n  ".join(select_list)
    from_tables = ", ".join(list({t for t, _ in mapping.values()}))
    q = f"CREATE VIEW {view_name} AS\nSELECT\n  {select_sql}\nFROM {from_tables};\n"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(q)

def make_table_columns(base_idx, n_cols):
    """Generate realistic table columns with a few shared names."""
    cols = []
    for i in range(n_cols):
        if i == 0 and random.random() < 0.8:
            # 80% of first columns are shared keys
            cols.append(random.choice(COMMON_KEYS))
        else:
            cols.append(f"col{base_idx}_{i}")
    # Add 1-2 semantic columns
    if random.random() < 0.7:
        cols.append(random.choice(COMMON_ATTRS))
    return cols

def gen_project(out_dir, n_tables=5, cols_range=(3,6), n_views=5):
    os.makedirs(out_dir, exist_ok=True)
    truth = []
    tables = {}

    # Generate base tables
    for i in range(n_tables):
        tname = f"raw_table_{i}"
        cols = make_table_columns(i, random.randint(cols_range[0], cols_range[1]))
        generate_table_sql(tname, cols, os.path.join(out_dir, f"{tname}.sql"))
        tables[tname] = cols

    # Generate dependent views
    for v in range(n_views):
        vname = f"view_{v}"
        mapping = {}
        for k in range(random.randint(3, 6)):
            t = random.choice(list(tables.keys()))
            c = random.choice(tables[t])
            # Keep the same name in output to ensure match
            out_col = c if random.random() < 0.8 else f"vcol_{v}_{k}"
            mapping[out_col] = (t, c)
            truth.append((f"{t}.{c}", f"{vname}.{out_col}"))
        generate_view_sql(vname, mapping, os.path.join(out_dir, f"{vname}.sql"))

    with open(os.path.join(out_dir, 'ground_truth.json'), 'w', encoding='utf-8') as f:
        json.dump(truth, f, indent=2)

    print(f"[+] Generated enhanced project at {out_dir} with {n_tables} tables and {n_views} views.")
    print("[+] Shared columns and realistic names included for better matching.")

if __name__ == '__main__':
    gen_project('examples/demo_project', n_tables=4, cols_range=(3,5), n_views=4)
