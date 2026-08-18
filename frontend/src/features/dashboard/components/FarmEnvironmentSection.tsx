'use client';

import React from 'react';
import { Cloud, Sprout } from 'lucide-react';
import { FARM_ENVIRONMENTS } from '../constants';
import styles from './FarmEnvironmentSection.module.css';

export default function FarmEnvironmentSection() {
  return (
    <div className={styles.container}>
      <div className={styles.sectionLabel}>
        <Cloud size={14} />
        Farm environment
      </div>
      <div className={styles.grid}>
        {FARM_ENVIRONMENTS.map((farm) => {
          let dotClass = styles.dotGreen;
          if (farm.status === 'amber') dotClass = styles.dotAmber;
          if (farm.status === 'red') dotClass = styles.dotRed;

          return (
            <div key={farm.id} className={styles.farmCard}>
              <div className={styles.header}>
                <span>
                  {farm.farmName} · {farm.cropName}
                </span>
                <span className={`${styles.statusDot} ${dotClass}`} />
              </div>

              <div className={styles.envRow}>
                <span className={styles.envLabel}>Temperature</span>
                <span className={styles.envVal}>{farm.temperature}</span>
              </div>

              <div className={styles.envRow}>
                <span className={styles.envLabel}>Humidity</span>
                <span className={styles.envVal}>{farm.humidity}</span>
                {farm.humidityAlert && (
                  <span
                    className={`${styles.badge} ${
                      farm.humidityAlert === 'Critical'
                        ? styles.badgeRed
                        : styles.badgeAmber
                    }`}
                  >
                    {farm.humidityAlert}
                  </span>
                )}
              </div>

              <div className={styles.envRow}>
                <span className={styles.envLabel}>Rainfall</span>
                <span className={styles.envVal}>{farm.rainfall}</span>
                {farm.rainfallAlert && (
                  <span className={`${styles.badge} ${styles.badgeRed}`}>
                    {farm.rainfallAlert}
                  </span>
                )}
              </div>

              <div className={styles.envRow}>
                <span className={styles.envLabel}>Wind</span>
                <span className={styles.envVal}>{farm.wind}</span>
              </div>

              <div className={styles.cropTag}>
                <Sprout size={13} className={styles.sproutIcon} />
                <span>
                  {farm.stage} · Day {farm.day}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
