import React, { useState } from 'react';
import styles from './ResolutionPanel.module.css';
import { ResolutionOutcome } from '../types';
import { Card } from '@/ui/Card';
import { Button } from '@/ui/Button';
import { CheckCircle, AlertTriangle, RotateCcw } from 'lucide-react';

interface ResolutionPanelProps {
  isSaving: boolean;
  resolutionOutcome: ResolutionOutcome | null;
  onResolve: (outcome: ResolutionOutcome, notes: string) => void;
  onNewDetection: () => void;
}

export const ResolutionPanel: React.FC<ResolutionPanelProps> = ({
  isSaving,
  resolutionOutcome,
  onResolve,
  onNewDetection,
}) => {
  const [selectedOutcome, setSelectedOutcome] = useState<ResolutionOutcome | null>(null);
  const [notes, setNotes] = useState('');

  const handleResolve = () => {
    if (selectedOutcome) {
      onResolve(selectedOutcome, notes);
    }
  };

  if (resolutionOutcome) {
    return (
      <Card className={styles.successCard}>
        <div className={styles.successContent}>
          <div className={styles.successIconWrapper}>
            <CheckCircle size={48} className={styles.successIcon} />
          </div>
          <h2 className={styles.successTitle}>
            {resolutionOutcome === 'resolved' && 'Case Resolved'}
            {resolutionOutcome === 'partially_resolved' && 'Case Monitored'}
            {resolutionOutcome === 'recurring' && 'Case Reopened'}
          </h2>
          <p className={styles.successMessage}>
            The resolution has been saved to your farm records.
          </p>
          <Button onClick={onNewDetection} variant="ghost" className={styles.newDetectionBtn}>
            New Detection
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className={styles.container}>
      <h2 className={styles.title}>Resolution</h2>
      
      <div className={styles.optionsContainer}>
        <div 
          className={`${styles.optionCard} ${selectedOutcome === 'resolved' ? styles.selected : ''}`}
          onClick={() => setSelectedOutcome('resolved')}
        >
          <CheckCircle size={20} className={styles.optionIcon} />
          <div className={styles.optionText}>
            <h4>Resolved</h4>
            <p>Issue fully resolved</p>
          </div>
        </div>

        <div 
          className={`${styles.optionCard} ${selectedOutcome === 'partially_resolved' ? styles.selected : ''}`}
          onClick={() => setSelectedOutcome('partially_resolved')}
        >
          <AlertTriangle size={20} className={styles.optionIcon} />
          <div className={styles.optionText}>
            <h4>Partially Resolved</h4>
            <p>Improvement seen, monitoring continues</p>
          </div>
        </div>

        <div 
          className={`${styles.optionCard} ${selectedOutcome === 'recurring' ? styles.selected : ''}`}
          onClick={() => setSelectedOutcome('recurring')}
        >
          <RotateCcw size={20} className={styles.optionIcon} />
          <div className={styles.optionText}>
            <h4>Recurring</h4>
            <p>Issue persists or has returned</p>
          </div>
        </div>
      </div>

      <div className={styles.notesSection}>
        <label htmlFor="resolution-notes" className={styles.notesLabel}>Notes (optional)</label>
        <textarea
          id="resolution-notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className={styles.textarea}
          rows={3}
          placeholder="Add any final observations..."
        />
      </div>

      <Button
        onClick={handleResolve}
        isDisabled={!selectedOutcome}
        isLoading={isSaving}
        variant="primary"
        className={styles.submitBtn}
      >
        Mark Resolved
      </Button>
    </Card>
  );
};
