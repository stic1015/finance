from datetime import UTC, datetime, timedelta

from app.schemas.models import BacktestRequest
from app.services.backtest.engine import run_backtest, validate_strategy_params


def build_candles(count: int = 220):
    start = datetime(2024, 1, 1, tzinfo=UTC)
    candles = []
    price = 100.0
    for index in range(count):
        price *= 1.002 if index % 7 else 0.998
        candles.append(
            {
                "timestamp": start + timedelta(days=index),
                "open": price * 0.99,
                "high": price * 1.01,
                "low": price * 0.98,
                "close": price,
                "volume": 1_000_000 + index * 1000,
            }
        )
    return candles


def test_strategy_validation_rejects_invalid_windows():
    try:
        validate_strategy_params("moving_average_trend", {"fast_window": 60, "slow_window": 20})
    except ValueError as exc:
        assert "fast_window" in str(exc)
    else:
        raise AssertionError("Expected validation error for invalid moving average windows.")


def test_backtest_runs_without_lookahead_crash():
    request = BacktestRequest(
        symbol="US.AAPL",
        strategy="moving_average_trend",
        start_date=datetime(2024, 1, 1, tzinfo=UTC),
        end_date=datetime(2024, 8, 1, tzinfo=UTC),
    )
    result = run_backtest(request, build_candles())
    assert result.status == "completed"
    assert result.metrics is not None
    assert result.metrics.trade_count >= 0
