'use client';

import React from 'react';
import { cn } from '@/utils/cn';
import styles from './PageTransition.module.css';

export interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export function PageTransition({ children, className }: PageTransitionProps) {
  return <div className={cn(styles.pageTransition, className)}>{children}</div>;
}

export default PageTransition;
