'use client';

import React from 'react';
import { SettingsTemplate } from '@/features';
import { NotificationSettings } from '@/features/settings/components/NotificationSettings';

export default function SettingsPage() {
  return (
    <SettingsTemplate
      notificationsSlot={<NotificationSettings />}
    />
  );
}
