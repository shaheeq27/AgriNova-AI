'use client';
import React, { useState } from 'react';

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
  style?: React.CSSProperties;
}

const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  className = '',
  style,
}) => {
  const [isVisible, setIsVisible] = useState(false);

  const containerStyle: React.CSSProperties = {
    position: 'relative',
    display: 'inline-block',
  };

  const getPositionStyles = (): React.CSSProperties => {
    switch (position) {
      case 'bottom':
        return { top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '8px' };
      case 'left':
        return { top: '50%', right: '100%', transform: 'translateY(-50%)', marginRight: '8px' };
      case 'right':
        return { top: '50%', left: '100%', transform: 'translateY(-50%)', marginLeft: '8px' };
      case 'top':
      default:
        return { bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: '8px' };
    }
  };

  const tooltipStyle: React.CSSProperties = {
    position: 'absolute',
    background: 'var(--surface-hover)',
    border: '1px solid var(--border)',
    color: 'var(--text-primary)',
    padding: '6px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: '"Inter", sans-serif',
    whiteSpace: 'nowrap',
    zIndex: 100,
    opacity: isVisible ? 1 : 0,
    visibility: isVisible ? 'visible' : 'hidden',
    transition: 'all 200ms ease-out',
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
    ...getPositionStyles(),
    ...style,
  };

  return (
    <div 
      style={containerStyle} 
      className={className}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      <div style={tooltipStyle}>
        {content}
      </div>
    </div>
  );
};

export default Tooltip;
