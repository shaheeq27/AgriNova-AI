import { useState, useEffect } from 'react';
import { historyAPI, FarmInsightsResponse, ApiError } from '@/lib/api';

export function useFarmInsights(farmId: string | undefined) {
  const [data, setData] = useState<FarmInsightsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);


  useEffect(() => {
    if (!farmId) return;

    let isMounted = true;
    
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const insights = await historyAPI.getInsights(farmId);
        if (isMounted) {
          setData(insights);
          setLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof ApiError ? err : new ApiError((err as Error).message, 500));
          setLoading(false);
        }
      }
    };
    
    fetchData();

    return () => {
      isMounted = false;
    };
  }, [farmId]);


  return { data, loading, error };
}
