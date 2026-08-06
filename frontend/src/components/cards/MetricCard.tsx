'use client';

import React from 'react';
import GlassCard from './GlassCard';
import Metric from '../typography/Metric';
import Label from '../typography/Label';

export interface MetricCardProps {
  label: string;
  value: number | string;
  suffix?: string;
  prefix?: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export default function MetricCard({
  label,
  value,
  suffix = '',
  prefix = '',
  change,
  changeType = 'positive',
  icon,
  className = '',
  glow = false,
}: MetricCardProps) {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'var(--color-success)';
      case 'negative':
        return 'var(--color-error)';
      case 'neutral':
      default:
        return 'var(--color-text-muted)';
    }
  };

  const formattedValue = typeof value === 'number' ? value : `${prefix}${value}`;

  return (
    <GlassCard glow={glow} className={className} padding="20px">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <Label>{label}</Label>
        {icon && <div style={{ color: 'var(--color-accent)' }}>{icon}</div>}
      </div>

      <Metric value={formattedValue} unit={suffix} />

      {change && (
        <div style={{ marginTop: '8px', fontSize: '12px', color: getChangeColor(), display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>{changeType === 'positive' ? '↑' : changeType === 'negative' ? '↓' : '•'}</span>
          <span>{change}</span>
        </div>
      )}
    </GlassCard>
  );
}
