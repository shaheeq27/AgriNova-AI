import React from 'react';
import styles from './DiagnosisResult.module.css';
import { ImageAnalysisResponse, SeverityLevel } from '../types';
import { Card } from '@/ui/Card';
import { Badge } from '@/ui/Badge';
import { Leaf, Bug } from 'lucide-react';

interface DiagnosisResultProps {
  analysisResult: ImageAnalysisResponse;
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

export const DiagnosisResult: React.FC<DiagnosisResultProps> = ({ analysisResult, detectionSaved, imagePreviewUrl, farmName }) => {
  const badgeVariant = analysisResult.knowledge_base_evidence ? getSeverityVariant(analysisResult.knowledge_base_evidence.severity) : 'success';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <Card className={styles.container}>
        {imagePreviewUrl && (
          <div className={styles.imageColumn}>
            <img src={imagePreviewUrl} alt="Analyzed crop" className={styles.analyzedImage} />
          </div>
        )}

        <div className={styles.detailsColumn}>
          <div className={styles.header}>
            <h2 className={styles.diseaseName}>
              {analysisResult.model_prediction.is_healthy ? 'Crop Appears Healthy' : analysisResult.model_prediction.predicted_disease}
            </h2>
            <Badge variant="ai" style={{ backgroundColor: 'rgba(52, 152, 219, 0.2)', color: '#3498db' }}>
              Model Probability: {(analysisResult.model_prediction.model_probability * 100).toFixed(1)}%
            </Badge>
          </div>


          {analysisResult.model_prediction.is_healthy && (
            <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(46, 204, 113, 0.1)', borderRadius: '8px', color: '#2ecc71', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Leaf size={20} />
              <span>No signs of disease detected.</span>
            </div>
          )}

          {!analysisResult.model_prediction.is_healthy && !analysisResult.knowledge_base_evidence && (
            <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(241, 196, 15, 0.1)', borderRadius: '8px', color: '#f1c40f', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '20px' }}>⚠️</span>
              <span>Prediction logged, but no knowledge base data is currently available for this specific disease.</span>
            </div>
          )}

          {detectionSaved && (
            farmName ? (
              <div className={styles.savedText}>
                <p>✓ Detection linked to {farmName}</p>
                <p>Added to Dashboard & Crop Timeline</p>
              </div>
            ) : (
              <div className={styles.savedText}>
                <p>✓ Analysis complete</p>
              </div>
            )
          )}
        </div>
      </Card>

      {!analysisResult.model_prediction.is_healthy && analysisResult.knowledge_base_evidence && (
        <Card className={styles.container} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
          <div className={styles.header} style={{ width: '100%', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>Knowledge Base Data</h3>
            <Badge variant={badgeVariant} className={`${styles.severityBadge} ${styles[`severity-${analysisResult.knowledge_base_evidence.severity}`]}`}>
              <span className={styles.severityIcon}>⚠</span> {analysisResult.knowledge_base_evidence.severity.toUpperCase()} SEVERITY
            </Badge>
          </div>

          <div className={styles.symptomsSection} style={{ marginTop: 0, width: '100%' }}>
            <h4 className={styles.sectionTitle}>Key Symptoms</h4>
            <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', color: 'rgba(255, 255, 255, 0.8)' }}>
              {analysisResult.knowledge_base_evidence.symptoms}
            </p>
          </div>

          <div className={styles.symptomsSection} style={{ marginTop: '16px', width: '100%' }}>
            <h4 className={styles.sectionTitle}>Prevention</h4>
            <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', color: 'rgba(255, 255, 255, 0.8)' }}>
              {analysisResult.knowledge_base_evidence.prevention}
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};
