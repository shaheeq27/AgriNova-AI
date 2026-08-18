/**
 * AgriNova AI — API Client
 *
 * Typed fetch wrapper with JWT injection, error handling, and base URL config.
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

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

export { ApiError };
export default request;
