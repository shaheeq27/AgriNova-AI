'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

interface StatisticsCardProps {
  label: string;
  value: number;
  unit?: string;
  icon?: React.ReactNode;
}

export default function StatisticsCard({ label, value, unit = '', icon }: StatisticsCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let current = 0;
    const increment = Math.ceil(value / 20) || 1;
    const interval = setInterval(() => {
      if (current < value) {
        current += increment;
        if (current > value) current = value;
        setDisplayValue(current);
      } else {
        clearInterval(interval);
      }
    }, 40);
    return () => clearInterval(interval);
  }, [value]);

  return (
    <GlassCard style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {label}
        </div>
        {icon && <div style={{ color: 'var(--accent-primary, #4ee86a)' }}>{icon}</div>}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-primary, #e8f5ec)', fontSize: '2rem', fontWeight: 300 }}>
          {displayValue}
        </div>
        {unit && (
          <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-secondary, #8fb89e)', fontSize: '1rem' }}>
            {unit}
          </div>
        )}
      </div>
    </GlassCard>
  );
}
