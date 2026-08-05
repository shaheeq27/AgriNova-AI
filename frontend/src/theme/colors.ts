/**
 * AgriNova AI — Color Tokens (TypeScript)
 */

export const colors = {
  bg: {
    primary: '#040a06',
    subtle: '#081410',
    surface: '#0d1f15',
    surfaceHover: '#122a1c',
    surfaceActive: '#173523',
    glass: 'rgba(13, 31, 21, 0.7)',
    overlay: 'rgba(4, 10, 6, 0.8)',
  },
  accent: {
    primary: '#4ee86a',
    secondary: '#2dd4a8',
    muted: '#1a5a3a',
    dim: '#14402a',
    faint: '#0d2e1e',
  },
  glow: {
    10: 'rgba(78, 232, 106, 0.10)',
    15: 'rgba(78, 232, 106, 0.15)',
    20: 'rgba(78, 232, 106, 0.20)',
    30: 'rgba(78, 232, 106, 0.30)',
  },
  text: {
    primary: '#e8f5ec',
    secondary: '#8fb89e',
    muted: '#5a8a6d',
    dim: '#3d6a52',
    inverse: '#040a06',
  },
  border: {
    default: 'rgba(78, 232, 106, 0.08)',
    hover: 'rgba(78, 232, 106, 0.16)',
    active: 'rgba(78, 232, 106, 0.28)',
    subtle: 'rgba(78, 232, 106, 0.04)',
  },
  status: {
    success: '#4ee86a',
    warning: '#f5a623',
    error: '#ef4444',
    info: '#3b82f6',
    critical: '#dc2626',
    healthy: '#4ee86a',
    stress: '#f5a623',
    disease: '#ef4444',
    neutral: '#8fb89e',
    optimal: '#2dd4a8',
  },
} as const;

export type ColorToken = typeof colors;
