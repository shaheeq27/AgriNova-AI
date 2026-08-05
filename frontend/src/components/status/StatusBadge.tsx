import React from 'react';

export interface StatusBadgeProps {
  status: 'active' | 'warning' | 'critical' | 'info' | 'neutral' | 'optimal';
  label: string;
  pulse?: boolean;
  size?: 'sm' | 'md';
  className?: string;
  style?: React.CSSProperties;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  pulse = false,
  size = 'md',
  className = '',
  style,
}) => {
  const getColors = () => {
    switch (status) {
      case 'active':
        return { bg: 'var(--accent-dim)', color: 'var(--accent-secondary)', border: 'var(--accent-muted)' };
      case 'optimal':
        return { bg: 'rgba(78, 232, 106, 0.1)', color: 'var(--accent-primary)', border: 'rgba(78, 232, 106, 0.3)' };
      case 'warning':
        return { bg: 'rgba(234, 179, 8, 0.1)', color: '#facc15', border: 'rgba(234, 179, 8, 0.3)' };
      case 'critical':
        return { bg: 'rgba(239, 68, 68, 0.1)', color: '#f87171', border: 'rgba(239, 68, 68, 0.3)' };
      case 'info':
        return { bg: 'rgba(56, 189, 248, 0.1)', color: '#7dd3fc', border: 'rgba(56, 189, 248, 0.3)' };
      case 'neutral':
      default:
        return { bg: 'var(--surface-hover)', color: 'var(--text-secondary)', border: 'var(--border)' };
    }
  };

  const colors = getColors();

  const getPadding = () => {
    switch (size) {
      case 'sm': return '4px 8px';
      case 'md':
      default: return '6px 12px';
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'sm': return '10px';
      case 'md':
      default: return '11px';
    }
  };

  const baseStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: getFontSize(),
    fontWeight: 600,
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    padding: getPadding(),
    borderRadius: '9999px',
    backgroundColor: colors.bg,
    color: colors.color,
    border: `1px solid ${colors.border}`,
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    ...style,
  };

  return (
    <div style={baseStyle} className={className}>
      {pulse && (
        <span style={{
          display: 'inline-block',
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: colors.color,
          animation: 'pulse 2s infinite cubic-bezier(0.4, 0, 0.2, 1)',
        }} />
      )}
      {label}
    </div>
  );
};

export default StatusBadge;
