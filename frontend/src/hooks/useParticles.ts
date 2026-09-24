'use client';
import { useMemo } from 'react';

const generateParticles = (count: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `particle-${i}`,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 2 + 1,
    delay: Math.random() * 5,
    duration: Math.random() * 5 + 5,
  }));
};

export function useParticles(count: number = 20) {
  return useMemo(() => generateParticles(count), [count]);
}
