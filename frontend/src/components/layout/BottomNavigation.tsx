'use client';
import React, { useState } from 'react';

const NAV_ITEMS = [
  { label: 'Dashboard', href: '/dashboard', icon: '⊞' },
  { label: 'Timeline', href: '/lifecycle', icon: '⏱' },  
  { label: 'Detect', href: '/detect', icon: '◎' },
  { label: 'AI Advisor', href: '/advisor', icon: '🧠' },
];

export default function BottomNavigation() {
  const [active, setActive] = useState('/dashboard');
  return (
    <div style={{
      position: 'fixed', bottom: 0, left: 0, right: 0, height: '64px',
      backgroundColor: 'var(--surface)', display: 'flex', justifyContent: 'space-around',
      alignItems: 'center', borderTop: '1px solid var(--border)', zIndex: 50
    }}>
      <style>{`
        @media (min-width: 768px) { .mobile-nav { display: none !important; } }
        .nav-item { transition: all 0.3s ease; }
        .nav-item.active { color: var(--accent-primary); text-shadow: 0 0 8px var(--accent-glow); transform: translateY(-2px); }
        .nav-item:not(.active) { color: var(--text-muted); }
      `}</style>
      <div className="mobile-nav" style={{ display: 'flex', width: '100%', justifyContent: 'space-around' }}>
        {NAV_ITEMS.map(item => (
          <div key={item.href} onClick={() => setActive(item.href)}
               className={`nav-item ${active === item.href ? 'active' : ''}`}
               style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', fontSize: '12px', fontFamily: 'Inter' }}>
            <span style={{ fontSize: '20px', marginBottom: '4px' }}>{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}