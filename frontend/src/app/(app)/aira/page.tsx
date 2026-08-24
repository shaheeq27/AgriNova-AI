'use client';

import React, { useState, useEffect } from 'react';
import { useAira } from '@/hooks/useAira';
import { ConversationSidebar } from '@/components/aira/ConversationSidebar';
import { AiraHeader } from '@/components/aira/AiraHeader';
import { SuggestedQuestions } from '@/components/aira/SuggestedQuestions';
import { MessageList } from '@/components/aira/MessageList';
import { ChatComposer } from '@/components/aira/ChatComposer';

export type SidebarState = 'expanded' | 'minimized' | 'hidden';

export default function AiraPage() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopState, setDesktopState] =
    useState<SidebarState>('expanded');

  const aira = useAira();

  useEffect(() => {
    const saved = localStorage.getItem(
      'airaSidebarState'
    ) as SidebarState | null;

    if (
      saved &&
      ['expanded', 'minimized', 'hidden'].includes(saved)
    ) {
      const restoreSidebarState = window.setTimeout(() => {
        setDesktopState(saved);
      }, 0);

      return () => window.clearTimeout(restoreSidebarState);
    }
  }, []);

  const cycleSidebarState = () => {
    setDesktopState((prev) => {
      const next: SidebarState =
        prev === 'expanded'
          ? 'minimized'
          : prev === 'minimized'
            ? 'hidden'
            : 'expanded';

      localStorage.setItem('airaSidebarState', next);

      return next;
    });
  };

  const hasMessages = aira.messages.length > 0;

  return (
    <div className="flex flex-col flex-1 min-h-0 w-full bg-[#131412] overflow-hidden rounded-2xl border border-white/5 shadow-2xl">

      {/* Header */}
      <AiraHeader
        activeFarm={aira.activeFarm}
        onToggleMobileSidebar={() =>
          setMobileSidebarOpen(true)
        }
        desktopState={desktopState}
        onCycleDesktopSidebar={cycleSidebarState}
      />

      {/* Workspace */}
      <div className="flex flex-1 min-h-0 overflow-hidden">

        {/* Conversation Sidebar */}
        <ConversationSidebar
          conversations={aira.conversations}
          currentId={aira.currentConversationId}
          onSelect={aira.loadConversation}
          onNew={aira.startNewConversation}
          onDelete={aira.deleteConversation}
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() =>
            setMobileSidebarOpen(false)
          }
          desktopState={desktopState}
        />

        {/* Main Chat */}
        <main className="flex-1 min-w-0 min-h-0 flex flex-col overflow-hidden">

          {/* Messages / Empty State */}
          <div
            className={`
              flex-1
              min-h-0
              min-w-0
              overflow-y-auto
              overflow-x-hidden
              scrollbar-thin
              scrollbar-thumb-white/10
              scrollbar-track-transparent
              ${!hasMessages
                ? 'flex items-center justify-center'
                : ''
              }
            `}
          >
            {!hasMessages ? (
              <div className="w-full min-h-full flex items-center justify-center px-4 py-8">
                <SuggestedQuestions
                  onSelect={aira.sendMessage}
                />
              </div>
            ) : (
              <MessageList
                messages={aira.messages}
                isTyping={aira.isTyping}
              />
            )}
          </div>

          {/* Composer Area */}
          <div className="flex-shrink-0 w-full">
            <ChatComposer
              onSend={aira.sendMessage}
              onStop={aira.abortGeneration}
              isTyping={aira.isTyping}
              disabled={aira.isLoading}
              error={aira.error}
            />
          </div>
        </main>
      </div>
    </div>
  );
}