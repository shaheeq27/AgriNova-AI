'use client';
import React from 'react';

interface SkeletonProps { width?: string; height?: string; borderRadius?: string; count?: number; gap?: string; }

export default function Skeleton({ width = '100%', height = '20px', borderRadius = '4px', count = 1, gap = '8px' }: SkeletonProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap }}>
      <style>{`@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }`}</style>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} style={{ 
          width, height, borderRadius, 
          background: 'linear-gradient(90deg, var(--surface) 25%, var(--surface-hover) 50%, var(--surface) 75%)',
          backgroundSize: '200% 100%', animation: 'shimmer 1.5s infinite linear' 
        }} />
      ))}
    </div>
  );
}