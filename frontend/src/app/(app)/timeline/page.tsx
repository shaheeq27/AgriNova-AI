'use client';

import React from 'react';
import { useTimeline } from '@/features/timeline/hooks/useTimeline';
import JourneyHeader from '@/features/timeline/components/JourneyHeader';
import JourneySummary from '@/features/timeline/components/JourneySummary';
import JourneyTimeline from '@/features/timeline/components/JourneyTimeline';
import StatusLegend from '@/features/timeline/components/StatusLegend';

export default function TimelinePage() {
  const { journey, expandedPhaseId, togglePhase, isLoading } = useTimeline();

  if (isLoading || !journey) {
    return (
      <>

        <main style={{ padding: '24px 24px', maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', color: '#8d928c', fontSize: 14 }}>
            Loading crop journey…
          </div>
        </main>
      </>
    );
  }

  return (
    <>

      <main style={{ padding: '24px 24px', maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 10 }}>
        <JourneyHeader
          cropName={journey.cropName}
          farmName={journey.farmName}
          season={journey.season}
        />

        <div style={{ marginTop: 24 }}>
          <JourneySummary
            currentDay={journey.currentDay}
            totalDays={journey.totalDays}
            progressPercent={journey.progressPercent}
            summary={journey.summary}
          />
        </div>

        <div style={{ marginTop: 40 }}>
          <JourneyTimeline
            phases={journey.phases}
            expandedPhaseId={expandedPhaseId}
            onTogglePhase={togglePhase}
            currentDay={journey.currentDay}
            totalDays={journey.totalDays}
            progressPercent={journey.progressPercent}
          />
        </div>

        <StatusLegend />
      </main>
    </>
  );
}
