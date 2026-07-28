from __future__ import annotations

import json
import math
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.main import app, create_app, registry


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert isinstance(payload["available_models"], list)


def test_existing_endpoints_keep_their_public_contract(client: TestClient) -> None:
    assert client.get("/readiness").status_code == 200
    assert client.get("/model-info").status_code == 200
    assert client.get("/explain/may31").status_code == 200

    model_info = client.get("/model-info").json()
    public_json = json.dumps(model_info).casefold()
    assert "parcelle_uid" not in public_json
    assert "id_parcel" not in public_json
    assert "geometry" not in public_json


def test_unknown_model_returns_503_when_artifact_missing(client: TestClient) -> None:
    response = client.post(
        "/predict/harvest-date",
        json={"horizon": "may31", "year": 2024, "features": {"SURF_PARC": 5.0}},
    )
    if not client.get("/health").json()["available_models"]:
        assert response.status_code == 503


@pytest.mark.parametrize("horizon", ["may31", "june15"])
def test_evaluation_exposes_163_anonymized_recalculable_cases(
    client: TestClient,
    horizon: str,
) -> None:
    response = client.get(f"/insights/evaluation/{horizon}")
    assert response.status_code == 200
    payload = response.json()
    cases = payload["test_cases"]

    assert len(cases) == payload["rows"]["test"] == 163
    assert len({case["case_id"] for case in cases}) == 163
    assert all(case["case_id"].startswith("case_") for case in cases)
    public_json = json.dumps(payload).casefold()
    assert "parcelle_uid" not in public_json
    assert "id_parcel" not in public_json
    assert "geometry" not in public_json

    mae = sum(case["absolute_error_days"] for case in cases) / len(cases)
    rmse = math.sqrt(
        sum(
            (case["predicted_doy"] - case["actual_doy"]) ** 2
            for case in cases
        )
        / len(cases)
    )
    coverage = sum(
        case["lower_90_doy"] <= case["actual_doy"] <= case["upper_90_doy"]
        for case in cases
    ) / len(cases)
    assert mae == pytest.approx(payload["metrics"]["mae_days"])
    assert rmse == pytest.approx(payload["metrics"]["rmse_days"])
    assert coverage == pytest.approx(
        payload["conformal_interval"]["empirical_test_coverage"]
    )


def test_horizon_comparison_is_strictly_paired_and_inconclusive(
    client: TestClient,
) -> None:
    response = client.get("/insights/horizon-comparison")
    assert response.status_code == 200
    payload = response.json()
    cases = payload["cases"]

    assert payload["sample_size"] == len(cases) == 163
    assert len({case["case_id"] for case in cases}) == 163
    mean_delta = sum(
        case["delta_absolute_error_days_june_minus_may"] for case in cases
    ) / len(cases)
    assert mean_delta == pytest.approx(
        payload["summary"]["mean_delta_absolute_error_days_june_minus_may"]
    )
    assert payload["summary"]["ci95_lower"] < 0 < payload["summary"]["ci95_upper"]
    assert payload["summary"]["conclusion"] == "inconclusive"

    may_cases = {
        case["case_id"]: case
        for case in client.get("/insights/evaluation/may31").json()["test_cases"]
    }
    june_cases = {
        case["case_id"]: case
        for case in client.get("/insights/evaluation/june15").json()["test_cases"]
    }
    assert set(may_cases) == set(june_cases) == {
        case["case_id"] for case in cases
    }
    for case in cases:
        case_id = case["case_id"]
        assert case["actual_doy"] == pytest.approx(may_cases[case_id]["actual_doy"])
        assert case["actual_doy"] == pytest.approx(june_cases[case_id]["actual_doy"])


def test_overview_comes_from_model_artifacts(client: TestClient) -> None:
    response = client.get("/insights/overview")
    assert response.status_code == 200
    payload = response.json()

    assert set(payload["horizons"]) == {"may31", "june15"}
    assert payload["horizons"]["may31"]["model_variable_count"] == 67
    assert payload["horizons"]["june15"]["model_variable_count"] == 72
    assert payload["horizons"]["may31"]["rows"]["test"] == 163
    assert payload["horizon_comparison"]["conclusion"] == "inconclusive"


