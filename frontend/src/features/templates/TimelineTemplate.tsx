'use client';

import React from 'react';
import PageContainer from '@/components/layout/PageContainer';
import Section from '@/components/layout/Section';

export interface TimelineTemplateProps {
  timelineSlot?: React.ReactNode;
  activeStageSlot?: React.ReactNode;
  taskListSlot?: React.ReactNode;
  className?: string;
}

export function TimelineTemplate({
  timelineSlot,
  activeStageSlot,
  taskListSlot,
  className = '',
}: TimelineTemplateProps) {
  return (
    <PageContainer title="Crop Lifecycle Timeline" subtitle="Stage tracking, growth progression & daily tasks" className={className}>
      {activeStageSlot && <div style={{ marginBottom: '24px' }}>{activeStageSlot}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: '24px' }}>
        <Section title="Growth Stages">
          {timelineSlot}
        </Section>
        <Section title="Stage Tasks & Operations">
          {taskListSlot}
        </Section>
      </div>
    </PageContainer>
  );
}

export default TimelineTemplate;
