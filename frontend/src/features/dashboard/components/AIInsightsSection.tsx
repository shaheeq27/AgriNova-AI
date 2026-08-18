'use client';

import React from 'react';
import { Sparkles, Droplets, Wind, TrendingUp } from 'lucide-react';
import { AI_INSIGHTS } from '../constants';
import styles from './AIInsightsSection.module.css';

export default function AIInsightsSection() {
  return (
    <div className={styles.container}>
      <div className={styles.sectionLabel}>
        <Sparkles size={14} className={styles.sparkleIcon} />
        AI insights
      </div>
      <div className={styles.card}>
        {AI_INSIGHTS.map((insight) => {
          let IconComponent = Droplets;
          if (insight.iconType === 'wind') IconComponent = Wind;
          if (insight.iconType === 'trending') IconComponent = TrendingUp;

          return (
            <div key={insight.id} className={styles.insightItem}>
              <div className={styles.insightIcon}>
                <IconComponent size={16} />
              </div>
              <div>
                <div className={styles.title}>{insight.title}</div>
                <div className={styles.body}>{insight.body}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
