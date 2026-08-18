import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Square } from 'lucide-react';

interface ChatComposerProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isTyping: boolean;
  disabled?: boolean;
}

export function ChatComposer({ onSend, onStop, isTyping, disabled = false }: ChatComposerProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSend = () => {
    if (input.trim() && !isTyping && !disabled) {
      onSend(input);
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleStop = () => {
    if (onStop) {
      onStop();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full bg-[#1B1C1B]/80 backdrop-blur-md p-4 border-t border-white/5 relative z-20">
      <div className="max-w-4xl mx-auto relative">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Aira about your farm..."
          disabled={isTyping || disabled}
          className="w-full bg-[#2A2A29] text-[#E4E2E0] placeholder-[#8D928C] rounded-2xl py-4 pl-4 pr-14 outline-none border border-white/5 focus:border-[#ADFF00]/40 transition-colors resize-none overflow-y-auto"
          style={{ minHeight: '56px', maxHeight: '150px' }}
          rows={1}
        />
        {isTyping ? (
          <button
            onClick={handleStop}
            className="absolute right-2 top-2 bottom-2 aspect-square flex items-center justify-center rounded-xl bg-red-500/20 text-red-500 hover:bg-red-500/30 transition-colors active:scale-95"
            title="Stop generating"
          >
            <Square size={16} fill="currentColor" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className="absolute right-2 top-2 bottom-2 aspect-square flex items-center justify-center rounded-xl bg-[#ADFF00] text-[#131412] disabled:opacity-50 disabled:bg-[#343533] disabled:text-[#8D928C] transition-colors hover:bg-[#BDFF33] active:scale-95"
          >
            <Send size={20} />
          </button>
        )}
      </div>
    </div>
  );
}
