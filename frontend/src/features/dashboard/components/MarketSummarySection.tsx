'use client';

import React, { useEffect, useState } from 'react';
import { TrendingUp, Clock, AlertCircle } from 'lucide-react';
import { marketAPI, MarketSummaryResponse } from '@/services/market.service';
import { useAuth } from '@/providers/AuthProvider';

interface Props {
  className?: string;
  activeCropNames: string[];
  isLoadingCrops?: boolean;
}

export function MarketSummarySection({ className = '', activeCropNames, isLoadingCrops = false }: Props) {
  const [data, setData] = useState<MarketSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (isLoadingCrops) return; // Wait for parent to finish loading crops
      
      if (activeCropNames.length === 0) {
        setLoading(false);
        setData(null);
        return;
      }
      
      setLoading(true);
      try {
        const res = await marketAPI.getSummary(activeCropNames);
        setData(res);
      } catch (err) {
        console.error('Failed to load market summary', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeCropNames]);

  if (loading) {
    return (
      <div className={`bg-surface-base border border-white/5 rounded-3xl p-6 ${className}`}>
        <h2 className="text-xl font-medium text-white mb-6">Market Watch</h2>
        <div className="animate-pulse space-y-4">
          <div className="h-16 bg-white/5 rounded-2xl w-full"></div>
          <div className="h-16 bg-white/5 rounded-2xl w-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-surface-base border border-white/5 rounded-3xl p-6 flex flex-col ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-brand-primary/10 rounded-xl">
            <TrendingUp className="w-5 h-5 text-brand-primary" />
          </div>
          <h2 className="text-xl font-medium text-white">Market Watch</h2>
        </div>
        
        {data?.last_updated && (
          <div className="flex items-center gap-1.5 text-xs text-text-tertiary">
            <Clock className="w-3.5 h-3.5" />
            <span>Updated {new Date(data.last_updated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}
      </div>

      {data?.data_status === 'unavailable' && (
        <div className="flex items-center gap-2 text-sm text-yellow-500/80 bg-yellow-500/10 p-4 rounded-2xl mb-4">
          <AlertCircle className="w-4 h-4" />
          <p>Live market data is currently unavailable.</p>
        </div>
      )}

      {(!data || data.items.length === 0) ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center p-6 bg-white/5 rounded-2xl border border-white/5 border-dashed">
          <TrendingUp className="w-8 h-8 text-text-tertiary mb-3" />
          <p className="text-sm text-text-secondary">No market data available</p>
          {data?.data_status !== 'unavailable' && (
            <p className="text-xs text-text-tertiary mt-1">Add crops to your farm to see relevant prices.</p>
          )}
        </div>
      ) : (
        <div className="flex-1 space-y-3 overflow-y-auto pr-2">
          {data.items.map((item, idx) => {
            const isUp = item.price_change_pct !== null && item.price_change_pct > 0;
            const isDown = item.price_change_pct !== null && item.price_change_pct < 0;

            return (
              <div 
                key={idx}
                className="flex items-center justify-between p-4 bg-surface-elevated/40 border border-white/5 rounded-2xl"
              >
                <div>
                  <h4 className="text-sm font-medium text-white">{item.commodity}</h4>
                  <p className="text-xs text-text-tertiary">{item.market_name}</p>
                </div>
                
                <div className="text-right">
                  <div className="text-sm font-medium text-white">
                    ₹{item.modal_price.toLocaleString()}<span className="text-[10px] text-text-tertiary">/q</span>
                  </div>
                  {item.price_change_pct !== null && (
                    <div className={`text-xs mt-0.5 ${isUp ? 'text-brand-primary' : isDown ? 'text-red-400' : 'text-text-tertiary'}`}>
                      {isUp ? '↑' : isDown ? '↓' : ''} {Math.abs(item.price_change_pct)}%
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
