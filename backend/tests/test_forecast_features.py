from datetime import UTC, datetime, timedelta

import pandas as pd

from app.services.forecast.feature_engineering import build_feature_frame


def test_forecast_feature_frame_aligns_future_target():
    start = datetime(2024, 1, 1, tzinfo=UTC)
    frame = pd.DataFrame(
        [
            {
                "timestamp": start + timedelta(days=index),
                "open": 100 + index,
                "high": 101 + index,
                "low": 99 + index,
                "close": 100 + index,
                "volume": 1_000_000 + index * 100,
            }
            for index in range(80)
        ]
    )
    features = build_feature_frame(frame)
    assert "future_return_5" in features.columns
    assert "future_class" in features.columns
    assert len(features) > 0
