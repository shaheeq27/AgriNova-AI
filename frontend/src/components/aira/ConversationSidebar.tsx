import React from 'react';
import { Plus, MessageSquare, Trash2, X } from 'lucide-react';
import { ConversationData } from '@/services/aira.service';

interface ConversationSidebarProps {
  conversations: ConversationData[];
  currentId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function ConversationSidebar({
  conversations,
  currentId,
  onSelect,
  onNew,
  onDelete,
  isOpen,
  onClose
}: ConversationSidebarProps) {
  
  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden" 
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <div className={`
        fixed md:static inset-y-0 left-0 z-50 
        w-72 bg-[#131412] border-r border-white/5 
        flex flex-col transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        {/* Header / New Chat */}
        <div className="p-4 border-b border-white/5 flex items-center justify-between">
          <button
            onClick={() => { onNew(); onClose(); }}
            className="flex-1 flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[#ADFF00]/10 text-[#ADFF00] hover:bg-[#ADFF00]/20 transition-colors font-medium text-sm"
          >
            <Plus size={18} />
            <span>New Conversation</span>
          </button>
          <button 
            onClick={onClose}
            className="md:hidden ml-2 p-2 text-[#8D928C] hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
          {conversations.length === 0 ? (
            <div className="text-center p-4 text-[#8D928C] type-body-sm mt-4">
              No conversations yet
            </div>
          ) : (
            <div className="flex flex-col gap-1">
              {conversations.map(conv => (
                <div 
                  key={conv.id}
                  className={`
                    group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors
                    ${currentId === conv.id ? 'bg-[#2A2A29] text-white' : 'hover:bg-[#1B1C1B] text-[#C4C8C1]'}
                  `}
                  onClick={() => { onSelect(conv.id); onClose(); }}
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    <MessageSquare size={16} className={currentId === conv.id ? 'text-[#ADFF00]' : 'text-[#8D928C]'} />
                    <span className="truncate text-sm font-medium">
                      {conv.title || 'New Conversation'}
                    </span>
                  </div>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(conv.id);
                    }}
                    className={`p-1.5 rounded-md hover:bg-red-500/20 hover:text-red-400 text-[#8D928C] opacity-0 group-hover:opacity-100 transition-all`}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
