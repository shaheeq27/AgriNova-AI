'use client';

import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, AlertCircle, TrendingUp } from 'lucide-react';
import { marketAPI, MarketPrice, MarketStatusResponse } from '@/services/market.service';
import { MarketPriceCard } from '@/components/cards/MarketPriceCard';

export default function MarketPage() {
  const [query, setQuery] = useState('Tomato');
  const [searchInput, setSearchInput] = useState('Tomato');
  const [prices, setPrices] = useState<MarketPrice[]>([]);
  const [status, setStatus] = useState<MarketStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, [query]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [priceRes, statusRes] = await Promise.all([
        marketAPI.getPrices(query),
        marketAPI.getStatus()
      ]);
      setPrices(priceRes.items || []);
      setStatus(statusRes);
    } catch (err) {
      console.error('Failed to load market data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await marketAPI.refresh();
      await loadData();
    } catch (err) {
      console.error('Refresh failed', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setQuery(searchInput.trim());
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto anim-page-enter">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-serif font-bold text-white mb-2">Market Intelligence</h1>
          <p className="text-sm text-text-secondary font-mono">Live mandi prices across India</p>
        </div>
        
        <div className="flex items-center gap-4">
          {status && (
            <div className="text-sm text-text-tertiary hidden md:block">
              {status.data_status === 'live' ? (
                <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-brand-primary"></span> Live Data</span>
              ) : status.data_status === 'cached' ? (
                <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Cached Data</span>
              ) : (
                <span className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-red-500"></span> Unavailable</span>
              )}
            </div>
          )}
          
          <button 
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-surface-elevated border border-white/10 rounded-xl text-sm font-medium hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="bg-surface-elevated/40 border border-white/5 rounded-3xl p-6 mb-8">
        <form onSubmit={handleSearch} className="relative max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search crop (e.g. Tomato, Rice)..."
            className="w-full bg-surface-base border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder-text-tertiary focus:outline-none focus:border-brand-primary/50 transition-colors"
          />
        </form>
      </div>

      {status?.data_status === 'unavailable' && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl flex items-start gap-3 mb-8">
          <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
          <div>
            <h4 className="font-medium">Market Data Unavailable</h4>
            <p className="text-sm mt-1 opacity-90">We could not fetch live market prices from the provider ({status.provider}). Please try refreshing later.</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-48 bg-surface-elevated/20 rounded-2xl animate-pulse"></div>
          ))}
        </div>
      ) : prices.length > 0 ? (
        <>
          <div className="mb-4 flex items-center justify-between text-sm text-text-secondary">
            <span>Showing {prices.length} markets for <strong className="text-white">{query}</strong></span>
            {status?.last_updated && (
              <span>Last updated: {new Date(status.last_updated).toLocaleString()}</span>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {prices.map(price => (
              <MarketPriceCard key={price.id} price={price} />
            ))}
          </div>
        </>
      ) : (
        <div className="py-20 text-center">
          <TrendingUp className="w-12 h-12 text-text-tertiary mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-medium text-white mb-2">No prices found</h3>
          <p className="text-text-secondary">We couldn't find any recent market data for "{query}".</p>
        </div>
      )}
    </div>
  );
}
