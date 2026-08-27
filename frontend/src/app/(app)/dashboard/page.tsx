'use client';

import React, { useEffect, useState } from 'react';
import { farmAPI } from '@/lib/api';
import {
  NeedsAttentionSection,
  FarmEnvironmentSection,
  ActivitiesAndOverdueSection,
  AIInsightsSection,
  FarmPerformanceSection,
  MarketSummarySection,
} from '@/features/dashboard';

export default function DashboardPage() {
  const [activeCropNames, setActiveCropNames] = useState<string[]>([]);
  const [loadingCrops, setLoadingCrops] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function fetchFarms() {
      try {
        const farms = await farmAPI.list();
        if (isMounted && farms) {
          const crops = new Set<string>();
          farms.farms.forEach(farm => {
            farm.crops?.forEach(crop => {
              if (crop.status !== 'harvested' && crop.status !== 'failed') {
                crops.add(crop.crop_name);
              }
            });
          });
          setActiveCropNames(Array.from(crops));
        }
      } catch (err) {
        console.error('Failed to fetch farms for market summary', err);
      } finally {
        if (isMounted) setLoadingCrops(false);
      }
    }
    fetchFarms();
    return () => { isMounted = false; };
  }, []);

  return (
    <>

      {/* Main Content Area with Smooth Page Entrance */}
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
        {/* Page Heading */}
        <div style={{ marginBottom: '24px' }}>
          <h1
            style={{
              fontSize: '28px',
              fontWeight: 700,
              color: '#F2F0E8',
              fontFamily: '"Source Serif 4", "Playfair Display", serif',
              margin: 0,
              letterSpacing: '0.01em',
            }}
          >
            Dashboard
          </h1>
          <p
            style={{
              fontSize: '12px',
              color: '#8d928c',
              fontFamily: '"JetBrains Mono", monospace',
              marginTop: '4px',
              margin: 0,
            }}
          >
            Farm Command Center & Overview
          </p>
        </div>

        {/* 1. Needs Your Attention */}
        <NeedsAttentionSection />

        {/* 2. Farm Environment */}
        <FarmEnvironmentSection />

        {/* 2.5. Market Watch (V5) */}
        <div style={{ marginBottom: '24px' }}>
          <MarketSummarySection activeCropNames={activeCropNames} isLoadingCrops={loadingCrops} />
        </div>

        {/* 3. Upcoming Activities + Overdue */}
        <ActivitiesAndOverdueSection />

        {/* 4. AI Insights */}
        <AIInsightsSection />

        {/* 5. Farm Performance */}
        <FarmPerformanceSection />
      </main>
    </>
  );
}
