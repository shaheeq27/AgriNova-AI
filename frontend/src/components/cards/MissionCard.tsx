'use client';
import React from 'react';
import GlassCard from './GlassCard';

interface MissionCardProps {
  title: string;
  description: string;
  progress: number;
}

export default function MissionCard({ title, description, progress }: MissionCardProps) {
  return (
    <GlassCard glow style={{ padding: '20px' }}>
      <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--accent-primary, #4ee86a)', fontSize: '0.65rem', letterSpacing: '0.1em', marginBottom: '8px' }}>
        MISSION OBJECTIVE
      </div>
      <h4 style={{ fontFamily: 'var(--font-serif, "Playfair Display")', color: 'var(--text-primary, #e8f5ec)', margin: '0 0 8px 0', fontSize: '1.1rem', fontWeight: 500 }}>
        {title}
      </h4>
      <p style={{ color: 'var(--text-secondary, #8fb89e)', fontSize: '0.8rem', margin: '0 0 16px 0', lineHeight: 1.5 }}>
        {description}
      </p>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ flex: 1, height: '4px', background: 'var(--background-subtle, #081410)', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ 
            height: '100%', 
            width: `${progress}%`, 
            background: 'var(--text-secondary, #8fb89e)',
            transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)'
          }} />
        </div>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-muted, #5a8a6d)', fontSize: '0.7rem' }}>
          {progress}%
        </div>
      </div>
    </GlassCard>
  );
}
