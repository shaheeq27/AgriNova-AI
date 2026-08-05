'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

interface AdvisorCardProps {
  message: string;
  onExecute?: () => void;
}

export default function AdvisorCard({ message, onExecute }: AdvisorCardProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);

  useEffect(() => {
    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < message.length) {
        setDisplayedText(message.slice(0, i + 1));
        i++;
      } else {
        clearInterval(typingInterval);
      }
    }, 30);
    return () => clearInterval(typingInterval);
  }, [message]);

  useEffect(() => {
    const cursorInterval = setInterval(() => setCursorVisible(v => !v), 500);
    return () => clearInterval(cursorInterval);
  }, []);

  return (
    <GlassCard style={{ borderLeft: '3px solid var(--accent-primary, #4ee86a)' }}>
      <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
        <div style={{ 
          width: '32px', 
          height: '32px', 
          borderRadius: '50%', 
          background: 'var(--accent-dim, #14402a)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          border: '1px solid var(--border, rgba(78, 232, 106, 0.08))',
          boxShadow: '0 0 12px rgba(78, 232, 106, 0.15)',
          animation: 'pulse 2s infinite cubic-bezier(0.4, 0, 0.2, 1)'
        }}>
          {/* Simple AI Icon placeholder */}
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-primary, #4ee86a)' }} />
        </div>
        
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--accent-primary, #4ee86a)', fontSize: '0.7rem', letterSpacing: '0.1em', marginBottom: '8px' }}>
            AI ADVISOR
          </div>
          <p style={{ color: 'var(--text-primary, #e8f5ec)', fontSize: '0.9rem', lineHeight: 1.6, margin: '0 0 20px 0', minHeight: '60px' }}>
            {displayedText}
            <span style={{ opacity: cursorVisible ? 1 : 0, transition: 'opacity 0.1s' }}>_</span>
          </p>
          
          {onExecute && (
            <button 
              onClick={onExecute}
              style={{
                background: 'var(--accent-dim, #14402a)',
                color: 'var(--accent-primary, #4ee86a)',
                border: '1px solid var(--border-hover, rgba(78, 232, 106, 0.16))',
                padding: '8px 16px',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono, "Space Mono")',
                fontSize: '0.75rem',
                letterSpacing: '0.05em',
                cursor: 'pointer',
                transition: 'all 250ms ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--accent-muted, #1a5a3a)';
                e.currentTarget.style.boxShadow = '0 0 8px rgba(78, 232, 106, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'var(--accent-dim, #14402a)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              EXECUTE SUGGESTION
            </button>
          )}
        </div>
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.05); opacity: 0.8; }
        }
      `}} />
    </GlassCard>
  );
}
