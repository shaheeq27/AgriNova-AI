/**
 * AgriNova AI — Typography Tokens
 * Extracted from Stitch Design System (Ethereal Precision Agriculture)
 */

export const typography = {
  family: {
    serif: "'Source Serif 4', 'Playfair Display', Georgia, serif",
    sans: "'Hanken Grotesk', 'Inter', system-ui, sans-serif",
    mono: "'JetBrains Mono', 'Space Mono', monospace",
  },
  size: {
    '2xs': '10px',
    xs: '11px',
    sm: '12px',
    base: '14px',
    md: '16px',
    lg: '18px',
    xl: '24px',
    '2xl': '32px',
    '3xl': '40px',
    '4xl': '48px',
    hero: '56px',
  },
  weight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  leading: {
    tight: 1.1,
    snug: 1.25,
    normal: 1.5,
    relaxed: 1.6,
    loose: 1.75,
  },
  tracking: {
    tight: '-0.02em',
    normal: '0',
    wide: '0.02em',
    wider: '0.06em',
    mono: '0.10em',
  },
  presets: {
    headlineLg: {
      fontFamily: "'Source Serif 4', serif",
      fontSize: '48px',
      fontWeight: 600,
      lineHeight: '56px',
      letterSpacing: '-0.02em',
    },
    headlineMd: {
      fontFamily: "'Source Serif 4', serif",
      fontSize: '32px',
      fontWeight: 600,
      lineHeight: '40px',
    },
    headlineSm: {
      fontFamily: "'Source Serif 4', serif",
      fontSize: '24px',
      fontWeight: 500,
      lineHeight: '32px',
    },
    bodyLg: {
      fontFamily: "'Hanken Grotesk', sans-serif",
      fontSize: '18px',
      fontWeight: 400,
      lineHeight: '28px',
    },
    bodyMd: {
      fontFamily: "'Hanken Grotesk', sans-serif",
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: '24px',
    },
    labelCaps: {
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: '12px',
      fontWeight: 500,
      lineHeight: '16px',
      letterSpacing: '0.10em',
      textTransform: 'uppercase' as const,
    },
    dataDisplay: {
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: '14px',
      fontWeight: 400,
      lineHeight: '20px',
    },
  },
} as const;

export type TypographyToken = typeof typography;
