import { useState, useEffect, useCallback } from 'react';
import { notificationAPI, NotificationItem, NotificationPreferences } from '../services/notification.service';

export function useNotifications() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination & Filtering state
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [unreadOnly, setUnreadOnly] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [skip, setSkip] = useState<number>(0);
  
  const LIMIT = 10;

  const fetchNotifications = useCallback(async (reset: boolean = false) => {
    try {
      setLoading(true);
      const currentSkip = reset ? 0 : skip;
      
      const response = await notificationAPI.getNotifications(unreadOnly, category, currentSkip, LIMIT);
      
      if (reset) {
        setNotifications(response.items);
      } else {
        setNotifications(prev => [...prev, ...response.items]);
      }
      
      setUnreadCount(response.unread_count);
      setHasMore(response.items.length === LIMIT);
      setSkip(currentSkip + LIMIT);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch notifications');
    } finally {
      setLoading(false);
    }
  }, [category, unreadOnly, skip]);

  const refreshUnreadCount = useCallback(async () => {
    try {
      const response = await notificationAPI.getUnreadCount();
      setUnreadCount(response.count);
    } catch (err) {
      console.error('Failed to fetch unread count', err);
    }
  }, []);

  const markRead = async (id: string) => {
    try {
      await notificationAPI.markRead(id);
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark read', err);
    }
  };

  const markAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all read', err);
    }
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchNotifications(false);
    }
  };

  // Reset when filters change
  useEffect(() => {
    const timer = setTimeout(() => fetchNotifications(true), 0);
    return () => clearTimeout(timer);
  }, [category, unreadOnly]); // eslint-disable-line react-hooks/exhaustive-deps

  // Initial load
  useEffect(() => {
    const timer = setTimeout(() => refreshUnreadCount(), 0);
    // Refresh count periodically (e.g., every 60s)
    const interval = setInterval(refreshUnreadCount, 60000);
    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    };
  }, [refreshUnreadCount]);

  return {
    notifications,
    unreadCount,
    loading,
    error,
    category,
    setCategory,
    unreadOnly,
    setUnreadOnly,
    hasMore,
    loadMore,
    markRead,
    markAllRead,
    refreshUnreadCount,
    refresh: () => fetchNotifications(true)
  };
}

export function useNotificationPreferences() {
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchPrefs = async () => {
      try {
        setLoading(true);
        const prefs = await notificationAPI.getPreferences();
        setPreferences(prefs);
        setError(null);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to fetch preferences');
      } finally {
        setLoading(false);
      }
    };
    fetchPrefs();
  }, []);

  const updatePreferences = async (data: Partial<NotificationPreferences>) => {
    try {
      setSaving(true);
      const updated = await notificationAPI.updatePreferences(data);
      setPreferences(updated);
      setError(null);
      return true;
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update preferences');
      return false;
    } finally {
      setSaving(false);
    }
  };

  return { preferences, loading, error, saving, updatePreferences };
}
