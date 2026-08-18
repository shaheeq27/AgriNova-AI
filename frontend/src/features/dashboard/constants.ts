import {
  AttentionAlert,
  FarmEnvironmentData,
  UpcomingTask,
  OverdueTask,
  AIInsight,
  PerformanceMetric,
  ActivityBar,
  DiseaseRisk,
} from './types';

export const ATTENTION_ALERTS: AttentionAlert[] = [
  {
    id: 'alert-1',
    severity: 'critical',
    title: 'Skip irrigation — Farm C (Wheat)',
    sub: '84 mm rainfall recorded today. Soil is at field capacity.',
    why: 'Why: rainfall threshold exceeded · no irrigation needed for 2 days',
    actionText: 'Mark noted',
  },
  {
    id: 'alert-2',
    severity: 'warning',
    title: 'Late blight risk — Farm A (Tomato)',
    sub: 'Humidity 87% + temperature 24°C: conditions favorable for late blight.',
    why: 'Why: disease trigger conditions met · inspect leaves today',
    actionText: 'Detect now',
  },
  {
    id: 'alert-3',
    severity: 'info',
    title: 'Harvest window opens in 4 days — Farm B (Rice)',
    sub: 'Based on sowing date + growth timeline. Prepare equipment.',
    why: 'Why: day 116 of 120-day cycle reached',
    actionText: 'View timeline',
  },
];

export const FARM_ENVIRONMENTS: FarmEnvironmentData[] = [
  {
    id: 'farm-a',
    farmName: 'Farm A',
    cropName: 'Tomato',
    stage: 'Vegetative stage',
    day: 42,
    temperature: '24°C',
    humidity: '87%',
    humidityAlert: 'High',
    rainfall: '12 mm',
    wind: '14 km/h',
    status: 'amber',
  },
  {
    id: 'farm-b',
    farmName: 'Farm B',
    cropName: 'Rice',
    stage: 'Grain filling',
    day: 116,
    temperature: '27°C',
    humidity: '72%',
    rainfall: '46 mm',
    wind: '8 km/h',
    status: 'green',
  },
  {
    id: 'farm-c',
    farmName: 'Farm C',
    cropName: 'Wheat',
    stage: 'Germination',
    day: 7,
    temperature: '23°C',
    humidity: '91%',
    humidityAlert: 'Critical',
    rainfall: '84 mm',
    rainfallAlert: 'Heavy',
    wind: '22 km/h',
    status: 'red',
  },
];

export const UPCOMING_TASKS: UpcomingTask[] = [
  {
    id: 'task-1',
    name: 'Fertilizer — NPK top-dress',
    farm: 'Farm A',
    crop: 'Tomato',
    when: 'Tomorrow',
    dotColor: '#22c55e',
  },
  {
    id: 'task-2',
    name: 'Irrigation — 25 mm',
    farm: 'Farm A',
    crop: 'Tomato',
    when: 'Wed',
    dotColor: '#3b82f6',
  },
  {
    id: 'task-3',
    name: 'Pesticide — fungicide spray',
    farm: 'Farm B',
    crop: 'Rice',
    when: 'Thu',
    dotColor: '#a855f7',
  },
  {
    id: 'task-4',
    name: 'Growth stage check',
    farm: 'Farm C',
    crop: 'Wheat',
    when: 'Fri',
    dotColor: '#f59e0b',
  },
  {
    id: 'task-5',
    name: 'Harvest — begin cutting',
    farm: 'Farm B',
    crop: 'Rice',
    when: 'Sat',
    dotColor: '#ef4444',
  },
];

export const OVERDUE_TASKS: OverdueTask[] = [
  {
    id: 'overdue-1',
    title: 'Germination data not entered',
    sub: 'Farm C · Wheat · Day 7 started 2 days ago',
  },
  {
    id: 'overdue-2',
    title: 'Irrigation not logged',
    sub: 'Farm A · Tomato · scheduled 3 days ago',
  },
  {
    id: 'overdue-3',
    title: 'Vegetative stage inspection missed',
    sub: 'Farm A · Tomato · due 5 days ago',
  },
  {
    id: 'overdue-4',
    title: 'Fertilizer log missing',
    sub: 'Farm B · Rice · was due last week',
  },
];

export const AI_INSIGHTS: AIInsight[] = [
  {
    id: 'insight-1',
    title: 'Move fertilizer for Farm A to Wednesday',
    body: 'Rain forecast Tuesday will wash nitrogen from topsoil. Applying Wednesday after soil drains improves uptake by an estimated 20–30%.',
    iconType: 'droplets',
  },
  {
    id: 'insight-2',
    title: 'Delay pesticide spray on Farm B',
    body: 'Wind speed 22 km/h forecast Thursday. Spraying above 15 km/h causes drift and reduces effectiveness. Friday looks suitable.',
    iconType: 'wind',
  },
  {
    id: 'insight-3',
    title: 'Farm C germination is 2 days behind schedule',
    body: 'Based on sowing date and expected germination window. Check soil temperature — below 18°C can delay wheat germination. Log field observation today.',
    iconType: 'trending',
  },
];

export const PERFORMANCE_METRICS: PerformanceMetric[] = [
  {
    label: 'Task compliance',
    value: '68%',
    sub: '34 of 50 tasks logged',
  },
  {
    label: 'Disease detections',
    value: '2',
    sub: 'this month · 1 resolved',
  },
  {
    label: 'Irrigation events',
    value: '11',
    sub: 'vs 14 recommended',
  },
  {
    label: 'Crops on schedule',
    value: '2 / 3',
    sub: 'Farm C behind by 2d',
  },
];

export const ACTIVITY_BARS: ActivityBar[] = [
  { height: '80%', type: 'green' },
  { height: '65%', type: 'green' },
  { height: '90%', type: 'green' },
  { height: '70%', type: 'green' },
  { height: '55%', type: 'accent' },
  { height: '75%', type: 'accent' },
  { height: '40%', type: 'accent' },
  { height: '30%', type: 'warn' },
];

export const DISEASE_RISKS: DiseaseRisk[] = [
  {
    farm: 'Farm A · Tomato',
    info: 'High humidity detected today',
    risk: 'Medium',
  },
  {
    farm: 'Farm B · Rice',
    info: 'Normal conditions',
    risk: 'Low',
  },
  {
    farm: 'Farm C · Wheat',
    info: 'Waterlogging risk from rain',
    risk: 'High',
  },
];
