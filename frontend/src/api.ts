import type {
  ComparisonResponse,
  EvaluationResponse,
  FeatureSchemaResponse,
  HealthResponse,
  Horizon,
  ObservatoryData,
  OverviewResponse,
  PredictionResponse,
} from "./types";

const API_PREFIX = "/api";
const REQUEST_TIMEOUT_MS = 12_000;

export class ApiError extends Error {
  status: number | null;
  detail: string;

  constructor(message: string, status: number | null = null, detail = "") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(`${API_PREFIX}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
      signal: controller.signal,
    });
    const payload = (await response.json().catch(() => null)) as
      | { detail?: string }
      | T
      | null;
    if (!response.ok) {
      const detail =
        payload && typeof payload === "object" && "detail" in payload
          ? String(payload.detail ?? "")
          : "";
      throw new ApiError(
        detail || `API request failed (${response.status})`,
        response.status,
        detail,
      );
    }
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("The API did not answer in time.");
    }
    throw new ApiError(error instanceof Error ? error.message : "The API is unreachable.");
  } finally {
    window.clearTimeout(timeout);
  }
}

export async function loadObservatory(): Promise<ObservatoryData> {
  const [
    health,
    overview,
    evaluationMay,
    evaluationJune,
    comparison,
    schemaMay,
    schemaJune,
  ] = await Promise.all([
    request<HealthResponse>("/health"),
    request<OverviewResponse>("/insights/overview"),
    request<EvaluationResponse>("/insights/evaluation/may31"),
    request<EvaluationResponse>("/insights/evaluation/june15"),
    request<ComparisonResponse>("/insights/horizon-comparison"),
    request<FeatureSchemaResponse>("/features/schema/may31"),
    request<FeatureSchemaResponse>("/features/schema/june15"),
  ]);

  return {
    health,
    overview,
    evaluations: { may31: evaluationMay, june15: evaluationJune },
    comparison,
    schemas: { may31: schemaMay, june15: schemaJune },
    fetchedAt: new Date(),
  };
}

export async function predictHarvest(
  horizon: Horizon,
  year: number,
  features: Record<string, unknown>,
): Promise<PredictionResponse> {
  return request<PredictionResponse>("/predict/harvest-date", {
    method: "POST",
    body: JSON.stringify({ horizon, year, features }),
  });
}

