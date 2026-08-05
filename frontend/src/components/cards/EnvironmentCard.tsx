'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

export default function EnvironmentCard() {
  const [time, setTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <GlassCard style={{ overflow: 'hidden' }}>
      {/* Subtle particle effect abstraction */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
        background: 'radial-gradient(circle at 50% 50%, rgba(78, 232, 106, 0.03) 0%, transparent 70%)',
        pointerEvents: 'none'
      }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h3 style={{ fontFamily: 'var(--font-serif, "Playfair Display")', color: 'var(--text-primary, #e8f5ec)', margin: 0, fontSize: '1.25rem', fontWeight: 400 }}>
          Environmental Intelligence
        </h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-primary, #4ee86a)', boxShadow: '0 0 8px var(--accent-primary, #4ee86a)' }} />
          <span style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--accent-primary, #4ee86a)', fontSize: '0.7rem', letterSpacing: '0.1em' }}>
            ACTIVE MONITORING
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        <div style={{ flex: 1, background: 'var(--background-subtle, #081410)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border, rgba(78, 232, 106, 0.08))' }}>
          <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Temperature</div>
          <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-primary, #e8f5ec)', fontSize: '1.5rem' }}>24.5°C</div>
        </div>
        <div style={{ flex: 1, background: 'var(--background-subtle, #081410)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border, rgba(78, 232, 106, 0.08))' }}>
          <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Humidity</div>
          <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-primary, #e8f5ec)', fontSize: '1.5rem' }}>68%</div>
        </div>
        <div style={{ flex: 1, background: 'var(--background-subtle, #081410)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border, rgba(78, 232, 106, 0.08))' }}>
          <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Soil Moisture</div>
          <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-primary, #e8f5ec)', fontSize: '1.5rem' }}>42%</div>
        </div>
      </div>

      <div style={{ marginTop: '24px', fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', display: 'flex', justifyContent: 'flex-end' }}>
        LOCAL TIME: {time}
      </div>
    </GlassCard>
  );
}
