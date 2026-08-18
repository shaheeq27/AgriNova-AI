'use client';

import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'lens' | 'soil';
  label?: string;
  isError?: boolean;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'lens',
      label,
      isError = false,
      className = '',
      style,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);
    const variantClass = variant === 'soil' ? 'input-soil' : 'input-field';

    return (
      <div style={{ width: '100%' }}>
        {label && (
          <label htmlFor={inputId} className="input-label">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`${variantClass} ${isError ? 'is-error' : ''} ${className}`}
          style={style}
          {...props}
        />
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
