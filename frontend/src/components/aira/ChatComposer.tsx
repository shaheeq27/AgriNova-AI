'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, Send, Square } from 'lucide-react';

interface ChatComposerProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isTyping: boolean;
  disabled?: boolean;
  error?: string | null;
}

export function ChatComposer({
  onSend,
  onStop,
  isTyping,
  disabled = false,
  error,
}: ChatComposerProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = '0px';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  }, [input]);

  const handleSend = () => {
    const message = input.trim();

    if (!message || isTyping || disabled) return;

    onSend(message);
    setInput('');

    if (textareaRef.current) {
      textareaRef.current.style.height = '0px';
    }
  };

  const handleStop = () => {
    onStop?.();
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        width: '100%',
        flexShrink: 0,
        padding: '0 24px 24px 24px',
        boxSizing: 'border-box',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '960px',
          margin: '0 auto',
          boxSizing: 'border-box',
        }}
      >
        {error && (
          <div
            style={{
              marginBottom: '8px',
              display: 'flex',
              width: '100%',
              alignItems: 'center',
              gap: '8px',
              borderRadius: '16px',
              border: '1px solid rgba(239,68,68,0.2)',
              background: 'rgba(239,68,68,0.1)',
              padding: '8px 16px',
              fontSize: '14px',
              color: '#f87171',
              boxSizing: 'border-box',
            }}
          >
            <AlertCircle size={16} style={{ flexShrink: 0 }} />

            <span
              style={{
                minWidth: 0,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {error}
            </span>
          </div>
        )}

        <div
          style={{
            width: '100%',
            minHeight: '64px',
            display: 'flex',
            alignItems: 'center',
            boxSizing: 'border-box',
            borderRadius: '32px',
            border: '1px solid rgba(255,255,255,0.10)',
            background: '#1B1C1B',
            padding: '7px 8px 7px 22px',
            boxShadow: '0 6px 24px rgba(0,0,0,0.28)',
            transition: 'border-color 200ms ease',
          }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Aira about your farm..."
            disabled={isTyping || disabled}
            rows={1}
            style={{
              flex: 1,
              minWidth: 0,
              width: '100%',
              maxHeight: '120px',
              resize: 'none',
              overflow: 'hidden',
              border: 'none',
              outline: 'none',
              background: 'transparent',
              color: '#E4E2E0',
              fontSize: '15px',
              lineHeight: '22px',
              padding: '8px 8px 8px 0',
              fontFamily: 'inherit',
              boxSizing: 'border-box',
            }}
          />

          <div
            style={{
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginLeft: '8px',
            }}
          >
            {isTyping ? (
              <button
                type="button"
                onClick={handleStop}
                title="Stop generating"
                style={{
                  width: '48px',
                  height: '48px',
                  flexShrink: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '50%',
                  border: '1px solid rgba(239,68,68,0.2)',
                  background: 'rgba(239,68,68,0.1)',
                  color: '#ef4444',
                  cursor: 'pointer',
                }}
              >
                <Square size={15} fill="currentColor" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSend}
                disabled={!input.trim() || disabled}
                title="Send message"
                style={{
                  width: '48px',
                  height: '48px',
                  flexShrink: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  borderRadius: '50%',
                  border: 'none',
                  background: input.trim() && !disabled
                    ? '#ADFF00'
                    : '#2A2A29',
                  color: input.trim() && !disabled
                    ? '#131412'
                    : '#8D928C',
                  cursor: input.trim() && !disabled
                    ? 'pointer'
                    : 'not-allowed',
                  boxShadow: input.trim() && !disabled
                    ? '0 0 10px rgba(173,255,0,0.16)'
                    : 'none',
                  margin: 0,
                }}
              >
                <Send size={17} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}