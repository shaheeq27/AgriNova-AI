import React from 'react';
import { MarketPrice } from '@/services/market.service';

interface Props {
  price: MarketPrice;
}

export function MarketPriceCard({ price }: Props) {
  const isUp = price.price_change_pct !== null && price.price_change_pct > 0;
  const isDown = price.price_change_pct !== null && price.price_change_pct < 0;

  return (
    <div style={{
      width: '100%',
      padding: '20px',
      borderRadius: '16px',
      backgroundColor: 'rgba(31, 41, 55, 0.5)',
      border: '1px solid rgba(255, 255, 255, 0.05)',
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ minWidth: 0, paddingRight: '12px', flex: 1 }}>
          <div style={{
            fontSize: '20px',
            lineHeight: '24px',
            fontWeight: 500,
            color: '#ffffff',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}>
            {price.commodity}
          </div>
          <div style={{
            fontSize: '13px',
            lineHeight: '18px',
            color: '#9ca3af',
            marginTop: '2px',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}>
            {price.market_name}, {price.state}
          </div>
        </div>

        {/* Trend */}
        {price.price_change_pct !== null && (
          <div style={{
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            padding: '4px 8px',
            borderRadius: '9999px',
            fontSize: '12px',
            fontWeight: 500,
            backgroundColor: isUp ? 'rgba(34, 197, 94, 0.1)' : isDown ? 'rgba(239, 68, 68, 0.1)' : 'rgba(255, 255, 255, 0.1)',
            color: isUp ? '#4ade80' : isDown ? '#f87171' : '#9ca3af'
          }}>
            {isUp ? '↑' : isDown ? '↓' : '—'} {Math.abs(price.price_change_pct)}%
          </div>
        )}
      </div>

      {/* Price */}
      <div style={{ marginTop: '14px' }}>
        <div style={{
          fontSize: '34px',
          lineHeight: '40px',
          fontWeight: 300,
          color: '#4ade80'
        }}>
          ₹{price.modal_price.toLocaleString()}
          <span style={{ fontSize: '14px', color: '#9ca3af', marginLeft: '4px' }}>/q</span>
        </div>
      </div>

      {/* Date */}
      <div style={{
        marginTop: '16px',
        textAlign: 'right',
        fontSize: '11px',
        color: '#6b7280'
      }}>
        Data as of {new Date(price.price_date).toLocaleDateString()}
      </div>
    </div>
  );
}
