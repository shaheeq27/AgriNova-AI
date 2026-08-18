/* ══════════════════════════════════════════════════════════════
   AgriNova AI — Disease Detection Service
   Wraps backend /api/v1/disease/* endpoints.
   ══════════════════════════════════════════════════════════════ */

import request from '@/lib/api';

/* ── Request / Response types matching backend schemas ── */

interface DetectRequest {
  crop_name: string;
  symptoms: string[];
}

export interface DiseaseMatch {
  disease_name: string;
  confidence: number;
  symptoms: string[];
  treatment: string;
  prevention: string;
  severity: string;
  explanation: string;
}

interface DetectResponse {
  matches: DiseaseMatch[];
  model_version: string;
}

export interface RecordCreateData {
  crop_id: string;
  disease_name: string;
  symptoms_observed?: string;
  severity?: string;
  detection_source?: string;
  notes?: string;
}

export interface RecordUpdateData {
  status?: string;
  treatment_applied?: string;
  notes?: string;
  resolved_at?: string;
}

export interface DiseaseRecord {
  id: string;
  crop_id: string;
  disease_name: string;
  confidence: number | null;
  detection_source: string;
  symptoms_observed: string | null;
  treatment_applied: string | null;
  severity: string;
  status: string;
  notes: string | null;
  detected_at: string;
  resolved_at: string | null;
  images: { id: string; file_path: string; file_name: string; uploaded_at: string }[];
}

/* ── API base URL ── */
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('agrinova_token');
}

export const DiseaseService = {
  /** Detect disease from symptoms (public endpoint) */
  detectFromSymptoms: (cropName: string, symptoms: string[]) =>
    request<DetectResponse>('/disease/detect', {
      method: 'POST',
      body: JSON.stringify({ crop_name: cropName, symptoms } satisfies DetectRequest),
    }),

  /** Upload a disease image for a crop (multipart form data) */
  uploadImage: async (cropId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE}/disease/upload/${cropId}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    const json = await res.json();
    if (!res.ok || json.status === 'error') throw new Error(json.message);
    return json.data as { file_path: string; file_name: string };
  },

  /** Create a disease record (farm-linked only) */
  createRecord: (data: RecordCreateData) =>
    request<DiseaseRecord>('/disease/record', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** Get disease records for a crop */
  getRecords: (cropId: string) =>
    request<DiseaseRecord[]>(`/disease/records/${cropId}`),

  /** Update a disease record (treatment applied, status, resolution) */
  updateRecord: (recordId: string, data: RecordUpdateData) =>
    request<DiseaseRecord>(`/disease/record/${recordId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  /** Get disease info from knowledge base */
  getDiseaseInfo: (diseaseName: string) =>
    request<Record<string, unknown>>(`/disease/info/${diseaseName}`),
};
