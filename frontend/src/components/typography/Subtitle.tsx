import React from 'react';

export interface SubtitleProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const Subtitle: React.FC<SubtitleProps> = ({
  children,
  className = '',
  style,
}) => {
  const baseStyle: React.CSSProperties = {
    fontFamily: '"Inter", sans-serif',
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.5,
    margin: 0,
    color: 'var(--text-secondary)',
    ...style,
  };

  return (
    <div style={baseStyle} className={className}>
      {children}
    </div>
  );
};

export default Subtitle;
