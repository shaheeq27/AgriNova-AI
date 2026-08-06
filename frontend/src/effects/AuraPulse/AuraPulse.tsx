'use client';

import React from 'react';

export interface AuraPulseProps {
  children: React.ReactNode;
  color?: string;
  size?: number;
  className?: string;
}

export function AuraPulse({
  children,
  color = 'rgba(78, 232, 106, 0.25)',
  size = 120,
  className = '',
}: AuraPulseProps) {
  return (
    <div
      className={className}
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          width: `${size}%`,
          height: `${size}%`,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
          animation: 'auraPulseAnim 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />
      <style jsx>{`
        @keyframes auraPulseAnim {
          0%, 100% {
            transform: scale(0.95);
            opacity: 0.4;
          }
          50% {
            transform: scale(1.15);
            opacity: 0.8;
          }
        }
      `}</style>
      <div style={{ position: 'relative', zIndex: 1 }}>{children}</div>
    </div>
  );
}

export default AuraPulse;
