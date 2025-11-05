
import networkx as nx
import json
import sqlite3
import os

class SDGStore:
    def __init__(self, sqlite_path: str = None):
        self.G = nx.DiGraph()
        self.sqlite_path = sqlite_path
        if sqlite_path:
            self._init_sqlite(sqlite_path)

    def _init_sqlite(self, path: str):
        self.conn = sqlite3.connect(path)
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS edges
                        (src TEXT, tgt TEXT, prob REAL, evidence TEXT, ts TEXT)''')
        self.conn.commit()

    def add_edge(self, src: str, tgt: str, score: float, artifact_id: str, timestamp: str):
        self.G.add_node(src)
        self.G.add_node(tgt)
        if self.G.has_edge(src, tgt):
            data = self.G[src][tgt]
            evidence = data.get('evidence', [])
            evidence.append({'artifact': artifact_id, 'score': score, 'ts': timestamp})
            combined = 1.0 - (1.0 - data.get('prob', 0.0))*(1.0 - score)
            data['prob'] = combined
            data['evidence'] = evidence
        else:
            self.G.add_edge(src, tgt, evidence=[{'artifact': artifact_id, 'score': score, 'ts': timestamp}], prob=score)
        if getattr(self, 'conn', None):
            cur = self.conn.cursor()
            cur.execute('INSERT INTO edges VALUES (?,?,?, ?,?)', (src, tgt, float(score), json.dumps([{'artifact': artifact_id, 'score': score, 'ts': timestamp}]), timestamp))
            self.conn.commit()

    def persist_json(self, path: str):
        out = {'nodes': list(self.G.nodes()), 'edges': []}
        for u, v, data in self.G.edges(data=True):
            out['edges'].append({'src': u, 'tgt': v, 'prob': float(data.get('prob', 0.0)), 'evidence': data.get('evidence', [])})
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2)

    def load_json(self, path: str):
        if not os.path.exists(path):
            return
        with open(path, 'r', encoding='utf-8') as f:
            j = json.load(f)
        for n in j.get('nodes', []):
            self.G.add_node(n)
        for e in j.get('edges', []):
            src = e['src']; tgt = e['tgt']; prob = e.get('prob', 0.0); evidence = e.get('evidence', [])
            self.G.add_edge(src, tgt, prob=prob, evidence=evidence)
