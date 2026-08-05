'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

export default function WeatherCard() {
  const [temp, setTemp] = useState(0);
  const [humidity, setHumidity] = useState(0);
  
  useEffect(() => {
    let t = 0;
    let h = 0;
    const interval = setInterval(() => {
      if (t < 24) { t++; setTemp(t); }
      if (h < 65) { h += 2; setHumidity(h > 65 ? 65 : h); }
      if (t >= 24 && h >= 65) { clearInterval(interval); }
    }, 40);
    return () => clearInterval(interval);
  }, []);

  return (
    <GlassCard glow>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontFamily: 'var(--font-sans, "Inter")' }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '3rem', fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-primary, #e8f5ec)', marginBottom: '8px', fontWeight: 300 }}>
            {temp}°C
          </div>
          <div style={{ color: 'var(--accent-primary, #4ee86a)', fontFamily: 'var(--font-mono, "Space Mono")', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            Partly Cloudy
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', flex: 1, textAlign: 'right' }}>
          <div>
            <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Humidity</div>
            <div style={{ color: 'var(--text-primary, #e8f5ec)', fontFamily: 'var(--font-mono, "Space Mono")' }}>{humidity}%</div>
          </div>
          <div>
            <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Wind</div>
            <div style={{ color: 'var(--text-primary, #e8f5ec)', fontFamily: 'var(--font-mono, "Space Mono")' }}>12 km/h</div>
          </div>
          <div>
            <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Rainfall</div>
            <div style={{ color: 'var(--text-primary, #e8f5ec)', fontFamily: 'var(--font-mono, "Space Mono")' }}>0 mm</div>
          </div>
          <div>
            <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>UV Index</div>
            <div style={{ color: 'var(--text-primary, #e8f5ec)', fontFamily: 'var(--font-mono, "Space Mono")' }}>Moderate</div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}
