from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class LocalDB:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None

    def init(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                upload_id TEXT,
                status TEXT NOT NULL,
                bytes_uploaded INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def store_metric(self, data: dict):
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO metrics (timestamp, data) VALUES (?, ?)",
            (now, json.dumps(data)),
        )
        self.conn.commit()

    def get_recent_metrics(self, limit: int = 100) -> list[dict]:
        cursor = self.conn.execute(
            "SELECT timestamp, data FROM metrics ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [{"timestamp": row[0], **json.loads(row[1])} for row in cursor.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()
