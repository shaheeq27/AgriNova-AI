'use client';

import React from 'react';
import { Sprout } from 'lucide-react';
import styles from './EmptyFarmState.module.css';

interface EmptyFarmStateProps {
  searchQuery?: string;
}

export function EmptyFarmState({ searchQuery }: EmptyFarmStateProps) {
  return (
    <div className={styles.emptyCard}>
      <Sprout size={48} className={styles.icon} />
      <h3 className={styles.title}>No Farms Found</h3>
      <p className={styles.description}>
        {searchQuery
          ? `No registered farms matching your query "${searchQuery}".`
          : 'Register your first farm above to manage your land and crop lifecycle.'}
      </p>
    </div>
  );
}

export default EmptyFarmState;
