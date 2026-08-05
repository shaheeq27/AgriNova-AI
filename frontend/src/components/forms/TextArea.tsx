'use client';
import React, { useState } from 'react';
import Label from '../typography/Label';

export interface TextAreaProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  rows?: number;
  error?: string;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const TextArea: React.FC<TextAreaProps> = ({
  label,
  placeholder,
  value,
  onChange,
  rows = 4,
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

  const textareaStyle: React.CSSProperties = {
    width: '100%',
    fontFamily: '"Inter", sans-serif',
    fontSize: '14px',
    lineHeight: 1.5,
    color: 'var(--text-primary)',
    background: 'var(--surface)',
    border: `1px solid ${error ? '#ef4444' : isFocused ? 'var(--border-hover)' : 'var(--border)'}`,
    borderRadius: '4px',
    padding: '12px 16px',
    outline: 'none',
    resize: 'vertical',
    minHeight: '80px',
    transition: 'all 300ms ease-out',
    boxShadow: isFocused && !error ? '0 0 0 1px var(--accent-dim)' : 'none',
    opacity: disabled ? 0.5 : 1,
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
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        rows={rows}
        style={textareaStyle}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
      {error && <p style={errorStyle}>{error}</p>}
    </div>
  );
};

export default TextArea;
