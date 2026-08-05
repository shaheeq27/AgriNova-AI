'use client';
import React from 'react';
import { useParticles } from '../../hooks/useParticles';

export default function SeedParticles() {
  const particles = useParticles(15);

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none', zIndex: -1, overflow: 'hidden' }}>
      <style>{`
        @keyframes float-seed {
          0% { transform: translateY(0) rotate(0deg); opacity: 0.1; }
          50% { opacity: 0.2; }
          100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
      `}</style>
      {particles.map(p => (
        <div
          key={p.id}
          style={{
            position: 'absolute',
            left: `${p.x}%`,
            bottom: `${p.y - 100}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            backgroundColor: 'var(--accent-muted, #1a5a3a)',
            borderRadius: '50%',
            opacity: 0,
            animation: `float-seed ${p.duration}s linear ${p.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
