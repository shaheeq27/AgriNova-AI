'use client';

import React from 'react';

export interface TimelinePulseProps {
  active?: boolean;
  color?: string;
  className?: string;
}

export function TimelinePulse({
  active = true,
  color = 'var(--color-accent)',
  className = '',
}: TimelinePulseProps) {
  if (!active) return null;

  return (
    <div
      className={className}
      style={{
        position: 'absolute',
        top: 0,
        left: '50%',
        transform: 'translateX(-50%)',
        width: '4px',
        height: '40px',
        borderRadius: '2px',
        background: `linear-gradient(to bottom, transparent, ${color}, transparent)`,
        animation: 'timelinePulseAnim 2.5s ease-in-out infinite',
        pointerEvents: 'none',
      }}
    >
      <style jsx>{`
        @keyframes timelinePulseAnim {
          0% {
            top: 0%;
            opacity: 0;
          }
          20% {
            opacity: 1;
          }
          80% {
            opacity: 1;
          }
          100% {
            top: 100%;
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}

export default TimelinePulse;
