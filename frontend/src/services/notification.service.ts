import { request } from '../lib/api';

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: string;
  severity: string;
  is_read: boolean;
  related_entity_type?: string;
  related_entity_id?: string;
  created_at: string;
}

export interface NotificationListResponse {
  items: NotificationItem[];
  total: number;
  unread_count: number;
}

export interface NotificationPreferences {
  email_enabled: boolean;
  weather_alerts: boolean;
  irrigation_reminders: boolean;
  fertilizer_reminders: boolean;
  market_alerts: boolean;
  ai_insights: boolean;
}

export const notificationAPI = {
  getNotifications: async (unread_only: boolean = false, category?: string, skip: number = 0, limit: number = 50) => {
    const params = new URLSearchParams();
    if (unread_only) params.append('unread_only', 'true');
    if (category) params.append('category', category);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    
    return request<NotificationListResponse>(`/notifications?${params.toString()}`);
  },
  
  getUnreadCount: async () => {
    return request<{count: number}>('/notifications/unread-count');
  },
  
  markRead: async (id: string) => {
    return request<{id: string, is_read: boolean}>(`/notifications/${id}/read`, {
      method: 'PUT'
    });
  },
  
  markAllRead: async () => {
    return request<{updated_count: number}>('/notifications/read-all', {
      method: 'PUT'
    });
  },
  
  getPreferences: async () => {
    return request<NotificationPreferences>('/preferences/notifications');
  },
  
  updatePreferences: async (data: Partial<NotificationPreferences>) => {
    return request<NotificationPreferences>('/preferences/notifications', {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
};
