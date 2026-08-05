import React from 'react';

export interface LogoProps {
  className?: string;
  style?: React.CSSProperties;
}

const Logo: React.FC<LogoProps> = ({
  className = '',
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    ...style,
  };

  const markStyle: React.CSSProperties = {
    width: '32px',
    height: '32px',
    borderRadius: '8px',
    background: 'linear-gradient(135deg, var(--accent-muted) 0%, var(--surface-hover) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '1px solid var(--border)',
    boxShadow: '0 0 16px var(--accent-glow)',
    animation: 'pulse 4s infinite ease-in-out',
    fontSize: '16px',
  };

  const textStyle: React.CSSProperties = {
    fontFamily: '"Playfair Display", serif',
    fontSize: '20px',
    fontWeight: 700,
    color: 'var(--text-primary)',
    margin: 0,
    letterSpacing: '0.02em',
  };

  const aiStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: '10px',
    color: 'var(--accent-primary)',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    marginLeft: '4px',
    verticalAlign: 'top',
  };

  return (
    <div style={containerStyle} className={className}>
      <div style={markStyle}>
        🌱
      </div>
      <div style={textStyle}>
        AgriNova<span style={aiStyle}>AI</span>
      </div>
    </div>
  );
};

export default Logo;
