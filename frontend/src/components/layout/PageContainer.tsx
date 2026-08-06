'use client';
import React from 'react';

export interface PageContainerProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  maxWidth?: string;
  className?: string;
  style?: React.CSSProperties;
}

export default function PageContainer({
  children,
  title,
  subtitle,
  maxWidth = '1200px',
  className = '',
  style = {},
}: PageContainerProps) {
  return (
    <div
      className={className}
      style={{
        maxWidth,
        margin: '0 auto',
        padding: '24px',
        animation: 'fadeInUp 0.5s ease-out',
        minHeight: '100vh',
        color: 'var(--text-primary)',
        fontFamily: 'Inter',
        ...style,
      }}
    >
      <style>{`
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
      {(title || subtitle) && (
        <div style={{ marginBottom: '32px' }}>
          {title && <h1 style={{ fontFamily: 'Playfair Display, serif', fontSize: '32px', margin: '0 0 8px 0' }}>{title}</h1>}
          {subtitle && <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '16px' }}>{subtitle}</p>}
        </div>
      )}
      {children}
    </div>
  );
}