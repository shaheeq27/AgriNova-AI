'use client';
import React, { useState } from 'react';

export interface SecondaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  type?: 'button' | 'submit';
  className?: string;
  style?: React.CSSProperties;
}

const SecondaryButton: React.FC<SecondaryButtonProps> = ({
  children,
  onClick,
  disabled = false,
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
    fontWeight: 500,
    padding: getPadding(),
    width: fullWidth ? '100%' : 'auto',
    borderRadius: '4px',
    border: '1px solid var(--border)',
    background: isHovered && !disabled ? 'var(--surface-hover)' : 'var(--surface)',
    color: 'var(--text-primary)',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: isHovered && !disabled ? 'inset 0 0 10px rgba(78, 232, 106, 0.05)' : 'none',
    borderColor: isHovered && !disabled ? 'var(--border-hover)' : 'var(--border)',
    ...style,
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={baseStyle}
      className={className}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {icon}
      {children}
    </button>
  );
};

export default SecondaryButton;
