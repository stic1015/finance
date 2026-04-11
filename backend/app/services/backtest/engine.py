from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import numpy as np
import pandas as pd

from app.schemas.models import (
    BacktestMetrics,
    BacktestRequest,
    BacktestResult,
    EquityPoint,
    MonthlyReturnPoint,
    MonthlyTradeSummary,
    PositionSpan,
    TradeLogEntry,
)
from app.services.backtest.strategies import STRATEGIES, build_signal_frame


def candles_to_frame(candles: list[dict] | list) -> pd.DataFrame:
    records = []
    for point in candles:
        if hasattr(point, "model_dump"):
            records.append(point.model_dump())
        else:
            records.append(point)
    frame = pd.DataFrame(records)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    return frame


def validate_strategy_params(strategy: str, params: dict) -> dict:
    defaults = STRATEGIES[strategy].default_params
    merged = {**defaults, **params}
    if strategy == "moving_average_trend" and merged["fast_window"] >= merged["slow_window"]:
        raise ValueError("fast_window must be smaller than slow_window.")
    if strategy == "trend_strength_volatility_filter" and merged["vol_short"] >= merged["vol_long"]:
        raise ValueError("vol_short must be smaller than vol_long.")
    if strategy == "relative_strength_regime_rotation" and merged["short_lookback"] >= merged["long_lookback"]:
        raise ValueError("short_lookback must be smaller than long_lookback.")
    return merged


