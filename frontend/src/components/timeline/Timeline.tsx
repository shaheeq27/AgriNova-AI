'use client';
import React from 'react';
import TimelineLine from './TimelineLine';

export default function Timeline({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ position: 'relative', paddingLeft: '40px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <TimelineLine />
      {children}
    </div>
  );
}