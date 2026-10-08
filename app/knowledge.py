from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from app.config import ROOT


class KnowledgeStore:
    """Only public knowledge is persisted; uploaded documents never enter SQLite."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.records = json.loads((ROOT / "data" / "knowledge.json").read_text(encoding="utf-8"))
        self.by_id = {r["id"]: r for r in self.records}
        with self.connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS cards (id TEXT PRIMARY KEY, payload TEXT NOT NULL, expires REAL NOT NULL)")

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def get(self, identifier: str):
        if identifier in self.by_id:
            return self.by_id[identifier], "local"
        with self.connect() as con:
            row = con.execute("SELECT payload, expires FROM cards WHERE id=?", (identifier,)).fetchone()
        if row and row[1] > time.time():
            return json.loads(row[0]), "cache"
        return None, "miss"

    def save(self, identifier: str, card: dict):
        with self.connect() as con:
            con.execute("INSERT OR REPLACE INTO cards VALUES (?,?,?)", (identifier, json.dumps(card), time.time() + 7 * 86400))

    def search(self, query: str, limit=12):
        query = query.strip().casefold()
        matches = [r for r in self.records if any(query in a.casefold() for a in r["aliases"]) or query in r["title"].casefold()]
        matches.sort(key=lambda r: (r["title"].casefold() != query, not r["title"].casefold().startswith(query), r["title"]))
        return [{"id": r["id"], "title": r["title"], "category": r["category"]} for r in matches[:limit]]
