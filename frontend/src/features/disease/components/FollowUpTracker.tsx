import React, { useRef } from 'react';
import styles from './FollowUpTracker.module.css';
import { TreatmentLogEntry } from '../types';
import { Card } from '@/ui/Card';
import { Button } from '@/ui/Button';
import { Camera, CheckCircle } from 'lucide-react';

interface FollowUpTrackerProps {
  treatmentLog: TreatmentLogEntry | null;
  followUpImageUrl: string | null;
  onUploadFollowUp: (file: File) => void;
  onProceedToResolve: () => void;
}

export const FollowUpTracker: React.FC<FollowUpTrackerProps> = ({
  treatmentLog,
  followUpImageUrl,
  onUploadFollowUp,
  onProceedToResolve,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFollowUp(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUploadFollowUp(e.dataTransfer.files[0]);
    }
  };

  return (
    <Card className={styles.container}>
      <div className={styles.header}>
        <Camera size={24} className={styles.icon} />
        <h2 className={styles.title}>Follow Up</h2>
      </div>

      {treatmentLog && (
        <div className={styles.summaryCard}>
          <div className={styles.summaryGrid}>
            <div className={styles.summaryItem}>
              <span className={styles.label}>Applied</span>
              <span className={styles.value}>{treatmentLog.dateApplied}</span>
            </div>
            <div className={styles.summaryItem}>
              <span className={styles.label}>Treatment</span>
              <span className={styles.value}>{treatmentLog.treatmentUsed}</span>
            </div>
          </div>
        </div>
      )}

      <div className={styles.uploadSection}>
        <h3 className={styles.uploadTitle}>Upload Follow-up Image</h3>
        
        {!followUpImageUrl ? (
          <div 
            className={styles.uploadZone}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <Camera size={32} className={styles.uploadIcon} />
            <p className={styles.uploadText}>Click or drag to upload image</p>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              className={styles.hiddenInput}
            />
          </div>
        ) : (
          <div className={styles.imagePreviewContainer}>
            <img src={followUpImageUrl} alt="Follow-up preview" className={styles.previewImage} />
            <div className={styles.successOverlay}>
              <CheckCircle size={32} className={styles.successIcon} />
            </div>
          </div>
        )}
      </div>

      <Button 
        onClick={onProceedToResolve} 
        variant="ghost" 
        className={styles.proceedButton}
      >
        Proceed to Resolution
      </Button>
    </Card>
  );
};
