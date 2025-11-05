import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

def visualize_sdg(json_path: str, min_prob: float = 0.0, save_path: str = None):
    """Load sdg.json and draw or save the dependency graph."""
    path = Path(json_path)
    if not path.exists():
        print(f"[!] File not found: {json_path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    G = nx.DiGraph()
    for node in data.get("nodes", []):
        G.add_node(node)
    for e in data.get("edges", []):
        prob = float(e.get("prob", 0.0))
        if prob >= min_prob:
            G.add_edge(e["src"], e["tgt"], weight=prob)

    if not G.edges:
        print("[!] No edges found above threshold; nothing to visualize.")
        return

    pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)

    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_size=400, node_color="#A0CBE2")
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle="->", alpha=0.5)

    edge_labels = {(u, v): f"{d['weight']:.2f}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    plt.title(f"StructureLineage – Schema Dependency Graph (min_prob={min_prob})")
    plt.axis("off")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200)
        print(f"[+] Saved graph to {save_path}")
    else:
        plt.show()

if __name__ == "__main__":
    json_path = "examples/demo_project/sdg.json"
    visualize_sdg(json_path, min_prob=0.7)
