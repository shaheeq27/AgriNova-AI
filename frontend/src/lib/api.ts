import type { ImageAnalysisResponse } from "@/features/disease/types";

/**
 * AgriNova AI — API Client
 *
 * Typed fetch wrapper with JWT injection, error handling, and base URL config.
 */

import { APP_CONFIG } from "@/config/app.config";

export const API_BASE_URL = APP_CONFIG.api.baseUrl;

export interface APIResponse<T = unknown> {
  status: "success" | "error";
  message: string;
  data: T;
  errors: { field: string; message: string }[];
}

class ApiError extends Error {
  status: number;
  errors: { field: string; message: string }[];

  constructor(message: string, status: number, errors: { field: string; message: string }[] = []) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errors = errors;
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("agrinova_token");
}

export async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const json: APIResponse<T> = await response.json();

  if (!response.ok || json.status === "error") {
    throw new ApiError(json.message || "Something went wrong", response.status, json.errors);
  }

  return json.data;
}

// ── Auth API ──
export interface UserData {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenData {
  access_token: string;
  token_type: string;
  user: UserData;
}

export const authAPI = {
  register: (data: { email: string; password: string; full_name: string; phone?: string }) =>
    request<TokenData>("/auth/register", { method: "POST", body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<TokenData>("/auth/login", { method: "POST", body: JSON.stringify(data) }),

  getProfile: () => request<UserData>("/auth/me"),

  updateProfile: (data: { full_name?: string; phone?: string }) =>
    request<UserData>("/auth/me", { method: "PUT", body: JSON.stringify(data) }),

  forgotPassword: (email: string) =>
    request<void>("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),

  resetPassword: (data: { reset_id: string; token: string; new_password: string }) =>
    request<void>("/auth/reset-password", { method: "POST", body: JSON.stringify(data) }),
};

// ── Farm API ──
export interface FarmData {
  id: string;
  user_id: string;
  name: string;
  location_city: string;
  location_state: string | null;
  latitude: number | null;
  longitude: number | null;
  total_area_acres: number;
  soil_type: string;
  water_source: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  crops: { id: string; crop_name: string; status: string; area_acres: number }[];
}

export interface FarmListData {
  farms: FarmData[];
  total: number;
}

export const farmAPI = {
  create: (data: {
    name: string;
    location_city: string;
    location_state?: string;
    total_area_acres: number;
    soil_type: string;
    water_source?: string;
    description?: string;
  }) => request<FarmData>("/farms", { method: "POST", body: JSON.stringify(data) }),

  list: () => request<FarmListData>("/farms"),

  get: (id: string) => request<FarmData>(`/farms/${id}`),

  update: (id: string, data: Partial<FarmData>) =>
    request<FarmData>(`/farms/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  delete: (id: string) => request<void>(`/farms/${id}`, { method: "DELETE" }),
};

// ── Knowledge Base API ──
export interface CropProfile {
  id: string;
  crop_name: string;
  description: string | null;
  temp_min: number;
  temp_max: number;
  rain_min: number;
  rain_max: number;
  humidity_min: number;
  humidity_max: number;
  ideal_soil_types: string;
  growing_season: string;
  total_duration_days: number | null;
  image_url: string | null;
}

export const knowledgeAPI = {
  listCrops: () => request<CropProfile[]>("/knowledge/crops"),
  getCrop: (name: string) => request<CropProfile>(`/knowledge/crops/${name}`),
  getCropStages: (name: string) => request<unknown[]>(`/knowledge/crops/${name}/stages`),
  listDiseases: () => request<unknown[]>("/knowledge/diseases"),
  listFertilizers: (crop?: string) =>
    request<unknown[]>(`/knowledge/fertilizers${crop ? `?crop_name=${crop}` : ""}`),
  listIrrigation: (crop?: string) =>
    request<unknown[]>(`/knowledge/irrigation${crop ? `?crop_name=${crop}` : ""}`),
};


// ── Farm Insights API ──
export interface CropPerformanceInsight {
  crop_name: string;
  variety: string | null;
  seasons_observed: string[];
  crops_observed: number;
  harvested_count: number;
  average_yield: number | null;
  yield_unit: string | null;
  best_yield: number | null;
  worst_yield: number | null;
  disease_records: number;
  fertilizer_applications: number;
  irrigation_applications: number;
  confidence: number | null;
}

export interface SeasonalPerformanceInsight {
  season: string;
  crops_observed: number;
  harvested_crops: number;
  average_yield: number | null;
  yield_unit: string | null;
  confidence: number | null;
}

export interface DiseasePatternInsight {
  disease_name: string;
  affected_crop: string;
  occurrence_count: number;
  resolved_count: number;
  active_count: number;
  common_severity: string | null;
  treatment_observed: string | null;
  confidence: number | null;
}

export interface InputUsageInsight {
  input_type: string;
  crop_name: string;
  application_count: number;
  total_quantity: number | null;
  quantity_unit: string | null;
  common_application_method: string | null;
  confidence: number | null;
}

export interface YieldTrendInsight {
  crop_name: string;
  yield_unit: string;
  observations: number;
  average_yield: number | null;
  highest_yield: number | null;
  lowest_yield: number | null;
  trend_direction: string | null;
  confidence: number | null;
}

export interface FarmInsightsResponse {
  crop_performance: CropPerformanceInsight[];
  seasonal_performance: SeasonalPerformanceInsight[];
  disease_patterns: DiseasePatternInsight[];
  input_usage: InputUsageInsight[];
  yield_trends: YieldTrendInsight[];
}

export const historyAPI = {
  getInsights: (farmId: string) => request<FarmInsightsResponse>(`/farms/${farmId}/insights`),
};

// ── Recommendations API ──
export interface CropRecommendation {
  crop_name: string;
  confidence: number;
  explanation: string;
  model_version: string;
  historically_adjusted: boolean;
  personalization_rationale: string | null;
}


export interface CropResponse {
  id: string;
  farm_id: string;
  crop_name: string;
  variety: string | null;
  season: string;
  planting_date: string | null;
  expected_harvest_date: string | null;
  actual_harvest_date: string | null;
  area_acres: number;
  status: string;
  yield_amount: number | null;
  yield_unit: string | null;
  created_at: string;
}

export interface CropListResponse {
  crops: CropResponse[];
  total: number;
}

export interface CropRecommendationRequest {
  temperature: number;
  humidity: number;
  rainfall: number;
  soil_type: string;
  n?: number;
  p?: number;
  k?: number;
  ph?: number;
  farm_id?: string;
}

export interface CropRecommendationResponse {
  recommendations: CropRecommendation[];
  input_conditions: Record<string, unknown>;
}


export interface ExplanationPayload {
  base_explanation: string;
  positive_factors: string[];
  negative_factors: string[];
  constraints_applied: string[];
}

export interface CropRecommendationV6 {
  crop_name: string;
  final_score: number;
  base_score: number;
  explanation: ExplanationPayload;
  personalization_applied: boolean;
  engine_version: string;
}

export interface CropRecommendationRequestV6 {
  farm_id?: string;
  location_name?: string;
  soil_type: string;
  season?: string;
  water_source?: string;
  temperature?: number;
  humidity?: number;
  rainfall?: number;
}

export interface CropRecommendationResponseV6 {
  recommendations: CropRecommendationV6[];
  input_conditions_used: Record<string, unknown>;
}

// ── Weather API ──
export interface WeatherCurrent {
  temperature: number | null;
  humidity: number | null;
  rainfall: number | null;
  wind_speed: number | null;
  condition: string;
  description: string;
  source: string;
}

export interface WeatherForecast {
  date: string;
  temp_min: number;
  temp_max: number;
  precipitation: number;
  wind_speed: number;
  condition: string;
}

export interface WeatherAlert {
  type: string;
  severity: string;
  message: string;
  date: string;
}

export interface WeatherResponse {
  current: WeatherCurrent;
  forecast: WeatherForecast[];
  alerts: WeatherAlert[];
}

export const weatherAPI = {
  getFarmWeather: (farmId: string) => request<WeatherResponse>(`/weather/farm/${farmId}`),
};

export const cropsAPI = {
  listByFarm: (farmId: string) => request<CropListResponse>(`/crops/farm/${farmId}`),
  plant: (data: Record<string, unknown>) => request<CropResponse>("/crops/plant", { method: "POST", body: JSON.stringify(data) }),
  getTimeline: (cropId: string) => request<{ stages?: Record<string, unknown>[]; current_stage?: string }>(`/crops/${cropId}/timeline`),
  getTasks: (cropId: string) => request<{ tasks?: Record<string, unknown>[] }>(`/crops/${cropId}/tasks`),
  recommend: (data: CropRecommendationRequest) =>
    request<CropRecommendationResponse>("/crops/recommend", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  recommendV6: (data: CropRecommendationRequestV6) =>
    request<CropRecommendationResponseV6>("/crops/v6/recommend", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export interface FertilizerRecommendation {
  fertilizer_type: string;
  quantity_per_acre: number;
  unit: string;
  timing: string;
  application_method: string | null;
  explanation: string;
  historically_adjusted: boolean;
  personalization_rationale: string | null;
}

export const fertilizerAPI = {
  getLogs: (cropId: string) => request<unknown[]>(`/fertilizer/logs/${cropId}`),
  recommend: (cropName: string, stage: string, soilType: string, farmId?: string) => {
    let url = `/fertilizer/recommend/${encodeURIComponent(cropName)}?stage=${encodeURIComponent(stage)}&soil_type=${encodeURIComponent(soilType)}`;
    if (farmId) url += `&farm_id=${encodeURIComponent(farmId)}`;
    return request<FertilizerRecommendation>(url);
  },
};

export interface IrrigationRecommendation {
  water_requirement_mm: number;
  frequency: string;
  method: string | null;
  explanation: string;
  weather_adjusted: boolean;
  historically_adjusted: boolean;
  personalization_rationale: string | null;
}

export const irrigationAPI = {
  getLogs: (cropId: string) => request<unknown[]>(`/irrigation/logs/${cropId}`),
  recommend: (cropName: string, stage: string, soilType: string, farmId?: string) => {
    let url = `/irrigation/recommend/${encodeURIComponent(cropName)}?stage=${encodeURIComponent(stage)}&soil_type=${encodeURIComponent(soilType)}`;
    if (farmId) url += `&farm_id=${encodeURIComponent(farmId)}`;
    return request<IrrigationRecommendation>(url);
  },
};

// ── Disease Detection API ──




export const diseaseAPI = {
  getRecords: (cropId: string) => request<unknown[]>(`/disease/records/${cropId}`),
  analyzeImage: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<ImageAnalysisResponse>("/disease/analyze-image", {
      method: "POST",
      body: formData,
    });
  }
};

export { ApiError };
export default request;

export interface FormContextData {
  locationText: string;
  soilText: string;
  seasonText: string;
  waterText: string;
}

export const activityAPI = {
  getForCrop: (cropId: string) => request<unknown[]>(`/activity/crop/${cropId}`)
};
