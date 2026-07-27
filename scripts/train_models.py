#!/usr/bin/env python3
"""Train leakage-aware baselines for the 31-May and 15-June horizons."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from agripredict.data import TARGET, common_parcel_year_keys, load_dataset, prepare_data
from agripredict.modeling import evaluate_candidates, global_feature_importance

DATASETS = {
    "may31": Path("data/master_ml_final_may31.csv"),
    "june15": Path("data/master_ml_final_june15.csv"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/models")
    parser.add_argument("--report-dir", default="reports/modeling")
    parser.add_argument("--allow-temporal-risk-features", action="store_true")
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def temporal_split(years: pd.Series) -> tuple[np.ndarray, np.ndarray, int]:
    latest_year = int(years.max())
    test_mask = years.eq(latest_year).to_numpy()
    train_mask = years.lt(latest_year).to_numpy()
    if train_mask.sum() < 20 or test_mask.sum() < 5:
        raise ValueError(
            f"A strict latest-year holdout is impossible: train={train_mask.sum()}, test={test_mask.sum()}, year={latest_year}"
        )
    return train_mask, test_mask, latest_year


def train_one(
    horizon: str,
    path: Path,
    output_root: Path,
    allow_temporal_risk_features: bool,
    random_state: int,
) -> dict:
    frame = load_dataset(path)
    prepared = prepare_data(
        frame,
        horizon,
        allow_temporal_risk_features=allow_temporal_risk_features,
    )
    train_mask, test_mask, test_year = temporal_split(prepared.years)
    X_train, X_test = prepared.X.loc[train_mask], prepared.X.loc[test_mask]
    y_train, y_test = prepared.y.loc[train_mask], prepared.y.loc[test_mask]
    groups_train = prepared.groups.loc[train_mask]

    evaluations = evaluate_candidates(
        X_train,
        y_train,
        groups_train,
        X_test,
        y_test,
        random_state=random_state,
    )
    best = evaluations[0]
    residual_q90 = float(np.quantile(np.abs(y_test.to_numpy() - best.predictions), 0.90))
    importance = global_feature_importance(best.fitted_model, X_test, y_test, random_state=random_state)

    model_dir = output_root / horizon
    model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(best.fitted_model, model_dir / "model.joblib")

    metadata = {
        "generated_at": utc_now(),
        "horizon": horizon,
        "dataset": str(path),
        "task": "parcel-level wheat harvest-date regression",
        "target": TARGET,
        "target_unit": "day_of_year",
        "test_year": test_year,
        "train_rows": int(train_mask.sum()),
        "test_rows": int(test_mask.sum()),
        "feature_count": int(prepared.X.shape[1]),
        "feature_columns": list(prepared.X.columns),
        "excluded_columns": list(prepared.excluded_columns),
        "allow_temporal_risk_features": allow_temporal_risk_features,
        "selected_model": best.name,
        "temporal_metrics": best.temporal_metrics,
        "group_cv_mae_mean": best.group_cv_mae_mean,
        "group_cv_mae_std": best.group_cv_mae_std,
        "residual_absolute_error_q90_days": residual_q90,
        "global_feature_importance": importance,
        "caution": "Predictive associations are not causal. The target is derived and must be presented as such.",
        "candidate_results": [
            {
                "model": evaluation.name,
                "temporal_metrics": evaluation.temporal_metrics,
                "group_cv_mae_mean": evaluation.group_cv_mae_mean,
                "group_cv_mae_std": evaluation.group_cv_mae_std,
            }
            for evaluation in evaluations
        ],
    }
    (model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata


def comparison_summary() -> dict:
    may = load_dataset(DATASETS["may31"])
    june = load_dataset(DATASETS["june15"])
    keys = common_parcel_year_keys(may, june)
    merged = keys.merge(may[["parcelle_uid", "year", TARGET]], on=["parcelle_uid", "year"]).merge(
        june[["parcelle_uid", "year", TARGET]],
        on=["parcelle_uid", "year"],
        suffixes=("_may31", "_june15"),
    )
    delta = pd.to_numeric(merged[f"{TARGET}_may31"], errors="coerce") - pd.to_numeric(
        merged[f"{TARGET}_june15"], errors="coerce"
    )
    return {
        "common_parcel_years": int(len(keys)),
        "target_equal_count": int(delta.fillna(np.inf).eq(0).sum()),
        "target_different_count": int(delta.fillna(np.inf).ne(0).sum()),
        "max_absolute_target_difference": float(delta.abs().max()) if delta.notna().any() else None,
    }


def markdown_report(payload: dict) -> str:
    lines = [
        "# AgriPredict AI — Benchmark initial",
        "",
        f"> Généré le `{payload['generated_at']}`.",
        "",
        "## Comparaison des horizons",
        "",
        f"- Parcelles-années communes : **{payload['horizon_comparison']['common_parcel_years']}**",
        f"- Cibles différentes : **{payload['horizon_comparison']['target_different_count']}**",
        "",
        "## Résultats temporels",
        "",
        "| Horizon | Année test | Modèle | MAE | RMSE | R² | ±5 jours | ±7 jours | CV groupé MAE |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for horizon, result in payload["horizons"].items():
        metrics = result["temporal_metrics"]
        lines.append(
            f"| {horizon} | {result['test_year']} | {result['selected_model']} | "
            f"{metrics['mae_days']:.3f} | {metrics['rmse_days']:.3f} | {metrics['r2']:.3f} | "
            f"{metrics['within_5_days']:.1%} | {metrics['within_7_days']:.1%} | "
            f"{result['group_cv_mae_mean']:.3f} |"
        )
    lines += [
        "",
        "## Règle de lecture",
        "",
        "Ces résultats utilisent un filtre conservateur qui exclut les variables de pic, de jour de l’année et les agrégats AMJ tant que leur disponibilité à la date de coupure et leur indépendance vis-à-vis de la cible ne sont pas démontrées.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    output_root = Path(args.output)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    horizons = {
        horizon: train_one(
            horizon,
            path,
            output_root,
            args.allow_temporal_risk_features,
            args.random_state,
        )
        for horizon, path in DATASETS.items()
    }
    payload = {
        "generated_at": utc_now(),
        "horizon_comparison": comparison_summary(),
        "horizons": horizons,
    }
    (report_dir / "benchmark.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / "benchmark.md").write_text(markdown_report(payload), encoding="utf-8")
    print(markdown_report(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
