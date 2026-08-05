'use client';
import React from 'react';
import { useAnimation } from '../../hooks/useAnimation';

interface CircleFillProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  bgColor?: string;
  children?: React.ReactNode;
  duration?: number;
}

export default function CircleFill({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  color = 'var(--accent-primary, #4ee86a)',
  bgColor = 'var(--surface, #0d1f15)',
  children,
  duration = 1000,
}: CircleFillProps) {
  const { ref, isVisible } = useAnimation();
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const percent = Math.max(0, Math.min(value / max, 1));
  const offset = isVisible ? circumference - percent * circumference : circumference;

  return (
    <div ref={ref} style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={bgColor}
          strokeWidth={strokeWidth}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="none"
          style={{ transition: `stroke-dashoffset ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)` }}
        />
      </svg>
      {children && (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {children}
        </div>
      )}
    </div>
  );
}
