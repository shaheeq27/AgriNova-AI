import React from 'react';
import { Bell, Droplets, Leaf, TrendingUp, Sparkles, Settings } from 'lucide-react';
import { NotificationItem as NotificationItemType } from '../../services/notification.service';

interface NotificationItemProps {
  notification: NotificationItemType;
  onMarkRead: (id: string) => void;
}

function timeAgo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  let interval = Math.floor(seconds / 31536000);
  if (interval >= 1) return interval + ' year' + (interval > 1 ? 's' : '') + ' ago';
  
  interval = Math.floor(seconds / 2592000);
  if (interval >= 1) return interval + ' month' + (interval > 1 ? 's' : '') + ' ago';
  
  interval = Math.floor(seconds / 86400);
  if (interval >= 1) return interval + ' day' + (interval > 1 ? 's' : '') + ' ago';
  
  interval = Math.floor(seconds / 3600);
  if (interval >= 1) return interval + ' hour' + (interval > 1 ? 's' : '') + ' ago';
  
  interval = Math.floor(seconds / 60);
  if (interval >= 1) return interval + ' min' + (interval > 1 ? 's' : '') + ' ago';
  
  return 'just now';
}

export function NotificationItem({ notification, onMarkRead }: NotificationItemProps) {
  const getIcon = (type: string) => {
    if (type.includes('weather')) return <Bell className="h-5 w-5 text-blue-400" />;
    if (type.includes('irrigation')) return <Droplets className="h-5 w-5 text-blue-500" />;
    if (type.includes('fertilizer') || type.includes('harvest')) return <Leaf className="h-5 w-5 text-green-500" />;
    if (type.includes('market')) return <TrendingUp className="h-5 w-5 text-purple-500" />;
    if (type.includes('ai_')) return <Sparkles className="h-5 w-5 text-amber-500" />;
    return <Settings className="h-5 w-5 text-gray-400" />;
  };

  return (
    <div 
      className={`p-4 border-b border-gray-800/50 hover:bg-gray-800/50 transition-colors ${!notification.is_read ? 'bg-gray-800/20' : ''}`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-1 shrink-0 p-2 rounded-full bg-gray-800">
          {getIcon(notification.type)}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start gap-2">
            <h4 className={`text-sm font-medium ${!notification.is_read ? 'text-white' : 'text-gray-300'}`}>
              {notification.title}
            </h4>
            <span className="text-xs text-gray-500 whitespace-nowrap">
              {timeAgo(notification.created_at)}
            </span>
          </div>
          
          <p className={`text-sm mt-1 line-clamp-2 ${!notification.is_read ? 'text-gray-300' : 'text-gray-400'}`}>
            {notification.message}
          </p>
          
          {!notification.is_read && (
            <button 
              onClick={() => onMarkRead(notification.id)}
              className="text-xs text-primary-400 hover:text-primary-300 mt-2 font-medium"
            >
              Mark as read
            </button>
          )}
        </div>
        
        {!notification.is_read && (
          <div className="shrink-0 w-2 h-2 mt-2 rounded-full bg-primary-500" />
        )}
      </div>
    </div>
  );
}
