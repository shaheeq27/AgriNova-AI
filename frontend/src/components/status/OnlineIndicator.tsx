import React from 'react';

export interface OnlineIndicatorProps {
  online?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const OnlineIndicator: React.FC<OnlineIndicatorProps> = ({
  online = true,
  className = '',
  style,
}) => {
  const color = online ? 'var(--accent-primary)' : 'var(--text-muted)';
  
  const baseStyle: React.CSSProperties = {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: color,
    boxShadow: online ? `0 0 12px ${color}` : 'none',
    animation: online ? 'pulse 2s infinite cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
    display: 'inline-block',
    ...style,
  };

  return (
    <span style={baseStyle} className={className} />
  );
};

export default OnlineIndicator;
