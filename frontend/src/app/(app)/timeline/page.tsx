'use client';

import React, { useEffect, useState } from 'react';
import { useTimeline } from '@/features/timeline/hooks/useTimeline';
import JourneyHeader from '@/features/timeline/components/JourneyHeader';
import JourneySummary from '@/features/timeline/components/JourneySummary';
import JourneyTimeline from '@/features/timeline/components/JourneyTimeline';
import StatusLegend from '@/features/timeline/components/StatusLegend';
import { farmAPI } from '@/lib/api';

export default function TimelinePage() {
  const { journey, expandedPhaseId, togglePhase, isLoading: timelineLoading, farms, crops, selectedFarmId, selectedCropId, setSelectedFarmId, setSelectedCropId } = useTimeline();
  const [hasFarms, setHasFarms] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    farmAPI.list().then(res => {
      if (isMounted) setHasFarms((res?.farms?.length || 0) > 0);
    }).catch(() => {
      if (isMounted) setHasFarms(false);
    });
    return () => { isMounted = false; };
  }, []);

  if (timelineLoading || hasFarms === null || (hasFarms === false && !journey)) {
    return (
      <main style={{ padding: '24px 24px', maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', color: '#8d928c', fontSize: 14 }}>
          Loading crop journey…
        </div>
      </main>
    );
  }

  return (
    <main style={{ padding: '24px 24px', maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 10 }}>
      {hasFarms === false ? (
        <>
          <div style={{ marginBottom: '24px', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid #f59e0b', padding: '12px 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ background: '#f59e0b', color: '#000', fontSize: '10px', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', letterSpacing: '0.05em' }}>PREVIEW</div>
            <div style={{ color: '#f59e0b', fontSize: '14px', fontWeight: 500 }}>Register your first farm to see your real farm timeline.</div>
          </div>
          <JourneyHeader
            cropName={journey!.cropName}
            farmName={journey!.farmName}
            season={journey!.season}
            farms={[]}
            crops={[]}
            selectedFarmId={null}
            selectedCropId={null}
            onSelectFarm={() => {}}
            onSelectCrop={() => {}}
            journey={journey}
          />
          <div style={{ marginTop: 24 }}>
            <JourneySummary currentDay={journey!.currentDay} totalDays={journey!.totalDays} progressPercent={journey!.progressPercent} summary={journey!.summary} />
          </div>
          <div style={{ marginTop: 40 }}>
            <JourneyTimeline phases={journey!.phases} expandedPhaseId={expandedPhaseId} onTogglePhase={togglePhase} currentDay={journey!.currentDay} totalDays={journey!.totalDays} progressPercent={journey!.progressPercent} />
          </div>
          <StatusLegend />
        </>
      ) : journey ? (
        <>
          <div style={{ marginBottom: '24px' }}>
            <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#F2F0E8', fontFamily: '"Source Serif 4", "Playfair Display", serif', margin: 0, letterSpacing: '0.01em' }}>Timeline</h1>
            <p style={{ fontSize: '12px', color: '#8d928c', fontFamily: '"JetBrains Mono", monospace', marginTop: '4px', margin: 0 }}>Farm Activity & Journey</p>
          </div>
          <JourneyHeader
            cropName={journey.cropName}
            farmName={journey.farmName}
            season={journey.season}
            farms={farms}
            crops={crops}
            selectedFarmId={selectedFarmId}
            selectedCropId={selectedCropId}
            onSelectFarm={setSelectedFarmId}
            onSelectCrop={setSelectedCropId}
            journey={journey}
          />
          <div style={{ marginTop: 24 }}>
            <JourneySummary currentDay={journey.currentDay} totalDays={journey.totalDays} progressPercent={journey.progressPercent} summary={journey.summary} />
          </div>
          <div style={{ marginTop: 40 }}>
            <JourneyTimeline phases={journey.phases} expandedPhaseId={expandedPhaseId} onTogglePhase={togglePhase} currentDay={journey.currentDay} totalDays={journey.totalDays} progressPercent={journey.progressPercent} />
          </div>
          <StatusLegend />
        </>
      ) : (
        <>
          <div style={{ marginBottom: '24px' }}>
            <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#F2F0E8', fontFamily: '"Source Serif 4", "Playfair Display", serif', margin: 0, letterSpacing: '0.01em' }}>Timeline</h1>
            <p style={{ fontSize: '12px', color: '#8d928c', fontFamily: '"JetBrains Mono", monospace', marginTop: '4px', margin: 0 }}>Farm Activity & Journey</p>
          </div>
          <div style={{
             padding: '40px',
             background: 'rgba(255,255,255,0.02)',
             borderRadius: '16px',
             border: '1px solid rgba(255,255,255,0.05)',
             textAlign: 'center',
             marginTop: '24px'
          }}>
             <h3 style={{ color: '#e8f5ec', fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>No Active Events</h3>
             <p style={{ color: '#8d928c', fontSize: '14px', maxWidth: '400px', margin: '0 auto' }}>
               There are currently no active timeline events or crop journeys for your registered farms.
             </p>
          </div>
        </>
      )}
    </main>
  );
}
