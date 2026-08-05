import React from 'react';

export interface AvatarProps {
  name: string;
  src?: string;
  size?: 'sm' | 'md' | 'lg';
  showOutline?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const Avatar: React.FC<AvatarProps> = ({
  name,
  src,
  size = 'md',
  showOutline = false,
  className = '',
  style,
}) => {
  const getDimensions = () => {
    switch (size) {
      case 'sm': return '32px';
      case 'lg': return '64px';
      case 'md':
      default: return '48px';
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'sm': return '12px';
      case 'lg': return '24px';
      case 'md':
      default: return '18px';
    }
  };

  const dim = getDimensions();

  const containerStyle: React.CSSProperties = {
    width: dim,
    height: dim,
    borderRadius: '50%',
    background: 'var(--surface-hover)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    border: showOutline ? '2px solid var(--accent-dim)' : '1px solid var(--border)',
    boxShadow: showOutline ? '0 0 16px var(--accent-glow)' : 'none',
    animation: showOutline ? 'pulse 3s infinite ease-in-out' : 'none',
    ...style,
  };

  const textStyle: React.CSSProperties = {
    fontFamily: '"Space Mono", monospace',
    fontSize: getFontSize(),
    fontWeight: 600,
    color: 'var(--text-secondary)',
    textTransform: 'uppercase',
  };

  const imageStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  };

  return (
    <div style={containerStyle} className={className} title={name}>
      {src ? (
        <img src={src} alt={name} style={imageStyle} />
      ) : (
        <span style={textStyle}>{name.charAt(0)}</span>
      )}
    </div>
  );
};

export default Avatar;
