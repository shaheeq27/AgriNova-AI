'use client';
import React from 'react';

interface PrescriptionProps { treatments: string[]; }

export default function Prescription({ treatments }: PrescriptionProps) {
  return (
    <div style={{ backgroundColor: 'var(--accent-dim)', padding: '20px', borderRadius: '12px', borderLeft: '4px solid var(--accent-primary)' }}>
      <h3 style={{ fontFamily: 'Inter', fontSize: '16px', color: 'var(--accent-primary)', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span>📋</span> Recommended Action Plan
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {treatments.map((t, i) => (
          <div key={i} style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
            <div style={{ width: '20px', height: '20px', borderRadius: '50%', backgroundColor: 'var(--accent-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: '2px' }}>
              <span style={{ color: '#000', fontSize: '12px' }}>✓</span>
            </div>
            <span style={{ color: 'var(--text-primary)', fontSize: '14px', lineHeight: '1.5' }}>{t}</span>
          </div>
        ))}
      </div>
    </div>
  );
}