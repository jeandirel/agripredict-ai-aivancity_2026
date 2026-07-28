"""FastAPI inference and scientific-insight service for AgriPredict AI."""

from __future__ import annotations

import calendar
import json
import math
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.schemas import (
    EvaluationResponse,
    ExplainResponse,
    FeatureSchemaResponse,
    HealthResponse,
    Horizon,
    HorizonComparisonResponse,
    InputEvidence,
    Modality,
    ModalityEvidence,
    ModelInfoResponse,
    OverviewResponse,
    PredictionRequest,
    PredictionResponse,
    ReadinessResponse,
    ReloadModelsResponse,
)

MODEL_ROOT = Path(os.getenv("AGRIPREDICT_MODEL_DIR", "artifacts/models"))
REPORT_ROOT = Path(os.getenv("AGRIPREDICT_REPORT_DIR", "reports/final"))
HORIZONS: tuple[Horizon, ...] = ("may31", "june15")
MODALITIES: tuple[Modality, ...] = ("context", "soil", "sentinel1", "sentinel2", "weather")
TEST_PREDICTION_COLUMNS = {
    "parcelle_uid",
    "year",
    "actual_doy",
    "predicted_doy",
    "lower_90_doy",
    "upper_90_doy",
    "absolute_error_days",
}


class ModelRegistry:
    """Load deployment models and their public scientific metadata."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.models: dict[str, Any] = {}
        self.metadata: dict[str, dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        self.models.clear()
        self.metadata.clear()
        for horizon in HORIZONS:
            model_path = self.root / horizon / "model.joblib"
            metadata_path = self.root / horizon / "metadata.json"
            if metadata_path.exists():
                self.metadata[horizon] = json.loads(metadata_path.read_text(encoding="utf-8"))
            if model_path.exists() and horizon in self.metadata:
                self.models[horizon] = joblib.load(model_path)

    def available(self) -> list[str]:
        return sorted(self.models)


def _parse_cors_origins(raw_value: str | None = None) -> list[str]:
    """Parse a restrictive comma-separated origin allowlist."""
    raw = os.getenv("AGRIPREDICT_CORS_ORIGINS", "") if raw_value is None else raw_value
    origins: list[str] = []
    for item in raw.split(","):
        candidate = item.strip().rstrip("/")
        if not candidate:
            continue
        parsed = urlsplit(candidate)
        if (
            candidate == "*"
            or parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(
                "AGRIPREDICT_CORS_ORIGINS must contain exact http(s) origins, never '*'"
            )
        normalized = f"{parsed.scheme}://{parsed.netloc}"
        if normalized not in origins:
            origins.append(normalized)
    return origins


def create_app(cors_origins: list[str] | None = None) -> FastAPI:
    """Create the API shell, including optional origin-restricted CORS."""
    api = FastAPI(
        title="AgriPredict AI API",
        version="1.1.0",
        description=(
            "Parcel-level wheat harvest-date prediction for the aivancity AI Clinic 2026. "
            "Research prototype restricted to Centre-Val de Loire."
        ),
    )
    origins = _parse_cors_origins() if cors_origins is None else _parse_cors_origins(
        ",".join(cors_origins)
    )
    if origins:
        api.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )
    return api


registry = ModelRegistry(MODEL_ROOT)
app = create_app()


def _metadata_or_503(horizon: Horizon) -> dict[str, Any]:
    metadata = registry.metadata.get(horizon)
    if metadata is None:
        raise HTTPException(
            status_code=503,
            detail=f"Scientific metadata for model '{horizon}' is not available",
        )
    return metadata


def _validated_or_503(model_class: type[Any], payload: dict[str, Any]) -> Any:
    try:
        return model_class.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Scientific artifacts are incomplete or invalid: {exc.errors()[0]['msg']}",
        ) from exc


_PARCEL_IDENTIFIER_PATTERN = re.compile(r"\b(?:parcelle_uid|ID_PARCEL)\b", re.IGNORECASE)
_GEOMETRY_KEYS = {
    "geometry",
    "geom",
    "wkt",
    "latitude",
    "longitude",
    "coordinates",
}


def _public_metadata_value(value: Any) -> Any:
    """Remove parcel identifiers and spatial records from public metadata."""
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, item in value.items():
            if key.casefold() in _GEOMETRY_KEYS:
                continue
            public_key = _PARCEL_IDENTIFIER_PATTERN.sub("case_id", str(key))
            output[public_key] = _public_metadata_value(item)
        return output
    if isinstance(value, list):
        return [_public_metadata_value(item) for item in value]
    if isinstance(value, str):
        return _PARCEL_IDENTIFIER_PATTERN.sub("case_id", value)
    return value


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=app.version,
        available_models=registry.available(),
    )


@app.get("/readiness", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    required = set(HORIZONS)
    available = set(registry.available())
    ready = required.issubset(available)
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        required_models=sorted(required),
        available_models=sorted(available),
        missing_models=sorted(required - available),
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        version=app.version,
        model_root=str(MODEL_ROOT),
        available_models=registry.available(),
        metadata=_public_metadata_value(registry.metadata),
    )


@app.post("/reload-models", response_model=ReloadModelsResponse)
def reload_models() -> ReloadModelsResponse:
    registry.reload()
    return ReloadModelsResponse(status="reloaded", available_models=registry.available())


def _feature_modality(feature: str) -> Modality:
    if feature in {"year", "SURF_PARC", "region"}:
        return "context"
    if feature.startswith("s1_"):
        return "sentinel1"
    if feature.startswith("s2_"):
        return "sentinel2"
    if feature.startswith("meteo_"):
        return "weather"
    return "soil"


def _modality_counts(expected: list[str]) -> dict[Modality, dict[str, int]]:
    counts = {
        modality: {"model_variables": 0, "user_features": 0}
        for modality in MODALITIES
    }
    for feature in expected:
        modality = _feature_modality(feature)
        counts[modality]["model_variables"] += 1
        if feature != "year":
            counts[modality]["user_features"] += 1
    return counts


def _input_evidence(expected: list[str], supplied: dict[str, Any]) -> InputEvidence:
    user_expected = [feature for feature in expected if feature != "year"]
    supplied_names = {
        feature
        for feature in user_expected
        if feature in supplied and supplied[feature] is not None
    }
    expected_count = len(user_expected)
    coverage = len(supplied_names) / max(1, expected_count)
    if len(supplied_names) == expected_count:
        level = "complete"
    elif coverage >= 0.5:
        level = "partial"
    else:
        level = "insufficient"

    by_modality: dict[Modality, ModalityEvidence] = {}
    for modality in MODALITIES:
        modality_expected = [
            feature for feature in user_expected if _feature_modality(feature) == modality
        ]
        modality_provided = [
            feature for feature in modality_expected if feature in supplied_names
        ]
        modality_coverage = len(modality_provided) / max(1, len(modality_expected))
        by_modality[modality] = ModalityEvidence(
            expected_user_features=len(modality_expected),
            provided_user_features=len(modality_provided),
            coverage_ratio=modality_coverage,
        )

    return InputEvidence(
        expected_model_variables=len(expected),
        expected_user_features=expected_count,
        provided_user_features=len(supplied_names),
        coverage_ratio=coverage,
        level=level,
        by_modality=by_modality,
    )


def _input_warnings(
    expected: list[str],
    supplied: dict[str, Any],
    year: int,
    metadata: dict[str, Any],
) -> tuple[list[str], InputEvidence]:
    warnings: list[str] = []
    evidence = _input_evidence(expected, supplied)
    if evidence.level == "insufficient":
        warnings.append(
            "Moins de 50 % des variables attendues sont fournies ; la majorité sera "
            "imputée et l’incertitude réelle peut être supérieure."
        )
    elif evidence.level == "partial":
        warnings.append(
            "Certaines variables sont absentes et seront imputées. "
            "Interprétez la prédiction avec prudence."
        )

    protocol = metadata.get("evaluation_protocol", {})
    test_year = protocol.get("test_year", metadata.get("test_year"))
    development_years = protocol.get("development_years", [])
    known_years = [int(value) for value in development_years if value is not None]
    if protocol.get("calibration_year") is not None:
        known_years.append(int(protocol["calibration_year"]))
    if test_year is not None:
        known_years.append(int(test_year))
    if known_years and (year < min(known_years) or year > max(known_years)):
        warnings.append(
            f"L’année {year} est hors de la période évaluée "
            f"{min(known_years)}–{max(known_years)}."
        )
    return warnings, evidence


def _day_of_year_limit(year: int) -> int:
    return 366 if calendar.isleap(year) else 365


def _date_from_doy(year: int, day_of_year: int) -> datetime:
    bounded = max(1, min(_day_of_year_limit(year), day_of_year))
    return datetime(year, 1, 1) + timedelta(days=bounded - 1)


@app.post("/predict/harvest-date", response_model=PredictionResponse)
def predict_harvest_date(request: PredictionRequest) -> PredictionResponse:
    if request.horizon not in registry.models:
        raise HTTPException(
            status_code=503,
            detail=f"Model '{request.horizon}' is not loaded",
        )

    metadata = _metadata_or_503(request.horizon)
    expected = metadata.get("feature_columns", [])
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Model metadata does not contain feature_columns",
        )

    row = dict(request.features)
    row["year"] = request.year
    frame = pd.DataFrame([{column: row.get(column) for column in expected}])
    try:
        predicted_doy = float(registry.models[request.horizon].predict(frame)[0])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Inference failed: {exc}") from exc
    if not math.isfinite(predicted_doy):
        raise HTTPException(status_code=422, detail="Inference returned a non-finite value")

    maximum_doy = _day_of_year_limit(request.year)
    rounded_doy = max(1, min(maximum_doy, int(round(predicted_doy))))
    predicted_date = _date_from_doy(request.year, rounded_doy)
    half_width = float(metadata.get("residual_absolute_error_q90_days", 7.0))
    low_doy = max(1, int(round(predicted_doy - half_width)))
    high_doy = min(maximum_doy, int(round(predicted_doy + half_width)))
    low_date = _date_from_doy(request.year, low_doy)
    high_date = _date_from_doy(request.year, high_doy)
    warnings, evidence = _input_warnings(
        expected,
        request.features,
        request.year,
        metadata,
    )

    return PredictionResponse(
        version=app.version,
        horizon=request.horizon,
        model=metadata.get("selected_model"),
        predicted_doy=predicted_doy,
        predicted_date=predicted_date.date().isoformat(),
        prediction_interval_approx_90={
            "method": metadata.get("conformal_interval", {}).get(
                "method",
                "split-conformal or residual quantile",
            ),
            "half_width_days": half_width,
            "low_doy": low_doy,
            "high_doy": high_doy,
            "low_date": low_date.date().isoformat(),
            "high_date": high_date.date().isoformat(),
        },
        input_coverage=evidence.coverage_ratio,
        input_evidence=evidence,
        warnings=warnings,
        domain="Wheat parcels in Centre-Val de Loire; extrapolation requires validation.",
        target_notice=(
            "The target is derived and is not presented as a direct field observation."
        ),
        human_oversight=(
            "The final harvest decision must remain with qualified agricultural actors."
        ),
    )


@app.get("/explain/{horizon}", response_model=ExplainResponse)
def explain(horizon: Horizon) -> ExplainResponse:
    metadata = _metadata_or_503(horizon)
    return _validated_or_503(
        ExplainResponse,
        {
            "horizon": horizon,
            "method": "permutation importance on the chronological test year",
            "global_feature_importance": metadata.get("global_feature_importance", []),
            "ablation_study": metadata.get("ablation_study", []),
            "caution": "Importance is predictive association, not causality.",
        },
    )


def _load_test_prediction_frame(horizon: Horizon) -> pd.DataFrame:
    metadata = _metadata_or_503(horizon)
    path = registry.root / horizon / "test_predictions.csv"
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Test predictions for '{horizon}' are not available",
        )
    try:
        frame = pd.read_csv(path, dtype={"parcelle_uid": "string"})
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=503,
            detail=f"Test predictions for '{horizon}' cannot be read",
        ) from exc
    missing = sorted(TEST_PREDICTION_COLUMNS - set(frame.columns))
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"Test predictions for '{horizon}' miss required columns: {missing}",
        )
    expected_rows = metadata.get("rows", {}).get("test")
    if expected_rows is not None and len(frame) != int(expected_rows):
        raise HTTPException(
            status_code=503,
            detail=(
                f"Test predictions for '{horizon}' contain {len(frame)} rows; "
                f"metadata requires {expected_rows}"
            ),
        )
    if frame[["parcelle_uid", "year"]].duplicated().any():
        raise HTTPException(
            status_code=503,
            detail=f"Test predictions for '{horizon}' contain duplicate cases",
        )
    return frame


def _source_key(row: Any) -> tuple[str, int]:
    return str(row.parcelle_uid), int(row.year)


def _case_id_map(frames: list[pd.DataFrame]) -> dict[tuple[str, int], str]:
    keys = {
        _source_key(row)
        for frame in frames
        for row in frame[["parcelle_uid", "year"]].itertuples(index=False)
    }
    width = max(4, len(str(len(keys))))
    return {
        key: f"case_{index:0{width}d}"
        for index, key in enumerate(sorted(keys), start=1)
    }


def _public_test_cases(
    frame: pd.DataFrame,
    case_ids: dict[tuple[str, int], str],
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False):
        cases.append(
            {
                "case_id": case_ids[_source_key(row)],
                "year": int(row.year),
                "actual_doy": float(row.actual_doy),
                "predicted_doy": float(row.predicted_doy),
                "lower_90_doy": float(row.lower_90_doy),
                "upper_90_doy": float(row.upper_90_doy),
                "absolute_error_days": float(row.absolute_error_days),
            }
        )
    return cases


@app.get("/insights/evaluation/{horizon}", response_model=EvaluationResponse)
def evaluation(horizon: Horizon) -> EvaluationResponse:
    metadata = _metadata_or_503(horizon)
    frame = _load_test_prediction_frame(horizon)
    case_ids = _case_id_map([frame])
    payload = {
        "generated_at": metadata.get("generated_at", ""),
        "horizon": horizon,
        "selected_model": metadata.get("selected_model"),
        "protocol": _public_metadata_value(metadata.get("evaluation_protocol", {})),
        "rows": metadata.get("rows", {}),
        "metrics": metadata.get("temporal_metrics", {}),
        "bootstrap_mae_ci95": metadata.get("bootstrap_mae_ci95", {}),
        "conformal_interval": metadata.get("conformal_interval", {}),
        "robustness": metadata.get("robustness_study", []),
        "ablations": metadata.get("ablation_study", []),
        "ood": metadata.get("ood_diagnostics", {}),
        "feature_importance": metadata.get("global_feature_importance", []),
        "test_cases": _public_test_cases(frame, case_ids),
        "limitations": metadata.get("limitations", []),
    }
    return _validated_or_503(EvaluationResponse, payload)


def _paired_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    may = _load_test_prediction_frame("may31")
    june = _load_test_prediction_frame("june15")
    joined = may.merge(
        june,
        on=["parcelle_uid", "year"],
        how="inner",
        suffixes=("_may31", "_june15"),
        validate="one_to_one",
    )
    if len(joined) != len(may) or len(joined) != len(june):
        raise HTTPException(
            status_code=503,
            detail="Horizon test predictions are not strictly aligned",
        )
    if not np.allclose(
        joined["actual_doy_may31"],
        joined["actual_doy_june15"],
        equal_nan=False,
    ):
        raise HTTPException(
            status_code=503,
            detail="Horizon test targets are inconsistent",
        )
    return may, june, joined


def _calculate_horizon_summary(joined: pd.DataFrame) -> dict[str, Any]:
    difference = (
        joined["absolute_error_days_june15"].to_numpy(dtype=float)
        - joined["absolute_error_days_may31"].to_numpy(dtype=float)
    )
    if not len(difference):
        raise HTTPException(status_code=503, detail="No paired horizon cases are available")
    generator = np.random.default_rng(42)
    means = np.empty(5000, dtype=float)
    for index in range(len(means)):
        sample = generator.integers(0, len(difference), size=len(difference))
        means[index] = float(np.mean(difference[sample]))
    lower, upper = np.quantile(means, [0.025, 0.975])
    conclusion = (
        "june15_better"
        if upper < 0
        else "may31_better"
        if lower > 0
        else "inconclusive"
    )
    return {
        "mean_delta_absolute_error_days_june_minus_may": float(np.mean(difference)),
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
        "probability_june15_lower_error": float(np.mean(means < 0)),
        "conclusion": conclusion,
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _summary_artifact() -> dict[str, Any] | None:
    for path in (
        registry.root / "horizon_comparison.json",
        REPORT_ROOT / "final_evaluation.json",
    ):
        payload = _load_json(path)
        if payload and isinstance(payload.get("horizon_comparison"), dict):
            return payload
    return None


def _comparison_payload() -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    may, june, joined = _paired_frames()
    mean_delta = float(
        np.mean(
            joined["absolute_error_days_june15"].to_numpy(dtype=float)
            - joined["absolute_error_days_may31"].to_numpy(dtype=float)
        )
    )
    artifact = _summary_artifact()
    summary = artifact.get("horizon_comparison", {}) if artifact else {}
    required_summary_fields = {
        "mean_delta_absolute_error_days_june_minus_may",
        "ci95_lower",
        "ci95_upper",
        "probability_june15_lower_error",
        "conclusion",
    }
    artifact_mean = summary.get("mean_delta_absolute_error_days_june_minus_may")
    if (
        not required_summary_fields.issubset(summary)
        or not isinstance(artifact_mean, (int, float))
        or any(
            not isinstance(summary.get(field), (int, float))
            for field in (
                "ci95_lower",
                "ci95_upper",
                "probability_june15_lower_error",
            )
        )
        or summary.get("conclusion")
        not in {"june15_better", "may31_better", "inconclusive"}
        or not math.isclose(
            float(artifact_mean),
            mean_delta,
            rel_tol=0,
            abs_tol=1e-9,
        )
    ):
        # The bootstrap is intentionally a fallback only. A finalized deployment
        # carries the canonical comparison beside the models, avoiding repeated
        # resampling on every dashboard request.
        summary = _calculate_horizon_summary(joined)

    case_ids = _case_id_map([may, june])
    cases: list[dict[str, Any]] = []
    for row in joined.itertuples(index=False):
        key = (str(row.parcelle_uid), int(row.year))
        may_error = float(row.absolute_error_days_may31)
        june_error = float(row.absolute_error_days_june15)
        cases.append(
            {
                "case_id": case_ids[key],
                "year": int(row.year),
                "actual_doy": float(row.actual_doy_may31),
                "may31_predicted_doy": float(row.predicted_doy_may31),
                "june15_predicted_doy": float(row.predicted_doy_june15),
                "may31_absolute_error_days": may_error,
                "june15_absolute_error_days": june_error,
                "delta_absolute_error_days_june_minus_may": june_error - may_error,
            }
        )
    generated_at = (
        str(artifact.get("generated_at", ""))
        if artifact
        else max(
            str(_metadata_or_503(horizon).get("generated_at", ""))
            for horizon in HORIZONS
        )
    )
    return summary, cases, generated_at


@app.get(
    "/insights/horizon-comparison",
    response_model=HorizonComparisonResponse,
)
def horizon_comparison() -> HorizonComparisonResponse:
    summary, cases, generated_at = _comparison_payload()
    return _validated_or_503(
        HorizonComparisonResponse,
        {
            "generated_at": generated_at,
            "sample_size": len(cases),
            "summary": summary,
            "cases": cases,
        },
    )


@app.get("/insights/overview", response_model=OverviewResponse)
def overview() -> OverviewResponse:
    metadata_by_horizon = {
        horizon: _metadata_or_503(horizon)
        for horizon in HORIZONS
    }
    summary, _, comparison_generated_at = _comparison_payload()
    summary_artifact = _summary_artifact() or {}
    reference = metadata_by_horizon["may31"]
    horizons: dict[str, Any] = {}
    for horizon, metadata in metadata_by_horizon.items():
        expected = list(metadata.get("feature_columns", []))
        horizons[horizon] = {
            "horizon": horizon,
            "cutoff_month_day": "05-31" if horizon == "may31" else "06-15",
            "selected_model": metadata.get("selected_model"),
            "model_variable_count": len(expected),
            "user_feature_count": len([item for item in expected if item != "year"]),
            "signals_by_modality": _modality_counts(expected),
            "rows": metadata.get("rows", {}),
            "metrics": metadata.get("temporal_metrics", {}),
            "conformal_interval": metadata.get("conformal_interval", {}),
            "ood": metadata.get("ood_diagnostics", {}),
        }
    payload = {
        "generated_at": summary_artifact.get(
            "generated_at",
            comparison_generated_at,
        ),
        "version": reference.get("version", app.version),
        "domain": reference.get("domain", ""),
        "target": reference.get("target", ""),
        "target_nature": reference.get("target_nature", ""),
        "protocol": _public_metadata_value(reference.get("evaluation_protocol", {})),
        "horizons": horizons,
        "horizon_comparison": summary,
        "scientific_status": summary_artifact.get(
            "scientific_status",
            "Research prototype requiring external agronomic validation before operational use.",
        ),
    }
    return _validated_or_503(OverviewResponse, payload)


_SOIL_LABELS: dict[str, tuple[str, str]] = {
    "phh2o": ("pH eau", "Water pH"),
    "nitrogen": ("Azote", "Nitrogen"),
    "soc": ("Carbone organique du sol", "Soil organic carbon"),
    "clay": ("Argile", "Clay"),
    "sand": ("Sable", "Sand"),
    "silt": ("Limon", "Silt"),
    "cec": ("Capacité d’échange cationique", "Cation exchange capacity"),
    "bdod": ("Densité apparente", "Bulk density"),
    "cfvo": ("Fragments grossiers", "Coarse fragments"),
    "wv0033": ("Eau à 33 kPa", "Water at 33 kPa"),
    "wv1500": ("Eau à 1 500 kPa", "Water at 1,500 kPa"),
    "wv0010": ("Eau à 10 kPa", "Water at 10 kPa"),
    "ocd": ("Densité de carbone organique", "Organic carbon density"),
}
_S2_LABELS: dict[str, tuple[str, str]] = {
    "s2_ndvi_march_mean": ("NDVI moyen — mars", "Mean NDVI — March"),
    "s2_ndvi_april_mean": ("NDVI moyen — avril", "Mean NDVI — April"),
    "s2_ndvi_may_mean": ("NDVI moyen — mai", "Mean NDVI — May"),
    "s2_ndvi_winter_mean": ("NDVI moyen — hiver", "Mean NDVI — winter"),
    "s2_ndvi_spring_mean": ("NDVI moyen — printemps", "Mean NDVI — spring"),
    "s2_ndwi_amplitude": ("Amplitude NDWI", "NDWI amplitude"),
    "s2_ndvi_std": ("Variabilité NDVI", "NDVI variability"),
    "s2_ndvi_amplitude": ("Amplitude NDVI", "NDVI amplitude"),
    "s2_evi_std": ("Variabilité EVI", "EVI variability"),
}
_WEATHER_LABELS: dict[str, tuple[str, str]] = {
    "meteo_t_winter_mean": ("Température moyenne hivernale", "Mean winter temperature"),
    "meteo_precip_winter_sum": ("Précipitations hivernales", "Winter precipitation"),
    "meteo_precip_spring_sum": ("Précipitations printanières", "Spring precipitation"),
    "meteo_et0_spring_sum": ("Évapotranspiration printanière", "Spring evapotranspiration"),
    "meteo_wb_spring": ("Bilan hydrique printanier", "Spring water balance"),
    "meteo_gdd_spring": ("Degrés-jours printaniers", "Spring growing degree days"),
    "meteo_gdd_to_may31": ("Degrés-jours au 31 mai", "Growing degree days to May 31"),
    "meteo_frost_days": ("Jours de gel", "Frost days"),
    "meteo_wb_amj": ("Bilan hydrique avril–juin", "April–June water balance"),
    "meteo_gdd_amj": ("Degrés-jours avril–juin", "April–June growing degree days"),
    "meteo_heat_stress_days": ("Jours de stress thermique", "Heat-stress days"),
    "meteo_dry_streak_max": ("Séquence sèche maximale", "Longest dry spell"),
    "meteo_wet_streak_max": ("Séquence humide maximale", "Longest wet spell"),
}


def _feature_label(feature: str) -> dict[str, str]:
    if feature == "year":
        return {"fr": "Année de campagne", "en": "Crop year"}
    if feature == "SURF_PARC":
        return {"fr": "Surface de la parcelle", "en": "Parcel area"}
    if feature == "region":
        return {"fr": "Région", "en": "Region"}
    if feature in _S2_LABELS:
        french, english = _S2_LABELS[feature]
        return {"fr": f"Sentinel‑2 · {french}", "en": f"Sentinel‑2 · {english}"}
    if feature in _WEATHER_LABELS:
        french, english = _WEATHER_LABELS[feature]
        return {"fr": french, "en": english}
    if feature.startswith("s1_"):
        detail = feature.removeprefix("s1_").replace("_", " ")
        return {
            "fr": f"Sentinel‑1 · {detail.upper()}",
            "en": f"Sentinel‑1 · {detail.upper()}",
        }
    if "-" in feature:
        base, depth = feature.rsplit("_", maxsplit=1)
        french, english = _SOIL_LABELS.get(
            base,
            (base.replace("_", " ").title(), base.replace("_", " ").title()),
        )
        return {"fr": f"{french} · {depth}", "en": f"{english} · {depth}"}
    readable = feature.replace("_", " ").title()
    return {"fr": readable, "en": readable}


def _feature_presentation(feature: str) -> dict[str, Any]:
    presentation: dict[str, Any] = {
        "kind": "numeric",
        "raw_unit": None,
        "display_unit": None,
        "conversion": {"scale": 1.0, "offset": 0.0, "decimals": 2},
    }
    if feature == "year":
        presentation["conversion"]["decimals"] = 0
    elif feature == "region":
        presentation["kind"] = "categorical"
        presentation["conversion"]["decimals"] = 0
    elif feature == "SURF_PARC":
        presentation.update(raw_unit="ha", display_unit="ha")
    elif feature.startswith("phh2o_"):
        presentation.update(raw_unit="pH × 10", display_unit="pH")
        presentation["conversion"].update(scale=0.1, decimals=1)
    elif feature.startswith("nitrogen_"):
        presentation.update(raw_unit="cg/kg", display_unit="g/kg")
        presentation["conversion"].update(scale=0.01, decimals=2)
    elif feature.startswith("soc_"):
        presentation.update(raw_unit="dg/kg", display_unit="g/kg")
        presentation["conversion"].update(scale=0.1, decimals=1)
    elif feature.startswith(("clay_", "sand_", "silt_")):
        presentation.update(raw_unit="g/kg", display_unit="g/kg")
        presentation["conversion"]["decimals"] = 0
    elif feature.startswith("cec_"):
        presentation.update(raw_unit="mmol(c)/kg", display_unit="cmol(c)/kg")
        presentation["conversion"].update(scale=0.1, decimals=1)
    elif feature.startswith("bdod_"):
        presentation.update(raw_unit="cg/cm³", display_unit="g/cm³")
        presentation["conversion"].update(scale=0.01, decimals=2)
    elif feature.startswith("cfvo_"):
        presentation.update(raw_unit="cm³/dm³", display_unit="% vol.")
        presentation["conversion"].update(scale=0.1, decimals=1)
    elif feature.startswith(("wv0033_", "wv1500_", "wv0010_")):
        presentation.update(raw_unit="10⁻³ cm³/cm³", display_unit="% vol.")
        presentation["conversion"].update(scale=0.1, decimals=1)
    elif feature.startswith("ocd_"):
        presentation.update(raw_unit="hg/m³", display_unit="kg/m³")
        presentation["conversion"].update(scale=0.1, decimals=1)
    elif feature.startswith("s1_"):
        presentation.update(raw_unit="dB", display_unit="dB")
    elif feature.startswith("s2_"):
        presentation["conversion"]["decimals"] = 3
    elif feature.startswith("meteo_t_"):
        presentation.update(raw_unit="°C", display_unit="°C")
        presentation["conversion"]["decimals"] = 1
    elif feature.startswith(("meteo_precip_", "meteo_et0_", "meteo_wb_")):
        presentation.update(raw_unit="mm", display_unit="mm")
        presentation["conversion"]["decimals"] = 1
    elif feature.startswith("meteo_gdd_"):
        presentation.update(raw_unit="°C·jour", display_unit="°C·jour")
        presentation["conversion"]["decimals"] = 1
    elif feature.startswith(
        (
            "meteo_frost_days",
            "meteo_heat_stress_days",
            "meteo_dry_streak_max",
            "meteo_wet_streak_max",
        )
    ):
        presentation.update(raw_unit="jours", display_unit="jours")
        presentation["conversion"]["decimals"] = 0
    return presentation


def _display_value(value: Any, presentation: dict[str, Any]) -> Any:
    if value is None or presentation["kind"] == "categorical":
        return value
    conversion = presentation["conversion"]
    converted = float(value) * conversion["scale"] + conversion["offset"]
    return round(converted, conversion["decimals"])


@app.get("/features/schema/{horizon}", response_model=FeatureSchemaResponse)
def feature_schema(horizon: Horizon) -> FeatureSchemaResponse:
    metadata = _metadata_or_503(horizon)
    expected = list(metadata.get("feature_columns", []))
    reference = metadata.get("reference_row", {})
    if not expected or not isinstance(reference, dict):
        raise HTTPException(
            status_code=503,
            detail=f"Feature schema for '{horizon}' is not available",
        )
    if any(feature not in reference for feature in expected):
        raise HTTPException(
            status_code=503,
            detail=f"Reference profile for '{horizon}' is incomplete",
        )

    features: list[dict[str, Any]] = []
    display_values: dict[str, Any] = {}
    for feature in expected:
        presentation = _feature_presentation(feature)
        display = _display_value(reference[feature], presentation)
        display_values[feature] = display
        features.append(
            {
                "name": feature,
                "label": _feature_label(feature),
                "modality": _feature_modality(feature),
                **presentation,
                "reference_raw": reference[feature],
                "reference_display": display,
            }
        )

    payload = {
        "horizon": horizon,
        "model_variable_count": len(expected),
        "user_feature_count": len([feature for feature in expected if feature != "year"]),
        "counts_by_modality": _modality_counts(expected),
        "reference_profile": {
            "id": "synthetic_median",
            "label": {
                "fr": "Profil médian synthétique",
                "en": "Synthetic median profile",
            },
            "description": {
                "fr": (
                    "Valeurs médianes de référence issues des données du modèle ; "
                    "ce profil ne représente aucune parcelle réelle."
                ),
                "en": (
                    "Reference median values from the model data; "
                    "this profile does not represent a real parcel."
                ),
            },
            "values": {feature: reference[feature] for feature in expected},
            "display_values": display_values,
        },
        "features": features,
    }
    return _validated_or_503(FeatureSchemaResponse, payload)
