import React from 'react';

export interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showGlow?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const Logo: React.FC<LogoProps> = ({
  size = 'md',
  showGlow = true,
  className = '',
  style,
}) => {
  const getMarkSize = () => {
    switch (size) {
      case 'sm':
        return { box: '24px', font: '12px' };
      case 'lg':
        return { box: '48px', font: '24px' };
      case 'md':
      default:
        return { box: '32px', font: '16px' };
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm':
        return '16px';
      case 'lg':
        return '28px';
      case 'md':
      default:
        return '20px';
    }
  };

  const markSize = getMarkSize();

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: size === 'lg' ? '16px' : '12px',
    ...style,
  };

  const markStyle: React.CSSProperties = {
    width: markSize.box,
    height: markSize.box,
    borderRadius: size === 'lg' ? '12px' : '8px',
    background: 'linear-gradient(135deg, var(--accent-muted) 0%, var(--surface-hover) 100%)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    border: '1px solid var(--border)',
    boxShadow: showGlow ? '0 0 20px var(--accent-glow)' : 'none',
    fontSize: markSize.font,
  };

  const textStyle: React.CSSProperties = {
    fontFamily: '"Playfair Display", serif',
    fontSize: getTextSize(),
    fontWeight: 700,
    color: 'var(--text-primary)',
    margin: 0,
    letterSpacing: '0.02em',
  };

  const aiStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: size === 'lg' ? '13px' : '10px',
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
