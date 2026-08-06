'use client';

import React from 'react';
import { useParticles } from '@/hooks/useParticles';
import { cn } from '@/utils/cn';
import styles from './Wind.module.css';

export interface WindProps {
  count?: number;
  className?: string;
}

export function Wind({ count = 4, className }: WindProps) {
  const particles = useParticles(count);

  return (
    <div className={cn(styles.container, className)}>
      {particles.map((p) => (
        <div
          key={p.id}
          className={styles.line}
          style={{
            top: `${p.y}%`,
            width: `${60 + p.size * 20}px`,
            animationDuration: `${p.duration * 2 + 10}s`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

export default Wind;
