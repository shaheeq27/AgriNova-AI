'use client';
import React from 'react';
import Label from '../typography/Label';

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  className = '',
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '12px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    ...style,
  };

  const trackStyle: React.CSSProperties = {
    position: 'relative',
    width: '40px',
    height: '24px',
    borderRadius: '12px',
    background: checked ? 'var(--accent-dim)' : 'var(--surface-hover)',
    border: `1px solid ${checked ? 'var(--accent-muted)' : 'var(--border)'}`,
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  };

  const thumbStyle: React.CSSProperties = {
    position: 'absolute',
    top: '2px',
    left: checked ? '18px' : '2px',
    width: '18px',
    height: '18px',
    borderRadius: '50%',
    background: checked ? 'var(--accent-primary)' : 'var(--text-muted)',
    boxShadow: checked ? '0 0 8px var(--accent-glow)' : 'none',
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  };

  return (
    <div 
      style={containerStyle} 
      className={className} 
      onClick={() => !disabled && onChange(!checked)}
      role="switch"
      aria-checked={checked}
    >
      <div style={trackStyle}>
        <div style={thumbStyle} />
      </div>
      {label && <Label style={{ cursor: 'pointer', margin: 0 }}>{label}</Label>}
    </div>
  );
};

export default Switch;
