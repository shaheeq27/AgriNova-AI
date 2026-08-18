import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { MessageData } from '@/services/aira.service';

interface MessageListProps {
  messages: MessageData[];
  isTyping: boolean;
}

export function MessageList({ messages, isTyping }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-8 custom-scrollbar">
      <div className="max-w-4xl mx-auto flex flex-col">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} interrupted={msg.interrupted} />
        ))}
        {isTyping && (
          <MessageBubble role="assistant" content="" isTyping={true} />
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
