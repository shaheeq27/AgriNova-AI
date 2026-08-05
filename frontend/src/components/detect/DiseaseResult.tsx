'use client';
import React from 'react';

interface DiseaseResultProps { name: string; pathogen: string; severity: 'low' | 'medium' | 'high'; description: string; }

export default function DiseaseResult({ name, pathogen, severity, description }: DiseaseResultProps) {
  const sevColor = severity === 'high' ? '#e84e4e' : severity === 'medium' ? '#e8b94e' : 'var(--accent-primary)';
  return (
    <div style={{
      backgroundColor: 'var(--surface)', padding: '24px', borderRadius: '16px',
      border: '1px solid var(--border)', animation: 'breatheShadow 4s infinite ease-in-out'
    }}>
      <style>{`@keyframes breatheShadow { 0%, 100% { boxShadow: 0 0 8px rgba(0,0,0,0.2); } 50% { boxShadow: 0 0 20px var(--surface-hover); } }`}</style>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <h2 style={{ fontFamily: 'Playfair Display, serif', fontSize: '28px', color: 'var(--text-primary)', margin: '0 0 4px 0' }}>{name}</h2>
          <div style={{ fontFamily: 'Space Mono', fontSize: '12px', color: 'var(--text-secondary)' }}>PATHOGEN: {pathogen}</div>
        </div>
        <div style={{ padding: '4px 12px', borderRadius: '12px', backgroundColor: 'rgba(255,255,255,0.05)', border: `1px solid ${sevColor}`, color: sevColor, fontSize: '12px', textTransform: 'uppercase' }}>
          {severity} Risk
        </div>
      </div>
      <p style={{ color: 'var(--text-muted)', fontSize: '15px', lineHeight: '1.6', margin: 0 }}>{description}</p>
    </div>
  );
}