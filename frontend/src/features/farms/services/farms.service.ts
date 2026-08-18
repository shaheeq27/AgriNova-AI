import { farmAPI } from '@/lib/api';
import { Farm, CreateFarmInput, FarmStatsData } from '../types';
import { DEFAULT_FARMS, CROP_DURATION_KB } from '../constants';

export class FarmsService {
  /**
   * List all user farms, falling back to default sample farms if API is unauthenticated or empty.
   */
  static async getFarms(): Promise<Farm[]> {
    try {
      const data = await farmAPI.list();
      if (data.farms && data.farms.length > 0) {
        return data.farms as Farm[];
      }
      return DEFAULT_FARMS;
    } catch {
      return DEFAULT_FARMS;
    }
  }

  /**
   * Create a new farm, falling back to a local Farm object if API call fails.
   */
  static async createFarm(input: CreateFarmInput): Promise<Farm> {
    try {
      const created = await farmAPI.create(input);
      return created as Farm;
    } catch {
      const localFarm: Farm = {
        id: `farm-${Date.now()}`,
        user_id: 'local-user',
        name: input.name,
        location_city: input.location_city,
        location_state: input.location_state || null,
        latitude: null,
        longitude: null,
        total_area_acres: input.total_area_acres,
        soil_type: input.soil_type,
        water_source: input.water_source || null,
        description: input.description || null,
        is_active: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        bannerImage: '/farm_3.jpg',
        crops: [],
      };
      return localFarm;
    }
  }

  /**
   * Compute aggregated statistics from a list of farms.
   */
  static calculateStats(farms: Farm[]): FarmStatsData {
    const totalFarms = farms.length;
    const totalArea = farms.reduce((acc, f) => acc + (f.total_area_acres || 0), 0);
    const activeFarms = farms.filter((f) => f.crops && f.crops.length > 0).length;
    const idleFarms = farms.filter((f) => !f.crops || f.crops.length === 0).length;

    return { totalFarms, totalArea, activeFarms, idleFarms };
  }

  /**
   * Lookup duration days from KB for a given crop name.
   */
  static getCropDurationDays(cropName?: string): number {
    if (!cropName) return 120;
    const lower = cropName.toLowerCase();
    for (const key of Object.keys(CROP_DURATION_KB)) {
      if (lower.includes(key)) {
        return CROP_DURATION_KB[key];
      }
    }
    return 120;
  }

  /**
   * Calculate current day and total crop duration days dynamically.
   */
  static calculateCropDays(plantingDateStr?: string, cropName?: string, defaultDay: number = 60) {
    const totalDays = this.getCropDurationDays(cropName);
    let currentDay = defaultDay;

    if (plantingDateStr) {
      const planted = new Date(plantingDateStr);
      const now = new Date();
      const diffTime = Math.max(0, now.getTime() - planted.getTime());
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      currentDay = Math.min(diffDays + 1, totalDays);
    }

    return { currentDay, totalDays };
  }
}
