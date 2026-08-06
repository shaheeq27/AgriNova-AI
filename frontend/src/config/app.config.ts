export const APP_CONFIG = {
  name: 'AgriNova AI',
  tagline: 'Where Nature Meets Intelligence',
  description: 'Precision Agriculture Platform Powered by Artificial Intelligence',
  version: '1.1.0',
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    timeout: 15000,
  },
  theme: {
    defaultMode: 'dark',
    accentColor: '#4EE86A',
  },
};
