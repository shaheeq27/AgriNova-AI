/**
 * AgriNova AI — Icon System Tokens
 * Rules: Lucide React ONLY, Stroke Width 1.75
 */

export const icons = {
  library: 'lucide-react',
  strokeWidth: 1.75,
  sizes: {
    xs: 16,
    sm: 20,
    md: 24,
    lg: 32,
  },
  defaultProps: {
    strokeWidth: 1.75,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  },
} as const;

export type IconSize = keyof typeof icons.sizes;
