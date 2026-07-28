import type {
  CoverageLevel,
  FeatureDescriptor,
  FeatureSchemaResponse,
  Horizon,
  InputEvidence,
  Language,
  Modality,
  ReferenceProfile,
} from "./types";

export const MODALITY_COLORS: Record<Modality, string> = {
  soil: "#d7a866",
  sentinel1: "#68b8ff",
  sentinel2: "#8fdb80",
  weather: "#f2d46f",
  context: "#e8b6ff",
  other: "#c9d8d1",
};

const MODALITY_ORDER: Modality[] = [
  "soil",
  "sentinel1",
  "sentinel2",
  "weather",
  "context",
  "other",
];

export function normalizeModality(value?: string, featureName = ""): Modality {
  const normalized = (value ?? "").toLowerCase().replace(/[\s_-]/g, "");
  if (normalized.includes("soil") || normalized.includes("sol")) return "soil";
  if (normalized.includes("sentinel1") || normalized === "s1") return "sentinel1";
  if (normalized.includes("sentinel2") || normalized === "s2") return "sentinel2";
  if (normalized.includes("weather") || normalized.includes("meteo")) return "weather";
  if (normalized.includes("context") || normalized.includes("other")) return "context";

  if (/^(phh2o|nitrogen|soc|clay|sand|silt|cec|bdod|cfvo|wv|ocd)/i.test(featureName))
    return "soil";
  if (/^s1_/i.test(featureName)) return "sentinel1";
  if (/^s2_/i.test(featureName)) return "sentinel2";
  if (/^meteo_/i.test(featureName)) return "weather";
  if (/^(year|region|SURF_PARC)$/i.test(featureName)) return "context";
  return "other";
}

export function modalityCounts(features: FeatureDescriptor[]): Record<Modality, number> {
  const counts: Record<Modality, number> = {
    soil: 0,
    sentinel1: 0,
    sentinel2: 0,
    weather: 0,
    context: 0,
    other: 0,
  };
  for (const feature of features) {
    counts[normalizeModality(feature.modality, feature.name)] += 1;
  }
  return counts;
}

export function activeModalities(features: FeatureDescriptor[]): Modality[] {
  const counts = modalityCounts(features);
  return MODALITY_ORDER.filter((modality) => counts[modality] > 0);
}

export function featureLabel(feature: FeatureDescriptor, language: Language): string {
  return (
    feature.label?.[language] ??
    (language === "fr" ? feature.label_fr : feature.label_en) ??
    feature.name.replaceAll("_", " ")
  );
}

export function referenceValues(
  profile: FeatureSchemaResponse["reference_profile"],
): Record<string, unknown> {
  const candidate = profile as ReferenceProfile;
  if (candidate.values && typeof candidate.values === "object") return { ...candidate.values };
  if (candidate.features && typeof candidate.features === "object") return { ...candidate.features };
  const entries = Object.entries(candidate).filter(
    ([key]) => !["label", "year", "name", "description"].includes(key),
  );
  return Object.fromEntries(entries);
}

export function referenceYear(
  profile: FeatureSchemaResponse["reference_profile"],
  fallback: number,
): number {
  const year = Number((profile as ReferenceProfile).year);
  return Number.isFinite(year) ? year : fallback;
}

export function displayValue(feature: FeatureDescriptor, rawValue: unknown): unknown {
  if (feature.reference_display !== undefined && rawValue === feature.reference_raw) {
    return feature.reference_display;
  }
  if (feature.display_value !== undefined && rawValue === feature.reference_value) {
    return feature.display_value;
  }
  if (typeof rawValue !== "number") return rawValue;
  const conversion = feature.conversion ?? {};
  const scale = feature.display_scale ?? conversion.scale ?? 1;
  const divisor = feature.display_divisor ?? conversion.divisor ?? 1;
  const offset = conversion.offset ?? 0;
  return (rawValue * scale) / divisor + offset;
}

export function rawValue(feature: FeatureDescriptor, displayed: unknown): unknown {
  if (typeof displayed !== "number") return displayed;
  const conversion = feature.conversion ?? {};
  const scale = feature.display_scale ?? conversion.scale ?? 1;
  const divisor = feature.display_divisor ?? conversion.divisor ?? 1;
  const offset = conversion.offset ?? 0;
  if (scale === 0) return displayed;
  return ((displayed - offset) * divisor) / scale;
}

export function formatNumber(
  value: number | undefined | null,
  language: Language,
  digits = 1,
): string {
  if (value === undefined || value === null || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat(language, {
    maximumFractionDigits: digits,
    minimumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(
  value: number | undefined | null,
  language: Language,
  digits = 0,
): string {
  if (value === undefined || value === null || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat(language, {
    style: "percent",
    maximumFractionDigits: digits,
  }).format(value);
}

export function formatDate(value: string | undefined, language: Language): string {
  if (!value) return "—";
  const date = new Date(`${value}T12:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(language, {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
}

export function horizonLabel(horizon: Horizon, language: Language): string {
  if (horizon === "may31") return language === "fr" ? "31 mai" : "May 31";
  return language === "fr" ? "15 juin" : "June 15";
}

export function cutoffIso(horizon: Horizon, year: number): string {
  return `${year}-${horizon === "may31" ? "05-31" : "06-15"}`;
}

export function dayDifference(startIso: string, endIso: string): number | null {
  const start = new Date(`${startIso}T12:00:00Z`).getTime();
  const end = new Date(`${endIso}T12:00:00Z`).getTime();
  if (!Number.isFinite(start) || !Number.isFinite(end)) return null;
  return Math.round((end - start) / 86_400_000);
}

export function coverageLevel(evidence?: InputEvidence, legacyCoverage?: number): CoverageLevel {
  const supplied = evidence?.coverage_level ?? evidence?.level;
  if (supplied === "complete" || supplied === "partial" || supplied === "insufficient") {
    return supplied;
  }
  const ratio = evidence?.coverage_ratio ?? legacyCoverage;
  if (ratio !== undefined && ratio >= 0.999) return "complete";
  if (ratio !== undefined && ratio >= 0.5) return "partial";
  return "insufficient";
}

export function parseFeatureFile(content: string, filename: string): Record<string, unknown> {
  if (filename.toLowerCase().endsWith(".json")) {
    const parsed = JSON.parse(content) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("JSON_OBJECT_REQUIRED");
    }
    return parsed as Record<string, unknown>;
  }

  const lines = content.trim().split(/\r?\n/).filter(Boolean);
  if (lines.length < 2) throw new Error("CSV_ROWS_REQUIRED");
  const separator = lines[0].includes(";") ? ";" : ",";
  const headers = lines[0].split(separator).map((value) => value.trim());
  const values = lines[1].split(separator).map((value) => value.trim());
  const result: Record<string, unknown> = {};
  headers.forEach((header, index) => {
    const value = values[index] ?? "";
    const numeric = Number(value.replace(",", "."));
    result[header] = value !== "" && Number.isFinite(numeric) ? numeric : value;
  });
  return result;
}
