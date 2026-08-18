'use client';

import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'glass' | 'soil' | 'command' | 'telemetry';
  isSelected?: boolean;
  hover?: boolean;
  children?: React.ReactNode;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'glass',
      isSelected = false,
      hover = true,
      children,
      className = '',
      style,
      ...props
    },
    ref
  ) => {
    let variantClass = 'card-glass';
    if (variant === 'soil') variantClass = 'card-soil';
    if (variant === 'command') variantClass = 'card-command';
    if (variant === 'telemetry') variantClass = 'card-telemetry';

    return (
      <div
        ref={ref}
        className={`card ${variantClass} ${isSelected ? 'is-selected' : ''} ${className}`}
        style={{
          transform: hover ? undefined : 'none',
          ...style,
        }}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';
export default Card;
