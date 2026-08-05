'use client';
import React, { useState } from 'react';

interface FABProps { icon: React.ReactNode; onClick: () => void; label?: string; }

export default function FloatingActionButton({ icon, onClick, label }: FABProps) {
  const [hover, setHover] = useState(false);
  return (
    <button 
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)} onClick={onClick}
      style={{
        position: 'fixed', bottom: '80px', right: '24px', width: '56px', height: '56px',
        borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))',
        border: 'none', color: '#000', display: 'flex', justifyContent: 'center', alignItems: 'center',
        cursor: 'pointer', zIndex: 40, transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: hover ? '0 0 20px var(--accent-primary)' : '0 4px 12px rgba(0,0,0,0.5)',
        transform: hover ? 'scale(1.05)' : 'scale(1)'
      }}>
      {icon}
    </button>
  );
}