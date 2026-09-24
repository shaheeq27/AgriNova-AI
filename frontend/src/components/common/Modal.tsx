'use client';
import React, { useEffect, useState } from 'react';
import Title from '../typography/Title';
import IconButton from '../buttons/IconButton';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  style?: React.CSSProperties;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  className = '',
  style,
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTimeout(() => setMounted(true), 0);
  }, []);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!mounted || !isOpen) return null;

  const getWidth = () => {
    switch (size) {
      case 'sm': return '400px';
      case 'lg': return '800px';
      case 'md':
      default: return '600px';
    }
  };

  const overlayStyle: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(4, 10, 6, 0.8)',
    backdropFilter: 'blur(4px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    animation: 'fadeIn 300ms ease-out',
  };

  const contentStyle: React.CSSProperties = {
    width: '100%',
    maxWidth: getWidth(),
    background: 'var(--surface-glass)',
    border: '1px solid var(--border)',
    borderRadius: '12px',
    boxShadow: '0 24px 48px rgba(0,0,0,0.4), 0 0 0 1px var(--border-hover)',
    maxHeight: '90vh',
    display: 'flex',
    flexDirection: 'column',
    animation: 'slideUp 300ms cubic-bezier(0.4, 0, 0.2, 1)',
    position: 'relative',
    ...style,
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '24px',
    borderBottom: '1px solid var(--border)',
  };

  const bodyStyle: React.CSSProperties = {
    padding: '24px',
    overflowY: 'auto',
  };

  const closeIcon = (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  );

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={contentStyle} onClick={e => e.stopPropagation()} className={className}>
        <div style={headerStyle}>
          {title ? (
            <Title as="h3" size="sm">{title}</Title>
          ) : <div />}
          <IconButton icon={closeIcon} label="Close modal" onClick={onClose} variant="ghost" />
        </div>
        <div style={bodyStyle}>
          {children}
        </div>
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
      `}} />
    </div>
  );
};

export default Modal;
