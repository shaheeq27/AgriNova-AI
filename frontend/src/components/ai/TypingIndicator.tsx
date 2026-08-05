'use client';
import React from 'react';

export default function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: '4px', alignItems: 'center', height: '24px' }}>
      <style>{`@keyframes typingDot { 0%, 100% { transform: translateY(0); opacity: 0.4; } 50% { transform: translateY(-4px); opacity: 1; } }`}</style>
      {[1,2,3].map(i => (
        <div key={i} style={{ 
          width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--accent-primary)',
          animation: `typingDot 1.4s infinite ease-in-out ${i * 0.15}s` 
        }} />
      ))}
    </div>
  );
}