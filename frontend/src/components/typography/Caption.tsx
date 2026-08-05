import React from 'react';

export interface CaptionProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const Caption: React.FC<CaptionProps> = ({
  children,
  className = '',
  style,
}) => {
  const baseStyle: React.CSSProperties = {
    fontFamily: '"Inter", sans-serif',
    fontSize: '11px',
    fontWeight: 400,
    lineHeight: 1.4,
    margin: 0,
    color: 'var(--text-muted)',
    ...style,
  };

  return (
    <span style={baseStyle} className={className}>
      {children}
    </span>
  );
};

export default Caption;
