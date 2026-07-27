"""Leakage-aware modeling, validation and reporting utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class ModelEvaluation:
    name: str
    temporal_metrics: dict[str, float]
    group_cv_mae_mean: float | None
    group_cv_mae_std: float | None
    fitted_model: Pipeline
    predictions: np.ndarray


def regression_metrics(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    absolute_error = np.abs(true - pred)
    return {
        "mae_days": float(mean_absolute_error(true, pred)),
        "rmse_days": float(np.sqrt(mean_squared_error(true, pred))),
        "median_absolute_error_days": float(np.median(absolute_error)),
        "r2": float(r2_score(true, pred)),
        "bias_days": float(np.mean(pred - true)),
        "p90_absolute_error_days": float(np.quantile(absolute_error, 0.90)),
        "within_3_days": float(np.mean(absolute_error <= 3)),
        "within_5_days": float(np.mean(absolute_error <= 5)),
        "within_7_days": float(np.mean(absolute_error <= 7)),
        "within_10_days": float(np.mean(absolute_error <= 10)),
    }


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric = list(X.select_dtypes(include=["number", "bool"]).columns)
    categorical = [column for column in X.columns if column not in numeric]
    numeric_pipeline = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric),
            ("categorical", categorical_pipeline, categorical),
        ],
        remainder="drop",
        sparse_threshold=0,
    )


def model_candidates(X: pd.DataFrame, random_state: int = 42) -> dict[str, Pipeline]:
    """Return strong tabular baselines plus a compact neural network."""
    preprocessor = build_preprocessor(X)

    def pipe(model: Any, *, scale: bool = False) -> Pipeline:
        steps: list[tuple[str, Any]] = [("preprocess", clone(preprocessor))]
        if scale:
            steps.append(("scale", StandardScaler()))
        steps.append(("model", model))
        return Pipeline(steps)

    return {
        "dummy_median": pipe(DummyRegressor(strategy="median")),
        "ridge": pipe(Ridge(alpha=10.0), scale=True),
        "random_forest": pipe(
            RandomForestRegressor(
                n_estimators=400,
                min_samples_leaf=2,
                max_features=0.75,
                n_jobs=-1,
                random_state=random_state,
            )
        ),
        "extra_trees": pipe(
            ExtraTreesRegressor(
                n_estimators=400,
                min_samples_leaf=2,
                max_features=0.9,
                n_jobs=-1,
                random_state=random_state,
            )
        ),
        "hist_gradient_boosting": pipe(
            HistGradientBoostingRegressor(
                learning_rate=0.05,
                max_iter=300,
                l2_regularization=1.0,
                random_state=random_state,
            )
        ),
        "mlp_neural_network": pipe(
            MLPRegressor(
                hidden_layer_sizes=(128, 64),
                activation="relu",
                alpha=1e-3,
                learning_rate_init=1e-3,
                max_iter=600,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=30,
                random_state=random_state,
            ),
            scale=True,
        ),
    }


def group_cv_mae(model: Pipeline, X: pd.DataFrame, y: pd.Series, groups: pd.Series) -> tuple[float, float] | None:
    unique_groups = int(groups.nunique())
    splits = min(5, unique_groups)
    if splits < 2:
        return None
    scores: list[float] = []
    splitter = GroupKFold(n_splits=splits)
    for train_index, valid_index in splitter.split(X, y, groups):
        fold_model = clone(model)
        fold_model.fit(X.iloc[train_index], y.iloc[train_index])
        prediction = fold_model.predict(X.iloc[valid_index])
        scores.append(float(mean_absolute_error(y.iloc[valid_index], prediction)))
    return float(np.mean(scores)), float(np.std(scores))


def evaluate_candidates(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    groups_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    random_state: int = 42,
) -> list[ModelEvaluation]:
    evaluations: list[ModelEvaluation] = []
    for name, candidate in model_candidates(X_train, random_state=random_state).items():
        fitted = clone(candidate)
        fitted.fit(X_train, y_train)
        prediction = fitted.predict(X_test)
        cv = group_cv_mae(candidate, X_train.reset_index(drop=True), y_train.reset_index(drop=True), groups_train.reset_index(drop=True))
        evaluations.append(
            ModelEvaluation(
                name=name,
                temporal_metrics=regression_metrics(y_test, prediction),
                group_cv_mae_mean=cv[0] if cv else None,
                group_cv_mae_std=cv[1] if cv else None,
                fitted_model=fitted,
                predictions=np.asarray(prediction),
            )
        )
    return sorted(evaluations, key=lambda item: item.temporal_metrics["mae_days"])


def global_feature_importance(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    *,
    random_state: int = 42,
    top_k: int = 20,
) -> list[dict[str, float | str]]:
    result = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="neg_mean_absolute_error",
        n_repeats=8,
        random_state=random_state,
        n_jobs=-1,
    )
    order = np.argsort(result.importances_mean)[::-1][:top_k]
    return [
        {
            "feature": str(X_test.columns[index]),
            "importance_mean": float(result.importances_mean[index]),
            "importance_std": float(result.importances_std[index]),
        }
        for index in order
    ]
