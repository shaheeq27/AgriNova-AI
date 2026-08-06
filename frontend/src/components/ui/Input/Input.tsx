'use client';

import React from 'react';
import { cn } from '@/utils/cn';
import styles from './Input.module.css';

export interface InputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  error?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  className?: string;
  id?: string;
}

export function Input({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  error,
  icon,
  disabled = false,
  className,
  id,
}: InputProps) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className={cn(styles.field, className)}>
      {label && (
        <label className="type-label" htmlFor={inputId}>
          {label}
        </label>
      )}
      <div className={styles.wrapper}>
        {icon && <span className={styles.icon}>{icon}</span>}
        <input
          id={inputId}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          className={cn(styles.input, icon ? styles.withIcon : undefined, error ? styles.error : undefined)}
        />
      </div>
      {error && <p className={styles.errorMessage}>{error}</p>}
    </div>
  );
}

export default Input;
