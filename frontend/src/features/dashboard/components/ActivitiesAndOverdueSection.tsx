'use client';

import React from 'react';
import { Calendar, Clock, XCircle } from 'lucide-react';
import { UPCOMING_TASKS, OVERDUE_TASKS } from '../constants';
import styles from './ActivitiesAndOverdueSection.module.css';

interface Props {
  isRealData?: boolean;
}

export default function ActivitiesAndOverdueSection({ isRealData }: Props) {
  return (
    <div className={styles.container}>
      <div className={styles.grid}>
        {/* Upcoming Activities Column */}
        <div className={styles.column}>
          <div className={styles.sectionLabel}>
            <Calendar size={14} />
            Upcoming activities
          </div>
          <div className={styles.card}>
            {isRealData ? (
              <div style={{ padding: '32px 24px', textAlign: 'center', color: '#8d928c', fontSize: '14px' }}>
                No upcoming activities.
              </div>
            ) : (
              UPCOMING_TASKS.map((task) => (
                <div key={task.id} className={styles.taskRow}>
                  <span
                    className={styles.taskDot}
                    style={{ backgroundColor: task.dotColor }}
                  />
                  <div className={styles.taskInfo}>
                    <div className={styles.taskName}>{task.name}</div>
                    <div className={styles.taskFarm}>
                      {task.farm} · {task.crop}
                    </div>
                  </div>
                  <div className={styles.taskWhen}>{task.when}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Overdue Column */}
        <div className={styles.column}>
          <div className={styles.sectionLabel}>
            <Clock size={14} className={styles.overdueIconLabel} />
            Overdue
          </div>
          <div className={styles.card}>
            {isRealData ? (
              <div style={{ padding: '32px 24px', textAlign: 'center', color: '#8d928c', fontSize: '14px' }}>
                No overdue activities.
              </div>
            ) : (
              OVERDUE_TASKS.map((item) => (
                <div key={item.id} className={styles.overdueRow}>
                  <XCircle size={16} className={styles.overdueIcon} />
                  <div>
                    <div className={styles.overdueTitle}>{item.title}</div>
                    <div className={styles.overdueSub}>{item.sub}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
