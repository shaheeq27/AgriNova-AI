import React from 'react';
import { cn } from '@/utils/cn';
import styles from './Divider.module.css';

export interface DividerProps {
  label?: string;
  className?: string;
}

export function Divider({ label, className }: DividerProps) {
  return (
    <div className={cn(styles.divider, className)}>
      <div className={styles.line} />
      {label && <span className={cn(styles.label, 'type-label')}>{label}</span>}
      {label && <div className={styles.line} />}
    </div>
  );
}

export default Divider;
