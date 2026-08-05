'use client';
import React, { useEffect, useState } from 'react';

interface TimelineCardProps {
  stageName: string;
  dateRange: string;
  status: 'completed' | 'active' | 'upcoming';
}

export default function TimelineCard({ stageName, dateRange, status }: TimelineCardProps) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    if (status === 'active') {
      const interval = setInterval(() => setPulse(p => !p), 2000);
      return () => clearInterval(interval);
    }
  }, [status]);

  const getStatusStyles = () => {
    switch (status) {
      case 'completed':
        return {
          bg: 'var(--surface-glass, rgba(13, 31, 21, 0.7))',
          border: 'var(--border, rgba(78, 232, 106, 0.08))',
          text: 'var(--text-muted, #5a8a6d)',
          accent: 'var(--accent-muted, #1a5a3a)',
          glow: 'none'
        };
      case 'active':
        return {
          bg: 'var(--surface, #0d1f15)',
          border: 'var(--border-hover, rgba(78, 232, 106, 0.16))',
          text: 'var(--text-primary, #e8f5ec)',
          accent: 'var(--accent-primary, #4ee86a)',
          glow: pulse ? '0 0 16px rgba(78, 232, 106, 0.15)' : '0 0 4px rgba(78, 232, 106, 0.05)'
        };
      case 'upcoming':
        return {
          bg: 'var(--background-subtle, #081410)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          text: 'var(--text-secondary, #8fb89e)',
          accent: '#333',
          glow: 'none'
        };
    }
  };

  const styles = getStatusStyles();

  return (
    <div style={{
      background: styles.bg,
      border: `1px solid ${styles.border}`,
      borderRadius: '8px',
      padding: '16px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      boxShadow: styles.glow,
      transition: 'all 1s ease',
      position: 'relative'
    }}>
      <div style={{
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        background: styles.accent,
        boxShadow: status === 'active' ? `0 0 8px ${styles.accent}` : 'none'
      }} />
      
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: 'var(--font-serif, "Playfair Display")', color: styles.text, fontSize: '1.1rem', marginBottom: '4px' }}>
          {stageName}
        </div>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-muted, #5a8a6d)', fontSize: '0.75rem' }}>
          {dateRange}
        </div>
      </div>
      
      <div style={{
        fontFamily: 'var(--font-mono, "Space Mono")',
        fontSize: '0.65rem',
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        color: styles.accent,
        padding: '4px 8px',
        borderRadius: '4px',
        background: status === 'active' ? 'var(--accent-dim, #14402a)' : 'transparent',
        border: status === 'active' ? `1px solid var(--border, rgba(78, 232, 106, 0.08))` : 'none'
      }}>
        {status}
      </div>
    </div>
  );
}
