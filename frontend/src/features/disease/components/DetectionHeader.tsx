'use client';
import React from 'react';
import styles from './DetectionHeader.module.css';

export const DetectionHeader: React.FC = () => {
  return (
    <div className={styles.headerContainer}>
      <h1 className={styles.title}>Crop <span style={{ color: 'var(--color-neon-mint, #ADFF00)' }}>Disease</span> Detection</h1>
      <p className={styles.subtitle} style={{ maxWidth: '420px', margin: '0 auto', lineHeight: '1.5' }}>
        Upload or capture a crop image and our AI will analyze it and provide accurate diagnosis
      </p>
    </div>
  );
};
