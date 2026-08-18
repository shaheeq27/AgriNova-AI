/**
 * AgriNova AI — Color Tokens
 * Extracted from Stitch Design System (Ethereal Precision Agriculture)
 */

export const colors = {
  bg: {
    primary: '#131412',
    subtle: '#0E0E0D',
    surface: '#1B1C1B',
    card: '#1F201F',
    surfaceHigh: '#2A2A29',
    surfaceHighest: '#343533',
    surfaceBright: '#393938',
    surfaceHover: '#262725',
    surfaceActive: '#2E302D',
    overlay: 'rgba(19, 20, 18, 0.85)',
  },
  soil: {
    deep: '#1A1412',
    container: '#574238',
    fixed: '#FBDFCE',
  },
  sprout: {
    tint: '#BBCBBB',
    container: '#0F1C12',
    fixed: '#D7E7D6',
  },
  neonMint: {
    primary: '#ADFF00',
    hover: '#BDFF33',
    glow10: 'rgba(173, 255, 0, 0.10)',
    glow15: 'rgba(173, 255, 0, 0.15)',
    glow25: 'rgba(173, 255, 0, 0.25)',
    glow35: 'rgba(173, 255, 0, 0.35)',
  },
  crystallineBlue: {
    primary: '#E0F2F1',
    glow15: 'rgba(224, 242, 241, 0.15)',
  },
  dataStream: {
    primary: '#22C55E',
    glow20: 'rgba(34, 197, 94, 0.20)',
  },
  text: {
    primary: '#E4E2E0',
    secondary: '#C4C8C1',
    muted: '#8D928C',
    dim: '#434843',
    inverse: '#0E0E0D',
    onMint: '#0E0E0D',
  },
  border: {
    default: 'rgba(141, 146, 140, 0.15)',
    hover: 'rgba(173, 255, 0, 0.35)',
    active: 'rgba(173, 255, 0, 0.60)',
    subtle: 'rgba(141, 146, 140, 0.08)',
    mint: 'rgba(173, 255, 0, 0.20)',
    blue: 'rgba(224, 242, 241, 0.15)',
  },
  status: {
    success: '#ADFF00',
    warning: '#DEC1B2',
    error: '#FFB4AB',
    errorContainer: '#93000A',
    info: '#E0F2F1',
    critical: '#FFB4AB',
    healthy: '#ADFF00',
    stress: '#DEC1B2',
    disease: '#FFB4AB',
    neutral: '#C4C8C1',
    optimal: '#E0F2F1',
  },
} as const;

export type ColorToken = typeof colors;
