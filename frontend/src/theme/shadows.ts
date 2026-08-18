/**
 * AgriNova AI — Shadow & Glow System Tokens
 * Extracted from Stitch Design System (Depth & Glow)
 */

export const shadows = {
  elevation: {
    xs: '0 1px 2px rgba(0, 0, 0, 0.40)',
    sm: '0 2px 4px rgba(0, 0, 0, 0.45)',
    md: '0 4px 16px rgba(0, 0, 0, 0.50)',
    lg: '0 10px 30px rgba(0, 0, 0, 0.65)',
    xl: '0 20px 48px rgba(0, 0, 0, 0.80)',
  },
  inner: {
    default: 'inset 0 1px 4px rgba(0, 0, 0, 0.50)',
    sm: 'inset 0 1px 2px rgba(0, 0, 0, 0.30)',
    top: 'inset 0 2px 6px rgba(0, 0, 0, 0.35)',
  },
  glow: {
    mintXs: '0 0 4px rgba(173, 255, 0, 0.10)',
    mintSm: '0 0 8px rgba(173, 255, 0, 0.15)',
    mintMd: '0 0 16px rgba(173, 255, 0, 0.25)',
    mintLg: '0 0 24px rgba(173, 255, 0, 0.35)',
    mintXl: '0 0 36px rgba(173, 255, 0, 0.50)',
    spectral: '0 0 16px rgba(224, 242, 241, 0.15)',
    spectralLg: '0 0 28px rgba(224, 242, 241, 0.25)',
    telemetry: '0 0 12px rgba(34, 197, 94, 0.25)',
  },
  card: {
    default: 'inset 0 1px 4px rgba(0, 0, 0, 0.50), 0 0 1px rgba(173, 255, 0, 0.05)',
    hover: 'inset 0 1px 4px rgba(0, 0, 0, 0.50), 0 0 16px rgba(173, 255, 0, 0.25), 0 8px 24px rgba(0, 0, 0, 0.50)',
    active: 'inset 0 1px 4px rgba(0, 0, 0, 0.50), 0 0 24px rgba(173, 255, 0, 0.35), 0 12px 32px rgba(0, 0, 0, 0.65)',
  },
  focus: {
    mint: '0 0 0 2px rgba(173, 255, 0, 0.40)',
    blue: '0 0 0 2px rgba(224, 242, 241, 0.30)',
  },
} as const;

export type ShadowsToken = typeof shadows;
