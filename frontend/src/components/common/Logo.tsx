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
        return '24px';
      case 'lg':
        return '48px';
      case 'md':
      default:
        return '36px';
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm':
        return '16px';
      case 'lg':
        return '26px';
      case 'md':
      default:
        return '20px';
    }
  };

  const boxSize = getMarkSize();

  const containerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: size === 'lg' ? '14px' : '10px',
    ...style,
  };

  const markStyle: React.CSSProperties = {
    width: boxSize,
    height: boxSize,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  };

  const textStyle: React.CSSProperties = {
    fontFamily: '"Source Serif 4", serif',
    fontSize: getTextSize(),
    fontWeight: 700,
    color: '#F2F0E8',
    margin: 0,
    letterSpacing: '0.02em',
  };

  const aiStyle: React.CSSProperties = {
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: size === 'lg' ? '13px' : '10px',
    color: '#ADFF00',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    marginLeft: '6px',
    verticalAlign: 'top',
  };

  return (
    <div style={containerStyle} className={className}>
      <div style={markStyle}>
        <img
          src="/logo_transparent.png"
          alt="AgriNova"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            filter: showGlow
              ? 'drop-shadow(0 0 8px rgba(173,255,0,0.5))'
              : 'none',
          }}
        />
      </div>
      <div style={textStyle}>
        AgriNova<span style={aiStyle}>AI</span>
      </div>
    </div>
  );
};

export default Logo;
