export const NAVIGATION_LINKS = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'Crops', href: '/crops', icon: 'Sprout' },
  { label: 'Farms', href: '/farms', icon: 'MapPin' },
  { label: 'Weather', href: '/weather', icon: 'CloudSun' },
  { label: 'Knowledge Base', href: '/knowledge', icon: 'BookOpen' },
];

export const SOIL_TYPES = [
  'Clay',
  'Loamy',
  'Sandy',
  'Black',
  'Red',
  'Alluvial',
  'Laterite',
] as const;

export const SEASONS = ['Kharif', 'Rabi', 'Zaid', 'Whole Year'] as const;

export const CROP_STAGES = [
  'Germination',
  'Seedling',
  'Vegetative',
  'Flowering',
  'Fruiting',
  'Maturity',
] as const;
