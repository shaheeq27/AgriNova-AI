'use client';
import React, { useState } from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  padding?: string;
  hover?: boolean; // default true
  glow?: boolean; // subtle green edge glow, default false
  onClick?: () => void;
  className?: string;
  style?: React.CSSProperties;
}

export default function GlassCard({ children, padding = '24px', hover = true, glow = false, onClick, className, style }: GlassCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={className}
      style={{
        background: 'var(--surface-glass, rgba(13, 31, 21, 0.7))',
        backdropFilter: 'blur(16px)',
        border: `1px solid ${isHovered && hover ? 'var(--border-hover, rgba(78, 232, 106, 0.16))' : 'var(--border, rgba(78, 232, 106, 0.08))'}`,
        borderRadius: '16px',
        padding,
        boxShadow: isHovered && hover
          ? 'inset 0 1px 4px rgba(0,0,0,0.3), 0 0 16px rgba(78,232,106,0.10), 0 8px 24px rgba(0,0,0,0.4)'
          : `inset 0 1px 4px rgba(0,0,0,0.3), 0 0 1px rgba(78,232,106,0.04)${glow ? ', 0 0 8px rgba(78,232,106,0.06)' : ''}`,
        transform: isHovered && hover ? 'translateY(-2px)' : 'none',
        transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
