'use client';

import React from 'react';
import { AlertTriangle, CloudRain, ShieldAlert, Calendar } from 'lucide-react';
import { ATTENTION_ALERTS } from '../constants';
import styles from './NeedsAttentionSection.module.css';

interface Props {
  isRealData?: boolean;
}

export default function NeedsAttentionSection({ isRealData }: Props) {
  return (
    <div className={styles.container}>
      <div className={styles.sectionLabel}>
        <AlertTriangle size={14} className={styles.iconLabel} />
        Needs your attention
      </div>
      <div className={styles.card}>
        {isRealData ? (
          <div style={{ padding: '32px 24px', textAlign: 'center', color: '#8d928c', fontSize: '14px' }}>
            No active events for your registered farms.
          </div>
        ) : (
          ATTENTION_ALERTS.map((alert) => {
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
          })
        )}
      </div>
    </div>
  );
}
