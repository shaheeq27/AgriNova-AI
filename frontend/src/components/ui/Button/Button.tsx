'use client';

import React from 'react';
import { cn } from '@/utils/cn';
import styles from './Button.module.css';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'icon';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  glow?: boolean;
}

export function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  icon,
  glow = false,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  const isIcon = variant === 'icon';

  return (
    <button
      className={cn(
        styles.button,
        styles[variant],
        !isIcon && styles[size],
        isIcon && styles[`icon${size.charAt(0).toUpperCase()}${size.slice(1)}` as 'iconSm' | 'iconMd' | 'iconLg'],
        fullWidth && styles.fullWidth,
        variant === 'primary' && glow && styles.primaryGlow,
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className={styles.loading}>🌱</span>
      ) : (
        <>
          {icon}
          {!isIcon && children}
        </>
      )}
    </button>
  );
}

export default Button;
