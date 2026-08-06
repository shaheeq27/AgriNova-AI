'use client';

import React from 'react';
import GlassCard from './GlassCard';
import StatusBadge from '../status/StatusBadge';
import Subtitle from '../typography/Subtitle';
import Label from '../typography/Label';

export interface StatusCardProps {
  title: string;
  status: 'active' | 'warning' | 'critical' | 'info' | 'neutral' | 'optimal';
  statusLabel: string;
  description?: string;
  updatedAt?: string;
  icon?: React.ReactNode;
  className?: string;
}

export default function StatusCard({
  title,
  status,
  statusLabel,
  description,
  updatedAt,
  icon,
  className = '',
}: StatusCardProps) {
  return (
    <GlassCard className={className} padding="20px">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {icon && <div style={{ color: 'var(--color-accent)' }}>{icon}</div>}
          <span style={{ fontFamily: 'var(--font-playfair)', fontSize: '18px', fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {title}
          </span>
        </div>
        <StatusBadge status={status} label={statusLabel} pulse={status === 'active' || status === 'critical'} />
      </div>

      {description && <Subtitle style={{ fontSize: '14px', marginBottom: '8px' }}>{description}</Subtitle>}
      {updatedAt && <Label style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Updated {updatedAt}</Label>}
    </GlassCard>
  );
}
