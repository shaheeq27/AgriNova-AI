/* ══════════════════════════════════════════════════════════
   AgriNova — Crop Journey Mock Data
   ──────────────────────────────────────────────────────────
   Rice · Green Valley Farm · Kharif 2026
   9 major lifecycle phases with events in select phases.
   Architecture supports any crop / any phase count.
   ══════════════════════════════════════════════════════════ */

import type { CropJourney } from './types';

export const MOCK_CROP_JOURNEY: CropJourney = {
  cropName: 'Rice',
  farmName: 'Green Valley Farm',
  season: 'Kharif 2026',
  plantingDate: '2026-06-03',
  totalDays: 120,
  currentDay: 64,
  progressPercent: 53,
  currentPhaseName: 'Vegetative Growth',

  summary: {
    totalEvents: 18,
    healthIssues: 2,
    treatmentsApplied: 4,
    aiInsights: 4,
  },

  phases: [
    /* ── 1. Land Preparation ── */
    {
      id: 'phase-land-prep',
      name: 'Land Preparation',
      stageOrder: 1,
      startDate: '2026-05-20',
      endDate: '2026-06-02',
      dayStart: -14,
      dayEnd: -1,
      status: 'completed',
      icon: '🚜',
      description: 'Prepare paddy fields, level soil, and establish irrigation channels.',
      events: [
        {
          id: 'ev-lp-1',
          date: '2026-05-22',
          category: 'milestone',
          title: 'Soil analysis completed',
          description: 'pH 6.2, ideal for rice. NPK levels within acceptable range.',
          icon: '🌱',
        },
        {
          id: 'ev-lp-2',
          date: '2026-05-28',
          category: 'milestone',
          title: 'Field leveling completed',
          description: 'Laser leveling across 12 acres finished.',
          icon: '🌱',
        },
      ],
    },

    /* ── 2. Seeding / Planting ── */
    {
      id: 'phase-seeding',
      name: 'Seeding / Planting',
      stageOrder: 2,
      startDate: '2026-06-03',
      endDate: '2026-06-09',
      dayStart: 1,
      dayEnd: 7,
      status: 'completed',
      icon: '🌱',
      description: 'Transplant seedlings into prepared paddy fields.',
      events: [
        {
          id: 'ev-sd-1',
          date: '2026-06-05',
          category: 'milestone',
          title: 'Seeds planted',
          description: 'Basmati 1121 variety transplanted across all sections.',
          icon: '🌱',
        },
      ],
    },

    /* ── 3. Germination ── */
    {
      id: 'phase-germination',
      name: 'Germination',
      stageOrder: 3,
      startDate: '2026-06-10',
      endDate: '2026-06-22',
      dayStart: 8,
      dayEnd: 20,
      status: 'completed',
      icon: '🌱',
      description: 'Root system develops and first shoots emerge above water line.',
      events: [
        {
          id: 'ev-gm-1',
          date: '2026-06-14',
          category: 'milestone',
          title: 'Germination confirmed',
          description: '92% emergence rate across all planted sections.',
          icon: '🌱',
        },
        {
          id: 'ev-gm-2',
          date: '2026-06-18',
          category: 'ai',
          title: 'AI Growth Assessment',
          description: 'Emergence rate 8% above regional average. No intervention needed.',
          icon: '🤖',
        },
      ],
    },

    /* ── 4. Early Growth ── */
    {
      id: 'phase-early-growth',
      name: 'Early Growth',
      stageOrder: 4,
      startDate: '2026-06-23',
      endDate: '2026-07-07',
      dayStart: 21,
      dayEnd: 35,
      status: 'completed',
      icon: '🌿',
      description: 'Tillering begins. Plant establishes strong root network and leaf canopy.',
      events: [
        {
          id: 'ev-eg-1',
          date: '2026-06-25',
          category: 'milestone',
          title: 'Strong root development',
          description: 'Root system penetration exceeds 15cm depth uniformly.',
          icon: '🌱',
        },
        {
          id: 'ev-eg-2',
          date: '2026-07-02',
          category: 'treatment',
          title: 'Fertilizer applied',
          description: 'NPK 19:19:19 applied at recommended dosage.',
          icon: '🌿',
        },
      ],
    },

    /* ── 5. Vegetative Growth — CURRENT PHASE ── */
    {
      id: 'phase-vegetative',
      name: 'Vegetative Growth',
      stageOrder: 5,
      startDate: '2026-07-08',
      endDate: '2026-08-15',
      dayStart: 36,
      dayEnd: 74,
      status: 'current',
      icon: '🌿',
      description:
        'Rapid biomass accumulation. Tiller count increasing. Leaf area index trending above seasonal average.',
      events: [
        {
          id: 'ev-vg-1',
          date: '2026-07-15',
          category: 'milestone',
          title: 'Growth milestone',
          description: 'Healthy vegetative growth observed. Tiller count at 18 per hill.',
          icon: '🌱',
        },
        {
          id: 'ev-vg-2',
          date: '2026-07-18',
          category: 'health',
          title: 'Pest detected',
          description: 'Leaf folder detected · Moderate severity across sections 2 & 4.',
          icon: '🐛',
        },
        {
          id: 'ev-vg-3',
          date: '2026-07-20',
          category: 'ai',
          title: 'AI Recommendation (Major)',
          description: 'Recommended treatment due to pest risk. Immediate action advised.',
          icon: '🤖',
        },
        {
          id: 'ev-vg-4',
          date: '2026-07-21',
          category: 'treatment',
          title: 'Pesticide applied',
          description: 'Chlorantraniliprole 18.5% SC applied to affected sections.',
          icon: '🧪',
        },
        {
          id: 'ev-vg-5',
          date: '2026-07-25',
          category: 'milestone',
          title: 'Pest controlled',
          description: 'Pest activity reduced significantly. No further damage observed.',
          icon: '✅',
        },
        {
          id: 'ev-vg-6',
          date: '2026-08-05',
          category: 'treatment',
          title: 'Fertilizer applied',
          description: 'Urea 46% top-dressing at 40 kg/acre.',
          icon: '🌿',
        },
      ],
    },

    /* ── 6. Flowering ── */
    {
      id: 'phase-flowering',
      name: 'Flowering',
      stageOrder: 6,
      startDate: '2026-08-16',
      endDate: '2026-09-05',
      dayStart: 75,
      dayEnd: 95,
      status: 'upcoming',
      icon: '🌾',
      description: 'Panicle initiation and anthesis. Critical pollination window.',
      events: [],
    },

    /* ── 7. Grain Development ── */
    {
      id: 'phase-grain-dev',
      name: 'Grain Development',
      stageOrder: 7,
      startDate: '2026-09-06',
      endDate: '2026-09-22',
      dayStart: 96,
      dayEnd: 112,
      status: 'upcoming',
      icon: '🌾',
      description: 'Grain filling and starch accumulation in developing kernels.',
      events: [],
    },

    /* ── 8. Maturity ── */
    {
      id: 'phase-maturity',
      name: 'Maturity',
      stageOrder: 8,
      startDate: '2026-09-23',
      endDate: '2026-09-28',
      dayStart: 113,
      dayEnd: 118,
      status: 'upcoming',
      icon: '🌾',
      description: 'Grain moisture drops below 20%. Panicles turn golden.',
      events: [],
    },

    /* ── 9. Harvest ── */
    {
      id: 'phase-harvest',
      name: 'Harvest',
      stageOrder: 9,
      startDate: '2026-09-29',
      endDate: '2026-10-01',
      dayStart: 119,
      dayEnd: 120,
      status: 'upcoming',
      icon: '🚜',
      description: 'Crop harvesting and threshing. Target moisture content: 14%.',
      events: [],
    },
  ],
};
