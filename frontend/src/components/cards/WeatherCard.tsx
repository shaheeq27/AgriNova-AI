'use client';
import React from 'react';
import GlassCard from './GlassCard';
import { WeatherCurrent } from '@/lib/api';
import { Cloud, Droplets, Wind, CloudRain, Sun } from 'lucide-react';

interface WeatherCardProps {
  farmName: string;
  location: string;
  current: WeatherCurrent | null;
  error?: boolean;
  onClick?: () => void;
  selected?: boolean;
}

export default function WeatherCard({ farmName, location, current, error, onClick, selected }: WeatherCardProps) {
  return (
    <div
      onClick={onClick}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        opacity: error ? 0.7 : 1,
        transition: 'all 0.2s',
        width: '100%',
        minHeight: '220px',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <GlassCard glow={selected} style={{ flex: 1, borderRadius: '18px', padding: 0 }} padding="none">
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          fontFamily: 'var(--font-sans, "Inter")',
          padding: '24px',
          height: '100%',
          boxSizing: 'border-box'
        }}>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <div style={{ color: 'var(--text-primary, #e8f5ec)', fontSize: '22px', fontWeight: 700, marginBottom: '4px' }}>
                {farmName}
              </div>
              <div style={{ color: 'var(--text-muted, #9ca3af)', fontSize: '14px' }}>
                {location}
              </div>
            </div>
            {!error && current && (
               <div style={{ color: selected ? 'var(--accent-primary, #4ee86a)' : 'var(--text-muted, #9ca3af)' }}>
                 {current.temperature !== null && current.temperature > 20 ? <Sun size={24} /> : <Cloud size={24} />}
               </div>
            )}
          </div>

          {error ? (
            <div style={{ color: 'var(--error, #ef4444)', fontSize: '14px', paddingTop: '20px' }}>
              Weather unavailable
            </div>
          ) : current ? (
            <>
              <div style={{ marginTop: '20px' }}>
                <div style={{ fontSize: '48px', fontWeight: 700, color: 'var(--text-primary, #e8f5ec)', lineHeight: 1, marginBottom: '4px' }}>
                  {current.temperature !== null ? `${Math.round(current.temperature)}°C` : '--'}
                </div>
                <div style={{ color: 'var(--accent-primary, #4ee86a)', fontSize: '15px', fontWeight: 600 }}>
                  {current.condition || 'Clear'}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '16px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '20px', marginTop: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }} title="Humidity">
                  <Droplets size={14} style={{ color: '#60a5fa' }} />
                  <span style={{ color: 'var(--text-primary, #e8f5ec)', fontSize: '14px' }}>
                    {current.humidity !== null ? `${Math.round(current.humidity)}%` : '--'}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }} title="Rainfall">
                  <CloudRain size={14} style={{ color: '#93c5fd' }} />
                  <span style={{ color: 'var(--text-primary, #e8f5ec)', fontSize: '14px' }}>
                    {current.rainfall !== null ? `${current.rainfall}mm` : '--'}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }} title="Wind Speed">
                  <Wind size={14} style={{ color: '#cbd5e1' }} />
                  <span style={{ color: 'var(--text-primary, #e8f5ec)', fontSize: '14px' }}>
                    {current.wind_speed !== null ? `${Math.round(current.wind_speed)}km/h` : '--'}
                  </span>
                </div>
              </div>
            </>
          ) : (
             <div style={{ fontSize: '14px', paddingTop: '20px', color: 'var(--text-muted)' }}>
               Loading weather...
             </div>
          )}

        </div>
      </GlassCard>
    </div>
  );
}
