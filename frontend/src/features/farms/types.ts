export interface Crop {
  id: string;
  crop_name: string;
  status: string;
  area_acres: number;
}

export interface Farm {
  id: string;
  user_id: string;
  name: string;
  location_city: string;
  location_state?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  total_area_acres: number;
  soil_type: string;
  water_source?: string | null;
  description?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  bannerImage?: string;
  stageName?: string;
  defaultDay?: number;
  crops?: Crop[];
}

export interface CreateFarmInput {
  name: string;
  location_city: string;
  location_state?: string;
  total_area_acres: number;
  soil_type: string;
  water_source?: string;
  description?: string;
}

export interface FarmStatsData {
  totalFarms: number;
  totalArea: number;
  activeFarms: number;
  idleFarms: number;
}

export type ViewMode = 'grid' | 'list';
