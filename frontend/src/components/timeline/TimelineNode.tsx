'use client';
import React from 'react';

interface TimelineNodeProps { status: 'active' | 'completed' | 'upcoming'; }

export default function TimelineNode({ status }: TimelineNodeProps) {
  const getStyles = () => {
    switch(status) {
      case 'active': return { bg: 'var(--accent-primary)', border: 'none', shadow: '0 0 12px var(--accent-glow)' };
      case 'completed': return { bg: 'var(--accent-muted)', border: 'none', shadow: 'none' };
      case 'upcoming': return { bg: 'transparent', border: '2px solid var(--text-muted)', shadow: 'none' };
    }
  };
  const { bg, border, shadow } = getStyles();

  return (
    <div style={{ 
      position: 'absolute', left: '-26px', top: '24px', width: '16px', height: '16px', borderRadius: '50%',
      backgroundColor: bg, border: border, boxShadow: shadow, zIndex: 2,
      animation: status === 'active' ? 'nodeBreathe 2s infinite ease-in-out' : 'none'
    }}>
      <style>{`@keyframes nodeBreathe { 0%, 100% { transform: scale(1); boxShadow: 0 0 8px var(--accent-glow); } 50% { transform: scale(1.2); boxShadow: 0 0 16px var(--accent-primary); } }`}</style>
    </div>
  );
}