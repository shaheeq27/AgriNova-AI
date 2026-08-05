'use client';
import React from 'react';

export default function LoadingScreen() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px' }}>
      <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
        {[1,2,3,4].map(i => (
          <div key={i} style={{ 
            width: '4px', height: '20px', backgroundColor: 'var(--accent-primary)', borderRadius: '2px',
            animation: `barRise 1.2s infinite ease-in-out ${i * 0.1}s` 
          }}>
            <style>{`@keyframes barRise { 0%, 100% { transform: scaleY(0.3); opacity: 0.4; } 50% { transform: scaleY(1); opacity: 1; } }`}</style>
          </div>
        ))}
      </div>
      <div style={{ fontFamily: 'Space Mono', color: 'var(--text-secondary)', fontSize: '12px' }}>Loading...</div>
    </div>
  );
}