import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

const metric = {
  mae_days: 1,
  rmse_days: 2,
  median_absolute_error_days: 1,
  r2: 0.1,
  bias_days: 0,
  p90_absolute_error_days: 3,
  within_3_days: 0.5,
  within_5_days: 0.7,
  within_7_days: 0.8,
  within_10_days: 0.9,
};

const protocol = {
  development_years: [2020, 2021, 2022],
  calibration_year: 2023,
  test_year: 2024,
  model_selection: "Grouped development folds",
  uncertainty: "Temporal calibration",
  test_usage: "Untouched final test",
};

const evaluation = (horizon: "may31" | "june15") => ({
  horizon,
  selected_model: "model",
  protocol,
  rows: { all: 1, development: 1, calibration: 1, test: 1 },
  metrics: metric,
  bootstrap_mae_ci95: { lower: 0, upper: 2 },
  conformal_interval: {
    nominal_coverage: 0.9,
    calibration_quantile_days: 2,
    empirical_test_coverage: 0.8,
    mean_width_days: 4,
    median_width_days: 4,
  },
  robustness: [{ scenario: "baseline", ...metric, delta_mae_days: 0, relative_mae_change: 0 }],
  ablations: [],
  ood: {
    numeric_feature_count: 1,
    distance_threshold_q95: 1,
    test_flagged_count: 0,
    test_flagged_rate: 0,
    test_distance_mean: 0,
    test_distance_max: 0,
    synthetic_ood_auc: 1,
  },
  feature_importance: [],
  test_cases: [
    {
      case_id: "case_0001",
      year: 2024,
      actual_doy: 180,
      predicted_doy: 181,
      lower_90_doy: 179,
      upper_90_doy: 183,
      absolute_error_days: 1,
    },
  ],
  limitations: [],
});

function json(value: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(value), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

describe("Harvest Observatory application states", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("states that scientific figures are unavailable when the API is offline", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    render(<App />);
    expect(
      (await screen.findAllByText(/L’observatoire ne peut pas afficher de chiffres/i)).length,
    ).toBeGreaterThan(0);
    expect(screen.getByText(/Voir la fenêtre de récolte/i)).toBeInTheDocument();
  });

  it("labels the reference data as a synthetic median profile", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/health")) {
          return json({ status: "ok", version: "test", available_models: ["may31", "june15"] });
        }
        if (url.endsWith("/insights/overview")) {
          return json({
            generated_at: "2026-01-01T12:00:00Z",
            version: "test",
            domain: "Test domain",
            target: "derived target",
            target_nature: "derived",
            protocol,
            horizons: {},
            horizon_comparison: {
              mean_delta_absolute_error_days_june_minus_may: 0,
              ci95_lower: -1,
              ci95_upper: 1,
              probability_june15_lower_error: 0.5,
              conclusion: "inconclusive",
            },
            scientific_status: "Research prototype",
          });
        }
        if (url.includes("/insights/evaluation/")) {
          return json(evaluation(url.endsWith("june15") ? "june15" : "may31"));
        }
        if (url.endsWith("/insights/horizon-comparison")) {
          return json({
            sample_size: 1,
            summary: {
              mean_delta_absolute_error_days_june_minus_may: 0,
              ci95_lower: -1,
              ci95_upper: 1,
              probability_june15_lower_error: 0.5,
              conclusion: "inconclusive",
            },
            cases: [
              {
                case_id: "case_0001",
                may31_absolute_error_days: 1,
                june15_absolute_error_days: 1,
              },
            ],
          });
        }
        if (url.includes("/features/schema/")) {
          const horizon = url.endsWith("june15") ? "june15" : "may31";
          return json({
            horizon,
            model_variable_count: 2,
            user_feature_count: 1,
            counts_by_modality: {
              context: { model_variables: 1, user_features: 0 },
              soil: { model_variables: 1, user_features: 1 },
            },
            reference_profile: {
              id: "synthetic_median",
              label: { fr: "Profil médian synthétique", en: "Synthetic median profile" },
              description: { fr: "Synthétique", en: "Synthetic" },
              values: { year: 2024, "phh2o_0-5cm": 67 },
              display_values: { year: 2024, "phh2o_0-5cm": 6.7 },
            },
            features: [
              {
                name: "year",
                label: { fr: "Année", en: "Year" },
                modality: "context",
                kind: "numeric",
                conversion: { scale: 1, offset: 0, decimals: 0 },
                reference_raw: 2024,
                reference_display: 2024,
              },
              {
                name: "phh2o_0-5cm",
                label: { fr: "pH du sol", en: "Soil pH" },
                modality: "soil",
                kind: "numeric",
                display_unit: "pH",
                conversion: { scale: 0.1, offset: 0, decimals: 1 },
                reference_raw: 67,
                reference_display: 6.7,
              },
            ],
          });
        }
        return Promise.reject(new Error(`Unexpected URL: ${url}`));
      }),
    );

    render(<App />);
    expect(
      (await screen.findAllByText(/Profil médian synthétique/i)).length,
    ).toBeGreaterThan(0);
    expect(screen.getByText(/exemple technique complet/i)).toBeInTheDocument();
  });
});
