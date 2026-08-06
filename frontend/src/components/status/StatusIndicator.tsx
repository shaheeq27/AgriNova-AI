'use client';

import React from 'react';
import PulseDot from './PulseDot';

export interface StatusIndicatorProps {
  status: 'active' | 'warning' | 'critical' | 'info' | 'neutral' | 'optimal';
  label: string;
  sublabel?: string;
  icon?: React.ReactNode;
}

export default function StatusIndicator({ status, label, sublabel, icon }: StatusIndicatorProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <PulseDot status={status} size={8} />
      {icon && <span style={{ color: 'var(--color-accent)' }}>{icon}</span>}
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
          {label}
        </span>
        {sublabel && (
          <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
            {sublabel}
          </span>
        )}
      </div>
    </div>
  );
}