@pytest.mark.parametrize(
    ("horizon", "model_count", "user_count", "weather_count"),
    [("may31", 67, 66, 8), ("june15", 72, 71, 13)],
)
def test_feature_schema_counts_and_display_conversions(
    client: TestClient,
    horizon: str,
    model_count: int,
    user_count: int,
    weather_count: int,
) -> None:
    response = client.get(f"/features/schema/{horizon}")
    assert response.status_code == 200
    payload = response.json()
    descriptors = {feature["name"]: feature for feature in payload["features"]}

    assert payload["model_variable_count"] == len(descriptors) == model_count
    assert payload["user_feature_count"] == user_count
    assert payload["counts_by_modality"]["soil"]["model_variables"] == 30
    assert payload["counts_by_modality"]["sentinel1"]["model_variables"] == 17
    assert payload["counts_by_modality"]["sentinel2"]["model_variables"] == 9
    assert (
        payload["counts_by_modality"]["weather"]["model_variables"]
        == weather_count
    )
    assert payload["reference_profile"]["id"] == "synthetic_median"
    assert len(payload["reference_profile"]["values"]) == model_count

    ph = descriptors["phh2o_0-5cm"]
    nitrogen = descriptors["nitrogen_0-5cm"]
    radar = descriptors["s1_vv_mean"]
    gdd = descriptors["meteo_gdd_spring"]
    assert ph["reference_display"] == pytest.approx(ph["reference_raw"] / 10)
    assert nitrogen["reference_display"] == pytest.approx(
        nitrogen["reference_raw"] / 100
    )
    assert radar["display_unit"] == "dB"
    assert gdd["display_unit"] == "°C·jour"


def test_prediction_reports_complete_and_insufficient_input_evidence(
    client: TestClient,
) -> None:
    schema = client.get("/features/schema/may31").json()
    complete_features = dict(schema["reference_profile"]["values"])
    complete_features.pop("year")
    complete = client.post(
        "/predict/harvest-date",
        json={"horizon": "may31", "year": 2024, "features": complete_features},
    )
    assert complete.status_code == 200
    complete_payload = complete.json()
    assert complete_payload["input_coverage"] == 1
    assert complete_payload["input_evidence"] == {
        **complete_payload["input_evidence"],
        "expected_model_variables": 67,
        "expected_user_features": 66,
        "provided_user_features": 66,
        "coverage_ratio": 1,
        "level": "complete",
    }

    insufficient = client.post(
        "/predict/harvest-date",
        json={"horizon": "may31", "year": 2024, "features": {"SURF_PARC": 5.0}},
    )
    assert insufficient.status_code == 200
    insufficient_payload = insufficient.json()
    assert insufficient_payload["input_evidence"]["level"] == "insufficient"
    assert insufficient_payload["input_evidence"]["provided_user_features"] == 1
    assert insufficient_payload["warnings"]


class _FixedPredictionModel:
    def __init__(self, value: float) -> None:
        self.value = value

    def predict(self, frame: Any) -> list[float]:
        return [self.value]


@pytest.mark.parametrize(
    ("year", "expected_date", "expected_high_doy"),
    [(2023, "2023-12-31", 365), (2024, "2024-12-31", 366)],
)
def test_prediction_clamps_day_of_year_for_leap_years(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    year: int,
    expected_date: str,
    expected_high_doy: int,
) -> None:
    metadata = {
        **registry.metadata["may31"],
        "feature_columns": ["year", "SURF_PARC"],
        "residual_absolute_error_q90_days": 0,
    }
    monkeypatch.setitem(registry.metadata, "may31", metadata)
    monkeypatch.setitem(registry.models, "may31", _FixedPredictionModel(366))

    response = client.post(
        "/predict/harvest-date",
        json={"horizon": "may31", "year": year, "features": {"SURF_PARC": 5.0}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_date"] == expected_date
    assert (
        payload["prediction_interval_approx_90"]["high_doy"]
        == expected_high_doy
    )


def test_prediction_rejects_non_finite_model_output(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(registry.models, "may31", _FixedPredictionModel(float("nan")))
    response = client.post(
        "/predict/harvest-date",
        json={"horizon": "may31", "year": 2024, "features": {"SURF_PARC": 5.0}},
    )
    assert response.status_code == 422


def test_missing_scientific_artifact_returns_503(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Any,
) -> None:
    monkeypatch.setattr(registry, "root", tmp_path)
    response = client.get("/insights/evaluation/may31")
    assert response.status_code == 503
    assert "not available" in response.json()["detail"]


def test_cors_is_optional_exact_and_restrictive() -> None:
    cors_app = create_app(["https://observatory.example"])

    @cors_app.get("/probe")
    def probe() -> dict[str, bool]:
        return {"ok": True}

    cors_client = TestClient(cors_app)
    allowed = cors_client.options(
        "/probe",
        headers={
            "Origin": "https://observatory.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.status_code == 200
    assert (
        allowed.headers["access-control-allow-origin"]
        == "https://observatory.example"
    )

    denied = cors_client.options(
        "/probe",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers

    with pytest.raises(ValueError, match="never"):
        create_app(["*"])
