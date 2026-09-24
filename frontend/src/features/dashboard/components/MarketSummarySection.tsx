'use client';

import React, { useEffect, useState } from 'react';
import { TrendingUp, Clock, AlertCircle } from 'lucide-react';
import { marketAPI, MarketSummaryResponse } from '@/services/market.service';

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
  }, [activeCropNames, isLoadingCrops]);

  // Section Label exactly matching other Dashboard components
  const sectionLabel = (
    <div style={{
      fontFamily: 'monospace, sans-serif',
      fontSize: '11px',
      fontWeight: 600,
      color: 'var(--color-text-muted, #8d928c)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      marginBottom: '10px',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    }}>
      <TrendingUp size={14} style={{ color: 'var(--accent-primary, #adff00)' }} />
      Market Watch
    </div>
  );

  const cardStyle = {
    background: 'var(--color-bg-card, rgba(31, 32, 31, 0.75))',
    backdropFilter: 'blur(16px)',
    border: '1px solid var(--color-border, rgba(141, 146, 140, 0.15))',
    borderRadius: '16px',
    padding: '20px 24px',
    width: '100%',
    minHeight: '100px',
    display: 'flex',
    flexDirection: 'column' as const,
    justifyContent: 'center',
    boxSizing: 'border-box' as const,
  };

  if (loading) {
    return (
      <div className={className} style={{ width: '100%' }}>
        {sectionLabel}
        <div style={cardStyle}>
          <div style={{ color: '#8d928c', fontSize: '14px', textAlign: 'center' }}>
            Loading market data...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={className} style={{ width: '100%' }}>
      {sectionLabel}

      <div style={cardStyle}>
        {data?.data_status === 'unavailable' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f59e0b', background: 'rgba(245, 158, 11, 0.1)', padding: '12px 16px', borderRadius: '12px', marginBottom: '16px' }}>
            <AlertCircle size={16} />
            <p style={{ fontSize: '14px' }}>Live market data is currently unavailable.</p>
          </div>
        )}

        {(!data || data.items.length === 0) ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
            <TrendingUp size={20} style={{ color: 'var(--accent-primary, #adff00)', marginBottom: '8px' }} />
            <p style={{ fontSize: '15px', fontWeight: 500, color: '#F2F0E8', marginBottom: '5px' }}>
              No market data available
            </p>
            {data?.data_status !== 'unavailable' && (
              <p style={{ fontSize: '13px', color: '#8d928c', opacity: 0.7 }}>
                Add crops to your farm to see relevant prices.
              </p>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {data.items.map((item, idx) => {
              const isUp = item.price_change_pct !== null && item.price_change_pct > 0;
              const isDown = item.price_change_pct !== null && item.price_change_pct < 0;

              return (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    borderRadius: '12px'
                  }}
                >
                  <div>
                    <h4 style={{ fontSize: '14px', fontWeight: 500, color: '#e4e2e0', marginBottom: '2px' }}>{item.commodity}</h4>
                    <p style={{ fontSize: '12px', color: '#8d928c' }}>{item.market_name}</p>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '14px', fontWeight: 500, color: '#e4e2e0' }}>
                      ₹{item.modal_price.toLocaleString()}<span style={{ fontSize: '10px', color: '#8d928c', marginLeft: '2px' }}>/q</span>
                    </div>
                    {item.price_change_pct !== null && (
                      <div style={{
                        fontSize: '12px',
                        marginTop: '2px',
                        color: isUp ? 'var(--accent-primary, #adff00)' : isDown ? '#ffb4ab' : '#8d928c'
                      }}>
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
    </div>
  );
}
