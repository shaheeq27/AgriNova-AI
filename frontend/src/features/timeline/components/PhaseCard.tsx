'use client';

import React from 'react';
import { CropJourneyPhase } from '../types';
import styles from './PhaseCard.module.css';

interface PhaseCardProps {
  phase: CropJourneyPhase;
  isExpanded: boolean;
  onToggle: () => void;
  side: 'left' | 'right';
  currentDay?: number;
  totalDays?: number;
  progressPercent?: number;
}

function formatDateRange(start: string, end: string) {
  const format = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };
  return `${format(start)} – ${format(end)}`;
}

export default function PhaseCard({ 
  phase, 
  isExpanded, 
  onToggle,
  currentDay,
  totalDays,
  progressPercent 
}: PhaseCardProps) {
  let cardClass = styles.card;
  if (phase.status === 'completed') cardClass += ` ${styles.cardCompleted}`;
  else if (phase.status === 'current') cardClass += ` ${styles.cardCurrent}`;
  else if (phase.status === 'upcoming') cardClass += ` ${styles.cardUpcoming}`;

  return (
    <div className={cardClass} onClick={onToggle}>
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <span className={styles.icon}>{phase.icon}</span>
          <span className={styles.phaseName}>{phase.name}</span>
        </div>
        <div className={styles.statusArea}>
          {phase.status === 'current' && <span className={styles.currentBadge}>CURRENT</span>}
          {phase.status === 'completed' && <span className={styles.completedBadge}>✓</span>}
          <span className={`${styles.chevron} ${isExpanded ? styles.chevronExpanded : ''}`}>
            ▼
          </span>
        </div>
      </div>
      
      <div className={styles.details}>
        <div className={styles.dateRow}>
          <span className={styles.dateRange}>{formatDateRange(phase.startDate, phase.endDate)}</span>
          <span className={styles.dayRange}>Day {phase.dayStart > 0 ? phase.dayStart : 1} to {phase.dayEnd}</span>
        </div>
        
        <div className={styles.footerRow}>
          {phase.events.length > 0 ? (
            <span className={styles.eventCount}>{phase.events.length} important event{phase.events.length !== 1 ? 's' : ''}</span>
          ) : (
            <span></span>
          )}
          {phase.status === 'current' && currentDay !== undefined && totalDays !== undefined && (
            <span className={styles.progressInfo}>Day {currentDay} / {totalDays} · {progressPercent}% Complete</span>
          )}
        </div>
      </div>
    </div>
  );
}
