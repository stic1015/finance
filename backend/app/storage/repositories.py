from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.schemas.models import BacktestResult


class SQLiteRepository:
    storage_mode = "sqlite"

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS watchlist (
                    symbol TEXT PRIMARY KEY,
                    added_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS latest_forecasts (
                    symbol TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
            if not conn.execute("SELECT symbol FROM watchlist LIMIT 1").fetchone():
                conn.executemany(
                    "INSERT OR IGNORE INTO watchlist(symbol) VALUES (?)",
                    [
                        ("HK.00700",),
                        ("HK.09988",),
                        ("HK.03690",),
                        ("HK.01810",),
                        ("HK.00981",),
                        ("HK.01211",),
                        ("HK.02318",),
                        ("HK.01398",),
                        ("HK.03988",),
                        ("HK.00939",),
                        ("HK.00005",),
                        ("HK.01024",),
                        ("HK.00941",),
                        ("HK.03888",),
                        ("HK.06618",),
                        ("SH.600519",),
                        ("SH.601318",),
                        ("SH.600036",),
                        ("SH.600276",),
                        ("SH.601398",),
                        ("SH.600900",),
                        ("SH.600309",),
                        ("SH.601899",),
                        ("SH.601288",),
                        ("SH.600030",),
                        ("SZ.000001",),
                        ("SZ.000333",),
                        ("SZ.000651",),
                        ("SZ.002594",),
                        ("SZ.300750",),
                    ],
                )

    def save_job(self, job: BacktestResult) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(job_id, kind, status, payload)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(job_id) DO UPDATE SET
                    status=excluded.status,
                    payload=excluded.payload
                """,
                (job.job_id, "backtest", job.status, job.model_dump_json()),
            )

    def get_job(self, job_id: str) -> BacktestResult | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT payload FROM jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if not row:
            return None
        return BacktestResult.model_validate_json(row["payload"])

    def list_watchlist(self) -> list[str]:
        with self.connect() as conn:
            rows = conn.execute("SELECT symbol FROM watchlist ORDER BY added_at").fetchall()
        return [row["symbol"] for row in rows]

    def save_latest_forecast(self, symbol: str, payload: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO latest_forecasts(symbol, payload)
                VALUES (?, ?)
                ON CONFLICT(symbol) DO UPDATE SET payload=excluded.payload
                """,
                (symbol, payload),
            )

    def get_latest_forecast(self, symbol: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT payload FROM latest_forecasts WHERE symbol = ?",
                (symbol,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row["payload"])


class MemoryRepository:
    storage_mode = "memory"

    def __init__(self) -> None:
        self.jobs: dict[str, BacktestResult] = {}
        self.watchlist = [
            "HK.00700",
            "HK.09988",
            "HK.03690",
            "HK.01810",
            "HK.00981",
            "HK.01211",
            "HK.02318",
            "HK.01398",
            "HK.03988",
            "HK.00939",
            "HK.00005",
            "HK.01024",
            "HK.00941",
            "HK.03888",
            "HK.06618",
            "SH.600519",
            "SH.601318",
            "SH.600036",
            "SH.600276",
            "SH.601398",
            "SH.600900",
            "SH.600309",
            "SH.601899",
            "SH.601288",
            "SH.600030",
            "SZ.000001",
            "SZ.000333",
            "SZ.000651",
            "SZ.002594",
            "SZ.300750",
        ]
        self.latest_forecasts: dict[str, dict] = {}

    def save_job(self, job: BacktestResult) -> None:
        self.jobs[job.job_id] = job

    def get_job(self, job_id: str) -> BacktestResult | None:
        return self.jobs.get(job_id)

    def list_watchlist(self) -> list[str]:
        return list(self.watchlist)

    def save_latest_forecast(self, symbol: str, payload: str) -> None:
        self.latest_forecasts[symbol] = json.loads(payload)

    def get_latest_forecast(self, symbol: str) -> dict | None:
        return self.latest_forecasts.get(symbol)
