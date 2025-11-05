
import re, difflib
import pandas as pd
from typing import Optional

def name_similarity(a: str, b: str) -> float:
    if a is None or b is None:
        return 0.0
    a_tokens = [t for t in re.split(r'[\W_]+', a.lower()) if t]
    b_tokens = [t for t in re.split(r'[\W_]+', b.lower()) if t]
    if not a_tokens or not b_tokens:
        return 0.0
    inter = len(set(a_tokens) & set(b_tokens))
    sim = inter / max(len(set(a_tokens)), len(set(b_tokens)))
    if sim == 0:
        sim = difflib.SequenceMatcher(None, a, b).ratio()
    return float(sim)

def value_cooccurrence(sample_left: Optional[pd.Series], sample_right: Optional[pd.Series]) -> float:
    if sample_left is None or sample_right is None:
        return 0.0
    try:
        if len(sample_left) == 0 or len(sample_right) == 0:
            return 0.0
    except Exception:
        return 0.0
    set_right = set(sample_right.dropna().unique())
    matches = sample_left.dropna().apply(lambda v: v in set_right).sum()
    return float(matches) / max(1, len(sample_left))
