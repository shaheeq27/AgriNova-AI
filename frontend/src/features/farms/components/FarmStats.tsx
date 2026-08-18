'use client';

import React from 'react';
import { Building2, Maximize2, Sprout, AlertCircle } from 'lucide-react';
import { FarmStatsData } from '../types';
import styles from './FarmStats.module.css';

interface FarmStatsProps {
  stats: FarmStatsData;
}

export function FarmStats({ stats }: FarmStatsProps) {
  return (
    <div className={styles.statsGrid}>
      {/* 1. Total Farms */}
      <div className={styles.statCard}>
        <div className={styles.iconWrapper}>
          <Building2 size={22} />
        </div>
        <div className={styles.statInfo}>
          <span className={styles.label}>Total Farms</span>
          <p className={styles.value}>{stats.totalFarms}</p>
          <span className={styles.subtext}>All registered farms</span>
        </div>
      </div>

      {/* 2. Total Area */}
      <div className={styles.statCard}>
        <div className={styles.iconWrapper}>
          <Maximize2 size={22} />
        </div>
        <div className={styles.statInfo}>
          <span className={styles.label}>Total Area</span>
          <p className={styles.value}>
            {stats.totalArea} <span className={styles.unit}>Acres</span>
          </p>
          <span className={styles.subtext}>Combined area</span>
        </div>
      </div>

      {/* 3. Active Farms */}
      <div className={styles.statCard}>
        <div className={styles.iconWrapper}>
          <Sprout size={22} />
        </div>
        <div className={styles.statInfo}>
          <span className={styles.label}>Active Farms</span>
          <p className={styles.value}>{stats.activeFarms}</p>
          <span className={styles.subtext}>Farms with active crops</span>
        </div>
      </div>

      {/* 4. Idle Farms */}
      <div className={styles.statCard}>
        <div className={styles.iconWrapper}>
          <AlertCircle size={22} />
        </div>
        <div className={styles.statInfo}>
          <span className={styles.label}>Idle Farms</span>
          <p className={styles.value}>{stats.idleFarms}</p>
          <span className={styles.subtext}>No crop assigned</span>
        </div>
      </div>
    </div>
  );
}

export default FarmStats;