def run_backtest(request: BacktestRequest, candles: list[dict] | list) -> BacktestResult:
    params = validate_strategy_params(request.strategy, request.params)
    frame = candles_to_frame(candles)
    frame = frame[
        (frame["timestamp"] >= request.start_date) & (frame["timestamp"] <= request.end_date)
    ].copy()
    signal = build_signal_frame(frame, request.strategy, params)
    frame["signal"] = signal.shift(1).fillna(0.0)
    frame["returns"] = frame["close"].pct_change().fillna(0.0)

    total_cost = (request.fee_bps + request.slippage_bps) / 10_000
    trades = frame["signal"].diff().abs().fillna(0.0)
    frame["strategy_returns"] = frame["signal"] * frame["returns"] - trades * total_cost
    frame["equity"] = request.initial_capital * (1 + frame["strategy_returns"]).cumprod()
    frame["benchmark_equity"] = request.initial_capital * (1 + frame["returns"]).cumprod()

    daily = frame["strategy_returns"]
    wins = int((daily > 0).sum())
    downside = frame["equity"] / frame["equity"].cummax() - 1
    trade_count = int(trades.sum())
    equity_curve = [
        EquityPoint(
            timestamp=row["timestamp"].to_pydatetime().replace(tzinfo=UTC),
            equity=float(row["equity"]),
            benchmark_equity=float(row["benchmark_equity"]),
        )
        for _, row in frame.iterrows()
    ]
    excess_return = float(frame["equity"].iloc[-1] / frame["benchmark_equity"].iloc[-1] - 1)

    monthly_returns = [
        MonthlyReturnPoint(month=str(month), return_rate=float(values.add(1).prod() - 1))
        for month, values in frame.groupby(frame["timestamp"].dt.strftime("%Y-%m"))["strategy_returns"]
    ]

    trade_log: list[TradeLogEntry] = []
    trade_rows = frame.loc[trades > 0, ["timestamp", "close", "signal"]].copy()
    trade_rows["prev_signal"] = frame["signal"].shift(1).fillna(0.0).loc[trade_rows.index]
    for _, row in trade_rows.iterrows():
        action = "rebalance"
        if float(row["signal"]) > float(row["prev_signal"]):
            action = "buy"
        elif float(row["signal"]) < float(row["prev_signal"]):
            action = "sell"
        trade_log.append(
            TradeLogEntry(
                timestamp=row["timestamp"].to_pydatetime().replace(tzinfo=UTC),
                month=row["timestamp"].strftime("%Y-%m"),
                action=action,
                price=float(row["close"]),
                previous_exposure=float(row["prev_signal"]),
                exposure=float(row["signal"]),
                equity=float(frame.loc[frame["timestamp"] == row["timestamp"], "equity"].iloc[-1]),
                benchmark_equity=float(
                    frame.loc[frame["timestamp"] == row["timestamp"], "benchmark_equity"].iloc[-1]
                ),
            )
        )

    trade_rows["month"] = trade_rows["timestamp"].dt.strftime("%Y-%m")
    monthly_trade_summaries: list[MonthlyTradeSummary] = []
    for month, month_frame in frame.groupby(frame["timestamp"].dt.strftime("%Y-%m")):
        month_trade_rows = trade_rows.loc[trade_rows["month"] == month]
        buy_count = int((month_trade_rows["signal"] > month_trade_rows["prev_signal"]).sum())
        sell_count = int((month_trade_rows["signal"] < month_trade_rows["prev_signal"]).sum())
        rebalance_count = int(len(month_trade_rows) - buy_count - sell_count)
        monthly_trade_summaries.append(
            MonthlyTradeSummary(
                month=str(month),
                return_rate=float(month_frame["strategy_returns"].add(1).prod() - 1),
                benchmark_return=float(month_frame["returns"].add(1).prod() - 1),
                start_equity=float(month_frame["equity"].iloc[0]),
                end_equity=float(month_frame["equity"].iloc[-1]),
                trade_count=int(len(month_trade_rows)),
                buy_count=buy_count,
                sell_count=sell_count,
                rebalance_count=rebalance_count,
            )
        )

    position_spans: list[PositionSpan] = []
    current_start = None
    current_exposure = 0.0
    previous_exposure = 0.0
    for _, row in frame.iterrows():
        exposure = float(row["signal"])
        timestamp = row["timestamp"].to_pydatetime().replace(tzinfo=UTC)
        if exposure != previous_exposure:
            if current_start is not None and previous_exposure > 0:
                position_spans.append(
                    PositionSpan(start=current_start, end=timestamp, exposure=previous_exposure)
                )
            current_start = timestamp if exposure > 0 else None
            current_exposure = exposure
            previous_exposure = exposure
    if current_start is not None and current_exposure > 0:
        position_spans.append(
            PositionSpan(
                start=current_start,
                end=frame["timestamp"].iloc[-1].to_pydatetime().replace(tzinfo=UTC),
                exposure=current_exposure,
            )
        )

    sharpe = 0.0
    if float(daily.std()) > 0:
        sharpe = float(np.sqrt(252) * daily.mean() / daily.std())

    annualized = float(
        (frame["equity"].iloc[-1] / request.initial_capital) ** (252 / max(len(frame), 1)) - 1
    )
    metrics = BacktestMetrics(
        cumulative_return=float(frame["equity"].iloc[-1] / request.initial_capital - 1),
        annualized_return=annualized,
        sharpe_ratio=sharpe,
        max_drawdown=float(downside.min()),
        win_rate=float(wins / max((daily != 0).sum(), 1)),
        trade_count=trade_count,
        benchmark_return=float(frame["benchmark_equity"].iloc[-1] / request.initial_capital - 1),
    )

    return BacktestResult(
        job_id=str(uuid4()),
        symbol=request.symbol,
        strategy=request.strategy,
        benchmark_symbol=request.benchmark_symbol,
        started_at=datetime.now(tz=UTC),
        completed_at=datetime.now(tz=UTC),
        status="completed",
        metrics=metrics,
        equity_curve=equity_curve,
        monthly_returns=monthly_returns,
        monthly_trade_summaries=monthly_trade_summaries,
        trade_log=trade_log,
        position_spans=position_spans,
        excess_return=excess_return,
        strategy_summary=STRATEGIES[request.strategy].logic_summary,
        params=params,
        caveats=[
            "Signals are shifted by one bar to reduce look-ahead bias.",
            "This backtest does not yet model survivorship bias across changing universes.",
            STRATEGIES[request.strategy].logic_summary,
        ],
    )
