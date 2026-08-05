'use client';
import React from 'react';

export default function SplashScreen() {
  return (
    <div style={{ 
      width: '100vw', height: '100vh', backgroundColor: 'var(--background)',
      display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 9999
    }}>
      <style>{`
        @keyframes breatheLogo { 0%, 100% { filter: drop-shadow(0 0 8px var(--accent-glow)); transform: scale(1); } 50% { filter: drop-shadow(0 0 24px var(--accent-primary)); transform: scale(1.02); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
      `}</style>
      <h1 style={{ 
        fontFamily: 'Playfair Display, serif', fontSize: '48px', color: 'var(--text-primary)',
        animation: 'breatheLogo 4s infinite ease-in-out', margin: '0 0 16px 0'
      }}>AgriNova</h1>
      <p style={{ 
        fontFamily: 'Inter', fontSize: '16px', color: 'var(--text-secondary)',
        animation: 'fadeIn 2s ease-out 0.5s both', margin: '0 0 48px 0', letterSpacing: '0.05em'
      }}>Where Nature Meets Intelligence</p>
      <div style={{ display: 'flex', gap: '8px' }}>
        {[1,2,3].map(i => (
          <div key={i} style={{ 
            width: '6px', height: '24px', backgroundColor: 'var(--accent-primary)', borderRadius: '3px',
            animation: `pulseBar 1s infinite ease-in-out ${i * 0.15}s` 
          }}>
            <style>{`@keyframes pulseBar { 0%, 100% { transform: scaleY(0.5); opacity: 0.5; } 50% { transform: scaleY(1); opacity: 1; } }`}</style>
          </div>
        ))}
      </div>
    </div>
  );
}