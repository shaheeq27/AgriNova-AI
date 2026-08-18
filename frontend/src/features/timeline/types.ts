/* ══════════════════════════════════════════════════════════
   AgriNova — Crop Journey / Timeline Feature Types
   ══════════════════════════════════════════════════════════ */

export type PhaseStatus = 'completed' | 'current' | 'upcoming';

export type EventCategory = 'milestone' | 'health' | 'treatment' | 'ai';

/** A single important event that occurred during a crop phase. */
export interface PhaseEvent {
  id: string;
  date: string;
  category: EventCategory;
  title: string;
  description: string;
  icon: string;
}

/** A major lifecycle phase of the crop journey. */
export interface CropJourneyPhase {
  id: string;
  name: string;
  stageOrder: number;
  startDate: string;
  endDate: string;
  dayStart: number;
  dayEnd: number;
  status: PhaseStatus;
  icon: string;
  description?: string;
  events: PhaseEvent[];
}

/** Summary metrics for the crop journey. */
export interface JourneySummaryData {
  totalEvents: number;
  healthIssues: number;
  treatmentsApplied: number;
  aiInsights: number;
}

/** The complete crop journey data structure. */
export interface CropJourney {
  cropName: string;
  farmName: string;
  season: string;
  plantingDate: string;
  totalDays: number;
  currentDay: number;
  progressPercent: number;
  currentPhaseName: string;
  phases: CropJourneyPhase[];
  summary: JourneySummaryData;
}
