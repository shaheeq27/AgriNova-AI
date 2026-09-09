'use client';

import React from 'react';
import { useNotificationPreferences } from '@/hooks/useNotifications';
import { Loader2, Mail, Bell, Droplets, Leaf, TrendingUp, Sparkles } from 'lucide-react';
import { Button } from '@/ui/Button';

export function NotificationSettings() {
  const { preferences, loading, saving, error, updatePreferences } = useNotificationPreferences();

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8 text-gray-500">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        <span>Loading preferences...</span>
      </div>
    );
  }

  if (error || !preferences) {
    return (
      <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
        Failed to load notification preferences: {error || 'Unknown error'}
      </div>
    );
  }

  const handleToggle = (key: keyof typeof preferences) => {
    updatePreferences({ [key]: !preferences[key] });
  };

  return (
    <div className="space-y-6">
      {/* Master Email Toggle */}
      <div className="p-4 rounded-xl border border-gray-800 bg-gray-900/50 flex items-center justify-between">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-primary-500/10 text-primary-400">
            <Mail className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-white font-medium">Email Notifications</h4>
            <p className="text-sm text-gray-400 mt-1">
              Receive important alerts and digests via email
            </p>
          </div>
        </div>
        <button
          onClick={() => handleToggle('email_enabled')}
          disabled={saving}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-gray-900 ${
            preferences.email_enabled ? 'bg-primary-500' : 'bg-gray-700'
          } ${saving ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              preferences.email_enabled ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      <div className="space-y-1">
        <h4 className="text-sm font-medium text-gray-300 mb-4 uppercase tracking-wider px-1">Notification Categories</h4>
        
        {/* Weather Alerts */}
        <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-gray-800/30 transition-colors">
          <div className="flex items-center gap-3">
            <Bell className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-sm font-medium text-white">Weather Alerts</p>
              <p className="text-xs text-gray-500">Severe weather warnings and extreme forecasts</p>
            </div>
          </div>
          <button
            onClick={() => handleToggle('weather_alerts')}
            disabled={saving}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
              preferences.weather_alerts ? 'bg-primary-500' : 'bg-gray-700'
            }`}
          >
            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${preferences.weather_alerts ? 'translate-x-5' : 'translate-x-1'}`} />
          </button>
        </div>

        {/* Irrigation Reminders */}
        <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-gray-800/30 transition-colors">
          <div className="flex items-center gap-3">
            <Droplets className="h-5 w-5 text-blue-500" />
            <div>
              <p className="text-sm font-medium text-white">Irrigation Reminders</p>
              <p className="text-xs text-gray-500">Scheduled watering based on soil moisture and crop needs</p>
            </div>
          </div>
          <button
            onClick={() => handleToggle('irrigation_reminders')}
            disabled={saving}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
              preferences.irrigation_reminders ? 'bg-primary-500' : 'bg-gray-700'
            }`}
          >
            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${preferences.irrigation_reminders ? 'translate-x-5' : 'translate-x-1'}`} />
          </button>
        </div>

        {/* Fertilizer Reminders */}
        <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-gray-800/30 transition-colors">
          <div className="flex items-center gap-3">
            <Leaf className="h-5 w-5 text-green-500" />
            <div>
              <p className="text-sm font-medium text-white">Fertilizer Reminders</p>
              <p className="text-xs text-gray-500">Nutrient application schedules and recommendations</p>
            </div>
          </div>
          <button
            onClick={() => handleToggle('fertilizer_reminders')}
            disabled={saving}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
              preferences.fertilizer_reminders ? 'bg-primary-500' : 'bg-gray-700'
            }`}
          >
            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${preferences.fertilizer_reminders ? 'translate-x-5' : 'translate-x-1'}`} />
          </button>
        </div>

        {/* Market Alerts */}
        <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-gray-800/30 transition-colors">
          <div className="flex items-center gap-3">
            <TrendingUp className="h-5 w-5 text-purple-500" />
            <div>
              <p className="text-sm font-medium text-white">Market Alerts</p>
              <p className="text-xs text-gray-500">Significant price changes for your active crops</p>
            </div>
          </div>
          <button
            onClick={() => handleToggle('market_alerts')}
            disabled={saving}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
              preferences.market_alerts ? 'bg-primary-500' : 'bg-gray-700'
            }`}
          >
            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${preferences.market_alerts ? 'translate-x-5' : 'translate-x-1'}`} />
          </button>
        </div>

        {/* AI Recommendations */}
        <div className="flex items-center justify-between py-3 px-4 rounded-lg hover:bg-gray-800/30 transition-colors">
          <div className="flex items-center gap-3">
            <Sparkles className="h-5 w-5 text-amber-500" />
            <div>
              <p className="text-sm font-medium text-white">AI Recommendations</p>
              <p className="text-xs text-gray-500">Intelligent insights and proactive farming advice</p>
            </div>
          </div>
          <button
            onClick={() => handleToggle('ai_insights')}
            disabled={saving}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
              preferences.ai_insights ? 'bg-primary-500' : 'bg-gray-700'
            }`}
          >
            <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${preferences.ai_insights ? 'translate-x-5' : 'translate-x-1'}`} />
          </button>
        </div>
      </div>
    </div>
  );
}
