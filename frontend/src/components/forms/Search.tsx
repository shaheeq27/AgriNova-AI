'use client';
import React, { useState } from 'react';

export interface SearchProps {
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  className?: string;
  style?: React.CSSProperties;
}

const Search: React.FC<SearchProps> = ({
  placeholder = 'Search...',
  value,
  onChange,
  className = '',
  style,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const wrapperStyle: React.CSSProperties = {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    width: '100%',
    ...style,
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    fontFamily: '"Inter", sans-serif',
    fontSize: '14px',
    color: 'var(--text-primary)',
    background: 'var(--surface)',
    border: `1px solid ${isFocused ? 'var(--border-hover)' : 'var(--border)'}`,
    borderRadius: '9999px',
    padding: '10px 16px 10px 40px',
    outline: 'none',
    transition: 'all 300ms ease-out',
    boxShadow: isFocused ? '0 0 0 1px var(--accent-dim)' : 'none',
  };

  const iconStyle: React.CSSProperties = {
    position: 'absolute',
    left: '14px',
    color: isFocused ? 'var(--text-primary)' : 'var(--text-muted)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'color 300ms ease-out',
  };

  return (
    <div style={wrapperStyle} className={className}>
      <div style={iconStyle}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={inputStyle}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
    </div>
  );
};

export default Search;
