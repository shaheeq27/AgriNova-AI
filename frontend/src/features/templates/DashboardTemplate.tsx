'use client';

import React from 'react';
import PageContainer from '@/components/layout/PageContainer';
import Section from '@/components/layout/Section';

export interface DashboardTemplateProps {
  header?: React.ReactNode;
  metricsRow?: React.ReactNode;
  mainContent?: React.ReactNode;
  sideContent?: React.ReactNode;
  className?: string;
}

export function DashboardTemplate({
  header,
  metricsRow,
  mainContent,
  sideContent,
  className = '',
}: DashboardTemplateProps) {
  return (
    <PageContainer title="Dashboard" subtitle="Farm operations & environmental intelligence" className={className}>
      {header && <div style={{ marginBottom: '24px' }}>{header}</div>}

      {metricsRow && (
        <Section style={{ marginBottom: '32px' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '20px',
            }}
          >
            {metricsRow}
          </div>
        </Section>
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: sideContent ? '1fr 340px' : '1fr',
          gap: '24px',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {mainContent}
        </div>
        {sideContent && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {sideContent}
          </div>
        )}
      </div>
    </PageContainer>
  );
}

export default DashboardTemplate;
