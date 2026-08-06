'use client';

import React from 'react';
import PageContainer from '@/components/layout/PageContainer';
import Section from '@/components/layout/Section';

export interface SettingsTemplateProps {
  profileSlot?: React.ReactNode;
  preferencesSlot?: React.ReactNode;
  notificationsSlot?: React.ReactNode;
  integrationsSlot?: React.ReactNode;
  className?: string;
}

export function SettingsTemplate({
  profileSlot,
  preferencesSlot,
  notificationsSlot,
  integrationsSlot,
  className = '',
}: SettingsTemplateProps) {
  return (
    <PageContainer title="Account & Platform Settings" subtitle="Preferences, notifications, and profile configuration" className={className}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px', maxWidth: '800px' }}>
        {profileSlot && <Section title="Profile Information">{profileSlot}</Section>}
        {preferencesSlot && <Section title="Farm Preferences">{preferencesSlot}</Section>}
        {notificationsSlot && <Section title="Notification Settings">{notificationsSlot}</Section>}
        {integrationsSlot && <Section title="Integrations & API">{integrationsSlot}</Section>}
      </div>
    </PageContainer>
  );
}

export default SettingsTemplate;
