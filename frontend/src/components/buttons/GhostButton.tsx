'use client';

/**
 * @deprecated Use Button with variant="ghost" from '@/components/ui/Button'
 */
import { Button, type ButtonProps } from '@/components/ui/Button';

export type GhostButtonProps = Omit<ButtonProps, 'variant'>;

export default function GhostButton(props: GhostButtonProps) {
  return <Button variant="ghost" {...props} />;
}

export { GhostButton };
