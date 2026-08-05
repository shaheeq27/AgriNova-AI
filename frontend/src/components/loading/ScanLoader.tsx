'use client';
import React from 'react';

export default function ScanLoader() {
  return (
    <div style={{ position: 'relative', width: '100%', height: '200px', backgroundColor: 'var(--surface)', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--border)' }}>
      <style>{`@keyframes scanSweep { 0% { top: -10%; } 50% { top: 100%; } 100% { top: -10%; } }`}</style>
      <div style={{ 
        position: 'absolute', left: 0, right: 0, height: '4px', background: 'var(--accent-primary)',
        boxShadow: '0 0 15px var(--accent-primary)', animation: 'scanSweep 3s infinite linear' 
      }} />
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Space Mono', color: 'var(--accent-primary)' }}>
        ANALYZING...
      </div>
    </div>
  );
}