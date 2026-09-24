'use client';

import React from 'react';
import { PhaseEvent } from '../types';
import styles from './PhaseEventList.module.css';
import { parseDateString, formatDateShort } from '@/utils/date';

interface PhaseEventListProps {
  events: PhaseEvent[];
}

function formatShortDate(dateString: string) {
  const pDate = parseDateString(dateString);
  return formatDateShort(pDate);
}

function getDotColor(category: string) {
  switch (category) {
    case 'milestone': return '#ADFF00';
    case 'health': return '#ff6b6b';
    case 'treatment': return '#4ecdc4';
    case 'ai': return '#a78bfa';
    default: return '#ADFF00';
  }
}

export default function PhaseEventList({ events }: PhaseEventListProps) {
  if (!events || events.length === 0) return null;

  return (
    <div className={styles.list}>
      {events.map((event) => (
        <div key={event.id} className={styles.event}>
          <div className={styles.eventDate}>
            {formatShortDate(event.date)}
          </div>
          <div className={styles.eventContent}>
            <div 
              className={styles.eventDot} 
              style={{ background: getDotColor(event.category) }}
            />
            <div className={styles.eventHeader}>
              <span className={styles.eventIcon}>{event.icon}</span>
              <span className={styles.eventTitle}>{event.title}</span>
            </div>
            <div className={styles.eventDescription}>
              {event.description}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
