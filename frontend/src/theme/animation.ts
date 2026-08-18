/**
 * AgriNova AI — Motion System Tokens
 * Extracted from Stitch Design System
 */

export const animation = {
  duration: {
    instant: '100ms',
    fast: '180ms',
    normal: '250ms',
    slow: '400ms',
    max: '500ms',
    ambient: '4000ms',
    bg: '20000ms',
  },
  easing: {
    easeOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    spring: 'cubic-bezier(0.16, 1, 0.3, 1)', // Buttons only
  },
  rules: {
    hoverTransform: 'translateY(-2px)',
    pressTransform: 'scale(0.98)',
    cardTransition: 'opacity 250ms cubic-bezier(0.4, 0, 0.2, 1), transform 250ms cubic-bezier(0.4, 0, 0.2, 1)',
    pageTransition: 'opacity 400ms cubic-bezier(0.4, 0, 0.2, 1), transform 400ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
} as const;

export type AnimationToken = typeof animation;
