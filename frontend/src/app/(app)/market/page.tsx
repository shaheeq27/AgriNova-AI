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
    <div className="market-container" style={{
      maxWidth: '1280px',
      width: 'calc(100% - 48px)',
      marginLeft: 'auto',
      marginRight: 'auto',
      paddingLeft: '0',
      paddingRight: '0',
    }}>
      <style>{`
        @media (max-width: 767px) {
          .market-container {
            width: calc(100% - 32px) !important;
          }
          .market-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr)) !important;
            gap: 16px !important;
          }
        }
        @media (min-width: 768px) and (max-width: 1199px) {
          .market-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
          }
        }
      `}</style>

      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginTop: '32px'
      }}>
        <div>
          <h1 style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '40px',
            lineHeight: '48px',
            fontWeight: 700,
            color: '#ffffff',
            margin: '0 0 4px 0'
          }}>Market Intelligence</h1>
          <p style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: '15px',
            lineHeight: '22px',
            color: '#9ca3af',
            margin: 0
          }}>Live mandi prices across India</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '6px' }}>
          {status && (
            <div style={{ fontSize: '14px', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: '8px' }} className="hidden md:flex">
              {status.data_status === 'live' ? (
                <><span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#22c55e' }}></span> Live Data</>
              ) : status.data_status === 'cached' ? (
                <><span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#eab308' }}></span> Cached Data</>
              ) : (
                <><span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444' }}></span> Unavailable</>
              )}
            </div>
          )}

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 16px',
              backgroundColor: 'rgba(31, 41, 55, 0.5)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              color: '#ffffff',
              fontSize: '14px',
              fontWeight: 500,
              cursor: refreshing ? 'not-allowed' : 'pointer',
              opacity: refreshing ? 0.5 : 1
            }}
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Search */}
      <div style={{ marginTop: '24px' }}>
        <form onSubmit={handleSearch} style={{ position: 'relative', width: '100%' }}>
          <Search size={20} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search crop (e.g. Tomato, Rice)..."
            style={{
              width: '100%',
              height: '48px',
              backgroundColor: 'rgba(17, 24, 39, 0.6)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              padding: '0 16px 0 48px',
              color: '#ffffff',
              fontSize: '15px',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
        </form>
      </div>

      {status?.data_status === 'unavailable' && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '16px', borderRadius: '12px', display: 'flex', alignItems: 'flex-start', gap: '12px', marginTop: '24px', color: '#f87171' }}>
          <AlertCircle size={20} style={{ marginTop: '2px', flexShrink: 0 }} />
          <div>
            <h4 style={{ fontWeight: 500, margin: '0 0 4px 0' }}>Market Data Unavailable</h4>
            <p style={{ fontSize: '14px', margin: 0, opacity: 0.9 }}>We could not fetch live market prices from the provider ({status.provider}). Please try refreshing later.</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="market-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '24px', marginTop: '52px' }}>
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} style={{ width: '100%', height: '170px', backgroundColor: 'rgba(31, 41, 55, 0.3)', borderRadius: '16px' }} className="animate-pulse"></div>
          ))}
        </div>
      ) : prices.length > 0 ? (
        <>
          {/* Market Metadata */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            height: '40px',
            marginTop: '12px',
            marginBottom: '16px'
          }}>
            <span style={{ fontSize: '14px', color: '#9ca3af' }}>Showing {prices.length} markets for <strong style={{ color: '#ffffff', fontWeight: 500 }}>{query}</strong></span>
            {status?.last_updated && (
              <span style={{ fontSize: '14px', color: '#9ca3af' }}>Last updated: {new Date(status.last_updated).toLocaleString()}</span>
            )}
          </div>

          {/* Market Card Grid */}
          <div className="market-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '24px' }}>
            {prices.map(price => (
              <MarketPriceCard key={price.id} price={price} />
            ))}
          </div>
        </>
      ) : (
        <div style={{ padding: '80px 0', textAlign: 'center' }}>
          <TrendingUp size={48} style={{ color: '#9ca3af', margin: '0 auto 16px auto', opacity: 0.5 }} />
          <h3 style={{ fontSize: '20px', fontWeight: 500, color: '#ffffff', marginBottom: '8px' }}>No prices found</h3>
          <p style={{ color: '#9ca3af' }}>We couldn't find any recent market data for "{query}".</p>
        </div>
      )}
    </div>
  );
}
