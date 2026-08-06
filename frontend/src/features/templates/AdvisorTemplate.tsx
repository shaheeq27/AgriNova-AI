'use client';

import React from 'react';
import PageContainer from '@/components/layout/PageContainer';

export interface AdvisorTemplateProps {
  chatFeedSlot?: React.ReactNode;
  promptBoxSlot?: React.ReactNode;
  suggestionsSlot?: React.ReactNode;
  sideContextSlot?: React.ReactNode;
  className?: string;
}

export function AdvisorTemplate({
  chatFeedSlot,
  promptBoxSlot,
  suggestionsSlot,
  sideContextSlot,
  className = '',
}: AdvisorTemplateProps) {
  return (
    <PageContainer title="AI Agronomist Advisor" subtitle="Conversational agricultural intelligence & decision support" className={className}>
      <div style={{ display: 'grid', gridTemplateColumns: sideContextSlot ? '1fr 300px' : '1fr', gap: '24px', height: 'calc(100vh - 200px)', minHeight: '500px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', borderRadius: 'var(--radius-lg)', background: 'var(--color-bg-glass)', border: '1px solid var(--color-border)', padding: '20px' }}>
          <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px' }}>
            {chatFeedSlot}
          </div>
          {suggestionsSlot && <div style={{ marginBottom: '12px' }}>{suggestionsSlot}</div>}
          <div>{promptBoxSlot}</div>
        </div>

        {sideContextSlot && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {sideContextSlot}
          </div>
        )}
      </div>
    </PageContainer>
  );
}

export default AdvisorTemplate;
