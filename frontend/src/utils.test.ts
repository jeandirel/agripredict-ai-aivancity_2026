import { describe, expect, it } from "vitest";
import type { FeatureDescriptor, InputEvidence } from "./types";
import {
  coverageLevel,
  cutoffIso,
  dayDifference,
  displayValue,
  formatDate,
  modalityCounts,
  parseFeatureFile,
  rawValue,
  referenceValues,
} from "./utils";

describe("scientific display helpers", () => {
  it("round-trips API-provided unit conversions", () => {
    const ph: FeatureDescriptor = {
      name: "phh2o_0-5cm",
      modality: "soil",
      conversion: { scale: 0.1, offset: 0 },
      reference_raw: 67,
      reference_display: 6.7,
    };
    expect(displayValue(ph, 67)).toBe(6.7);
    expect(rawValue(ph, 6.7)).toBeCloseTo(67);
  });

  it("keeps horizon cutoffs valid and calculates lead time across a leap year", () => {
    expect(cutoffIso("may31", 2024)).toBe("2024-05-31");
    expect(cutoffIso("june15", 2024)).toBe("2024-06-15");
    expect(dayDifference("2024-05-31", "2024-07-01")).toBe(31);
    expect(formatDate("2024-07-01", "fr")).toMatch(/juillet/i);
  });

  it("uses explicit evidence levels before legacy coverage", () => {
    const evidence: InputEvidence = {
      level: "partial",
      coverage_ratio: 1,
    };
    expect(coverageLevel(evidence, 1)).toBe("partial");
    expect(coverageLevel(undefined, 0.2)).toBe("insufficient");
    expect(coverageLevel(undefined, 1)).toBe("complete");
  });

  it("extracts only actual feature values from a reference profile", () => {
    expect(
      referenceValues({
        id: "synthetic_median",
        label: { fr: "Profil", en: "Profile" },
        values: { soil: 1, weather: 2 },
      }),
    ).toEqual({ soil: 1, weather: 2 });
  });

  it("parses JSON and a single-row CSV without silently accepting invalid JSON", () => {
    expect(parseFeatureFile('{"soil": 1}', "features.json")).toEqual({ soil: 1 });
    expect(parseFeatureFile("soil;region\n1,5;Centre", "features.csv")).toEqual({
      soil: 1.5,
      region: "Centre",
    });
    expect(() => parseFeatureFile("[]", "features.json")).toThrow("JSON_OBJECT_REQUIRED");
  });

  it("counts modalities from schema rather than hard-coded scientific figures", () => {
    const counts = modalityCounts([
      { name: "phh2o_0-5cm", modality: "soil" },
      { name: "s1_vv_mean", modality: "sentinel1" },
      { name: "meteo_gdd_amj", modality: "weather" },
      { name: "region", modality: "context" },
    ]);
    expect(counts.soil).toBe(1);
    expect(counts.sentinel1).toBe(1);
    expect(counts.sentinel2).toBe(0);
    expect(counts.weather).toBe(1);
  });
});

