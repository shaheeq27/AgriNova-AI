'use client';

import React from 'react';
import {
  NeedsAttentionSection,
  FarmEnvironmentSection,
  ActivitiesAndOverdueSection,
  AIInsightsSection,
  FarmPerformanceSection,
} from '@/features/dashboard';

export default function DashboardPage() {
  return (
    <>

      {/* Main Content Area with Smooth Page Entrance */}
      <main
        className="anim-page-enter"
        style={{
          padding: '24px',
          maxWidth: 1400,
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
