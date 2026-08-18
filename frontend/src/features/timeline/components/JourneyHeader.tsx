'use client';

import React from 'react';
import styles from './JourneyHeader.module.css';

interface JourneyHeaderProps {
  cropName: string;
  farmName: string;
  season: string;
}

export default function JourneyHeader({ cropName, farmName, season }: JourneyHeaderProps) {
  return (
    <div className={styles.header}>
      <div className={styles.titleSection}>
        <h1 className={styles.title}>Crop Journey</h1>
        <p className={styles.subtitle}>Track your crop's complete life cycle</p>
      </div>

      <div className={styles.selectors}>
        <div className={styles.pill}>
          <span className={styles.icon}>🌾</span>
          {cropName}
          <span className={styles.arrow}>▼</span>
        </div>
        <div className={styles.pill}>
          <span className={styles.icon}>🏡</span>
          {farmName}
          <span className={styles.arrow}>▼</span>
        </div>
        <div className={styles.pill}>
          <span className={styles.icon}>📅</span>
          {season}
          <span className={styles.arrow}>▼</span>
        </div>
      </div>

      <button className={styles.exportButton}>
        Export Report ↓
      </button>
    </div>
  );
}
