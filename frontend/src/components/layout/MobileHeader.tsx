'use client';
import React from 'react';

export default function MobileHeader() {
  return (
    <header style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '16px 24px', backgroundColor: 'var(--surface-glass)', backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--border)', position: 'sticky', top: 0, zIndex: 40
    }}>
      <style>{`
        @media (min-width: 768px) { header { display: none !important; } }
        @keyframes breathe { 0% { text-shadow: 0 0 4px var(--accent-glow); } 50% { text-shadow: 0 0 12px var(--accent-primary); } 100% { text-shadow: 0 0 4px var(--accent-glow); } }
      `}</style>
      <div style={{ fontFamily: 'Playfair Display, serif', fontSize: '20px', color: 'var(--text-primary)', animation: 'breathe 4s infinite ease-in-out' }}>
        AgriNova AI
      </div>
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <span style={{ color: 'var(--text-secondary)' }}>☁️</span>
        <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: '2px solid var(--accent-primary)', backgroundColor: 'var(--accent-dim)' }} />
      </div>
    </header>
  );
}