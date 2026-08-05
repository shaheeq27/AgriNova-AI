'use client';
import React, { useState } from 'react';
import Label from '../typography/Label';

export interface SelectOption {
  label: string;
  value: string;
}

export interface SelectProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  options: SelectOption[];
  error?: string;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const Select: React.FC<SelectProps> = ({
  label,
  value,
  onChange,
  options,
  error,
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

  const selectWrapperStyle: React.CSSProperties = {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    width: '100%',
  };

  const selectStyle: React.CSSProperties = {
    width: '100%',
    fontFamily: '"Inter", sans-serif',
    fontSize: '14px',
    color: 'var(--text-primary)',
    background: 'var(--surface)',
    border: `1px solid ${error ? '#ef4444' : isFocused ? 'var(--border-hover)' : 'var(--border)'}`,
    borderRadius: '4px',
    padding: '12px 36px 12px 16px',
    outline: 'none',
    appearance: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 300ms ease-out',
    boxShadow: isFocused && !error ? '0 0 0 1px var(--accent-dim)' : 'none',
    opacity: disabled ? 0.5 : 1,
  };

  const chevronStyle: React.CSSProperties = {
    position: 'absolute',
    right: '12px',
    pointerEvents: 'none',
    color: 'var(--text-muted)',
    display: 'flex',
    alignItems: 'center',
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
      <div style={selectWrapperStyle}>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          style={selectStyle}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <div style={chevronStyle}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
      {error && <p style={errorStyle}>{error}</p>}
    </div>
  );
};

export default Select;
