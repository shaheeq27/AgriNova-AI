import React from 'react';
import styles from './DiagnosisResult.module.css';
import { DiagnosisData, SeverityLevel } from '../types';
import { Card } from '@/ui/Card';
import { Badge } from '@/ui/Badge';
import { Leaf, Bug } from 'lucide-react';

interface DiagnosisResultProps {
  diagnosis: DiagnosisData;
  detectionSaved: boolean;
  imagePreviewUrl?: string | null;
  farmName?: string;
}

const getSeverityVariant = (severity: SeverityLevel) => {
  switch (severity) {
    case 'critical':
      return 'error';
    case 'high':
    case 'moderate':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'warning';
  }
};

export const DiagnosisResult: React.FC<DiagnosisResultProps> = ({ diagnosis, detectionSaved, imagePreviewUrl, farmName }) => {
  const badgeVariant = getSeverityVariant(diagnosis.severity);

  return (
    <Card className={styles.container}>
      {imagePreviewUrl && (
        <div className={styles.imageColumn}>
          <img src={imagePreviewUrl} alt="Analyzed crop" className={styles.analyzedImage} />
        </div>
      )}
      
      <div className={styles.detailsColumn}>
        <div className={styles.header}>
          <h2 className={styles.diseaseName}>{diagnosis.diseaseName}</h2>
          <Badge variant={badgeVariant} className={`${styles.severityBadge} ${styles[`severity-${diagnosis.severity}`]}`}>
            <span className={styles.severityIcon}>⚠</span> {diagnosis.severity.toUpperCase()}
          </Badge>
        </div>
        <p className={styles.scientificName}>{diagnosis.scientificName}</p>
        
        <p className={styles.description}>{diagnosis.description}</p>
        
        <div className={styles.symptomsSection}>
          <h3 className={styles.sectionTitle}>Key Symptoms</h3>
          <ul className={styles.symptomsList}>
            {diagnosis.symptoms.slice(0, 2).map((symptom, index) => (
              <li key={index} className={styles.symptomItem}>
                {index === 0 ? <Leaf size={16} className={styles.icon} /> : <Bug size={16} className={styles.icon} />}
                <span>{symptom}</span>
              </li>
            ))}
          </ul>
        </div>

        {detectionSaved && (
          farmName ? (
            <div className={styles.savedText}>
              <p>✓ Detection linked to {farmName}</p>
              <p>Added to Dashboard</p>
              <p>Added to Crop Timeline</p>
            </div>
          ) : (
            <div className={styles.savedText}>
              <p>✓ Analysis complete</p>
            </div>
          )
        )}
      </div>
    </Card>
  );
};
