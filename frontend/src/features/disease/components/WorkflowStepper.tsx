'use client';
import React from 'react';
import styles from './WorkflowStepper.module.css';
import { WorkflowStage, StepperStage } from '../types';
import { Check } from 'lucide-react';

interface WorkflowStepperProps {
  currentStage: WorkflowStage;
}

const STEPPER_STAGES: { id: StepperStage; label: string }[] = [
  { id: 'detect', label: 'DETECT' },
  { id: 'understand', label: 'UNDERSTAND' },
  { id: 'treat', label: 'TREAT' },
  { id: 'followup', label: 'FOLLOW UP' },
  { id: 'resolve', label: 'RESOLVE' },
];

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({ currentStage }) => {
  // Determine active stepper position
  let activeIndex = 0;
  if (currentStage === 'result') activeIndex = 2; // TREAT
  if (currentStage === 'followup') activeIndex = 3; // FOLLOW UP
  if (currentStage === 'resolved') activeIndex = 4; // RESOLVE

  return (
    <div className={styles.stepperContainer}>
      {STEPPER_STAGES.map((stage, index) => {
        const isCompleted = index < activeIndex || (currentStage === 'resolved' && index === 4);
        const isCurrent = index === activeIndex && currentStage !== 'resolved';
        
        return (
          <React.Fragment key={stage.id}>
            <div className={styles.step}>
              <div className={`
                ${styles.node} 
                ${isCompleted ? styles.completed : ''} 
                ${isCurrent ? styles.current : ''}
              `}>
                {isCompleted && <Check size={14} className={styles.checkIcon} />}
                {isCurrent && <div className={styles.pulseNode} />}
              </div>
              <span className={`
                ${styles.label} 
                ${isCompleted ? styles.completedLabel : ''} 
                ${isCurrent ? styles.currentLabel : ''}
              `}>
                {stage.label}
              </span>
            </div>
            {index < STEPPER_STAGES.length - 1 && (
              <div className={`${styles.line} ${isCompleted ? styles.lineCompleted : ''}`} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
