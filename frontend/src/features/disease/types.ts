/* ══════════════════════════════════════════════════════════════
   AgriNova AI — Disease Detection Types
   5-stage workflow: DETECT → UNDERSTAND → TREAT → FOLLOW UP → RESOLVE
   ══════════════════════════════════════════════════════════════ */

/** Page-level workflow state */
export type WorkflowStage = 'initial' | 'analyzing' | 'result' | 'followup' | 'resolved';

/** Stepper stages matching the visual lifecycle */
export type StepperStage = 'detect' | 'understand' | 'treat' | 'followup' | 'resolve';

/** Disease severity levels */
export type SeverityLevel = 'critical' | 'high' | 'moderate' | 'low';

/** Resolution outcome options */
export type ResolutionOutcome = 'resolved' | 'partially_resolved' | 'recurring';

/** Dosage unit options for combined quantity+unit control */
export type DosageUnit = 'ml' | 'L' | 'g' | 'kg';

export interface MLModelPrediction {
  predicted_crop: string;
  predicted_disease: string;
  model_probability: number;
  is_healthy: boolean;
}

export interface KBDiseaseInfo {
  disease_name: string;
  symptoms: string;
  treatment: string;
  prevention: string;
  severity: SeverityLevel;
}

export interface ImageAnalysisResponse {
  model_prediction: MLModelPrediction;
  knowledge_base_evidence: KBDiseaseInfo | null;
}

/** Treatment log entry submitted by the farmer */
export interface TreatmentLogEntry {
  treatmentUsed: string;
  dateApplied: string;
  quantity: number;
  unit: DosageUnit;
}

/** Farm option for the dropdown */
export interface FarmOption {
  id: string;
  name: string;
  isStandalone: boolean;
}

/** Full state for the disease detection workflow */
export interface DiseaseDetectionState {
  stage: WorkflowStage;
  selectedImage: File | null;
  imagePreviewUrl: string | null;
  selectedFarm: FarmOption | null;
  analysisResult: ImageAnalysisResponse | null;
  treatmentLog: TreatmentLogEntry | null;
  showTreatmentForm: boolean;
  followUpImage: File | null;
  followUpImageUrl: string | null;
  resolutionOutcome: ResolutionOutcome | null;
  resolutionNotes: string;
  isAnalyzing: boolean;
  isSaving: boolean;
  detectionSaved: boolean;
  error: string | null;
}
