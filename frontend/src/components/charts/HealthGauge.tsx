'use client';
import React, { useEffect, useState } from 'react';

interface HealthGaugeProps {
  value: number; // 0-100
  size?: number; // width in px, height will be half
  strokeWidth?: number;
}

export default function HealthGauge({ value, size = 200, strokeWidth = 12 }: HealthGaugeProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * Math.PI; // Semi-circle
  const [offset, setOffset] = useState(circumference);

  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(circumference - (value / 100) * circumference);
    }, 100);
    return () => clearTimeout(timer);
  }, [value, circumference]);

  const getColor = () => {
    if (value > 80) return 'var(--accent-primary, #4ee86a)';
    if (value > 50) return '#ffcc00';
    return '#ff4d4d';
  };

  const color = getColor();

  return (
    <div style={{ position: 'relative', width: size, height: size / 2, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <svg width={size} height={size / 2} style={{ overflow: 'hidden' }}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth/2} ${size/2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth/2} ${size/2}`}
          fill="none"
          stroke="var(--surface-hover, #122a1c)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Foreground arc */}
        <path
          d={`M ${strokeWidth/2} ${size/2} A ${radius} ${radius} 0 0 1 ${size - strokeWidth/2} ${size/2}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.5s ease' }}
        />
      </svg>
      <div style={{
        position: 'absolute',
        bottom: 0,
        fontFamily: 'var(--font-mono, "Space Mono")',
        color: 'var(--text-primary, #e8f5ec)',
        fontSize: '2rem',
        lineHeight: 1
      }}>
        {value}
      </div>
    </div>
  );
}
