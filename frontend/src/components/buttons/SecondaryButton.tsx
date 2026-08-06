'use client';

/**
 * @deprecated Use Button with variant="secondary" from '@/components/ui/Button'
 */
import { Button, type ButtonProps } from '@/components/ui/Button';

export type SecondaryButtonProps = Omit<ButtonProps, 'variant'>;

export default function SecondaryButton(props: SecondaryButtonProps) {
  return <Button variant="secondary" {...props} />;
}

export { SecondaryButton };
