'use client';
import React from 'react';

export default function TimelineLine() {
  return (
    <div style={{ position: 'absolute', left: '16px', top: 0, bottom: 0, width: '2px', backgroundColor: 'var(--accent-dim)', zIndex: 1, overflow: 'hidden' }}>
      <style>{`@keyframes linePulse { 0% { transform: translateY(100%); } 100% { transform: translateY(-100%); } }`}</style>
      <div style={{ 
        width: '100%', height: '30%', background: 'linear-gradient(to top, transparent, var(--accent-primary), transparent)',
        animation: 'linePulse 4s infinite linear' 
      }} />
    </div>
  );
}