from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ProbabilisticModelBundle:
    classifier: object
    regressor: object
    family: str


def create_model_bundle() -> ProbabilisticModelBundle:
    try:
        from xgboost import XGBClassifier, XGBRegressor

        classifier = XGBClassifier(
            max_depth=3,
            n_estimators=120,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
        )
        regressor = XGBRegressor(
            max_depth=3,
            n_estimators=120,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
        )
        return ProbabilisticModelBundle(classifier=classifier, regressor=regressor, family="xgboost")
    except Exception:  # pragma: no cover
        from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

        return ProbabilisticModelBundle(
            classifier=GradientBoostingClassifier(random_state=7),
            regressor=GradientBoostingRegressor(random_state=7),
            family="gradient_boosting_fallback",
        )


def normalize_probabilities(probabilities: np.ndarray) -> list[float]:
    probabilities = np.clip(probabilities, 0.0, 1.0)
    total = probabilities.sum()
    if total <= 0:
        return [0.33, 0.34, 0.33]
    return [float(value / total) for value in probabilities]
