'use client';

import React from 'react';
import { useNotificationPreferences } from '@/hooks/useNotifications';
import { Loader2, Mail, Bell, Droplets, Leaf, TrendingUp, Sparkles } from 'lucide-react';

export function NotificationSettings() {
  const { preferences, loading, saving, error, updatePreferences } = useNotificationPreferences();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '32px', color: '#9ca3af' }}>
        <Loader2 className="animate-spin" style={{ width: '24px', height: '24px', marginRight: '8px' }} />
        <span>Loading preferences...</span>
      </div>
    );
  }

  if (error || !preferences) {
    return (
      <div style={{ padding: '16px', borderRadius: '20px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#f87171', fontSize: '14px' }}>
        Failed to load notification preferences: {error || 'Unknown error'}
      </div>
    );
  }

  const handleToggle = (key: keyof typeof preferences) => {
    updatePreferences({ [key]: !preferences[key] });
  };

  const RenderToggle = ({ id, checked }: { id: string, checked: boolean }) => (
    <button
      onClick={() => handleToggle(id as any)}
      disabled={saving}
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        width: '44px',
        height: '24px',
        borderRadius: '9999px',
        backgroundColor: checked ? 'var(--primary-500, #2e7d32)' : '#374151',
        border: 'none',
        cursor: saving ? 'not-allowed' : 'pointer',
        opacity: saving ? 0.5 : 1,
        transition: 'background-color 0.2s',
        padding: 0
      }}
    >
      <span
        style={{
          display: 'inline-block',
          width: '18px',
          height: '18px',
          backgroundColor: '#ffffff',
          borderRadius: '50%',
          transform: checked ? 'translateX(22px)' : 'translateX(4px)',
          transition: 'transform 0.2s'
        }}
      />
    </button>
  );

  return (
    <div style={{
      width: '100%',
      padding: '32px',
      borderRadius: '20px',
      border: '1px solid rgba(75, 85, 99, 0.4)',
      backgroundColor: 'rgba(17, 24, 39, 0.5)',
      boxSizing: 'border-box'
    }}>
      <h2 style={{
        fontFamily: 'Playfair Display, serif',
        fontSize: '24px',
        fontWeight: 600,
        margin: 0,
        color: '#ffffff'
      }}>Notification Settings</h2>

      <div style={{ marginTop: '24px' }}>
        {/* Master Email Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', minHeight: '56px', marginBottom: '16px' }}>
          <div style={{ width: '20px', height: '20px', color: '#60a5fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Mail size={20} />
          </div>
          <div style={{ flex: 1, marginLeft: '14px' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Email Notifications</div>
            <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '2px' }}>Receive important alerts and digests via email</div>
          </div>
          <RenderToggle id="email_enabled" checked={preferences.email_enabled} />
        </div>

        {/* Weather Alerts */}
        <div style={{ display: 'flex', alignItems: 'center', minHeight: '56px', marginBottom: '16px' }}>
          <div style={{ width: '20px', height: '20px', color: '#60a5fa', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Bell size={20} />
          </div>
          <div style={{ flex: 1, marginLeft: '14px' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Weather Alerts</div>
            <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '2px' }}>Severe weather warnings and extreme forecasts</div>
          </div>
          <RenderToggle id="weather_alerts" checked={preferences.weather_alerts} />
        </div>

        {/* Irrigation Reminders */}
        <div style={{ display: 'flex', alignItems: 'center', minHeight: '56px', marginBottom: '16px' }}>
          <div style={{ width: '20px', height: '20px', color: '#3b82f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Droplets size={20} />
          </div>
          <div style={{ flex: 1, marginLeft: '14px' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Irrigation Reminders</div>
            <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '2px' }}>Scheduled watering based on soil moisture and crop needs</div>
          </div>
          <RenderToggle id="irrigation_reminders" checked={preferences.irrigation_reminders} />
        </div>

        {/* Fertilizer Reminders */}
        <div style={{ display: 'flex', alignItems: 'center', minHeight: '56px', marginBottom: '16px' }}>
          <div style={{ width: '20px', height: '20px', color: '#22c55e', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Leaf size={20} />
          </div>
          <div style={{ flex: 1, marginLeft: '14px' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Fertilizer Reminders</div>
            <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '2px' }}>Nutrient application schedules and recommendations</div>
          </div>
          <RenderToggle id="fertilizer_reminders" checked={preferences.fertilizer_reminders} />
        </div>

        {/* Market Alerts */}
        <div style={{ display: 'flex', alignItems: 'center', minHeight: '56px', marginBottom: '16px' }}>
          <div style={{ width: '20px', height: '20px', color: '#a855f7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <TrendingUp size={20} />
          </div>
          <div style={{ flex: 1, marginLeft: '14px' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Market Alerts</div>
            <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '2px' }}>Significant price changes for your active crops</div>
          </div>
          <RenderToggle id="market_alerts" checked={preferences.market_alerts} />
        </div>

        {/* AI Recommendations */}
        <div style={{ display: 'flex', alignItems: 'center', minHeight: '56px' }}>
          <div style={{ width: '20px', height: '20px', color: '#f59e0b', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Sparkles size={20} />
          </div>
          <div style={{ flex: 1, marginLeft: '14px' }}>
            <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>AI Recommendations</div>
            <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '2px' }}>Intelligent insights and proactive farming advice</div>
          </div>
          <RenderToggle id="ai_insights" checked={preferences.ai_insights} />
        </div>
      </div>
    </div>
  );
}
