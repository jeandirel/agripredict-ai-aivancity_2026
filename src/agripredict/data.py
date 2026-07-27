"""Dataset loading, leakage guards and split helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

TARGET = "harvest_doy_derived"
ROW_KEY_COLUMN = "parcelle_uid"
GROUP_COLUMN = "ID_PARCEL"
YEAR_COLUMN = "year"
IDENTIFIER_COLUMNS = {ROW_KEY_COLUMN, GROUP_COLUMN}


@dataclass(frozen=True)
class PreparedData:
    X: pd.DataFrame
    y: pd.Series
    groups: pd.Series
    years: pd.Series
    excluded_columns: tuple[str, ...]


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load a CSV and enforce the minimum project schema."""
    frame = pd.read_csv(path, low_memory=False)
    required = {TARGET, ROW_KEY_COLUMN, GROUP_COLUMN, YEAR_COLUMN}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"Dataset is empty: {path}")
    return frame


def temporal_risk_reason(column: str, horizon: str) -> str | None:
    """Return a conservative leakage-risk reason for one feature.

    Peak, day-of-year and April-May-June aggregate features are excluded until
    their generation windows and target lineage are proven. This intentionally
    favors scientific validity over an optimistic score.
    """
    lower = column.lower()
    if column == TARGET:
        return "target"
    if column in IDENTIFIER_COLUMNS:
        return "identifier memorisation risk"
    if "peak" in lower:
        return "peak statistic requires cutoff and target-lineage validation"
    if "_doy" in lower or lower.endswith("doy"):
        return "day-of-year feature requires cutoff and target-lineage validation"
    if "_amj_" in lower:
        return "April-May-June aggregate may include observations after the cutoff"
    if horizon == "may31" and any(token in lower for token in ("june", "jun_", "to_june")):
        return "June information is unavailable at the 31-May cutoff"
    return None


def prepare_data(
    frame: pd.DataFrame,
    horizon: str,
    *,
    allow_temporal_risk_features: bool = False,
) -> PreparedData:
    """Build leakage-aware features and aligned target/group/year vectors.

    `parcelle_uid` is the parcel-year row key. `ID_PARCEL` is the stable parcel
    identifier used for grouped validation so that the same physical parcel
    cannot leak across folds through different years.
    """
    if horizon not in {"may31", "june15"}:
        raise ValueError("horizon must be 'may31' or 'june15'")

    clean = frame.copy()
    clean[TARGET] = pd.to_numeric(clean[TARGET], errors="coerce")
    clean[YEAR_COLUMN] = pd.to_numeric(clean[YEAR_COLUMN], errors="coerce")
    clean = clean.dropna(
        subset=[TARGET, YEAR_COLUMN, ROW_KEY_COLUMN, GROUP_COLUMN]
    ).reset_index(drop=True)

    excluded: list[str] = []
    feature_columns: list[str] = []
    for column in clean.columns:
        reason = temporal_risk_reason(column, horizon)
        if column == TARGET:
            excluded.append(column)
        elif reason and not allow_temporal_risk_features:
            excluded.append(column)
        else:
            feature_columns.append(column)

    if not feature_columns:
        raise ValueError("No feature columns remain after leakage filtering")

    return PreparedData(
        X=clean[feature_columns],
        y=clean[TARGET].astype(float),
        groups=clean[GROUP_COLUMN].astype(str),
        years=clean[YEAR_COLUMN].astype(int),
        excluded_columns=tuple(sorted(excluded)),
    )


def common_parcel_year_keys(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    """Return the parcel-year intersection used for a fair horizon comparison."""
    keys = [ROW_KEY_COLUMN, YEAR_COLUMN]
    left_keys = left[keys].drop_duplicates()
    right_keys = right[keys].drop_duplicates()
    return left_keys.merge(right_keys, on=keys, how="inner")
