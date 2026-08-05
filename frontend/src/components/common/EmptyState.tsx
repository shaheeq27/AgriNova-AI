'use client';
import React from 'react';
import Title from '../typography/Title';
import Subtitle from '../typography/Subtitle';
import SecondaryButton from '../buttons/SecondaryButton';

export interface EmptyStateProps {
  icon: string;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  style?: React.CSSProperties;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = '',
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '64px 32px',
    textAlign: 'center',
    background: 'var(--surface)',
    border: '1px dashed var(--border)',
    borderRadius: '8px',
    ...style,
  };

  const iconStyle: React.CSSProperties = {
    fontSize: '48px',
    marginBottom: '24px',
    animation: 'float 4s infinite ease-in-out',
    filter: 'drop-shadow(0 0 12px rgba(78, 232, 106, 0.2))',
  };

  const titleStyle: React.CSSProperties = {
    marginBottom: '8px',
  };

  const descStyle: React.CSSProperties = {
    marginBottom: action ? '24px' : '0',
    maxWidth: '400px',
  };

  return (
    <div style={containerStyle} className={className}>
      <div style={iconStyle}>{icon}</div>
      <Title as="h3" size="md" style={titleStyle}>{title}</Title>
      <Subtitle style={descStyle}>{description}</Subtitle>
      {action && (
        <SecondaryButton onClick={action.onClick}>
          {action.label}
        </SecondaryButton>
      )}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes float {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
          100% { transform: translateY(0px); }
        }
      `}} />
    </div>
  );
};

export default EmptyState;
