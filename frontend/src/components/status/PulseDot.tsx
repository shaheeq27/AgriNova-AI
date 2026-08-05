import React from 'react';

export interface PulseDotProps {
  status?: 'active' | 'warning' | 'critical' | 'info' | 'neutral' | 'optimal';
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}

const PulseDot: React.FC<PulseDotProps> = ({
  status = 'active',
  size = 8,
  className = '',
  style,
}) => {
  const getColor = () => {
    switch (status) {
      case 'active':
      case 'optimal': return 'var(--accent-primary)';
      case 'warning': return '#facc15';
      case 'critical': return '#f87171';
      case 'info': return '#7dd3fc';
      case 'neutral': return 'var(--text-muted)';
      default: return 'var(--accent-primary)';
    }
  };

  const color = getColor();

  const baseStyle: React.CSSProperties = {
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '50%',
    backgroundColor: color,
    boxShadow: `0 0 ${size * 2}px ${color}`,
    animation: 'pulse 2s infinite cubic-bezier(0.4, 0, 0.2, 1)',
    display: 'inline-block',
    ...style,
  };

  return (
    <span style={baseStyle} className={className} />
  );
};

export default PulseDot;
