/* ══════════════════════════════════════════════════════════════
   AgriNova AI — Disease Detection Constants
   ══════════════════════════════════════════════════════════════ */

import type { FarmOption, DosageUnit, StepperStage } from './types';

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

/** Accepted image MIME types */
export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

/** Max image file size in bytes (10MB) */
export const MAX_IMAGE_SIZE = 10 * 1024 * 1024;
