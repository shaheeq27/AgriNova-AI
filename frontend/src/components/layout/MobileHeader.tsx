'use client';
import React from 'react';
import Image from 'next/image';

export default function MobileHeader() {
  return (
    <header
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '12px 20px',
        backgroundColor: 'rgba(19, 20, 18, 0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(173, 255, 0, 0.15)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
      }}
    >
      <style>{`
        @media (min-width: 768px) { header { display: none !important; } }
      `}</style>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Image
          src="/logo_transparent.png"
          alt="AgriNova AI"
          width={32}
          height={32}
          className="object-contain"
          style={{ filter: 'drop-shadow(0 0 6px rgba(173,255,0,0.5))' }}
          priority
        />
        <span
          style={{
            fontFamily: 'Source Serif 4, serif',
            fontSize: '18px',
            fontWeight: 700,
            color: '#F2F0E8',
          }}
        >
          AgriNova <span style={{ color: '#ADFF00', fontSize: '14px', fontFamily: 'JetBrains Mono, monospace' }}>AI</span>
        </span>
      </div>

      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            border: '1px solid rgba(173, 255, 0, 0.4)',
            backgroundColor: 'rgba(173, 255, 0, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ADFF00',
            fontSize: '12px',
            fontWeight: 600,
          }}
        >
          U
        </div>
      </div>
    </header>
  );
}