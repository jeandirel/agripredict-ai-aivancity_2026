"""FastAPI inference service for AgriPredict AI."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_ROOT = Path(os.getenv("AGRIPREDICT_MODEL_DIR", "artifacts/models"))


class PredictionRequest(BaseModel):
    horizon: Literal["may31", "june15"]
    year: int = Field(ge=2000, le=2100)
    features: dict[str, Any]


class ModelRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.models: dict[str, Any] = {}
        self.metadata: dict[str, dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        self.models.clear()
        self.metadata.clear()
        for horizon in ("may31", "june15"):
            model_path = self.root / horizon / "model.joblib"
            metadata_path = self.root / horizon / "metadata.json"
            if model_path.exists() and metadata_path.exists():
                self.models[horizon] = joblib.load(model_path)
                self.metadata[horizon] = json.loads(metadata_path.read_text(encoding="utf-8"))

    def available(self) -> list[str]:
        return sorted(self.models)


registry = ModelRegistry(MODEL_ROOT)
app = FastAPI(
    title="AgriPredict AI API",
    version="1.0.0",
    description=(
        "Parcel-level wheat harvest-date prediction for the aivancity AI Clinic 2026. "
        "Research prototype restricted to Centre-Val de Loire."
    ),
)


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": app.version,
        "available_models": registry.available(),
    }


@app.get("/readiness")
def readiness() -> dict[str, Any]:
    required = {"may31", "june15"}
    available = set(registry.available())
    ready = required.issubset(available)
    return {
        "status": "ready" if ready else "not_ready",
        "required_models": sorted(required),
        "available_models": sorted(available),
        "missing_models": sorted(required - available),
    }


@app.get("/model-info")
def model_info() -> dict[str, Any]:
    return {
        "version": app.version,
        "model_root": str(MODEL_ROOT),
        "available_models": registry.available(),
        "metadata": registry.metadata,
    }


@app.post("/reload-models")
def reload_models() -> dict[str, Any]:
    registry.reload()
    return {"status": "reloaded", "available_models": registry.available()}


def _input_warnings(
    expected: list[str],
    supplied: dict[str, Any],
    year: int,
    metadata: dict[str, Any],
) -> tuple[list[str], float]:
    warnings: list[str] = []
    non_year_expected = [column for column in expected if column != "year"]
    supplied_count = sum(
        column in supplied and supplied[column] is not None for column in non_year_expected
    )
    coverage = supplied_count / max(1, len(non_year_expected))
    if coverage < 0.50:
        warnings.append(
            "Moins de 50 % des variables attendues sont fournies ; la majorité sera imputée et l’incertitude réelle peut être supérieure."
        )
    elif coverage < 0.80:
        warnings.append(
            "Certaines variables sont absentes et seront imputées. Interprétez la prédiction avec prudence."
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
            f"L’année {year} est hors de la période évaluée {min(known_years)}–{max(known_years)}."
        )
    return warnings, coverage


@app.post("/predict/harvest-date")
def predict_harvest_date(request: PredictionRequest) -> dict[str, Any]:
    if request.horizon not in registry.models:
        raise HTTPException(status_code=503, detail=f"Model '{request.horizon}' is not loaded")

    metadata = registry.metadata[request.horizon]
    expected = metadata.get("feature_columns", [])
    if not expected:
        raise HTTPException(status_code=503, detail="Model metadata does not contain feature_columns")

    row = dict(request.features)
    row.setdefault("year", request.year)
    frame = pd.DataFrame([{column: row.get(column) for column in expected}])
    try:
        predicted_doy = float(registry.models[request.horizon].predict(frame)[0])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Inference failed: {exc}") from exc

    rounded_doy = max(1, min(366, int(round(predicted_doy))))
    predicted_date = datetime(request.year, 1, 1) + timedelta(days=rounded_doy - 1)
    half_width = float(metadata.get("residual_absolute_error_q90_days", 7.0))
    low_doy = max(1, int(round(predicted_doy - half_width)))
    high_doy = min(366, int(round(predicted_doy + half_width)))
    low_date = datetime(request.year, 1, 1) + timedelta(days=low_doy - 1)
    high_date = datetime(request.year, 1, 1) + timedelta(days=high_doy - 1)
    warnings, input_coverage = _input_warnings(expected, row, request.year, metadata)

    return {
        "version": app.version,
        "horizon": request.horizon,
        "model": metadata.get("selected_model"),
        "predicted_doy": predicted_doy,
        "predicted_date": predicted_date.date().isoformat(),
        "prediction_interval_approx_90": {
            "method": metadata.get("conformal_interval", {}).get("method", "split-conformal or residual quantile"),
            "half_width_days": half_width,
            "low_doy": low_doy,
            "high_doy": high_doy,
            "low_date": low_date.date().isoformat(),
            "high_date": high_date.date().isoformat(),
        },
        "input_coverage": input_coverage,
        "warnings": warnings,
        "domain": "Wheat parcels in Centre-Val de Loire; extrapolation requires validation.",
        "target_notice": "The target is derived and is not presented as a direct field observation.",
        "human_oversight": "The final harvest decision must remain with qualified agricultural actors.",
    }


@app.get("/explain/{horizon}")
def explain(horizon: Literal["may31", "june15"]) -> dict[str, Any]:
    if horizon not in registry.metadata:
        raise HTTPException(status_code=503, detail=f"Model '{horizon}' is not loaded")
    metadata = registry.metadata[horizon]
    return {
        "horizon": horizon,
        "method": "permutation importance on the chronological test year",
        "global_feature_importance": metadata.get("global_feature_importance", []),
        "ablation_study": metadata.get("ablation_study", []),
        "caution": "Importance is predictive association, not causality.",
    }
