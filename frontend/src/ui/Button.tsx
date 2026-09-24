'use client';

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'telemetry' | 'scan';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  isDisabled?: boolean;
  icon?: React.ReactNode;
  children?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      isDisabled = false,
      icon,
      children,
      className = '',
      style,
      ...props
    },
    ref
  ) => {
    let variantClass = 'btn-primary';
    if (variant === 'secondary') variantClass = 'btn-secondary';
    if (variant === 'ghost') variantClass = 'btn-ghost';
    if (variant === 'danger') variantClass = 'btn-danger';
    if (variant === 'telemetry') variantClass = 'btn-telemetry';
    if (variant === 'scan') variantClass = 'btn-scan-pulsing';

    const padding =
      size === 'sm' ? '6px 14px' : size === 'lg' ? '14px 32px' : '10px 24px';
    const fontSize = size === 'sm' ? 'var(--text-sm)' : size === 'lg' ? 'var(--text-lg)' : 'var(--text-md)';

    return (
      <button
        ref={ref}
        disabled={isDisabled || isLoading}
        className={`btn ${variantClass} ${isDisabled ? 'is-disabled' : ''} ${isLoading ? 'is-loading' : ''} ${className}`}
        style={{
          padding,
          fontSize,
          ...style,
        }}
        {...props}
      >
        {isLoading ? (
          <span
            style={{
              width: '16px',
              height: '16px',
              border: '2px solid currentColor',
              borderTopColor: 'transparent',
              borderRadius: '50%',
              animation: 'icon-rotate 1s linear infinite',
            }}
          />
        ) : (
          icon
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;
