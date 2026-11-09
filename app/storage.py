import sqlite3
from contextlib import closing

SCHEMA = """CREATE TABLE IF NOT EXISTS messages(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sender TEXT NOT NULL, text TEXT NOT NULL,
  intent TEXT NOT NULL, urgent INTEGER NOT NULL, confidence REAL NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""


class Storage:
    def __init__(self, path: str = "demo.db"):
        self.path = path
        with closing(self._conn()) as c, c:
            c.execute(SCHEMA)

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def add(self, sender, text, r):
        with closing(self._conn()) as c, c:
            cur = c.execute(
                "INSERT INTO messages(sender,text,intent,urgent,confidence) VALUES(?,?,?,?,?)",
                (sender, text, r.intent, int(r.urgent), r.confidence))
            return cur.lastrowid

    def recent(self, limit=20):
        with closing(self._conn()) as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM messages ORDER BY id DESC LIMIT ?", (limit,))]

    def stats(self):
        with closing(self._conn()) as c:
            return {r["intent"]: r["n"] for r in c.execute(
                "SELECT intent, COUNT(*) n FROM messages GROUP BY intent")}
