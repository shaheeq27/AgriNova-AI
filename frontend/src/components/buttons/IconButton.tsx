'use client';
import React, { useState } from 'react';

export interface IconButtonProps {
  icon: React.ReactNode;
  onClick?: () => void;
  label: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'ghost' | 'surface';
  active?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const IconButton: React.FC<IconButtonProps> = ({
  icon,
  onClick,
  label,
  size = 'md',
  variant = 'ghost',
  active = false,
  className = '',
  style,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getDimensions = () => {
    switch (size) {
      case 'sm': return '32px';
      case 'lg': return '48px';
      case 'md':
      default: return '40px';
    }
  };

  const dim = getDimensions();

  const baseStyle: React.CSSProperties = {
    width: dim,
    height: dim,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: variant === 'surface' ? '1px solid var(--border)' : 'none',
    background: active ? 'var(--accent-dim)' : (variant === 'surface' ? 'var(--surface)' : 'transparent'),
    color: active ? 'var(--accent-primary)' : (isHovered ? 'var(--text-primary)' : 'var(--text-muted)'),
    cursor: 'pointer',
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: active ? '0 0 12px var(--accent-glow)' : (isHovered && variant === 'surface' ? '0 0 8px rgba(255,255,255,0.05)' : 'none'),
    padding: 0,
    ...style,
  };

  return (
    <button
      type="button"
      onClick={onClick}
      style={baseStyle}
      className={className}
      aria-label={label}
      title={label}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {icon}
    </button>
  );
};

export default IconButton;
