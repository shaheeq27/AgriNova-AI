import React from 'react';

export interface LabelProps {
  children: React.ReactNode;
  htmlFor?: string;
  className?: string;
  style?: React.CSSProperties;
}

const Label: React.FC<LabelProps> = ({
  children,
  htmlFor,
  className = '',
  style,
}) => {
  const baseStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: '11px',
    fontWeight: 500,
    lineHeight: 1,
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    margin: 0,
    color: 'var(--text-muted)',
    display: 'block',
    ...style,
  };

  return (
    <label htmlFor={htmlFor} style={baseStyle} className={className}>
      {children}
    </label>
  );
};

export default Label;
