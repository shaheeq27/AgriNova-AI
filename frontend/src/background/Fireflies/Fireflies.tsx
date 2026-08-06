'use client';

import React from 'react';
import { useParticles } from '@/hooks/useParticles';
import { cn } from '@/utils/cn';
import styles from './Fireflies.module.css';

export interface FirefliesProps {
  count?: number;
  className?: string;
}

export function Fireflies({ count = 10, className }: FirefliesProps) {
  const particles = useParticles(count);

  return (
    <div className={cn(styles.container, className)}>
      {particles.map((p) => (
        <div
          key={p.id}
          className={cn(styles.particle, styles.blink)}
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            animationDuration: `${p.duration * 0.5}s`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

export default Fireflies;
