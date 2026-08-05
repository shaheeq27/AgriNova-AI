'use client';
import React from 'react';
import { useParticles } from '../../hooks/useParticles';

export default function Fireflies() {
  const particles = useParticles(10);

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none', zIndex: -1 }}>
      <style>{`
        @keyframes blink-firefly {
          0%, 100% { opacity: 0.05; transform: scale(1); }
          50% { opacity: 0.15; transform: scale(1.5); box-shadow: 0 0 8px 2px var(--accent-primary, #4ee86a); }
        }
      `}</style>
      {particles.map(p => (
        <div
          key={p.id}
          style={{
            position: 'absolute',
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            backgroundColor: 'var(--accent-primary, #4ee86a)',
            borderRadius: '50%',
            animation: `blink-firefly ${p.duration * 0.5}s ease-in-out ${p.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
