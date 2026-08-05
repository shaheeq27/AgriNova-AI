import React from 'react';

export interface TitleProps {
  children: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  gradient?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const Title: React.FC<TitleProps> = ({
  children,
  as: Component = 'h2',
  size = 'lg',
  gradient = false,
  className = '',
  style,
}) => {
  const getFontSize = () => {
    switch (size) {
      case 'sm': return '1.5rem';
      case 'md': return '2rem';
      case 'xl': return '3rem';
      case 'lg':
      default: return '2.5rem';
    }
  };

  const baseStyle: React.CSSProperties = {
    fontFamily: '"Playfair Display", serif',
    fontSize: getFontSize(),
    fontWeight: 600,
    lineHeight: 1.2,
    margin: 0,
    color: gradient ? 'transparent' : 'var(--text-primary)',
    backgroundImage: gradient ? 'linear-gradient(90deg, var(--text-primary), var(--text-secondary))' : undefined,
    WebkitBackgroundClip: gradient ? 'text' : undefined,
    ...style,
  };

  return (
    <Component style={baseStyle} className={className}>
      {children}
    </Component>
  );
};

export default Title;
