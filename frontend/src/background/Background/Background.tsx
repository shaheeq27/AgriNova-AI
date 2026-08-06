'use client';

import React from 'react';
import { cn } from '@/utils/cn';
import { Fireflies } from '../Fireflies';
import { SeedParticles } from '../SeedParticles';
import { Wind } from '../Wind';
import styles from './Background.module.css';

export interface BackgroundProps {
  shader?: boolean;
  fireflies?: boolean;
  fireflyCount?: number;
  seeds?: boolean;
  seedCount?: number;
  wind?: boolean;
  windCount?: number;
  groundGlow?: boolean;
  fog?: boolean;
  noise?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export function Background({
  shader = true,
  fireflies = true,
  fireflyCount = 12,
  seeds = true,
  seedCount = 15,
  wind = false,
  windCount = 4,
  groundGlow = true,
  fog = true,
  noise = true,
  className,
  children,
}: BackgroundProps) {
  return (
    <div className={cn(styles.root, className)} aria-hidden="true">
      {shader && <div className={styles.shader} />}
      {fog && <div className={styles.fog} />}
      {noise && <div className={styles.noise} />}
      {groundGlow && <div className={styles.groundGlow} />}
      {wind && <Wind count={windCount} />}
      {seeds && <SeedParticles count={seedCount} />}
      {fireflies && <Fireflies count={fireflyCount} />}
      {children}
    </div>
  );
}

export default Background;
