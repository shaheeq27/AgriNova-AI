'use client';

import React from 'react';

export interface LogoFloatProps {
  children: React.ReactNode;
  duration?: number;
  distance?: number;
  className?: string;
}

export function LogoFloat({
  children,
  duration = 6,
  distance = 12,
  className = '',
}: LogoFloatProps) {
  return (
    <div
      className={className}
      style={{
        display: 'inline-block',
        animation: `logoFloatAnim ${duration}s ease-in-out infinite alternate`,
      }}
    >
      <style jsx>{`
        @keyframes logoFloatAnim {
          0% {
            transform: translateY(0px) rotate(0deg);
          }
          50% {
            transform: translateY(-${distance}px) rotate(1deg);
          }
          100% {
            transform: translateY(0px) rotate(0deg);
          }
        }
      `}</style>
      {children}
    </div>
  );
}

export default LogoFloat;
