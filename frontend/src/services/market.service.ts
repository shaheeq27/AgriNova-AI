import { request } from '@/lib/api';

export type DataStatus = 'live' | 'cached' | 'unavailable';

export interface MarketPrice {
  id: string;
  commodity: string;
  variety: string | null;
  market_name: string;
  district: string;
  state: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  price_date: string;
  source: string;
  fetched_at: string;
  price_change_pct: number | null;
}

export interface MarketPriceListResponse {
  items: MarketPrice[];
  total: number;
  last_updated: string | null;
  data_status: DataStatus;
}

export interface MarketComparisonItem {
  market_name: string;
  district: string;
  state: string;
  min_price: number;
  max_price: number;
  modal_price: number;
  price_date: string;
}

export interface MarketComparisonResponse {
  commodity: string;
  markets: MarketComparisonItem[];
  last_updated: string | null;
  data_status: DataStatus;
}

export interface MarketSummaryItem {
  commodity: string;
  market_name: string;
  modal_price: number;
  price_date: string;
  price_change_pct: number | null;
  trend: 'up' | 'down' | 'stable' | null;
}

export interface MarketSummaryResponse {
  items: MarketSummaryItem[];
  last_updated: string | null;
  data_status: DataStatus;
}

export interface MarketStatusResponse {
  provider: string;
  is_healthy: boolean;
  last_updated: string | null;
  total_records: number;
  data_status: DataStatus;
}

export const marketAPI = {
  getPrices: (commodity: string, state?: string) => {
    const params = new URLSearchParams({ commodity });
    if (state) params.append('state', state);
    return request<MarketPriceListResponse>(`/market/prices?${params.toString()}`);
  },

  getPricesByMarket: (marketName: string) => {
    return request<MarketPriceListResponse>(`/market/prices/${marketName}`);
  },

  comparePrices: (commodity: string, markets: string[]) => {
    const params = new URLSearchParams({ commodity });
    markets.forEach(m => params.append('markets', m));
    return request<MarketComparisonResponse>(`/market/compare?${params.toString()}`);
  },

  getSummary: (commodities: string[]) => {
    const params = new URLSearchParams();
    commodities.forEach(c => params.append('commodities', c));
    return request<MarketSummaryResponse>(`/market/summary?${params.toString()}`);
  },

  getStatus: () => {
    return request<MarketStatusResponse>('/market/status');
  },

  refresh: () => {
    return request<{ records_fetched: number }>('/market/refresh', {
      method: 'POST',
    });
  },
};
