'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

interface DiseaseCardProps {
  diseaseName: string;
  confidence: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
}

export default function DiseaseCard({ diseaseName, confidence, severity, description }: DiseaseCardProps) {
  const [displayedConf, setDisplayedConf] = useState(0);
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    let c = 0;
    const interval = setInterval(() => {
      if (c < confidence) {
        c += Math.ceil((confidence - c) / 5) || 1;
        if (c > confidence) c = confidence;
        setDisplayedConf(c);
      } else {
        clearInterval(interval);
      }
    }, 50);
    return () => clearInterval(interval);
  }, [confidence]);

  useEffect(() => {
    if (severity === 'CRITICAL') {
      const interval = setInterval(() => setPulse(p => !p), 5000);
      return () => clearInterval(interval);
    }
  }, [severity]);

  const severityColor = severity === 'CRITICAL' ? '#ff4d4d' : severity === 'HIGH' ? '#ff9900' : 'var(--accent-primary, #4ee86a)';

  return (
    <GlassCard style={{ borderLeft: `3px solid ${severityColor}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h4 style={{ fontFamily: 'var(--font-serif, "Playfair Display")', color: 'var(--text-primary, #e8f5ec)', margin: 0, fontSize: '1.25rem', fontWeight: 500 }}>
          {diseaseName}
        </h4>
        <div style={{ 
          padding: '4px 8px', 
          borderRadius: '4px', 
          background: severity === 'CRITICAL' ? 'rgba(255, 77, 77, 0.1)' : 'var(--accent-dim, #14402a)', 
          color: severityColor,
          fontFamily: 'var(--font-mono, "Space Mono")',
          fontSize: '0.7rem',
          border: `1px solid ${severity === 'CRITICAL' ? 'rgba(255, 77, 77, 0.3)' : 'var(--border, rgba(78, 232, 106, 0.08))'}`,
          transition: 'all 1s ease',
          boxShadow: pulse ? `0 0 12px ${severityColor}40` : 'none'
        }}>
          {severity}
        </div>
      </div>
      
      <p style={{ color: 'var(--text-secondary, #8fb89e)', fontSize: '0.85rem', margin: '0 0 20px 0', lineHeight: 1.6 }}>
        {description}
      </p>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ flex: 1, height: '4px', background: 'var(--background-subtle, #081410)', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ 
            height: '100%', 
            width: `${displayedConf}%`, 
            background: 'var(--accent-primary, #4ee86a)',
            transition: 'width 0.1s linear'
          }} />
        </div>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--accent-primary, #4ee86a)', fontSize: '0.8rem' }}>
          {displayedConf}% CONFIDENCE
        </div>
      </div>
    </GlassCard>
  );
}
