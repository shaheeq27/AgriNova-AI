import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import TypingIndicator from '../ai/TypingIndicator';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  isTyping?: boolean;
  interrupted?: boolean;
}

export function MessageBubble({ role, content, isTyping = false, interrupted = false }: MessageBubbleProps) {
  const isAI = role === 'assistant';

  // Strip any accidental internal context blocks the LLM might leak
  // e.g. [FARM CONTEXT]...[/FARM CONTEXT]
  const cleanContent = content.replace(/\[[A-Z\s]+\][\s\S]*?\[\/[A-Z\s]+\]/g, '').trim();

  return (
    <div className={`flex w-full ${isAI ? 'justify-start' : 'justify-end'} mb-6 group`}>
      <div className={`flex gap-4 max-w-[85%] ${isAI ? 'flex-row' : 'flex-row-reverse'}`}>
        
        {/* Avatar */}
        <div className="flex-shrink-0 mt-1">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center border ${
            isAI 
              ? 'bg-[#1F201F] border-[#ADFF00]/30 text-[#ADFF00]' 
              : 'bg-[#574238] border-[#FBDFCE]/30 text-[#FBDFCE]'
          }`}>
            {isAI ? <Bot size={16} strokeWidth={1.75} /> : <User size={16} strokeWidth={1.75} />}
          </div>
        </div>

        {/* Bubble */}
        <div className={`px-5 py-4 rounded-2xl relative ${
          isAI
            ? 'bg-[#1B1C1B] border border-[#ADFF00]/10 rounded-tl-sm text-[#E4E2E0]'
            : 'bg-[#2A2A29] border border-white/5 rounded-tr-sm text-[#E4E2E0]'
        }`}>
          {isTyping ? (
            <div className="py-2">
              <TypingIndicator />
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <div className={`prose prose-invert max-w-none ${isAI ? 'prose-a:text-[#ADFF00]' : ''}`}>
                <ReactMarkdown>
                  {cleanContent}
                </ReactMarkdown>
              </div>
              {interrupted && (
                <div className="text-sm text-yellow-500/80 italic mt-2 border-t border-yellow-500/20 pt-2">
                  Aira's response was interrupted. You can try again.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
