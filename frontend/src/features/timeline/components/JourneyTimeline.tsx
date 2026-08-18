'use client';

import React from 'react';
import { CropJourneyPhase } from '../types';
import PhaseCard from './PhaseCard';
import PhaseExpandedPanel from './PhaseExpandedPanel';
import styles from './JourneyTimeline.module.css';

interface JourneyTimelineProps {
  phases: CropJourneyPhase[];
  expandedPhaseId: string | null;
  onTogglePhase: (phaseId: string) => void;
  currentDay: number;
  totalDays: number;
  progressPercent: number;
}

export default function JourneyTimeline({
  phases,
  expandedPhaseId,
  onTogglePhase,
  currentDay,
  totalDays,
  progressPercent,
}: JourneyTimelineProps) {
  return (
    <div className={styles.timeline}>
      {/* Central Glowing Spine */}
      <div className={styles.spineContainer}>
        <div className={styles.spine}>
          <div className={styles.pastLabel}>PAST</div>
          <div className={styles.futureLabel}>FUTURE</div>
        </div>
      </div>

      {/* Timeline Grid */}
      <div className={styles.timelineGrid}>
        {phases.map((phase) => {
          const isExpanded = expandedPhaseId === phase.id;
          const isLeft = phase.stageOrder % 2 !== 0;

          let nodeClass = styles.node;
          if (phase.status === 'completed') nodeClass += ` ${styles.nodeCompleted}`;
          else if (phase.status === 'current') nodeClass += ` ${styles.nodeCurrent}`;
          else nodeClass += ` ${styles.nodeUpcoming}`;

          const connectorClass =
            phase.status === 'current'
              ? styles.connectorCurrent
              : phase.status === 'upcoming'
                ? styles.connectorUpcoming
                : '';

          const cardBlock = (
            <>
              <PhaseCard
                phase={phase}
                isExpanded={isExpanded}
                onToggle={() => onTogglePhase(phase.id)}
                side={isLeft ? 'left' : 'right'}
                currentDay={currentDay}
                totalDays={totalDays}
                progressPercent={progressPercent}
              />
              <PhaseExpandedPanel events={phase.events} isExpanded={isExpanded} />
            </>
          );

          return (
            <React.Fragment key={phase.id}>
              {/* Column 1: Left content (desktop) / hidden (mobile via CSS) */}
              <div className={`${styles.leftCell} ${isLeft ? '' : styles.emptyCell}`}>
                {isLeft && (
                  <>
                    {cardBlock}
                    <div className={`${styles.connectorLeft} ${connectorClass}`} />
                  </>
                )}
              </div>

              {/* Column 2: Center node */}
              <div className={styles.nodeCell}>
                <div className={nodeClass}>
                  {phase.status === 'completed' && '✓'}
                  {phase.status === 'current' && <div className={styles.pulseDot} />}
                </div>
              </div>

              {/* Column 3: Right content (desktop) / all content (mobile via CSS) */}
              <div className={`${styles.rightCell} ${!isLeft ? '' : styles.emptyCell}`}>
                {!isLeft && (
                  <>
                    {cardBlock}
                    <div className={`${styles.connectorRight} ${connectorClass}`} />
                  </>
                )}
                {/* Mobile duplicate: render left-side cards in right column too,
                    shown only on mobile via CSS */}
                {isLeft && (
                  <div className={styles.mobileOnly}>
                    {cardBlock}
                  </div>
                )}
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
