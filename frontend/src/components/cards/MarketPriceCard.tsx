import React from 'react';
import { MarketPrice } from '@/services/market.service';

interface Props {
  price: MarketPrice;
}

export function MarketPriceCard({ price }: Props) {
  const isUp = price.price_change_pct !== null && price.price_change_pct > 0;
  const isDown = price.price_change_pct !== null && price.price_change_pct < 0;

  return (
    <div className="bg-surface-elevated/40 backdrop-blur-xl border border-white/5 rounded-2xl p-6 hover:border-brand-primary/30 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-medium text-white">{price.commodity}</h3>
          <p className="text-sm text-text-secondary">
            {price.market_name}, {price.state}
          </p>
        </div>
        {price.price_change_pct !== null && (
          <div
            className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              isUp
                ? 'bg-brand-primary/10 text-brand-primary'
                : isDown
                ? 'bg-red-500/10 text-red-400'
                : 'bg-white/10 text-text-secondary'
            }`}
          >
            {isUp ? '↑' : isDown ? '↓' : '—'} {Math.abs(price.price_change_pct)}%
          </div>
        )}
      </div>

      <div className="mb-4">
        <div className="text-3xl font-light text-brand-primary">
          ₹{price.modal_price.toLocaleString()}
          <span className="text-sm text-text-secondary ml-1">/q</span>
        </div>
        <p className="text-xs text-text-tertiary mt-1">Modal Price</p>
      </div>

      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/5">
        <div>
          <p className="text-xs text-text-tertiary">Min Price</p>
          <p className="text-sm text-white">₹{price.min_price.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-text-tertiary">Max Price</p>
          <p className="text-sm text-white">₹{price.max_price.toLocaleString()}</p>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-text-tertiary text-right">
        Data as of {new Date(price.price_date).toLocaleDateString()}
      </div>
    </div>
  );
}
