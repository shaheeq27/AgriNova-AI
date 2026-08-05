'use client';
import React, { useEffect, useState } from 'react';

interface CircularProgressProps {
  value: number; // 0-100
  size?: number; // px, default 80
  strokeWidth?: number; // default 6
  color?: string; // default accent-primary
  label?: string;
  animated?: boolean; // default true
}

export default function CircularProgress({ 
  value, 
  size = 80, 
  strokeWidth = 6, 
  color = 'var(--accent-primary, #4ee86a)',
  label,
  animated = true 
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const [offset, setOffset] = useState(circumference);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => {
        setOffset(circumference - (value / 100) * circumference);
      }, 100);
      return () => clearTimeout(timer);
    } else {
      setOffset(circumference - (value / 100) * circumference);
    }
  }, [value, circumference, animated]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--surface-hover, #122a1c)"
          strokeWidth={strokeWidth}
        />
        {/* Foreground arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: animated ? 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)' : 'none' }}
        />
      </svg>
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'var(--font-mono, "Space Mono")',
        color: 'var(--text-primary, #e8f5ec)',
        fontSize: size * 0.25,
      }}>
        {value}%
      </div>
      {label && (
        <div style={{ marginTop: '8px', fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--text-muted, #5a8a6d)', fontSize: '0.7rem', textTransform: 'uppercase' }}>
          {label}
        </div>
      )}
    </div>
  );
}
