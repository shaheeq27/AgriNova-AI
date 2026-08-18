'use client';

import React from 'react';
import { Sprout, Clock } from 'lucide-react';
import styles from './DashboardHeader.module.css';

export default function DashboardHeader() {
  return (
    <div className={styles.topbar}>
      <div className={styles.logo}>
        <Sprout size={18} className={styles.leafIcon} />
        AgriNova AI
        <span className={styles.badge}>3 farms active</span>
      </div>
      <div className={styles.right}>
        <span className={styles.meta}>
          <Clock size={13} />
          Mon, 9 Aug 2026 · 07:14 AM
        </span>
        <div className={styles.avatar}>RK</div>
      </div>
    </div>
  );
}
