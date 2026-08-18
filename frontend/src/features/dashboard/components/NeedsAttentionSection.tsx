'use client';

import React from 'react';
import { AlertTriangle, CloudRain, ShieldAlert, Calendar } from 'lucide-react';
import { ATTENTION_ALERTS } from '../constants';
import styles from './NeedsAttentionSection.module.css';

export default function NeedsAttentionSection() {
  return (
    <div className={styles.container}>
      <div className={styles.sectionLabel}>
        <AlertTriangle size={14} className={styles.iconLabel} />
        Needs your attention
      </div>
      <div className={styles.card}>
        {ATTENTION_ALERTS.map((alert) => {
          let IconComponent = AlertTriangle;
          if (alert.severity === 'critical') IconComponent = CloudRain;
          else if (alert.severity === 'warning') IconComponent = ShieldAlert;
          else if (alert.severity === 'info') IconComponent = Calendar;

          return (
            <div
              key={alert.id}
              className={`${styles.alertItem} ${styles[alert.severity]}`}
            >
              <IconComponent size={18} className={styles.alertIcon} />
              <div className={styles.content}>
                <div className={styles.title}>{alert.title}</div>
                <div className={styles.sub}>{alert.sub}</div>
                <div className={styles.why}>{alert.why}</div>
              </div>
              <div className={styles.actionWrapper}>
                <button className={styles.btn}>{alert.actionText}</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
