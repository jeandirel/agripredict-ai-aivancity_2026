"""Advanced, leakage-aware evaluation utilities for AgriPredict AI.

The module implements the scientific protocol used for the final report:
- model selection without consulting the final year;
- chronological calibration and test years;
- split-conformal prediction intervals;
- modality ablations;
- robustness and out-of-distribution diagnostics;
- bootstrap confidence intervals and paired horizon comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

from agripredict.modeling import (
    global_feature_importance,
    model_candidates,
    regression_metrics,
)


@dataclass(frozen=True)
class ChronologicalMasks:
    development: np.ndarray
    calibration: np.ndarray
    test: np.ndarray
    development_years: tuple[int, ...]
    calibration_year: int
    test_year: int


@dataclass
class StrictEvaluation:
    selected_model_name: str
    fitted_evaluation_model: Any
    temporal_metrics: dict[str, float]
    selection_scores: list[dict[str, float | str | None]]
    calibration_quantile_days: float
    interval_coverage: float
    interval_mean_width_days: float
    interval_median_width_days: float
    predictions: np.ndarray
    lower_bounds: np.ndarray
    upper_bounds: np.ndarray
    feature_importance: list[dict[str, float | str]]
    bootstrap_mae_ci95: tuple[float, float]


def chronological_masks(years: pd.Series) -> ChronologicalMasks:
    """Create development, calibration and untouched latest-year test masks."""
    numeric_years = pd.to_numeric(years, errors="raise").astype(int)
    unique_years = tuple(sorted(int(year) for year in numeric_years.unique()))
    if len(unique_years) < 3:
        raise ValueError(
            "At least three distinct years are required for development, calibration and final test"
        )
    calibration_year = unique_years[-2]
    test_year = unique_years[-1]
    development_years = unique_years[:-2]
    development = numeric_years.isin(development_years).to_numpy()
    calibration = numeric_years.eq(calibration_year).to_numpy()
    test = numeric_years.eq(test_year).to_numpy()
    if development.sum() < 20 or calibration.sum() < 5 or test.sum() < 5:
        raise ValueError(
            "Chronological split is too small: "
            f"development={development.sum()}, calibration={calibration.sum()}, test={test.sum()}"
        )
    return ChronologicalMasks(
        development=development,
        calibration=calibration,
        test=test,
        development_years=development_years,
        calibration_year=calibration_year,
        test_year=test_year,
    )


def _group_cv_scores(
    candidate: Any,
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    *,
    max_splits: int = 5,
) -> tuple[float, float]:
    unique_groups = int(groups.nunique())
    splits = min(max_splits, unique_groups)
    if splits < 2:
        raise ValueError("At least two parcel groups are required")
    fold_scores: list[float] = []
    splitter = GroupKFold(n_splits=splits)
    for train_index, validation_index in splitter.split(X, y, groups):
        fitted = clone(candidate)
        fitted.fit(X.iloc[train_index], y.iloc[train_index])
        prediction = fitted.predict(X.iloc[validation_index])
        fold_scores.append(float(mean_absolute_error(y.iloc[validation_index], prediction)))
    return float(np.mean(fold_scores)), float(np.std(fold_scores))


def select_model_without_test(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    *,
    random_state: int = 42,
) -> tuple[str, list[dict[str, float | str | None]]]:
    """Select the model family using grouped CV on development years only."""
    results: list[dict[str, float | str | None]] = []
    for name, candidate in model_candidates(X, random_state=random_state).items():
        try:
            mean_score, std_score = _group_cv_scores(candidate, X, y, groups)
            results.append(
                {
                    "model": name,
                    "group_cv_mae_mean": mean_score,
                    "group_cv_mae_std": std_score,
                    "status": "ok",
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "model": name,
                    "group_cv_mae_mean": None,
                    "group_cv_mae_std": None,
                    "status": f"failed: {type(exc).__name__}: {exc}",
                }
            )
    valid = [item for item in results if item["group_cv_mae_mean"] is not None]
    if not valid:
        raise RuntimeError("Every model candidate failed during grouped model selection")
    valid.sort(key=lambda item: float(item["group_cv_mae_mean"]))
    return str(valid[0]["model"]), results


def conformal_quantile(residuals: np.ndarray, alpha: float = 0.10) -> float:
    """Finite-sample split-conformal absolute-residual quantile."""
    values = np.asarray(residuals, dtype=float)
    if values.size == 0:
        raise ValueError("Calibration residuals are empty")
    level = min(1.0, np.ceil((values.size + 1) * (1 - alpha)) / values.size)
    return float(np.quantile(values, level, method="higher"))


def bootstrap_mae_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    n_bootstrap: int = 2000,
    random_state: int = 42,
) -> tuple[float, float]:
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if true.size != pred.size or true.size == 0:
        raise ValueError("Bootstrap inputs must be non-empty and aligned")
    generator = np.random.default_rng(random_state)
    scores = np.empty(n_bootstrap, dtype=float)
    for index in range(n_bootstrap):
        sample = generator.integers(0, true.size, size=true.size)
        scores[index] = mean_absolute_error(true[sample], pred[sample])
    return float(np.quantile(scores, 0.025)), float(np.quantile(scores, 0.975))


def strict_evaluate(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    years: pd.Series,
    *,
    random_state: int = 42,
    alpha: float = 0.10,
) -> tuple[StrictEvaluation, ChronologicalMasks]:
    """Run the final no-test-selection protocol for one forecasting horizon."""
    masks = chronological_masks(years)
    X_development = X.loc[masks.development].reset_index(drop=True)
    y_development = y.loc[masks.development].reset_index(drop=True)
    groups_development = groups.loc[masks.development].reset_index(drop=True)
    X_calibration = X.loc[masks.calibration].reset_index(drop=True)
    y_calibration = y.loc[masks.calibration].reset_index(drop=True)
    X_test = X.loc[masks.test].reset_index(drop=True)
    y_test = y.loc[masks.test].reset_index(drop=True)

    selected_name, selection_scores = select_model_without_test(
        X_development,
        y_development,
        groups_development,
        random_state=random_state,
    )
    selected = model_candidates(X_development, random_state=random_state)[selected_name]
    fitted = clone(selected)
    fitted.fit(X_development, y_development)

    calibration_prediction = fitted.predict(X_calibration)
    residuals = np.abs(y_calibration.to_numpy(dtype=float) - calibration_prediction)
    radius = conformal_quantile(residuals, alpha=alpha)

    prediction = np.asarray(fitted.predict(X_test), dtype=float)
    lower = prediction - radius
    upper = prediction + radius
    true = y_test.to_numpy(dtype=float)
    coverage = float(np.mean((true >= lower) & (true <= upper)))
    importance = global_feature_importance(
        fitted,
        X_test,
        y_test,
        random_state=random_state,
        top_k=25,
    )
    evaluation = StrictEvaluation(
        selected_model_name=selected_name,
        fitted_evaluation_model=fitted,
        temporal_metrics=regression_metrics(y_test, prediction),
        selection_scores=selection_scores,
        calibration_quantile_days=radius,
        interval_coverage=coverage,
        interval_mean_width_days=float(np.mean(upper - lower)),
        interval_median_width_days=float(np.median(upper - lower)),
        predictions=prediction,
        lower_bounds=lower,
        upper_bounds=upper,
        feature_importance=importance,
        bootstrap_mae_ci95=bootstrap_mae_ci(true, prediction, random_state=random_state),
    )
    return evaluation, masks


def feature_modality(column: str) -> str:
    """Map one project feature to a documented modality."""
    if column in {"year", "SURF_PARC", "region"}:
        return "context"
    if column.startswith(
        (
            "phh2o_",
            "nitrogen_",
            "soc_",
            "clay_",
            "sand_",
            "silt_",
            "cec_",
            "bdod_",
            "cfvo_",
            "wv",
            "ocd_",
        )
    ):
        return "soil"
    if column.startswith("s1_"):
        return "sentinel1"
    if column.startswith("s2_"):
        return "sentinel2"
    if column.startswith("meteo_"):
        return "weather"
    return "other"


def columns_for_modalities(columns: Iterable[str], modalities: set[str]) -> list[str]:
    selected = [column for column in columns if feature_modality(column) in modalities]
    context = [column for column in columns if feature_modality(column) == "context"]
    return list(dict.fromkeys(context + selected))


def ablation_study(
    X: pd.DataFrame,
    y: pd.Series,
    years: pd.Series,
    model_name: str,
    masks: ChronologicalMasks,
    *,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Evaluate fixed model family across modality subsets on the untouched test year."""
    configurations: dict[str, set[str]] = {
        "context_only": set(),
        "soil": {"soil"},
        "sentinel1": {"sentinel1"},
        "sentinel2": {"sentinel2"},
        "weather": {"weather"},
        "satellite": {"sentinel1", "sentinel2"},
        "soil_weather": {"soil", "weather"},
        "satellite_weather": {"sentinel1", "sentinel2", "weather"},
        "satellite_soil": {"sentinel1", "sentinel2", "soil"},
        "all_modalities": {"soil", "sentinel1", "sentinel2", "weather", "other"},
    }
    rows: list[dict[str, Any]] = []
    for label, modalities in configurations.items():
        subset_columns = columns_for_modalities(X.columns, modalities)
        if not subset_columns:
            continue
        X_subset = X[subset_columns]
        X_train = X_subset.loc[masks.development | masks.calibration]
        y_train = y.loc[masks.development | masks.calibration]
        X_test = X_subset.loc[masks.test]
        y_test = y.loc[masks.test]
        candidate = model_candidates(X_train, random_state=random_state)[model_name]
        fitted = clone(candidate)
        fitted.fit(X_train, y_train)
        prediction = fitted.predict(X_test)
        rows.append(
            {
                "configuration": label,
                "modalities": sorted(modalities),
                "feature_count": len(subset_columns),
                **regression_metrics(y_test, prediction),
            }
        )
    return sorted(rows, key=lambda item: float(item["mae_days"]))


