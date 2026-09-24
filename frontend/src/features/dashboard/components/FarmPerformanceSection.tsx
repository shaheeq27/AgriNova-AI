'use client';

import React from 'react';
import { BarChart3 } from 'lucide-react';
import {
  PERFORMANCE_METRICS,
  ACTIVITY_BARS,
  DISEASE_RISKS,
} from '../constants';
import styles from './FarmPerformanceSection.module.css';

interface Props {
  isRealData?: boolean;
}

export default function FarmPerformanceSection({ isRealData }: Props) {
  return (
    <div className={styles.container}>
      <div className={styles.sectionLabel}>
        <BarChart3 size={14} />
        Farm performance
      </div>

      <div className={styles.card}>
        {isRealData ? (
          <div style={{ padding: '64px 24px', textAlign: 'center', color: '#8d928c', fontSize: '14px' }}>
            Not enough historical data yet.
          </div>
        ) : (
          <>
            {/* Metric Cards Top Row */}
            <div className={styles.metricsGrid}>
              {PERFORMANCE_METRICS.map((metric) => (
                <div key={metric.label} className={styles.perfMetric}>
                  <div className={styles.perfLabel}>{metric.label}</div>
                  <div className={styles.perfVal}>{metric.value}</div>
                  <div className={styles.perfSub}>{metric.sub}</div>
                </div>
              ))}
            </div>

            {/* 2-Column Bottom Row */}
            <div className={styles.bottomGrid}>
              {/* Subcard 1: 30-day task activity */}
              <div className={styles.subCard}>
                <div className={styles.subTitle}>30-day task activity</div>
                <div className={styles.trendLabel}>
                  <span>Week 1</span>
                  <span>Week 2</span>
                  <span>Week 3</span>
                  <span>This week</span>
                </div>
                <div className={styles.trendBars}>
                  {ACTIVITY_BARS.map((bar, idx) => {
                    let barClass = styles.barGreen;
                    if (bar.type === 'accent') barClass = styles.barAccent;
                    if (bar.type === 'warn') barClass = styles.barWarn;

                    return (
                      <div
                        key={idx}
                        className={`${styles.bar} ${barClass}`}
                        style={{ height: bar.height }}
                      />
                    );
                  })}
                </div>
              </div>

              {/* Subcard 2: Disease risk by farm */}
              <div className={styles.subCard}>
                <div className={styles.subTitle}>Disease risk by farm</div>
                {DISEASE_RISKS.map((item) => {
                  let badgeClass = styles.riskLow;
                  if (item.risk === 'Medium') badgeClass = styles.riskMed;
                  if (item.risk === 'High') badgeClass = styles.riskHigh;

                  return (
                    <div key={item.farm} className={styles.diseaseRow}>
                      <div style={{ flex: 1 }}>
                        <div className={styles.diseaseCrop}>{item.farm}</div>
                        <div className={styles.diseaseFarm}>{item.info}</div>
                      </div>
                      <span className={`${styles.riskBadge} ${badgeClass}`}>
                        {item.risk}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
