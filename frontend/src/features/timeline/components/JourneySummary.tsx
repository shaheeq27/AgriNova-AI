'use client';

import React from 'react';
import styles from './JourneySummary.module.css';
import type { JourneySummaryData } from '../types';

interface JourneySummaryProps {
  currentDay: number;
  totalDays: number;
  progressPercent: number;
  summary: JourneySummaryData;
}

export default function JourneySummary({
  currentDay,
  totalDays,
  progressPercent,
  summary,
}: JourneySummaryProps) {
  return (
    <div className={styles.container}>
      {/* Crop Progress */}
      <div className={styles.card}>
        <div className={styles.label}>Crop Progress</div>
        <div className={styles.valueRow}>
          <span className={styles.value}>Day {currentDay}</span>
          <span className={styles.subLabel}>/ {totalDays}</span>
        </div>
        <div className={styles.progressContainer}>
          <div className={styles.progressBar} style={{ width: `${progressPercent}%` }} />
        </div>
        <div className={styles.progressText}>{progressPercent}%</div>
      </div>

      {/* Important Events */}
      <div className={styles.card}>
        <div className={styles.iconRow}>
          <span className={styles.icon}>📋</span>
          <div className={styles.label}>Important Events</div>
        </div>
        <div className={styles.value}>{summary.totalEvents}</div>
        <div className={styles.subLabel}>Total recorded</div>
      </div>

      {/* Health Issues */}
      <div className={styles.card}>
        <div className={styles.iconRow}>
          <span className={styles.icon}>🛡️</span>
          <div className={styles.label}>Health Issues</div>
        </div>
        <div className={styles.value}>{summary.healthIssues}</div>
        <div className={styles.subLabel}>Detected</div>
      </div>

      {/* Treatments Applied */}
      <div className={styles.card}>
        <div className={styles.iconRow}>
          <span className={styles.icon}>🧪</span>
          <div className={styles.label}>Treatments Applied</div>
        </div>
        <div className={styles.value}>{summary.treatmentsApplied}</div>
        <div className={styles.subLabel}>Completed</div>
      </div>

      {/* AI Insights */}
      <div className={styles.card}>
        <div className={styles.iconRow}>
          <span className={styles.icon}>🤖</span>
          <div className={styles.label}>AI Insights</div>
        </div>
        <div className={styles.value}>{summary.aiInsights}</div>
        <div className={styles.subLabel}>Major recommendations</div>
      </div>
    </div>
  );
}
