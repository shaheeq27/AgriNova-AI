import React, { useRef, useEffect } from 'react';
import { X, CheckCircle, Bell, Loader2 } from 'lucide-react';
import { useNotifications } from '../../hooks/useNotifications';
import { NotificationItem } from './NotificationItem';
import { Button } from '../../ui/Button';

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const CATEGORIES = [
  { id: 'all', label: 'All' },
  { id: 'weather', label: 'Weather' },
  { id: 'irrigation', label: 'Irrigation' },
  { id: 'fertilizer', label: 'Fertilizer' },
  { id: 'market', label: 'Market' },
  { id: 'ai', label: 'AI' }
];

export function NotificationDrawer({ isOpen, onClose }: NotificationDrawerProps) {
  const { 
    notifications, 
    loading, 
    category, 
    setCategory, 
    markRead, 
    markAllRead, 
    hasMore, 
    loadMore,
    unreadCount
  } = useNotifications();
  
  const drawerRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (isOpen && drawerRef.current && !drawerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop overlay for mobile (optional, but good for focus) */}
      <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 sm:hidden" onClick={onClose} />
      
      {/* Drawer */}
      <div 
        ref={drawerRef}
        className="fixed inset-y-0 right-0 z-50 w-full sm:w-[400px] bg-gray-900 border-l border-gray-800 shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-gray-400" />
            <h2 className="text-lg font-semibold text-white">Notifications</h2>
            {unreadCount > 0 && (
              <span className="bg-primary-500/20 text-primary-400 text-xs px-2 py-0.5 rounded-full font-medium">
                {unreadCount} new
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <button 
                onClick={() => markAllRead()}
                className="text-xs text-gray-400 hover:text-white transition-colors flex items-center gap-1 p-2 rounded-md hover:bg-gray-800"
                title="Mark all as read"
              >
                <CheckCircle className="h-4 w-4" />
                <span className="sr-only sm:not-sr-only">Mark all read</span>
              </button>
            )}
            <button 
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Categories */}
        <div className="p-3 border-b border-gray-800 overflow-x-auto scrollbar-hide">
          <div className="flex gap-2">
            {CATEGORIES.map(cat => {
              const isActive = (cat.id === 'all' && !category) || cat.id === category;
              return (
                <button
                  key={cat.id}
                  onClick={() => setCategory(cat.id === 'all' ? undefined : cat.id)}
                  className={`px-3 py-1.5 text-xs font-medium rounded-full whitespace-nowrap transition-colors ${
                    isActive 
                      ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' 
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300 border border-transparent'
                  }`}
                >
                  {cat.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          {notifications.length === 0 && !loading ? (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center text-gray-500">
              <Bell className="h-12 w-12 text-gray-700 mb-4" />
              <p className="text-sm">You have no notifications in this category.</p>
            </div>
          ) : (
            <div className="flex flex-col">
              {notifications.map(notification => (
                <NotificationItem 
                  key={notification.id} 
                  notification={notification} 
                  onMarkRead={markRead}
                />
              ))}
              
              {/* Load More */}
              {hasMore && (
                <div className="p-4 flex justify-center border-t border-gray-800/50">
                  <Button 
                    variant="secondary" 
                    size="sm" 
                    onClick={loadMore} 
                    disabled={loading}
                    className="w-full text-xs"
                  >
                    {loading ? (
                      <><Loader2 className="mr-2 h-3 w-3 animate-spin" /> Loading...</>
                    ) : (
                      'Load older notifications'
                    )}
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
