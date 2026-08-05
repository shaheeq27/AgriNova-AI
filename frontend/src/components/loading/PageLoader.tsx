'use client';
import React from 'react';
import LoadingScreen from './LoadingScreen';

export default function PageLoader() {
  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--background)' }}>
      <LoadingScreen />
    </div>
  );
}