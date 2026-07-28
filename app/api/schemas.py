"""Stable public API contracts for AgriPredict AI."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Horizon = Literal["may31", "june15"]
Modality = Literal["context", "soil", "sentinel1", "sentinel2", "weather"]
CoverageLevel = Literal["complete", "partial", "insufficient"]


class ApiModel(BaseModel):
    """Base model shared by response contracts."""

    model_config = ConfigDict(extra="forbid")


class PredictionRequest(ApiModel):
    horizon: Horizon
    year: int = Field(ge=2000, le=2100)
    features: dict[str, Any]


class HealthResponse(ApiModel):
    status: Literal["ok"]
    version: str
    available_models: list[str]


class ReadinessResponse(ApiModel):
    status: Literal["ready", "not_ready"]
    required_models: list[str]
    available_models: list[str]
    missing_models: list[str]


class ModelInfoResponse(ApiModel):
    version: str
    model_root: str
    available_models: list[str]
    metadata: dict[str, dict[str, Any]]


class ReloadModelsResponse(ApiModel):
    status: Literal["reloaded"]
    available_models: list[str]


class PredictionInterval(ApiModel):
    method: str
    half_width_days: float
    low_doy: int
    high_doy: int
    low_date: str
    high_date: str


class ModalityEvidence(ApiModel):
    expected_user_features: int
    provided_user_features: int
    coverage_ratio: float = Field(ge=0, le=1)


class InputEvidence(ApiModel):
    expected_model_variables: int
    expected_user_features: int
    provided_user_features: int
    coverage_ratio: float = Field(ge=0, le=1)
    level: CoverageLevel
    by_modality: dict[Modality, ModalityEvidence]


class PredictionResponse(ApiModel):
    version: str
    horizon: Horizon
    model: str | None
    predicted_doy: float
    predicted_date: str
    prediction_interval_approx_90: PredictionInterval
    input_coverage: float = Field(ge=0, le=1)
    input_evidence: InputEvidence
    warnings: list[str]
    domain: str
    target_notice: str
    human_oversight: str


class FeatureImportance(ApiModel):
    feature: str
    importance_mean: float
    importance_std: float


class MetricSet(ApiModel):
    mae_days: float
    rmse_days: float
    median_absolute_error_days: float
    r2: float
    bias_days: float
    p90_absolute_error_days: float
    within_3_days: float
    within_5_days: float
    within_7_days: float
    within_10_days: float


class AblationResult(MetricSet):
    configuration: str
    modalities: list[str]
    feature_count: int


class RobustnessResult(MetricSet):
    scenario: str
    delta_mae_days: float
    relative_mae_change: float


class OodDiagnostics(ApiModel):
    numeric_feature_count: int
    distance_threshold_q95: float
    test_flagged_count: int
    test_flagged_rate: float
    test_distance_mean: float
    test_distance_max: float
    synthetic_ood_auc: float


class BootstrapInterval(ApiModel):
    lower: float
    upper: float


class ConformalInterval(ApiModel):
    nominal_coverage: float
    calibration_quantile_days: float
    empirical_test_coverage: float
    mean_width_days: float
    median_width_days: float


class EvaluationProtocol(ApiModel):
    development_years: list[int]
    calibration_year: int
    test_year: int
    model_selection: str
    uncertainty: str
    test_usage: str


class DatasetRows(ApiModel):
    all: int
    development: int
    calibration: int
    test: int


class EvaluationPoint(ApiModel):
    case_id: str
    year: int
    actual_doy: float
    predicted_doy: float
    lower_90_doy: float
    upper_90_doy: float
    absolute_error_days: float


class ExplainResponse(ApiModel):
    horizon: Horizon
    method: str
    global_feature_importance: list[FeatureImportance]
    ablation_study: list[AblationResult]
    caution: str


class EvaluationResponse(ApiModel):
    generated_at: str
    horizon: Horizon
    selected_model: str
    protocol: EvaluationProtocol
    rows: DatasetRows
    metrics: MetricSet
    bootstrap_mae_ci95: BootstrapInterval
    conformal_interval: ConformalInterval
    robustness: list[RobustnessResult]
    ablations: list[AblationResult]
    ood: OodDiagnostics
    feature_importance: list[FeatureImportance]
    test_cases: list[EvaluationPoint]
    limitations: list[str]


class HorizonComparisonSummary(ApiModel):
    mean_delta_absolute_error_days_june_minus_may: float
    ci95_lower: float
    ci95_upper: float
    probability_june15_lower_error: float
    conclusion: Literal["june15_better", "may31_better", "inconclusive"]


class HorizonComparisonPoint(ApiModel):
    case_id: str
    year: int
    actual_doy: float
    may31_predicted_doy: float
    june15_predicted_doy: float
    may31_absolute_error_days: float
    june15_absolute_error_days: float
    delta_absolute_error_days_june_minus_may: float


class HorizonComparisonResponse(ApiModel):
    generated_at: str
    sample_size: int
    summary: HorizonComparisonSummary
    cases: list[HorizonComparisonPoint]


class ModalityCount(ApiModel):
    model_variables: int
    user_features: int


class HorizonOverview(ApiModel):
    horizon: Horizon
    cutoff_month_day: str
    selected_model: str
    model_variable_count: int
    user_feature_count: int
    signals_by_modality: dict[Modality, ModalityCount]
    rows: DatasetRows
    metrics: MetricSet
    conformal_interval: ConformalInterval
    ood: OodDiagnostics


class OverviewResponse(ApiModel):
    generated_at: str
    version: str
    domain: str
    target: str
    target_nature: str
    protocol: EvaluationProtocol
    horizons: dict[Horizon, HorizonOverview]
    horizon_comparison: HorizonComparisonSummary
    scientific_status: str


class LocalizedText(ApiModel):
    fr: str
    en: str


class DisplayConversion(ApiModel):
    scale: float
    offset: float = 0
    decimals: int = Field(ge=0, le=8)


class FeatureDescriptor(ApiModel):
    name: str
    label: LocalizedText
    modality: Modality
    kind: Literal["numeric", "categorical"]
    raw_unit: str | None
    display_unit: str | None
    conversion: DisplayConversion
    reference_raw: Any
    reference_display: Any


class ReferenceProfile(ApiModel):
    id: Literal["synthetic_median"]
    label: LocalizedText
    description: LocalizedText
    values: dict[str, Any]
    display_values: dict[str, Any]


class FeatureSchemaResponse(ApiModel):
    horizon: Horizon
    model_variable_count: int
    user_feature_count: int
    counts_by_modality: dict[Modality, ModalityCount]
    reference_profile: ReferenceProfile
    features: list[FeatureDescriptor]
