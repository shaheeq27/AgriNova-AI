'use client';

import React, { useState } from 'react';
import { useAira } from '@/hooks/useAira';
import { ConversationSidebar } from '@/components/aira/ConversationSidebar';
import { AiraHeader } from '@/components/aira/AiraHeader';
import { SuggestedQuestions } from '@/components/aira/SuggestedQuestions';
import { MessageList } from '@/components/aira/MessageList';
import { ChatComposer } from '@/components/aira/ChatComposer';

export default function AiraPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const aira = useAira();

  return (
    <div className="flex h-screen bg-[#0E0E0D] overflow-hidden fixed inset-0 z-50">
      <ConversationSidebar
        conversations={aira.conversations}
        currentId={aira.currentConversationId}
        onSelect={aira.loadConversation}
        onNew={aira.startNewConversation}
        onDelete={aira.deleteConversation}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#131412] relative">
        <AiraHeader 
          activeFarm={aira.activeFarm} 
          onToggleSidebar={() => setIsSidebarOpen(true)} 
        />

        <div className="flex-1 overflow-hidden relative">
          {aira.messages.length === 0 ? (
            <div className="h-full overflow-y-auto">
              <SuggestedQuestions onSelect={aira.sendMessage} />
            </div>
          ) : (
            <MessageList 
              messages={aira.messages} 
              isTyping={aira.isTyping} 
            />
          )}
        </div>

        <ChatComposer 
          onSend={aira.sendMessage} 
          onStop={aira.abortGeneration}
          isTyping={aira.isTyping}
          disabled={aira.isLoading}
        />
      </div>
    </div>
  );
}
