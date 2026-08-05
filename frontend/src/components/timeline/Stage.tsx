'use client';
import React from 'react';
import TimelineNode from './TimelineNode';

interface StageProps { name: string; dateRange: string; status: 'active' | 'completed' | 'upcoming'; description?: string; children?: React.ReactNode; }

export default function Stage({ name, dateRange, status, description, children }: StageProps) {
  return (
    <div style={{ 
      position: 'relative', backgroundColor: 'var(--surface)', padding: '24px', borderRadius: '12px',
      border: '1px solid var(--border)', transition: 'all 0.3s ease',
      opacity: status === 'upcoming' ? 0.6 : 1,
      boxShadow: status === 'active' ? 'inset 0 0 20px var(--accent-glow)' : 'none'
    }}>
      <TimelineNode status={status} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <h3 style={{ fontFamily: 'Playfair Display, serif', fontSize: '20px', margin: 0, color: status === 'active' ? 'var(--accent-primary)' : 'var(--text-primary)' }}>{name}</h3>
        <span style={{ fontFamily: 'Space Mono', fontSize: '12px', color: 'var(--text-secondary)' }}>{dateRange}</span>
      </div>
      {description && <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '16px' }}>{description}</p>}
      {children && <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>{children}</div>}
    </div>
  );
}