import { useState, useCallback } from 'react';
import { cropsAPI, CropRecommendationRequest, CropRecommendationResponse, ApiError } from '@/lib/api';

export function useCropRecommendation() {
  const [data, setData] = useState<CropRecommendationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchRecommendations = useCallback(async (params: CropRecommendationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const res = await cropsAPI.recommend(params);
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
