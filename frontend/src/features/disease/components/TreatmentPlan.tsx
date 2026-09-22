import React, { useState } from 'react';
import styles from './TreatmentPlan.module.css';
import { ImageAnalysisResponse, TreatmentLogEntry, DosageUnit } from '../types';
import { DOSAGE_UNITS } from '../constants';
import { Card } from '@/ui/Card';
import { Button } from '@/ui/Button';
import { Pill } from 'lucide-react';

interface TreatmentPlanProps {
  analysisResult: ImageAnalysisResponse;
  showTreatmentForm: boolean;
  isSaving: boolean;
  onOpenForm: () => void;
  onCloseForm: () => void;
  onLogTreatment: (entry: TreatmentLogEntry) => void;
  isStandalone?: boolean;
  onReset?: () => void;
}

export const TreatmentPlan: React.FC<TreatmentPlanProps> = ({
  analysisResult,
  showTreatmentForm,
  isSaving,
  onOpenForm,
  onCloseForm,
  onLogTreatment,
  isStandalone,
  onReset,
}) => {
  const [treatmentUsed, setTreatmentUsed] = useState('');
  const [dateApplied, setDateApplied] = useState('');
  const [quantity, setQuantity] = useState<number | ''>('');
  const [unit, setUnit] = useState<DosageUnit>('ml');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!treatmentUsed || !dateApplied || quantity === '') return;

    onLogTreatment({
      treatmentUsed,
      dateApplied,
      quantity: Number(quantity),
      unit,
    });
  };

  return (
    <div className={styles.container}>
      <Card className={styles.treatmentCard}>
        <div className={styles.header}>
          <Pill size={24} className={styles.icon} />
          <h2 className={styles.title}>Treatment</h2>
        </div>

        <div className={styles.productSection}>
          <div className={styles.detailsGrid}>
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Recommended Action:</span>
              <span className={styles.detailValue}>{analysisResult.knowledge_base_evidence?.treatment}</span>
            </div>
          </div>
        </div>
      </Card>

      {!showTreatmentForm ? (
        <Card className={styles.actionCard}>
          {isStandalone ? (
            <div className={styles.actionPrompt}>
              <h3 className={styles.actionTitle}>🔎 Standalone analysis</h3>
              <p className={styles.actionText}>Treatment logging is optional for standalone analysis.</p>
              <div className={styles.buttonGroup}>
                <Button onClick={onOpenForm} className={styles.logButton} variant="primary">
                  LOG TREATMENT (optional)
                </Button>
                <Button onClick={onReset} className={styles.resetButton} variant="secondary">
                  ↻ Analyze Another Image
                </Button>
              </div>
            </div>
          ) : (
            <div className={styles.actionPrompt}>
              <h3 className={styles.actionTitle}>🌱 Farm-linked detection</h3>
              <p className={styles.actionText}>✓ Treatment logging required for this case.</p>
              <Button onClick={onOpenForm} className={styles.logButton} variant="primary">
                LOG TREATMENT
              </Button>
            </div>
          )}
        </Card>
      ) : (
        <Card className={styles.formCard}>
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label>Treatment Used</label>
              <input
                type="text"
                value={treatmentUsed}
                onChange={(e) => setTreatmentUsed(e.target.value)}
                required
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Date Applied</label>
              <input
                type="date"
                value={dateApplied}
                onChange={(e) => setDateApplied(e.target.value)}
                required
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label>Quantity & Unit</label>
              <div className={styles.combinedControl}>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value === '' ? '' : Number(e.target.value))}
                  required
                  min="0"
                  step="any"
                  className={styles.quantityInput}
                />
                <select
                  value={unit}
                  onChange={(e) => setUnit(e.target.value as DosageUnit)}
                  className={styles.unitSelect}
                >
                  {DOSAGE_UNITS.map(u => (
                    <option key={u} value={u}>{u}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className={styles.formActions}>
              <Button type="button" variant="ghost" onClick={onCloseForm}>
                Cancel
              </Button>
              <Button type="submit" isLoading={isSaving} variant="primary">
                Save Treatment
              </Button>
            </div>
          </form>
        </Card>
      )}
    </div>
  );
};
