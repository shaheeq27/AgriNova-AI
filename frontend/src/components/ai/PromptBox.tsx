'use client';
import React, { useState } from 'react';

export default function PromptBox({ onSend }: { onSend?: (text: string) => void }) {
  const [text, setText] = useState('');
  const [focus, setFocus] = useState(false);

  return (
    <div style={{ 
      display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 16px',
      backgroundColor: 'var(--surface)', borderRadius: '24px', border: `1px solid ${focus ? 'var(--accent-primary)' : 'var(--border)'}`,
      transition: 'all 0.3s ease', boxShadow: focus ? '0 0 12px var(--accent-glow)' : 'none'
    }}>
      <input 
        type="text" value={text} onChange={e => setText(e.target.value)}
        onFocus={() => setFocus(true)} onBlur={() => setFocus(false)}
        placeholder="Ask Advisor..." 
        style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--text-primary)', outline: 'none', fontSize: '15px' }}
      />
      <button 
        onClick={() => { if (onSend && text) onSend(text); setText(''); }}
        style={{ background: 'transparent', border: 'none', color: text ? 'var(--accent-primary)' : 'var(--text-muted)', cursor: 'pointer', transition: 'color 0.3s ease' }}>
        <span style={{ fontSize: '20px' }}>↗</span>
      </button>
    </div>
  );
}