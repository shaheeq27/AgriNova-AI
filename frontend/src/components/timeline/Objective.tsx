'use client';
import React from 'react';

interface ObjectiveProps { label: string; completed?: boolean; }

export default function Objective({ label, completed }: ObjectiveProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px', borderRadius: '6px', backgroundColor: 'var(--surface-hover)' }}>
      <div style={{ 
        width: '18px', height: '18px', borderRadius: '4px', border: completed ? 'none' : '1px solid var(--text-muted)',
        backgroundColor: completed ? 'var(--accent-primary)' : 'transparent',
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        {completed && <span style={{ color: '#000', fontSize: '12px' }}>✓</span>}
      </div>
      <span style={{ color: completed ? 'var(--text-secondary)' : 'var(--text-primary)', fontSize: '14px', textDecoration: completed ? 'line-through' : 'none' }}>
        {label}
      </span>
    </div>
  );
}