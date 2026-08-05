'use client';
import React from 'react';

export default function ScreenWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ position: 'relative', width: '100%', minHeight: '100vh', zIndex: 1, backgroundColor: 'var(--background)' }}>
      {children}
    </div>
  );
}