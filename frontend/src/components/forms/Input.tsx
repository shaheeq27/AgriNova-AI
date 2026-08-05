'use client';
import React, { useState } from 'react';
import Label from '../typography/Label';

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
  style?: React.CSSProperties;
}

const Input: React.FC<InputProps> = ({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  error,
  icon,
  disabled = false,
  className = '',
  style,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    width: '100%',
    ...style,
  };

  const inputWrapperStyle: React.CSSProperties = {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    width: '100%',
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    fontFamily: '"Inter", sans-serif',
    fontSize: '14px',
    color: 'var(--text-primary)',
    background: 'var(--surface)',
    border: `1px solid ${error ? '#ef4444' : isFocused ? 'var(--border-hover)' : 'var(--border)'}`,
    borderRadius: '4px',
    padding: `12px 16px ${icon ? '12px 40px' : '12px 16px'}`,
    outline: 'none',
    transition: 'all 300ms ease-out',
    boxShadow: isFocused && !error ? '0 0 0 1px var(--accent-dim)' : 'none',
    opacity: disabled ? 0.5 : 1,
  };

  const iconStyle: React.CSSProperties = {
    position: 'absolute',
    left: '12px',
    color: isFocused ? 'var(--text-primary)' : 'var(--text-muted)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'color 300ms ease-out',
  };

  const errorStyle: React.CSSProperties = {
    fontFamily: '"Inter", sans-serif',
    fontSize: '12px',
    color: '#ef4444',
    margin: 0,
  };

  return (
    <div style={containerStyle} className={className}>
      {label && <Label>{label}</Label>}
      <div style={inputWrapperStyle}>
        {icon && <div style={iconStyle}>{icon}</div>}
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          style={inputStyle}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
      </div>
      {error && <p style={errorStyle}>{error}</p>}
    </div>
  );
};

export default Input;
