'use client';
import React from 'react';

export interface SectionProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  delay?: number;
  className?: string;
  style?: React.CSSProperties;
}

export default function Section({
  children,
  title,
  subtitle,
  action,
  delay = 0,
  className = '',
  style = {},
}: SectionProps) {
  return (
    <section
      className={className}
      style={{
        marginBottom: '40px',
        animation: `fadeInUp 0.5s ease-out ${delay}ms both`,
        ...style,
      }}
    >
      <style>{`
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
      {(title || action) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            {title && <h2 style={{ fontFamily: 'Playfair Display, serif', fontSize: '24px', margin: '0 0 4px 0', color: 'var(--text-primary)' }}>{title}</h2>}
            {subtitle && <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '14px', fontFamily: 'Inter' }}>{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div>{children}</div>
    </section>
  );
}