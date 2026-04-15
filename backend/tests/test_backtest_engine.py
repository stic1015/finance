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


def test_sar_ema144_validation_rejects_invalid_params():
    try:
        validate_strategy_params(
            "sar_ema144_breakout",
            {"ema_window": 1, "sar_step": 0.02, "sar_max": 0.2},
        )
    except ValueError as exc:
        assert "ema_window" in str(exc)
    else:
        raise AssertionError("Expected validation error for invalid SAR/EMA params.")


def test_sar_ema144_backtest_runs():
    request = BacktestRequest(
        symbol="US.AAPL",
        strategy="sar_ema144_breakout",
        start_date=datetime(2024, 1, 1, tzinfo=UTC),
        end_date=datetime(2024, 8, 1, tzinfo=UTC),
        params={"ema_window": 144, "sar_step": 0.02, "sar_max": 0.2},
    )
    result = run_backtest(request, build_candles(320))
    assert result.status == "completed"
    assert result.metrics is not None
    assert len(result.equity_curve) > 0


def test_ema_adx_validation_rejects_invalid_windows():
    try:
        validate_strategy_params(
            "ema_adx_trend_follow",
            {"fast_ema": 89, "slow_ema": 21, "adx_window": 14, "adx_threshold": 20},
        )
    except ValueError as exc:
        assert "fast_ema" in str(exc)
    else:
        raise AssertionError("Expected validation error for EMA/ADX window ordering.")


def test_keltner_atr_breakout_backtest_runs():
    request = BacktestRequest(
        symbol="HK.00700",
        strategy="keltner_atr_breakout",
        start_date=datetime(2024, 1, 1, tzinfo=UTC),
        end_date=datetime(2024, 8, 1, tzinfo=UTC),
        params={"ema_window": 34, "atr_window": 20, "atr_multiplier": 1.8},
    )
    result = run_backtest(request, build_candles(320))
    assert result.status == "completed"
    assert result.metrics is not None
    assert result.metrics.trade_count >= 0


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
    assert result.monthly_returns
    assert result.monthly_trade_summaries
    assert result.trade_log is not None
    assert result.position_spans is not None
    assert result.strategy_summary
    if result.trade_log:
        assert result.trade_log[0].month
        assert result.trade_log[0].previous_exposure >= 0
