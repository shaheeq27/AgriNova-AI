'use client';
import React from 'react';
import ChatBubble from './ChatBubble';

interface AIResponseProps { message: string; actions?: React.ReactNode; }

export default function AIResponse({ message, actions }: AIResponseProps) {
  return (
    <div style={{ backgroundColor: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '12px', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 16px', borderBottom: '1px solid var(--border)', backgroundColor: 'var(--surface-hover)' }}>
        <span style={{ fontSize: '18px' }}>🧠</span>
        <span style={{ fontFamily: 'Space Mono', fontSize: '12px', color: 'var(--accent-primary)', letterSpacing: '1px' }}>AI ADVISOR</span>
      </div>
      <div style={{ padding: '16px' }}>
        <ChatBubble isAI message={message} />
      </div>
      {actions && <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', display: 'flex', gap: '8px' }}>{actions}</div>}
    </div>
  );
}