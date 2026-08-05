'use client';
import React, { useState } from 'react';

export interface PrimaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  type?: 'button' | 'submit';
  className?: string;
  style?: React.CSSProperties;
}

const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  icon,
  size = 'md',
  fullWidth = false,
  type = 'button',
  className = '',
  style,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getPadding = () => {
    switch (size) {
      case 'sm': return '8px 16px';
      case 'lg': return '16px 32px';
      case 'md':
      default: return '12px 24px';
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'sm': return '13px';
      case 'lg': return '16px';
      case 'md':
      default: return '14px';
    }
  };

  const baseStyle: React.CSSProperties = {
    fontFamily: '"Inter", sans-serif',
    fontSize: getFontSize(),
    fontWeight: 600,
    padding: getPadding(),
    width: fullWidth ? '100%' : 'auto',
    borderRadius: '4px',
    border: 'none',
    background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%)',
    color: '#040a06',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: isHovered && !disabled && !loading ? '0 0 20px var(--accent-glow)' : 'none',
    position: 'relative',
    overflow: 'hidden',
    ...style,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      style={baseStyle}
      className={`btn-primary ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {loading ? (
        <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>🌱</span>
      ) : (
        <>
          {icon}
          {children}
        </>
      )}
    </button>
  );
};

export default PrimaryButton;
