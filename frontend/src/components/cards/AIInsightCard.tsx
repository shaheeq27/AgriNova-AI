'use client';
import React from 'react';

interface AIInsightCardProps {
  message: string;
}

export default function AIInsightCard({ message }: AIInsightCardProps) {
  return (
    <div style={{
      background: 'var(--surface-glass, rgba(13, 31, 21, 0.7))',
      backdropFilter: 'blur(16px)',
      border: '1px solid var(--border-hover, rgba(78, 232, 106, 0.16))',
      borderRadius: '8px',
      padding: '16px',
      boxShadow: '0 0 12px rgba(78, 232, 106, 0.05)',
      display: 'flex',
      gap: '12px',
      alignItems: 'flex-start'
    }}>
      <div style={{ 
        width: '20px', 
        height: '20px', 
        borderRadius: '50%', 
        background: 'var(--accent-primary, #4ee86a)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        boxShadow: '0 0 8px rgba(78, 232, 106, 0.4)'
      }}>
        {/* Sparkle abstraction */}
        <div style={{ width: '4px', height: '4px', background: '#fff', borderRadius: '50%' }} />
      </div>
      <div>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--accent-primary, #4ee86a)', fontSize: '0.65rem', letterSpacing: '0.1em', marginBottom: '4px' }}>
          AI ADVISOR
        </div>
        <p style={{ color: 'var(--text-primary, #e8f5ec)', fontSize: '0.85rem', margin: 0, lineHeight: 1.4 }}>
          {message}
        </p>
      </div>
    </div>
  );
}
