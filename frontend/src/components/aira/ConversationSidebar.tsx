import React, { useMemo } from 'react';
import { Plus, Trash2, X, MessageSquare, Sprout } from 'lucide-react';
import { ConversationData } from '@/services/aira.service';
import { SidebarState } from '@/app/(app)/aira/page';

interface ConversationSidebarProps {
  conversations: ConversationData[];
  currentId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  desktopState: SidebarState;
}

export function ConversationSidebar({
  conversations,
  currentId,
  onSelect,
  onNew,
  onDelete,
  mobileOpen,
  onCloseMobile,
  desktopState
}: ConversationSidebarProps) {
  
  const isExpanded = desktopState === 'expanded';
  const isMinimized = desktopState === 'minimized';
  const isHidden = desktopState === 'hidden';

  const transitionStyle: React.CSSProperties = {
    transition: 'all 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  };

  const hiddenStyle: React.CSSProperties = {
    width: 0,
    minWidth: 0,
    flexBasis: 0,
    padding: 0,
    margin: 0,
    borderWidth: 0,
    opacity: 0,
    overflow: 'hidden' as const,
  };

  // Group conversations by date
  const groupedConversations = useMemo(() => {
    const today: ConversationData[] = [];
    const prev7: ConversationData[] = [];
    const older: ConversationData[] = [];
    
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    conversations.forEach(conv => {
      const convDate = new Date(conv.updated_at).toISOString().split('T')[0];
      if (convDate === todayStr) {
        today.push(conv);
      } else if (convDate >= sevenDaysAgo) {
        prev7.push(conv);
      } else {
        older.push(conv);
      }
    });

    return { today, prev7, older };
  }, [conversations]);

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDateLabel = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - d.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays}d ago`;
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  };

  const renderGroup = (label: string, items: ConversationData[], isToday = false) => {
    if (items.length === 0) return null;

    return (
      <div className="mb-6">
        {!isMinimized && (
          <div className="px-4 py-2 type-body-sm text-[#8D928C] mb-1">
            {label}
          </div>
        )}
        <div className="flex flex-col gap-1">
          {items.map(conv => (
            <div 
              key={conv.id}
              title={conv.title || 'New Conversation'}
              className={`
                group flex items-center p-3 mx-2 rounded-xl cursor-pointer transition-colors
                ${currentId === conv.id ? 'bg-[#2A2A29] text-white' : 'hover:bg-[#2A2A29] text-[#C4C8C1]'}
                ${isMinimized ? 'justify-center mx-1 px-0' : 'justify-between'}
              `}
              onClick={() => { onSelect(conv.id); onCloseMobile(); }}
            >
              <div className={`flex items-center gap-3 overflow-hidden ${isMinimized ? 'justify-center' : ''}`}>
                <div className={`flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg ${currentId === conv.id ? 'bg-[#ADFF00]/10 text-[#ADFF00]' : 'bg-[#1F201F] text-[#8D928C]'}`}>
                  {currentId === conv.id ? <Sprout size={16} /> : <MessageSquare size={16} />}
                </div>
                {!isMinimized && (
                  <span className="truncate text-[14px] font-medium text-[#C4C8C1] group-hover:text-white transition-colors">
                    {conv.title || 'New Conversation'}
                  </span>
                )}
              </div>
              
              {!isMinimized && (
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="text-[12px] text-[#8D928C] group-hover:hidden">
                    {isToday ? formatTime(conv.updated_at) : formatDateLabel(conv.updated_at)}
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(conv.id);
                    }}
                    title="Delete Conversation"
                    className="p-1.5 rounded-md hover:bg-red-500/20 hover:text-red-400 text-[#8D928C] hidden group-hover:block transition-all"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Mobile Overlay */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden" 
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <div 
        className={`
          fixed md:static inset-y-0 left-0 z-50 
          bg-[#131412] flex flex-col
          ${mobileOpen ? 'translate-x-0 w-[280px] border-r border-white/5' : '-translate-x-full md:translate-x-0'}
          ${!mobileOpen && isExpanded ? 'md:w-[260px] border-r border-white/5' : ''}
          ${!mobileOpen && isMinimized ? 'md:w-[64px] border-r border-white/5' : ''}
        `}
        style={{
          ...transitionStyle,
          ...((!mobileOpen && isHidden) ? hiddenStyle : {})
        }}
      >
        <div className="p-4 flex flex-col gap-4 border-b border-transparent">
          {/* Header */}
          <div className={`flex items-center ${isMinimized ? 'justify-center' : 'justify-between'} h-8`}>
            {!isMinimized && (
              <h3 className="text-white font-medium text-[16px] flex items-center gap-2">
                Conversations
              </h3>
            )}
            <button 
              onClick={onCloseMobile}
              className="md:hidden p-2 text-[#8D928C] hover:text-white flex-shrink-0"
            >
              <X size={20} />
            </button>
          </div>

          {/* New Conversation Button */}
          <button
            onClick={() => { onNew(); onCloseMobile(); }}
            title="New Conversation"
            className={`
              flex items-center justify-center gap-2 rounded-xl transition-all duration-300
              ${isMinimized 
                ? 'w-10 h-10 bg-[#1F201F] text-[#ADFF00] hover:bg-[#ADFF00]/10 mx-auto' 
                : 'w-full py-3 bg-[#1F201F] text-[#ADFF00] hover:bg-[#ADFF00]/10 border border-[#ADFF00]/10 font-medium text-[14px]'
              }
            `}
          >
            <Plus size={isMinimized ? 20 : 18} />
            {!isMinimized && <span>New Conversation</span>}
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto py-2 custom-scrollbar">
          {conversations.length === 0 ? (
            <div className="text-center p-4 text-[#8D928C] text-[13px] mt-4">
              {!isMinimized && "No conversations yet"}
            </div>
          ) : (
            <div className="flex flex-col">
              {renderGroup('Today', groupedConversations.today, true)}
              {renderGroup('Previous 7 Days', groupedConversations.prev7)}
              {renderGroup('Older', groupedConversations.older)}
              
              {!isMinimized && conversations.length > 0 && (
                <div className="text-center py-6 text-[12px] text-[#8D928C]/50">
                  No more conversations
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
