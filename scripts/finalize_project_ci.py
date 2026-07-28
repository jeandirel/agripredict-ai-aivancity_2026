#!/usr/bin/env python3
"""Run the final scientific protocol with a bounded CI compute budget.

The initial benchmark already compares the compact MLP with tree and linear
models. The final no-test-selection protocol focuses on the strong classical
candidate families, uses three parcel-grouped folds, and lowers ensemble sizes
only for CI delivery. The scientific split, conformal calibration, ablations,
robustness, OOD and reporting remain unchanged.
"""

from __future__ import annotations

import runpy
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import GroupKFold

import agripredict.advanced as advanced
import agripredict.modeling as modeling

_ORIGINAL_MODEL_CANDIDATES = modeling.model_candidates


def bounded_model_candidates(
    X: pd.DataFrame,
    random_state: int = 42,
) -> dict[str, Any]:
    candidates = _ORIGINAL_MODEL_CANDIDATES(X, random_state=random_state)
    candidates.pop("mlp_neural_network", None)
    if "random_forest" in candidates:
        candidates["random_forest"].set_params(model__n_estimators=180)
    if "extra_trees" in candidates:
        candidates["extra_trees"].set_params(model__n_estimators=180)
    if "hist_gradient_boosting" in candidates:
        candidates["hist_gradient_boosting"].set_params(model__max_iter=180)
    return candidates


def bounded_select_model_without_test(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    *,
    random_state: int = 42,
) -> tuple[str, list[dict[str, float | str | None]]]:
    unique_groups = int(groups.nunique())
    splits = min(3, unique_groups)
    if splits < 2:
        raise ValueError("At least two stable parcel groups are required")

    results: list[dict[str, float | str | None]] = []
    splitter = GroupKFold(n_splits=splits)
    for name, candidate in bounded_model_candidates(X, random_state=random_state).items():
        scores: list[float] = []
        try:
            for train_index, validation_index in splitter.split(X, y, groups):
                fitted = clone(candidate)
                fitted.fit(X.iloc[train_index], y.iloc[train_index])
                prediction = fitted.predict(X.iloc[validation_index])
                scores.append(float(mean_absolute_error(y.iloc[validation_index], prediction)))
            results.append(
                {
                    "model": name,
                    "group_cv_mae_mean": float(np.mean(scores)),
                    "group_cv_mae_std": float(np.std(scores)),
                    "folds": splits,
                    "status": "ok",
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "model": name,
                    "group_cv_mae_mean": None,
                    "group_cv_mae_std": None,
                    "folds": splits,
                    "status": f"failed: {type(exc).__name__}: {exc}",
                }
            )

    valid = [item for item in results if item["group_cv_mae_mean"] is not None]
    if not valid:
        raise RuntimeError("Every bounded final-selection candidate failed")
    valid.sort(key=lambda item: float(item["group_cv_mae_mean"]))
    return str(valid[0]["model"]), results


# Patch the module globals used by strict_evaluate and by the finalizer imported
# after this point. The baseline workflow and normal local command remain intact.
modeling.model_candidates = bounded_model_candidates
advanced.model_candidates = bounded_model_candidates
advanced.select_model_without_test = bounded_select_model_without_test

sys.argv[0] = "scripts/finalize_project.py"
runpy.run_path("scripts/finalize_project.py", run_name="__main__")
