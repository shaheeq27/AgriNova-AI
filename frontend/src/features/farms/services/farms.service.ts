import { farmAPI, cropsAPI } from '@/lib/api';
import { Farm, CreateFarmInput, FarmStatsData } from '../types';
import { DEFAULT_FARMS, CROP_DURATION_KB } from '../constants';
import { parseDateString } from '@/utils/date';

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

      // If a crop was provided, plant it immediately
      if (input.crop_name && input.season && input.planting_date) {
        try {
          await cropsAPI.plant({
            farm_id: (created as Farm).id,
            crop_name: input.crop_name,
            season: input.season,
            area_acres: input.total_area_acres,
            planting_date: input.planting_date
          });
        } catch (e) {
          console.error("Failed to plant crop during farm creation:", e);
        }
      }

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
  static calculateCropDays(plantingDateStr?: string, cropName?: string, createdAtStr?: string) {
    const totalDays = this.getCropDurationDays(cropName);

    // Use created_at as fallback if plantingDate is missing
    const targetDateStr = plantingDateStr || createdAtStr;

    if (!targetDateStr) {
      return { currentDay: 1, totalDays };
    }

    const planted = parseDateString(targetDateStr);
    if (!planted) {
      return { currentDay: 1, totalDays };
    }

    const now = new Date();
    now.setHours(0, 0, 0, 0);

    const diffTime = now.getTime() - planted.getTime();
    const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

    let currentDay = diffDays + 1;
    currentDay = Math.max(1, Math.min(currentDay, totalDays));

    return { currentDay, totalDays };
  }
}
