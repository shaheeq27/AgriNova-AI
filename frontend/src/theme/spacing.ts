/**
 * AgriNova AI — Grid & Layout Tokens
 * Extracted from Stitch Design System
 */

export const spacing = {
  unit: '8px',
  scale: {
    0: '0px',
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    5: '20px',
    6: '24px',
    7: '28px',
    8: '32px',
    9: '36px',
    10: '40px',
    12: '48px',
    14: '56px',
    16: '64px',
    20: '80px',
    24: '96px',
  },
  layout: {
    containerPadding: '24px',
    gutter: '16px',
    sectionGap: '48px',
    sidebarWidth: '280px',
    sidebarCollapsed: '72px',
    contentMaxWidth: '1600px',
    navbarHeight: '64px',
    bottomNavHeight: '64px',
    mobilePadding: '16px',
  },
} as const;

export type SpacingToken = typeof spacing;
