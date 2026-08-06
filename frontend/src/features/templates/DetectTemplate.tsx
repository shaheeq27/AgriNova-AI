'use client';

import React from 'react';
import PageContainer from '@/components/layout/PageContainer';
import Section from '@/components/layout/Section';

export interface DetectTemplateProps {
  uploadSlot?: React.ReactNode;
  resultSlot?: React.ReactNode;
  prescriptionSlot?: React.ReactNode;
  historySlot?: React.ReactNode;
  className?: string;
}

export function DetectTemplate({
  uploadSlot,
  resultSlot,
  prescriptionSlot,
  historySlot,
  className = '',
}: DetectTemplateProps) {
  return (
    <PageContainer title="Disease Detection" subtitle="AI Diagnostic Engine & Crop Health Assessment" className={className}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        <Section title="Image Upload & Scanner">
          {uploadSlot}
        </Section>

        <Section title="Diagnostic Result">
          {resultSlot}
        </Section>
      </div>

      {prescriptionSlot && (
        <Section title="Treatment Prescription" style={{ marginTop: '32px' }}>
          {prescriptionSlot}
        </Section>
      )}

      {historySlot && (
        <Section title="Scan History" style={{ marginTop: '32px' }}>
          {historySlot}
        </Section>
      )}
    </PageContainer>
  );
}

export default DetectTemplate;
