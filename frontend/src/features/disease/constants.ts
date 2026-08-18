/* ══════════════════════════════════════════════════════════════
   AgriNova AI — Disease Detection Constants
   ══════════════════════════════════════════════════════════════ */

import type { DiagnosisData, FarmOption, DosageUnit, StepperStage } from './types';

/** Stepper stage definitions for the visual lifecycle */
export const STEPPER_STAGES: { key: StepperStage; label: string }[] = [
  { key: 'detect', label: 'DETECT' },
  { key: 'understand', label: 'UNDERSTAND' },
  { key: 'treat', label: 'TREAT' },
  { key: 'followup', label: 'FOLLOW UP' },
  { key: 'resolve', label: 'RESOLVE' },
];

/** Available dosage units for the combined quantity+unit control */
export const DOSAGE_UNITS: DosageUnit[] = ['ml', 'L', 'g', 'kg'];

/** Standalone farm option (not linked to any user farm) */
export const STANDALONE_FARM: FarmOption = {
  id: 'standalone',
  name: 'Standalone — Not my farm',
  isStandalone: true,
};

/**
 * Mock diagnosis data — simulates what a CV model would return.
 * Used for demo since the backend currently only supports symptom-based detection.
 */
export const MOCK_DIAGNOSIS: DiagnosisData = {
  diseaseName: 'Leaf Folder',
  scientificName: 'Cnaphalocrocis medinalis',
  severity: 'moderate',
  symptoms: [
    'Narrow and longitudinally rolled leaves',
    'Pale feeding streaks on leaf surface',
  ],
  description:
    'Leaf folder is a common rice pest whose larvae fold leaves and feed on the inner surface, causing significant photosynthetic loss and visible foliar damage.',
  recommendedAction:
    'Apply insecticide to affected areas using foliar spray. Focus on leaf undersides where larvae are most active.',
  actionUrgency: 'Take action within 1 week to prevent further spread.',
  whyRecommendation:
    'Early intervention targets active larval populations before they pupate and produce a second generation. The moderate severity indicates the infestation has not yet caused irreversible damage, so timely treatment can fully restore crop health.',
  treatment: {
    productName: 'Chlorantraniliprole 18.5% SC',
    dosage: '150 ml per acre',
    applicationMethod: 'Foliar spray',
    instructions:
      'Apply in the evening when pest activity is highest. Ensure thorough coverage of leaf undersides. Re-apply after 14 days if infestation persists.',
  },
  naturalTreatment: null, // No effective natural treatment for leaf folder
};

/** Accepted image MIME types */
export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

/** Max image file size in bytes (10MB) */
export const MAX_IMAGE_SIZE = 10 * 1024 * 1024;
