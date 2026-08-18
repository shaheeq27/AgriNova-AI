'use client';

import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'ai' | 'offline';
  pulse?: boolean;
  children?: React.ReactNode;
}

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      variant = 'success',
      pulse = false,
      children,
      className = '',
      style,
      ...props
    },
    ref
  ) => {
    let variantClass = 'badge-success';
    if (variant === 'warning') variantClass = 'badge-warning';
    if (variant === 'error') variantClass = 'badge-error';
    if (variant === 'ai') variantClass = 'badge-ai';
    if (variant === 'offline') variantClass = 'badge-offline';

    return (
      <span
        ref={ref}
        className={`badge ${variantClass} ${className}`}
        style={style}
        {...props}
      >
        {pulse && (
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: 'currentColor',
              animation: 'status-pulse 2.5s var(--ease-in-out) infinite',
            }}
          />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';
export default Badge;
