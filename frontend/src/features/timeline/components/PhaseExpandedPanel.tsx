'use client';

import React from 'react';
import { PhaseEvent } from '../types';
import PhaseEventList from './PhaseEventList';
import styles from './PhaseExpandedPanel.module.css';

interface PhaseExpandedPanelProps {
  events: PhaseEvent[];
  isExpanded: boolean;
}

export default function PhaseExpandedPanel({ events, isExpanded }: PhaseExpandedPanelProps) {
  return (
    <div className={`${styles.panel} ${isExpanded ? styles.panelExpanded : ''}`}>
      <div className={styles.panelInner}>
        <div className={styles.contentWrapper}>
          {events && events.length > 0 ? (
            <PhaseEventList events={events} />
          ) : (
            <div className={styles.emptyState}>No events recorded for this phase yet.</div>
          )}
        </div>
      </div>
    </div>
  );
}
