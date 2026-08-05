/**
 * AgriNova AI — Animation Tokens
 */

export const animation = {
  duration: {
    instant: '100ms',
    fast: '200ms',
    normal: '300ms',
    slow: '400ms',
    max: '500ms',
    organic: '4s',
    bg: '20s',
  },
  easing: {
    out: 'cubic-bezier(0.4, 0, 0.2, 1)',
    spring: 'cubic-bezier(0.16, 1, 0.3, 1)',
    bounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    smooth: 'cubic-bezier(0.4, 0, 0, 1)',
  },
} as const;
