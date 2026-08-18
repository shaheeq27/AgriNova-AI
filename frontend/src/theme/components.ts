/**
 * AgriNova AI — Primitive Component Variant Specifications
 * Extracted from Stitch Design System
 */

export const componentVariants = {
  button: {
    primary: {
      bg: '#ADFF00',
      color: '#0E0E0D',
      fontFamily: "'Hanken Grotesk', sans-serif",
      fontWeight: 600,
      radius: '8px',
      hoverTransform: 'translateY(-2px)',
      pressTransform: 'scale(0.98)',
      hoverGlow: '0 0 16px rgba(173, 255, 0, 0.25)',
    },
    secondary: {
      bg: 'rgba(31, 32, 31, 0.60)',
      border: '1px solid rgba(141, 146, 140, 0.15)',
      color: '#E4E2E0',
      backdropFilter: 'blur(12px)',
      radius: '8px',
    },
    ghost: {
      bg: 'transparent',
      color: '#C4C8C1',
      border: '1px solid transparent',
      hoverBg: '#2A2A29',
    },
    danger: {
      bg: '#93000A',
      color: '#FFB4AB',
      border: '1px solid rgba(255, 180, 171, 0.20)',
    },
    telemetry: {
      bg: '#2A2A29',
      border: '1px solid rgba(173, 255, 0, 0.20)',
      color: '#ADFF00',
      fontFamily: "'JetBrains Mono', monospace",
      letterSpacing: '0.10em',
      textTransform: 'uppercase' as const,
      radius: '8px',
    },
  },

  card: {
    glass: {
      bg: 'rgba(19, 20, 18, 0.75)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(141, 146, 140, 0.15)',
      radius: '12px',
    },
    soil: {
      bg: '#1A1412',
      border: '1px solid rgba(251, 220, 206, 0.08)',
      radius: '12px',
    },
    command: {
      bg: '#1F201F',
      border: '1px solid rgba(173, 255, 0, 0.20)',
      radius: '24px',
      boxShadow: '0 0 16px rgba(173, 255, 0, 0.10)',
    },
    telemetry: {
      bg: '#0E0E0D',
      border: '1px solid rgba(141, 146, 140, 0.08)',
      radius: '8px',
      fontFamily: "'JetBrains Mono', monospace",
    },
  },

  input: {
    default: {
      bg: '#1B1C1B',
      border: '1px solid rgba(141, 146, 140, 0.25)',
      radius: '8px',
      focusBorder: '#ADFF00',
      focusRing: '0 0 0 2px rgba(173, 255, 0, 0.40)',
    },
    soil: {
      bg: 'transparent',
      borderBottom: '1px solid rgba(141, 146, 140, 0.15)',
      focusBorderBottom: '#ADFF00',
    },
  },

  badge: {
    success: { bg: 'rgba(173, 255, 0, 0.12)', color: '#ADFF00' },
    warning: { bg: 'rgba(222, 193, 178, 0.12)', color: '#DEC1B2' },
    error: { bg: 'rgba(255, 180, 171, 0.12)', color: '#FFB4AB' },
    ai: { bg: 'rgba(173, 255, 0, 0.15)', color: '#ADFF00', glow: '0 0 4px rgba(173, 255, 0, 0.10)' },
    offline: { bg: 'rgba(141, 146, 140, 0.15)', color: '#8D928C' },
  },

  navigation: {
    commandRail: {
      bg: 'rgba(19, 20, 18, 0.85)',
      backdropFilter: 'blur(20px)',
      borderRight: '1px solid rgba(141, 146, 140, 0.15)',
      width: '280px',
      activeItemBg: '#343533',
      activeItemColor: '#ADFF00',
    },
    mobileBar: {
      bg: 'rgba(19, 20, 18, 0.90)',
      backdropFilter: 'blur(20px)',
      borderTop: '1px solid rgba(141, 146, 140, 0.15)',
      height: '64px',
    },
  },
} as const;

export type ComponentVariantsToken = typeof componentVariants;
