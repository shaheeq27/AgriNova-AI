'use client';
import React from 'react';
import TypingIndicator from './TypingIndicator';

interface ChatBubbleProps { message?: string; isAI?: boolean; timestamp?: string; typing?: boolean; }

export default function ChatBubble({ message, isAI = false, timestamp, typing = false }: ChatBubbleProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: isAI ? 'flex-start' : 'flex-end', marginBottom: '16px' }}>
      <div style={{ 
        maxWidth: '80%', padding: '12px 16px', borderRadius: '12px',
        backgroundColor: isAI ? 'var(--surface-hover)' : 'var(--accent-dim)',
        borderLeft: isAI ? '3px solid var(--accent-primary)' : 'none',
        borderRight: !isAI ? '3px solid var(--accent-secondary)' : 'none',
        color: 'var(--text-primary)', fontSize: '15px', lineHeight: '1.5'
      }}>
        {typing ? <TypingIndicator /> : message}
      </div>
      {timestamp && <span style={{ fontFamily: 'Space Mono', fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>{timestamp}</span>}
    </div>
  );
}