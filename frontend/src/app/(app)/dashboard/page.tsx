'use client';

import React, { useEffect, useState } from 'react';
import { farmAPI } from '@/lib/api';
import type { FarmData } from '@/lib/api';
import {
  NeedsAttentionSection,
  FarmEnvironmentSection,
  ActivitiesAndOverdueSection,
  AIInsightsSection,
  FarmPerformanceSection,
  MarketSummarySection,
} from '@/features/dashboard';

export default function DashboardPage() {
  const [farms, setFarms] = useState<FarmData[]>([]);
  const [activeCropNames, setActiveCropNames] = useState<string[]>([]);
  const [loadingCrops, setLoadingCrops] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function fetchFarms() {
      try {
        const res = await farmAPI.list();
        if (isMounted && res && res.farms) {
          setFarms(res.farms);
          const crops = new Set<string>();
          res.farms.forEach(farm => {
            farm.crops?.forEach(crop => {
              if (crop.status !== 'harvested' && crop.status !== 'failed') {
                crops.add(crop.crop_name);
              }
            });
          });
          setActiveCropNames(Array.from(crops));
        }
      } catch (err) {
        console.error('Failed to fetch farms for dashboard', err);
      } finally {
        if (isMounted) setLoadingCrops(false);
      }
    }
    fetchFarms();
    return () => { isMounted = false; };
  }, []);

  const isRealData = farms.length > 0;

  return (
    <>
      <main
        className="anim-page-enter"
        style={{
          padding: '24px',
          width: '100%',
          margin: '0 auto',
          position: 'relative',
          zIndex: 10,
        }}
      >
        <div style={{ marginBottom: '32px' }}>
          <h1
            style={{
              fontSize: '36px',
              fontWeight: 700,
              color: '#F2F0E8',
              fontFamily: '"Source Serif 4", "Playfair Display", serif',
              margin: 0,
              letterSpacing: '0.01em',
              lineHeight: 1.1,
            }}
          >
            Dashboard<span style={{ color: 'var(--accent-primary, #adff00)' }}>.</span>
          </h1>
          <p
            style={{
              fontSize: '15px',
              color: '#8d928c',
              fontFamily: '"JetBrains Mono", monospace',
              marginTop: '6px',
              margin: 0,
              opacity: 0.7,
            }}
          >
            Farm Command Center & Overview
          </p>
        </div>

        {!loadingCrops && !isRealData && (
          <div style={{ marginBottom: '24px', color: '#8d928c', fontSize: '14px', lineHeight: '1.5' }}>
            <span style={{ color: 'var(--accent-primary, #adff00)', fontSize: '13px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginRight: '8px' }}>
              [ DEMO PREVIEW ]
            </span>
            This is a preview of your AgriNova dashboard. Register a farm to see your actual farm data here.
          </div>
        )}

        {/* Both Demo and Real states use the original showcase composition. */}
        {/* We pass isRealData to the components so they can internally render clean empty states if real backend data is missing. */}
        <NeedsAttentionSection isRealData={isRealData} />

        <FarmEnvironmentSection isRealData={isRealData} />

        <div style={{ marginBottom: '24px' }}>
          <MarketSummarySection activeCropNames={activeCropNames} isLoadingCrops={loadingCrops} />
        </div>

        <ActivitiesAndOverdueSection isRealData={isRealData} />

        <AIInsightsSection isRealData={isRealData} />

        <FarmPerformanceSection isRealData={isRealData} />

      </main>
    </>
  );
}