def robustness_study(
    model: Any,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    *,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Measure degradation under missingness, noise and missing modalities."""
    generator = np.random.default_rng(random_state)
    baseline_prediction = model.predict(X_test)
    baseline = regression_metrics(y_test, baseline_prediction)
    scenarios: list[tuple[str, pd.DataFrame]] = [("baseline", X_test.copy())]

    numeric = list(X_test.select_dtypes(include=["number", "bool"]).columns)
    if numeric:
        missing = X_test.copy()
        mask = generator.random((len(missing), len(numeric))) < 0.10
        numeric_values = missing[numeric].astype(float).to_numpy()
        numeric_values[mask] = np.nan
        missing.loc[:, numeric] = numeric_values
        scenarios.append(("numeric_missing_10pct", missing))

        noisy = X_test.copy()
        for column in numeric:
            train_column = pd.to_numeric(X_train[column], errors="coerce")
            scale = float(train_column.std())
            if np.isfinite(scale) and scale > 0:
                values = pd.to_numeric(noisy[column], errors="coerce").to_numpy(dtype=float)
                noisy[column] = values + generator.normal(0.0, 0.05 * scale, size=len(values))
        scenarios.append(("numeric_noise_5pct_std", noisy))

    for modality in ("soil", "sentinel1", "sentinel2", "weather"):
        columns = [column for column in X_test.columns if feature_modality(column) == modality]
        if columns:
            dropped = X_test.copy()
            dropped.loc[:, columns] = np.nan
            scenarios.append((f"missing_{modality}", dropped))

    results: list[dict[str, Any]] = []
    for name, frame in scenarios:
        try:
            metrics = regression_metrics(y_test, model.predict(frame))
            results.append(
                {
                    "scenario": name,
                    **metrics,
                    "delta_mae_days": float(metrics["mae_days"] - baseline["mae_days"]),
                    "relative_mae_change": float(
                        (metrics["mae_days"] - baseline["mae_days"]) / baseline["mae_days"]
                    ),
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "scenario": name,
                    "status": f"failed: {type(exc).__name__}: {exc}",
                }
            )
    return results


def ood_diagnostics(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    *,
    random_state: int = 42,
) -> dict[str, float | int]:
    """Build a transparent numeric-distance OOD diagnostic with synthetic stress cases."""
    numeric = list(X_train.select_dtypes(include=["number", "bool"]).columns)
    if not numeric:
        return {"numeric_feature_count": 0, "test_flagged_rate": 0.0, "synthetic_ood_auc": 0.5}
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    train_values = scaler.fit_transform(imputer.fit_transform(X_train[numeric]))
    test_values = scaler.transform(imputer.transform(X_test[numeric]))
    train_distance = np.sqrt(np.mean(np.square(train_values), axis=1))
    test_distance = np.sqrt(np.mean(np.square(test_values), axis=1))
    threshold = float(np.quantile(train_distance, 0.95))

    generator = np.random.default_rng(random_state)
    synthetic = test_values.copy()
    if synthetic.size:
        feature_count = max(1, int(np.ceil(synthetic.shape[1] * 0.20)))
        selected = generator.choice(synthetic.shape[1], size=feature_count, replace=False)
        synthetic[:, selected] += generator.choice([-5.0, 5.0], size=(len(synthetic), feature_count))
    synthetic_distance = np.sqrt(np.mean(np.square(synthetic), axis=1))
    labels = np.concatenate([np.zeros(len(test_distance)), np.ones(len(synthetic_distance))])
    scores = np.concatenate([test_distance, synthetic_distance])
    auc = float(roc_auc_score(labels, scores)) if len(np.unique(labels)) == 2 else 0.5
    return {
        "numeric_feature_count": len(numeric),
        "distance_threshold_q95": threshold,
        "test_flagged_count": int(np.sum(test_distance > threshold)),
        "test_flagged_rate": float(np.mean(test_distance > threshold)),
        "test_distance_mean": float(np.mean(test_distance)),
        "test_distance_max": float(np.max(test_distance)),
        "synthetic_ood_auc": auc,
    }


def segmented_metrics(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    predictions: np.ndarray,
) -> list[dict[str, Any]]:
    """Report errors by target timing and parcel-surface quartiles."""
    frame = pd.DataFrame(
        {
            "target": y_test.to_numpy(dtype=float),
            "prediction": np.asarray(predictions, dtype=float),
        }
    )
    frame["absolute_error"] = np.abs(frame["target"] - frame["prediction"])
    output: list[dict[str, Any]] = []
    try:
        frame["target_quartile"] = pd.qcut(frame["target"], q=4, duplicates="drop")
        for label, group in frame.groupby("target_quartile", observed=True):
            output.append(
                {
                    "segment_type": "target_quartile",
                    "segment": str(label),
                    "rows": int(len(group)),
                    **regression_metrics(group["target"], group["prediction"].to_numpy()),
                }
            )
    except ValueError:
        pass

    if "SURF_PARC" in X_test.columns:
        surface = pd.to_numeric(X_test["SURF_PARC"], errors="coerce").reset_index(drop=True)
        valid = surface.notna()
        try:
            labels = pd.qcut(surface[valid], q=4, duplicates="drop")
            for label in labels.cat.categories:
                index = labels.index[labels == label]
                group = frame.loc[index]
                output.append(
                    {
                        "segment_type": "surface_quartile",
                        "segment": str(label),
                        "rows": int(len(group)),
                        **regression_metrics(group["target"], group["prediction"].to_numpy()),
                    }
                )
        except ValueError:
            pass
    return output


def paired_horizon_bootstrap(
    y_true: np.ndarray,
    may_predictions: np.ndarray,
    june_predictions: np.ndarray,
    *,
    n_bootstrap: int = 5000,
    random_state: int = 42,
) -> dict[str, float | str]:
    """Paired bootstrap of June-15 minus May-31 absolute error."""
    true = np.asarray(y_true, dtype=float)
    may_error = np.abs(true - np.asarray(may_predictions, dtype=float))
    june_error = np.abs(true - np.asarray(june_predictions, dtype=float))
    if not (len(true) == len(may_error) == len(june_error)):
        raise ValueError("Paired horizon arrays are not aligned")
    difference = june_error - may_error
    generator = np.random.default_rng(random_state)
    means = np.empty(n_bootstrap, dtype=float)
    for index in range(n_bootstrap):
        sample = generator.integers(0, len(difference), size=len(difference))
        means[index] = np.mean(difference[sample])
    lower, upper = np.quantile(means, [0.025, 0.975])
    mean = float(np.mean(difference))
    conclusion = "june15_better" if upper < 0 else "may31_better" if lower > 0 else "inconclusive"
    return {
        "mean_delta_absolute_error_days_june_minus_may": mean,
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
        "probability_june15_lower_error": float(np.mean(means < 0)),
        "conclusion": conclusion,
    }
