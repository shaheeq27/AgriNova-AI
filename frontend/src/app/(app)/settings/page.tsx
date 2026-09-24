'use client';

import React from 'react';
import { SettingsTemplate } from '@/features';
import { NotificationSettings } from '@/features/settings/components/NotificationSettings';
import { AccountSettings } from '@/features/settings/components/AccountSettings';
import { DeveloperSettings } from '@/features/settings/components/DeveloperSettings';

export default function SettingsPage() {
  return (
    <SettingsTemplate
      notificationsSlot={<NotificationSettings />}
      accountSlot={<AccountSettings />}
      developerSlot={<DeveloperSettings />}
    />
  );
}
