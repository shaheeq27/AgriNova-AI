/**
 * AgriNova AI — Typography Tokens
 */

export const typography = {
  family: {
    serif: "'Playfair Display', 'Georgia', serif",
    sans: "'Inter', system-ui, -apple-system, sans-serif",
    mono: "'Space Mono', 'Courier New', monospace",
  },
  size: {
    '2xs': '10px',
    xs: '11px',
    sm: '13px',
    base: '14px',
    md: '15px',
    lg: '18px',
    xl: '22px',
    '2xl': '28px',
    '3xl': '36px',
    '4xl': '48px',
    hero: '56px',
  },
  weight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },
  leading: {
    tight: 1.1,
    snug: 1.2,
    normal: 1.5,
    relaxed: 1.6,
    loose: 1.8,
  },
} as const;
