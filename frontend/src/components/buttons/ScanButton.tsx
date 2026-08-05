'use client';
import React, { useState } from 'react';

export interface ScanButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const ScanButton: React.FC<ScanButtonProps> = ({
  children,
  onClick,
  disabled = false,
  className = '',
  style,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const baseStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: '14px',
    fontWeight: 600,
    letterSpacing: '0.05em',
    padding: '16px 32px',
    borderRadius: '4px',
    border: '1px solid var(--accent-primary)',
    background: isHovered && !disabled ? 'var(--accent-dim)' : 'rgba(20, 64, 42, 0.3)',
    color: 'var(--accent-primary)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: isHovered && !disabled ? '0 0 24px var(--accent-glow), inset 0 0 12px var(--accent-glow)' : '0 0 12px var(--accent-glow)',
    textTransform: 'uppercase',
    ...style,
  };

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      style={baseStyle}
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span style={{ 
        display: 'inline-block',
        width: '8px', 
        height: '8px', 
        borderRadius: '50%',
        backgroundColor: 'var(--accent-primary)',
        boxShadow: '0 0 8px var(--accent-primary)',
        animation: 'pulse 2s infinite'
      }} />
      {children}
    </button>
  );
};

export default ScanButton;
