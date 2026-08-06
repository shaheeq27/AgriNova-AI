'use client';

import React from 'react';
import { cn } from '@/utils/cn';
import styles from './Card.module.css';

export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: CardPadding;
  hover?: boolean;
  glow?: boolean;
}

export function Card({
  padding = 'md',
  hover = true,
  glow = false,
  onClick,
  className,
  children,
  ...props
}: CardProps) {
  const paddingClass = {
    none: styles.paddingNone,
    sm: styles.paddingSm,
    md: styles.paddingMd,
    lg: styles.paddingLg,
  }[padding];

  return (
    <div
      className={cn(
        styles.card,
        paddingClass,
        hover && styles.hoverable,
        glow && styles.glow,
        onClick && styles.interactive,
        className,
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
}

export default Card;
