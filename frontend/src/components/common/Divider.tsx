import React from 'react';
import Label from '../typography/Label';

export interface DividerProps {
  label?: string;
  className?: string;
  style?: React.CSSProperties;
}

const Divider: React.FC<DividerProps> = ({
  label,
  className = '',
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    width: '100%',
    margin: '24px 0',
    ...style,
  };

  const lineStyle: React.CSSProperties = {
    flex: 1,
    height: '1px',
    backgroundColor: 'var(--border)',
  };

  const labelStyle: React.CSSProperties = {
    padding: '0 16px',
  };

  return (
    <div style={containerStyle} className={className}>
      <div style={lineStyle} />
      {label && (
        <div style={labelStyle}>
          <Label>{label}</Label>
        </div>
      )}
      {label && <div style={lineStyle} />}
    </div>
  );
};

export default Divider;
