'use client';

import React from 'react';
import { Background } from '@/background';
import { cn } from '@/utils/cn';
import styles from './AuthenticationLayout.module.css';

export interface AuthenticationLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function AuthenticationLayout({ children, className }: AuthenticationLayoutProps) {
  return (
    <div className={cn(styles.root, className)}>
      <Background fireflies seeds groundGlow fog noise />
      <div className={styles.card}>{children}</div>
    </div>
  );
}

export default AuthenticationLayout;
