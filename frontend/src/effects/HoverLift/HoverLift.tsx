'use client';

import React, { useState } from 'react';

export interface HoverLiftProps {
  children: React.ReactNode;
  liftPx?: number;
  durationMs?: number;
  glow?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export function HoverLift({
  children,
  liftPx = 4,
  durationMs = 250,
  glow = false,
  className = '',
  style = {},
}: HoverLiftProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        transform: isHovered ? `translateY(-${liftPx}px)` : 'translateY(0)',
        boxShadow: isHovered && glow ? '0 8px 24px rgba(78, 232, 106, 0.15)' : undefined,
        transition: `transform ${durationMs}ms cubic-bezier(0.16, 1, 0.3, 1), box-shadow ${durationMs}ms ease`,
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export default HoverLift;
