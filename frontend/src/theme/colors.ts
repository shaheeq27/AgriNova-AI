/**
 * AgriNova AI — Color Tokens (v1.1)
 */

export const colors = {
  bg: {
    primary: '#010603',
    subtle: '#041008',
    surface: '#07140A',
    card: '#0B1B10',
    surfaceHover: '#0F2216',
    surfaceActive: '#132A1C',
    overlay: 'rgba(1, 6, 3, 0.85)',
  },
  accent: {
    primary: '#66FF88',
    secondary: '#55F6FF',
    muted: '#4FAE68',
    dim: '#2D6B42',
    faint: '#1A3D28',
  },
  glow: {
    10: 'rgba(102, 255, 136, 0.10)',
    15: 'rgba(102, 255, 136, 0.15)',
    20: 'rgba(102, 255, 136, 0.20)',
    30: 'rgba(102, 255, 136, 0.30)',
  },
  cyan: {
    primary: '#55F6FF',
    glow: 'rgba(85, 246, 255, 0.12)',
  },
  text: {
    primary: '#E8F5EC',
    secondary: '#8FB89E',
    muted: '#5A8A6D',
    dim: '#3D6A52',
    inverse: '#010603',
  },
  border: {
    default: 'rgba(102, 255, 136, 0.08)',
    hover: 'rgba(102, 255, 136, 0.16)',
    active: 'rgba(102, 255, 136, 0.28)',
    subtle: 'rgba(102, 255, 136, 0.04)',
  },
  status: {
    success: '#66FF88',
    warning: '#FFC857',
    error: '#FF6B6B',
    info: '#55F6FF',
    critical: '#FF6B6B',
    healthy: '#66FF88',
    stress: '#FFC857',
    disease: '#FF6B6B',
    neutral: '#8FB89E',
    optimal: '#55F6FF',
  },
} as const;

export type ColorToken = typeof colors;
