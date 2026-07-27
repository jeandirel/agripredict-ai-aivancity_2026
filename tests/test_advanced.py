from __future__ import annotations

import numpy as np
import pandas as pd

from agripredict.advanced import (
    chronological_masks,
    conformal_quantile,
    feature_modality,
    ood_diagnostics,
    paired_horizon_bootstrap,
)


def test_chronological_masks_reserve_penultimate_and_latest_years() -> None:
    years = pd.Series([2020, 2020, 2021, 2021, 2022, 2022, 2023, 2024])
    masks = chronological_masks(years)
    assert masks.development_years == (2020, 2021, 2022)
    assert masks.calibration_year == 2023
    assert masks.test_year == 2024
    assert int(masks.development.sum()) == 6
    assert int(masks.calibration.sum()) == 1
    assert int(masks.test.sum()) == 1


def test_conformal_quantile_is_conservative() -> None:
    residuals = np.arange(1, 11, dtype=float)
    radius = conformal_quantile(residuals, alpha=0.10)
    assert radius == 10.0


def test_feature_modality_mapping() -> None:
    assert feature_modality("phh2o_0-5cm") == "soil"
    assert feature_modality("s1_vv_mean") == "sentinel1"
    assert feature_modality("s2_ndvi_may_mean") == "sentinel2"
    assert feature_modality("meteo_gdd_spring") == "weather"
    assert feature_modality("SURF_PARC") == "context"


def test_paired_bootstrap_identifies_consistently_better_june_predictions() -> None:
    true = np.array([100, 110, 120, 130, 140], dtype=float)
    may = np.array([108, 118, 128, 138, 148], dtype=float)
    june = np.array([101, 111, 121, 131, 141], dtype=float)
    result = paired_horizon_bootstrap(true, may, june, n_bootstrap=500, random_state=7)
    assert result["mean_delta_absolute_error_days_june_minus_may"] < 0
    assert result["conclusion"] == "june15_better"


def test_ood_diagnostics_detects_synthetic_shift() -> None:
    generator = np.random.default_rng(42)
    train = pd.DataFrame(generator.normal(size=(200, 5)), columns=list("abcde"))
    test = pd.DataFrame(generator.normal(size=(50, 5)), columns=list("abcde"))
    result = ood_diagnostics(train, test, random_state=42)
    assert result["numeric_feature_count"] == 5
    assert 0.0 <= result["test_flagged_rate"] <= 1.0
    assert result["synthetic_ood_auc"] > 0.8
