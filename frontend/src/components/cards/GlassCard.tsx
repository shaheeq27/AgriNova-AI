'use client';

/**
 * @deprecated Use Card from '@/components/ui/Card'
 */
import { Card, type CardProps, type CardPadding } from '@/components/ui/Card';

export interface GlassCardProps extends Omit<CardProps, 'padding'> {
  padding?: CardPadding | string;
}

const paddingMap: Record<string, CardPadding> = {
  '16px': 'sm',
  '24px': 'md',
  '32px': 'lg',
  '0': 'none',
};

export default function GlassCard({
  padding = 'md',
  hover = true,
  glow = false,
  ...props
}: GlassCardProps) {
  const resolvedPadding =
    typeof padding === 'string' && padding in paddingMap
      ? paddingMap[padding]
      : (padding as CardPadding);

  return <Card padding={resolvedPadding} hover={hover} glow={glow} {...props} />;
}

export { GlassCard };
