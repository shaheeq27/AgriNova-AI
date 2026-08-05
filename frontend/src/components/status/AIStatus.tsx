import React from 'react';
import TerminalText from '../typography/TerminalText';
import PulseDot from './PulseDot';

export interface AIStatusProps {
  label?: string;
  active?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const AIStatus: React.FC<AIStatusProps> = ({
  label = 'AI ADVISOR ACTIVE',
  active = true,
  className = '',
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '4px 12px',
    borderRadius: '9999px',
    border: '1px solid var(--border)',
    background: 'rgba(13, 31, 21, 0.5)',
    backdropFilter: 'blur(4px)',
    ...style,
  };

  return (
    <div style={containerStyle} className={className}>
      <PulseDot status={active ? 'active' : 'neutral'} size={6} />
      <TerminalText style={{ color: active ? 'var(--accent-primary)' : 'var(--text-muted)' }}>
        {label}
      </TerminalText>
    </div>
  );
};

export default AIStatus;
