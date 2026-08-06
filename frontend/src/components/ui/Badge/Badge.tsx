import React from 'react';
import { cn } from '@/utils/cn';
import styles from './Badge.module.css';

export type BadgeStatus =
  | 'active'
  | 'optimal'
  | 'warning'
  | 'critical'
  | 'info'
  | 'neutral'
  | 'success'
  | 'error';

export type BadgeSize = 'sm' | 'md';

export interface BadgeProps {
  status?: BadgeStatus;
  label: string;
  pulse?: boolean;
  size?: BadgeSize;
  className?: string;
}

export function Badge({
  status = 'neutral',
  label,
  pulse = false,
  size = 'md',
  className,
}: BadgeProps) {
  return (
    <span className={cn(styles.badge, styles[status], styles[size], className)}>
      {pulse && <span className={styles.pulse} />}
      {label}
    </span>
  );
}

export default Badge;
