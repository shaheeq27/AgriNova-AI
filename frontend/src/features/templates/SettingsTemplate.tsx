'use client';

import React from 'react';

export interface SettingsTemplateProps {
  profileSlot?: React.ReactNode;
  preferencesSlot?: React.ReactNode;
  integrationsSlot?: React.ReactNode;
  notificationsSlot?: React.ReactNode;
  accountSlot?: React.ReactNode;
  developerSlot?: React.ReactNode;
  className?: string;
}

export function SettingsTemplate({
  notificationsSlot,
  accountSlot,
  developerSlot,
  className = '',
}: SettingsTemplateProps) {
  return (
    <div className={`settings-container ${className}`}>
      <style>{`
        .settings-container {
          width: calc(100% - 32px);
          max-width: 1200px;
          margin: 0 auto;
          box-sizing: border-box;
        }
        @media (min-width: 768px) {
          .settings-container {
            width: calc(100% - 64px);
          }
        }
        .settings-header {
          margin-top: 32px;
          margin-bottom: 32px;
          text-align: center;
        }
        .settings-h1 {
          font-family: 'Playfair Display', serif;
          font-size: 40px;
          line-height: 48px;
          font-weight: 700;
          color: var(--text-primary, #ffffff);
          margin: 0 0 8px 0;
        }
        .settings-subtitle {
          font-family: 'Inter', sans-serif;
          font-size: 16px;
          line-height: 24px;
          color: var(--text-secondary, #9ca3af);
          margin: 0;
        }
        .settings-grid {
          display: flex;
          flex-direction: column;
          gap: 32px;
          width: 100%;
        }
      `}</style>

      <div className="settings-header">
        <h1 className="settings-h1">Account & Platform Settings</h1>
        <p className="settings-subtitle">Preferences, notifications, and profile configuration</p>
      </div>

      <div className="settings-grid">
        {notificationsSlot && <div>{notificationsSlot}</div>}
        {accountSlot && <div>{accountSlot}</div>}
        {developerSlot && <div>{developerSlot}</div>}
      </div>
    </div>
  );
}

export default SettingsTemplate;
