'use client';
import React from 'react';
import { useParticles } from '../../hooks/useParticles';

export default function WindLines() {
  const particles = useParticles(4);

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none', zIndex: -1, overflow: 'hidden' }}>
      <style>{`
        @keyframes drift-wind {
          0% { transform: translateX(-100%); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateX(100vw); opacity: 0; }
        }
      `}</style>
      {particles.map(p => (
        <div
          key={p.id}
          style={{
            position: 'absolute',
            top: `${p.y}%`,
            left: 0,
            width: `${60 + p.size * 20}px`,
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(78, 232, 106, 0.03), transparent)',
            animation: `drift-wind ${p.duration * 2 + 10}s linear ${p.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
