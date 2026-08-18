'use client';
import React from 'react';
import styles from './AnalyzingState.module.css';

interface AnalyzingStateProps {
  imagePreviewUrl: string;
}

export const AnalyzingState: React.FC<AnalyzingStateProps> = ({ imagePreviewUrl }) => {
  return (
    <div className={styles.container}>
      <div className={styles.imageWrapper}>
        <img src={imagePreviewUrl} alt="Analyzing" className={styles.image} />
        <div className={styles.scanLine}></div>
        
        {/* Viewfinder brackets */}
        <div className={`${styles.bracket} ${styles.tl}`}></div>
        <div className={`${styles.bracket} ${styles.tr}`}></div>
        <div className={`${styles.bracket} ${styles.bl}`}></div>
        <div className={`${styles.bracket} ${styles.br}`}></div>
        
        {/* Pulsing rings */}
        <div className={styles.pulseRing}></div>
        <div className={styles.pulseRingDelayed}></div>
      </div>
      
      <div className={styles.textContainer}>
        <h2 className={styles.title}>
          ANALYZING CROP IMAGE<span className={styles.dots}>...</span>
        </h2>
        <p className={styles.subtitle}>AgriNova AI is examining visible symptoms...</p>
      </div>
    </div>
  );
};
