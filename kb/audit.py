"""Append-only audit log: who asked what, what they got, and what they were denied."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from kb.models import Principal


class AuditLog:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("""CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, ts TEXT, user TEXT,
                           groups TEXT, question TEXT, retrieved TEXT, denied TEXT, cited TEXT, ms INTEGER)""")
        # SQLite triggers make the table append-only: no UPDATE, no DELETE
        for op in ("UPDATE", "DELETE"):
            self.db.execute(f"""CREATE TRIGGER IF NOT EXISTS audit_no_{op.lower()} BEFORE {op} ON audit
                                BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END""")

    def log(self, user: Principal, question: str, retrieved: list[str], denied: list[str],
            cited: list[str], ms: int) -> None:
        with self.db:
            self.db.execute("INSERT INTO audit (ts, user, groups, question, retrieved, denied, cited, ms) "
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (datetime.now(timezone.utc).isoformat(timespec="seconds"), user.email,
                             ",".join(sorted(user.groups)), question, json.dumps(retrieved),
                             json.dumps(denied), json.dumps(cited), ms))

    def recent(self, n: int = 50) -> list[dict]:
        cur = self.db.execute("SELECT ts, user, groups, question, retrieved, denied, cited, ms "
                              "FROM audit ORDER BY id DESC LIMIT ?", (n,))
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]
