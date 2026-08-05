'use client';
import React, { useState, MouseEvent } from 'react';

export function useRipple(): { onMouseDown: (e: MouseEvent<HTMLElement>) => void; ripples: React.ReactNode } {
  const [ripplesList, setRipplesList] = useState<{ x: number; y: number; id: number }[]>([]);

  const onMouseDown = (e: MouseEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple = { x, y, id: Date.now() };
    setRipplesList((prev) => [...prev, newRipple]);

    setTimeout(() => {
      setRipplesList((prev) => prev.filter((r) => r.id !== newRipple.id));
    }, 600); // match animation duration
  };

  const ripples = (
    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, overflow: 'hidden', pointerEvents: 'none', borderRadius: 'inherit' }}>
      <style>{`
        @keyframes ripple-effect {
          0% { transform: scale(0); opacity: 0.35; }
          100% { transform: scale(3); opacity: 0; }
        }
      `}</style>
      {ripplesList.map((ripple) => (
        <div
          key={ripple.id}
          style={{
            position: 'absolute',
            left: ripple.x - 10,
            top: ripple.y - 10,
            width: 20,
            height: 20,
            background: 'var(--accent-primary, #4ee86a)',
            borderRadius: '50%',
            opacity: 0,
            animation: 'ripple-effect 600ms linear forwards',
          }}
        />
      ))}
    </div>
  );

  return { onMouseDown, ripples };
}
