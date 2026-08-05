'use client';
import React, { useEffect, useState } from 'react';

interface ConfidenceProps { value: number; label?: string; animated?: boolean; }

export default function Confidence({ value, label = 'CONFIDENCE', animated = true }: ConfidenceProps) {
  const [displayVal, setDisplayVal] = useState(animated ? 0 : value);
  useEffect(() => {
    if (!animated) return;
    let start = 0;
    const duration = 1500;
    const stepTime = Math.abs(Math.floor(duration / value));
    const timer = setInterval(() => {
      start += 1;
      setDisplayVal(start);
      if (start >= value) clearInterval(timer);
    }, stepTime);
    return () => clearInterval(timer);
  }, [value, animated]);

  const isHigh = value >= 90;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{ 
        fontFamily: 'Space Mono', fontSize: '48px', color: isHigh ? 'var(--accent-primary)' : 'var(--text-primary)',
        textShadow: isHigh ? '0 0 16px var(--accent-glow)' : 'none'
      }}>
        {displayVal}%
      </div>
      <div style={{ fontFamily: 'Inter', fontSize: '12px', color: 'var(--text-muted)', letterSpacing: '2px' }}>{label}</div>
    </div>
  );
}