from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import uuid4

from app.schemas.models import BacktestRequest, BacktestResult
from app.services.backtest.engine import run_backtest
from app.storage.repositories import SQLiteRepository


class BacktestJobService:
    def __init__(self, repository: SQLiteRepository, max_workers: int = 2) -> None:
        self.repository = repository
        self.executor_message = ""
        try:
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
            self.executor_mode = "process_pool"
        except PermissionError:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self.executor_mode = "thread_pool"
            self.executor_message = (
                "ProcessPoolExecutor was unavailable in this environment; backtest jobs run in a thread pool."
            )

    def submit(self, request: BacktestRequest, candles: list[dict]) -> BacktestResult:
        job = BacktestResult(
            job_id=str(uuid4()),
            symbol=request.symbol,
            strategy=request.strategy,
            benchmark_symbol=request.benchmark_symbol,
            started_at=datetime.now(tz=UTC),
            status="queued",
            params=request.params,
        )
        self.repository.save_job(job)

        future = self.executor.submit(run_backtest, request, candles)

        def _on_done(completed_future):
            try:
                result = completed_future.result()
                result.job_id = job.job_id
                self.repository.save_job(result)
            except Exception as exc:  # pragma: no cover
                failed = BacktestResult(
                    job_id=job.job_id,
                    symbol=request.symbol,
                    strategy=request.strategy,
                    benchmark_symbol=request.benchmark_symbol,
                    started_at=job.started_at,
                    completed_at=datetime.now(tz=UTC),
                    status="failed",
                    params=request.params,
                    error=str(exc),
                )
                self.repository.save_job(failed)

        future.add_done_callback(_on_done)
        queued = job.model_copy(update={"status": "running"})
        self.repository.save_job(queued)
        return queued

    def get(self, job_id: str) -> BacktestResult | None:
        return self.repository.get_job(job_id)
