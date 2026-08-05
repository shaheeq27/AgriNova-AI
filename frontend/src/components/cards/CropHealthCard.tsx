'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';
import CircularProgress from '../charts/CircularProgress';

export default function CropHealthCard() {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => setPulse(p => !p), 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <GlassCard>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 style={{ fontFamily: 'var(--font-serif, "Playfair Display")', color: 'var(--text-primary, #e8f5ec)', margin: '0 0 8px 0', fontSize: '1.25rem', fontWeight: 400 }}>
            Crop Health Overview
          </h3>
          <p style={{ color: 'var(--text-secondary, #8fb89e)', fontSize: '0.85rem', margin: 0, maxWidth: '200px', lineHeight: 1.5 }}>
            Overall field vitality is optimal. No immediate actions required.
          </p>
          
          <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
            <span style={{ 
              padding: '4px 8px', 
              borderRadius: '4px', 
              background: 'var(--accent-dim, #14402a)', 
              color: 'var(--accent-primary, #4ee86a)',
              fontFamily: 'var(--font-mono, "Space Mono")',
              fontSize: '0.7rem',
              border: '1px solid var(--border, rgba(78, 232, 106, 0.08))',
              transition: 'all 1s ease',
              boxShadow: pulse ? '0 0 8px rgba(78, 232, 106, 0.2)' : 'none'
            }}>
              VITALITY: HIGH
            </span>
          </div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div style={{ color: 'var(--text-muted, #5a8a6d)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '8px', fontFamily: 'var(--font-mono, "Space Mono")' }}>
            AVG HEALTH
          </div>
          <CircularProgress value={92} size={100} strokeWidth={6} />
        </div>
      </div>
    </GlassCard>
  );
}
