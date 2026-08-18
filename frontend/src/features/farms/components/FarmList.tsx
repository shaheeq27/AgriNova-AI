'use client';

import React from 'react';
import { Grid, List } from 'lucide-react';
import { Farm, ViewMode } from '../types';
import { FarmCard } from './FarmCard';
import { EmptyFarmState } from './EmptyFarmState';
import styles from './FarmList.module.css';

interface FarmListProps {
  farms: Farm[];
  loading: boolean;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  searchQuery?: string;
}

export function FarmList({
  farms,
  loading,
  viewMode,
  onViewModeChange,
  searchQuery,
}: FarmListProps) {
  return (
    <div className={styles.container}>
      <div className={styles.headerRow}>
        <h2 className={styles.sectionTitle}>My Farms</h2>

        {/* View Toggle Buttons */}
        <div className={styles.viewToggle}>
          <button
            onClick={() => onViewModeChange('grid')}
            className={`${styles.toggleBtn} ${viewMode === 'grid' ? styles.toggleBtnActive : ''}`}
            title="Grid View"
          >
            <Grid size={16} />
          </button>
          <button
            onClick={() => onViewModeChange('list')}
            className={`${styles.toggleBtn} ${viewMode === 'list' ? styles.toggleBtnActive : ''}`}
            title="List View"
          >
            <List size={16} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingSkeletonGrid}>
          {[1, 2, 3].map((i) => (
            <div key={i} className={styles.skeletonCard} />
          ))}
        </div>
      ) : farms.length === 0 ? (
        <EmptyFarmState searchQuery={searchQuery} />
      ) : (
        <div className={viewMode === 'grid' ? styles.gridContainer : styles.listContainer}>
          {farms.map((farm, index) => (
            <FarmCard key={farm.id} farm={farm} index={index} />
          ))}
        </div>
      )}
    </div>
  );
}

export default FarmList;
