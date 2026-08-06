'use client';

import React from 'react';
import { useAnimation } from '@/hooks/useAnimation';
import { cn } from '@/utils/cn';
import styles from './FadeIn.module.css';

export type FadeInDirection = 'up' | 'down' | 'left' | 'right' | 'none';

export interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: FadeInDirection;
  className?: string;
}

export function FadeIn({
  children,
  delay = 0,
  duration = 500,
  direction = 'up',
  className,
}: FadeInProps) {
  const { ref, isVisible } = useAnimation();

  return (
    <div
      ref={ref}
      className={cn(
        styles.fadeIn,
        isVisible ? styles.visible : cn(styles.hidden, styles[direction]),
        className,
      )}
      style={{
        transitionDelay: `${delay}ms`,
        transitionDuration: `${duration}ms`,
      }}
    >
      {children}
    </div>
  );
}

export default FadeIn;
