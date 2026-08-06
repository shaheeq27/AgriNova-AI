'use client';

import React from 'react';
import { useParticles } from '@/hooks/useParticles';
import { cn } from '@/utils/cn';
import styles from './SeedParticles.module.css';

export interface SeedParticlesProps {
  count?: number;
  className?: string;
}

export function SeedParticles({ count = 15, className }: SeedParticlesProps) {
  const particles = useParticles(count);

  return (
    <div className={cn(styles.container, className)}>
      {particles.map((p) => (
        <div
          key={p.id}
          className={styles.seed}
          style={{
            left: `${p.x}%`,
            bottom: `${p.y - 100}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            animationDuration: `${p.duration}s`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

export default SeedParticles;
