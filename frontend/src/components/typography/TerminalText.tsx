import React from 'react';

export interface TerminalTextProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const TerminalText: React.FC<TerminalTextProps> = ({
  children,
  className = '',
  style,
}) => {
  const baseStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: '13px',
    fontWeight: 500,
    lineHeight: 1.4,
    margin: 0,
    color: 'var(--accent-primary)',
    textShadow: '0 0 8px var(--accent-glow)',
    ...style,
  };

  return (
    <div style={baseStyle} className={className}>
      {children}
    </div>
  );
};

export default TerminalText;
