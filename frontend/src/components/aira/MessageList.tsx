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
    <div className="w-full flex flex-col gap-4 px-6 md:px-12 py-6 pb-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} role={msg.role} content={msg.content} interrupted={msg.interrupted} />
      ))}
      {isTyping && (
        <MessageBubble role="assistant" content="" isTyping={true} />
      )}
      <div ref={bottomRef} className="h-4" />
    </div>
  );
}
