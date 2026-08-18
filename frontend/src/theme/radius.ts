/**
 * AgriNova AI — Border Radius Tokens
 * Extracted from Stitch Design System (Organic-Geometric)
 */

export const radius = {
  xs: '2px',
  sm: '4px',       // 0.25rem - Subtle chips
  md: '8px',       // 0.5rem  - Buttons & Inputs (DEFAULT)
  lg: '12px',      // 0.75rem - Standard cards
  xl: '24px',      // 1.5rem  - Large glass containers
  '2xl': '32px',   // Command center panels
  full: '9999px',  // Pills, badges, rounded avatars
} as const;

export type RadiusToken = typeof radius;
