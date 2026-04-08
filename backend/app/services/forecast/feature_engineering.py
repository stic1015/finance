from __future__ import annotations

import numpy as np
import pandas as pd


def build_feature_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
    frame = dataframe.copy()
    frame["return_1"] = frame["close"].pct_change()
    frame["return_5"] = frame["close"].pct_change(5)
    frame["volatility_10"] = frame["return_1"].rolling(10).std()
    frame["volatility_20"] = frame["return_1"].rolling(20).std()
    frame["sma_10"] = frame["close"].rolling(10).mean()
    frame["sma_20"] = frame["close"].rolling(20).mean()
    frame["sma_ratio"] = frame["sma_10"] / frame["sma_20"]
    frame["volume_ratio"] = frame["volume"] / frame["volume"].rolling(20).mean()
    frame["range_ratio"] = (frame["high"] - frame["low"]) / frame["close"]
    frame["future_return_5"] = frame["close"].shift(-5) / frame["close"] - 1

    conditions = [
        frame["future_return_5"] > 0.02,
        frame["future_return_5"] < -0.02,
    ]
    frame["future_class"] = np.select(conditions, [2, 0], default=1)
    return frame.dropna().reset_index(drop=True)
