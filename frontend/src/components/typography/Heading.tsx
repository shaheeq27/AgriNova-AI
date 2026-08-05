import React from 'react';

export interface HeadingProps {
  children: React.ReactNode;
  as?: 'h3' | 'h4' | 'h5' | 'h6';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  style?: React.CSSProperties;
}

const Heading: React.FC<HeadingProps> = ({
  children,
  as: Component = 'h3',
  size = 'md',
  className = '',
  style,
}) => {
  const getFontSize = () => {
    switch (size) {
      case 'sm': return '1.125rem';
      case 'lg': return '1.75rem';
      case 'md':
      default: return '1.5rem';
    }
  };

  const baseStyle: React.CSSProperties = {
    fontFamily: '"Playfair Display", serif',
    fontSize: getFontSize(),
    fontWeight: 600,
    lineHeight: 1.3,
    margin: 0,
    color: 'var(--text-primary)',
    ...style,
  };

  return (
    <Component style={baseStyle} className={className}>
      {children}
    </Component>
  );
};

export default Heading;
