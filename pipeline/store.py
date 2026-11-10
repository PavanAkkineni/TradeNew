"""Local storage: raw response files plus a SQLite catalog of every fetch.

Layout (scales to the whole market: one folder per endpoint, one file per symbol):

  data_store/raw/<endpoint>/<SYMBOL>.json
  data_store/raw/<endpoint>/<SYMBOL>/<variant>.json   (news months, transcript quarters)
  data_store/raw/global/<endpoint>.json|csv
  data_store/catalog.sqlite                            (fetch log)
"""
import gzip
import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS fetch_log (
    endpoint   TEXT NOT NULL,
    symbol     TEXT NOT NULL,          -- '*' for market-wide data
    variant    TEXT NOT NULL,          -- '' when the endpoint has one call
    path       TEXT,
    status     TEXT NOT NULL,          -- ok | empty | premium | invalid | info | quota | http
    message    TEXT,
    bytes      INTEGER,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (endpoint, symbol, variant)
);
"""


def raw_path(endpoint: str, symbol: Optional[str], variant: str, ext: str) -> Path:
    if symbol is None:
        if variant:
            return config.RAW_DIR / "global" / endpoint / f"{variant}.{ext}"
        return config.RAW_DIR / "global" / f"{endpoint}.{ext}"
    sym = symbol.upper().replace("/", "_")
    if variant:
        return config.RAW_DIR / endpoint / sym / f"{variant}.{ext}"
    return config.RAW_DIR / endpoint / f"{sym}.{ext}"


def _open(path: Path, mode: str):
    if str(path).endswith(".gz"):
        return gzip.open(path, mode + "t", encoding="utf-8")
    return open(path, mode, encoding="utf-8")


def write_payload(path: Path, payload) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with (gzip.open(tmp, "wt", encoding="utf-8") if path.name.endswith(".gz")
          else open(tmp, "w", encoding="utf-8")) as f:
        if isinstance(payload, str):
            f.write(payload)
        else:
            json.dump(payload, f, ensure_ascii=False)
    os.replace(tmp, path)
    if path.name.endswith(".json.gz"):          # drop an older uncompressed copy
        old = path.with_name(path.name[:-3])
        if old.exists():
            old.unlink()
    return path.stat().st_size


def read_json(path: Path):
    with _open(Path(path), "r") as f:
        return json.load(f)


def find_raw(endpoint: str, symbol: Optional[str], variant: str = "") -> Optional[Path]:
    """Locate a stored raw file whatever its extension (.json, .json.gz, .csv)."""
    for ext in ("json", "json.gz", "csv"):
        p = raw_path(endpoint, symbol, variant, ext)
        if p.exists():
            return p
    return None


class Catalog:
    def __init__(self, db_path: Path = config.CATALOG_DB):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(_SCHEMA)
        self.lock = threading.Lock()

    def get(self, endpoint: str, symbol: str, variant: str):
        with self.lock:
            row = self.conn.execute(
                "SELECT status, fetched_at, path FROM fetch_log WHERE endpoint=? AND symbol=? AND variant=?",
                (endpoint, symbol, variant),
            ).fetchone()
        return row

    def is_fresh(self, endpoint: str, symbol: str, variant: str, ttl_days: Optional[float]) -> bool:
        row = self.get(endpoint, symbol, variant)
        if not row:
            return False
        status, fetched_at, _ = row
        if status not in ("ok", "empty"):
            return False                      # failures are always retried
        age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(fetched_at)).total_seconds() / 86400
        if status == "empty":
            return age_days < 7               # e.g. a transcript not published yet
        if ttl_days is None:
            return True
        return age_days < ttl_days

    def record(self, endpoint, symbol, variant, status, path=None, message=None, nbytes=None):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO fetch_log VALUES (?,?,?,?,?,?,?,?)",
                (endpoint, symbol, variant, str(path) if path else None, status,
                 (message or "")[:500], nbytes, now),
            )
            self.conn.commit()

    def query(self, sql: str, params=()):
        with self.lock:
            return self.conn.execute(sql, params).fetchall()
