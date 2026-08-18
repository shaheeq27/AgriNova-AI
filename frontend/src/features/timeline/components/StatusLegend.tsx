'use client';

import React from 'react';
import styles from './StatusLegend.module.css';

export default function StatusLegend() {
  return (
    <div className={styles.container}>
      <div className={styles.item}>
        <span className={styles.completedDot} />
        <span className={styles.label}>Completed</span>
      </div>
      <div className={styles.item}>
        <span className={styles.currentDot} />
        <span className={styles.label}>Current</span>
      </div>
      <div className={styles.item}>
        <span className={styles.upcomingDot} />
        <span className={styles.label}>Upcoming</span>
      </div>
    </div>
  );
}
