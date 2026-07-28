export type Language = "fr" | "en";
export type Horizon = "may31" | "june15";
export type Modality = "soil" | "sentinel1" | "sentinel2" | "weather" | "context" | "other";
export type CoverageLevel = "complete" | "partial" | "insufficient";

export interface HealthResponse {
  status: string;
  version?: string;
  available_models?: Horizon[];
}

export interface EvaluationProtocol {
  development_years?: number[];
  calibration_year?: number;
  test_year?: number;
  model_selection?: string;
  uncertainty?: string;
  test_usage?: string;
}

export interface MetricSet {
  mae_days?: number;
  rmse_days?: number;
  median_absolute_error_days?: number;
  r2?: number;
  bias_days?: number;
  p90_absolute_error_days?: number;
  within_3_days?: number;
  within_5_days?: number;
  within_7_days?: number;
  within_10_days?: number;
}

export interface HorizonOverview {
  horizon?: Horizon;
  model_variable_count?: number;
  user_feature_count?: number;
  cutoff_month_day?: string;
  selected_model?: string;
  signals_by_modality?: Record<string, {
    model_variables: number;
    user_features: number;
  }>;
  rows?: {
    all?: number;
    development?: number;
    calibration?: number;
    test?: number;
  };
  metrics?: MetricSet;
  temporal_metrics?: MetricSet;
  conformal_interval?: ConformalInterval;
  ood?: OodDiagnostics;
  ood_diagnostics?: OodDiagnostics;
}

export interface OverviewResponse {
  generated_at?: string;
  version?: string;
  domain?: string;
  target?: {
    name?: string;
    nature?: string;
    unit?: string;
    notice?: string;
  } | string;
  target_nature?: string;
  protocol?: EvaluationProtocol;
  horizons?: Partial<Record<Horizon, HorizonOverview>>;
  comparison?: ComparisonSummary;
  horizon_comparison?: ComparisonSummary;
  scientific_status?: string;
  limitations?: string[];
}

export interface FeatureDescriptor {
  name: string;
  label?: Partial<Record<Language, string>>;
  label_fr?: string;
  label_en?: string;
  modality?: Modality | string;
  raw_unit?: string | null;
  display_unit?: string | null;
  reference_value?: unknown;
  display_value?: unknown;
  reference_raw?: unknown;
  reference_display?: unknown;
  conversion?: {
    scale?: number;
    divisor?: number;
    offset?: number;
  } | null;
  display_scale?: number;
  display_divisor?: number;
  description?: Partial<Record<Language, string>>;
}

export interface ReferenceProfile {
  label?: Partial<Record<Language, string>> | string;
  year?: number;
  values?: Record<string, unknown>;
  features?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface FeatureSchemaResponse {
  horizon: Horizon;
  model_feature_count?: number;
  model_variable_count: number;
  user_feature_count: number;
  counts_by_modality?: Record<string, {
    model_variables: number;
    user_features: number;
  }>;
  reference_profile: ReferenceProfile | Record<string, unknown>;
  features: FeatureDescriptor[];
}

export interface RobustnessScenario extends MetricSet {
  scenario: string;
  delta_mae_days?: number;
  relative_mae_change?: number;
}

export interface AblationResult extends MetricSet {
  configuration: string;
  modalities?: string[];
  feature_count?: number;
}

export interface FeatureImportance {
  feature: string;
  importance_mean: number;
  importance_std?: number;
  modality?: Modality | string;
}

export interface OodDiagnostics {
  numeric_feature_count?: number;
  distance_threshold_q95?: number;
  test_flagged_count?: number;
  test_flagged_rate?: number;
  test_distance_mean?: number;
  test_distance_max?: number;
  synthetic_ood_auc?: number;
}

export interface TestCase {
  case_id: string;
  year?: number;
  actual_doy: number;
  predicted_doy: number;
  absolute_error?: number;
  absolute_error_days?: number;
  interval_low_doy?: number;
  interval_high_doy?: number;
  lower_90_doy?: number;
  upper_90_doy?: number;
}

export interface EvaluationResponse {
  horizon: Horizon;
  metrics: MetricSet;
  bootstrap_mae_ci95?: {
    lower?: number;
    upper?: number;
  };
  conformal_interval?: ConformalInterval;
  robustness?: RobustnessScenario[];
  robustness_study?: RobustnessScenario[];
  ablations?: AblationResult[];
  ablation_study?: AblationResult[];
  ood?: OodDiagnostics;
  ood_diagnostics?: OodDiagnostics;
  feature_importance?: FeatureImportance[];
  global_feature_importance?: FeatureImportance[];
  test_cases: TestCase[];
  limitations?: string[];
}

export interface ComparisonSummary {
  n_cases?: number;
  mean_delta_absolute_error_days?: number;
  mean_delta_absolute_error_days_june_minus_may?: number;
  median_delta_absolute_error_days?: number;
  ci95_lower?: number;
  ci95_upper?: number;
  probability_june15_lower_error?: number;
  conclusion?: string;
}

export interface ComparisonCase {
  case_id: string;
  actual_doy?: number;
  predicted_doy_may31?: number;
  predicted_doy_june15?: number;
  may31_predicted_doy?: number;
  june15_predicted_doy?: number;
  absolute_error_may31?: number;
  absolute_error_june15?: number;
  may31_absolute_error_days: number;
  june15_absolute_error_days: number;
  delta_absolute_error_june_minus_may?: number;
  delta_absolute_error_days_june_minus_may?: number;
}

export interface ComparisonResponse {
  generated_at?: string;
  sample_size?: number;
  summary: ComparisonSummary;
  cases: ComparisonCase[];
}

export interface CoverageModality {
  expected?: number;
  supplied?: number;
  coverage?: number;
}

export interface InputEvidence {
  expected_model_features?: number;
  expected_model_variables?: number;
  expected_user_features?: number;
  supplied_user_features?: number;
  supplied_feature_count?: number;
  provided_user_features?: number;
  coverage_ratio?: number;
  coverage_level?: CoverageLevel;
  level?: CoverageLevel;
  by_modality?: Record<string, CoverageModality | number>;
  coverage_by_modality?: Record<string, CoverageModality | number>;
}

export interface ConformalInterval {
  method?: string;
  nominal_coverage?: number;
  calibration_quantile_days?: number;
  empirical_test_coverage?: number;
  mean_width_days?: number;
  median_width_days?: number;
  half_width_days?: number;
  low_doy?: number;
  high_doy?: number;
  low_date?: string;
  high_date?: string;
}

export interface PredictionResponse {
  version?: string;
  horizon: Horizon;
  model?: string;
  predicted_doy: number;
  predicted_date: string;
  prediction_interval_approx_90: ConformalInterval;
  input_coverage?: number;
  input_evidence?: InputEvidence;
  warnings?: string[];
  domain?: string;
  target_notice?: string;
  human_oversight?: string;
}

export interface ObservatoryData {
  health: HealthResponse;
  overview: OverviewResponse;
  evaluations: Record<Horizon, EvaluationResponse>;
  comparison: ComparisonResponse;
  schemas: Record<Horizon, FeatureSchemaResponse>;
  fetchedAt: Date;
}
