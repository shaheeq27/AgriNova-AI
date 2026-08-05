'use client';
import React, { useState } from 'react';

interface SuggestionProps { text: string; onClick?: () => void; }

export default function Suggestion({ text, onClick }: SuggestionProps) {
  const [hover, setHover] = useState(false);
  return (
    <button 
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)} onClick={onClick}
      style={{
        padding: '8px 16px', borderRadius: '20px', backgroundColor: 'transparent',
        border: `1px solid ${hover ? 'var(--accent-primary)' : 'var(--border)'}`,
        color: hover ? 'var(--text-primary)' : 'var(--text-muted)', cursor: 'pointer',
        fontSize: '13px', transition: 'all 0.3s ease'
      }}>
      {text}
    </button>
  );
}