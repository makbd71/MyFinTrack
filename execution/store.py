"""SQLite transaction store with dedup by Message-ID and fingerprint."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from .parsers.base import Transaction

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id              INTEGER PRIMARY KEY,
    message_id      TEXT NOT NULL,
    fingerprint     TEXT NOT NULL UNIQUE,
    sender          TEXT NOT NULL,
    occurred_at     TEXT NOT NULL,       -- ISO 8601 with original offset
    occurred_utc    TEXT NOT NULL,       -- ISO 8601 UTC, for range queries
    type            TEXT NOT NULL CHECK (type IN ('income','expense','transfer')),
    amount          TEXT NOT NULL,       -- Decimal as text, never float
    currency        TEXT NOT NULL,
    card_or_account TEXT,
    merchant        TEXT,
    category        TEXT NOT NULL,
    raw_snippet     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_tx_occurred ON transactions(occurred_utc);

CREATE TABLE IF NOT EXISTS processed_emails (
    message_id   TEXT PRIMARY KEY,
    sender       TEXT,
    result       TEXT NOT NULL,          -- parsed | excluded | unparsed | error
    reason       TEXT,
    processed_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS checkpoints (
    name  TEXT PRIMARY KEY,              -- e.g. 'imap:FinComm:uidvalidity'
    value TEXT NOT NULL
);
"""


def _utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


class Store:
    def __init__(self, path: Path | str):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    # --- transactions -------------------------------------------------------
    def add(self, tx: Transaction) -> bool:
        """Insert; return False if it duplicates an existing transaction."""
        cur = self.conn.execute(
            """INSERT OR IGNORE INTO transactions
               (message_id, fingerprint, sender, occurred_at, occurred_utc, type, amount,
                currency, card_or_account, merchant, category, raw_snippet)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (tx.message_id, tx.fingerprint(), tx.sender, tx.occurred_at.isoformat(),
             _utc(tx.occurred_at),
             tx.type, str(tx.amount), tx.currency, tx.card_or_account, tx.merchant,
             tx.category, tx.raw_snippet),
        )
        self.conn.commit()
        return cur.rowcount == 1

    def between(self, start: datetime, end: datetime) -> list[Transaction]:
        """Transactions with start <= occurred_at < end (compared in UTC)."""
        rows = self.conn.execute(
            "SELECT * FROM transactions WHERE occurred_utc >= ? AND occurred_utc < ? ORDER BY occurred_utc",
            (_utc(start), _utc(end)),
        ).fetchall()
        return [Transaction(
            message_id=r["message_id"], sender=r["sender"],
            occurred_at=datetime.fromisoformat(r["occurred_at"]),
            type=r["type"], amount=Decimal(r["amount"]), currency=r["currency"],
            card_or_account=r["card_or_account"], merchant=r["merchant"],
            category=r["category"], raw_snippet=r["raw_snippet"] or "",
        ) for r in rows]

    # --- email bookkeeping --------------------------------------------------
    def is_processed(self, message_id: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM processed_emails WHERE message_id=?", (message_id,)
        ).fetchone() is not None

    def mark_processed(self, message_id: str, sender: str, result: str, reason: str = "") -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO processed_emails (message_id, sender, result, reason) VALUES (?,?,?,?)",
            (message_id, sender, result, reason),
        )
        self.conn.commit()

    def get_checkpoint(self, name: str) -> str | None:
        row = self.conn.execute("SELECT value FROM checkpoints WHERE name=?", (name,)).fetchone()
        return row["value"] if row else None

    def set_checkpoint(self, name: str, value: str) -> None:
        self.conn.execute("INSERT OR REPLACE INTO checkpoints (name, value) VALUES (?,?)", (name, value))
        self.conn.commit()
