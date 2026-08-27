import { useState, useCallback } from 'react';
import { fertilizerAPI, FertilizerRecommendation, ApiError } from '@/lib/api';

export function useFertilizerRecommendation() {
  const [data, setData] = useState<FertilizerRecommendation | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchRecommendations = useCallback(async (cropName: string, stage: string, soilType: string, farmId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fertilizerAPI.recommend(cropName, stage, soilType, farmId);
      setData(res);
      setLoading(false);
      return res;
    } catch (err: unknown) {
      const apiError = err instanceof ApiError ? err : new ApiError((err as Error).message || 'Unknown error', 500);
      setError(apiError);
      setLoading(false);
      throw apiError;
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, fetchRecommendations, reset };
}
