/**
 * @deprecated Use Badge from '@/components/ui/Badge'
 */
import { Badge, type BadgeProps, type BadgeStatus } from '@/components/ui/Badge';

export type StatusBadgeProps = {
  status: BadgeStatus;
  label: string;
  pulse?: boolean;
  size?: 'sm' | 'md';
  className?: string;
  style?: React.CSSProperties;
};

export default function StatusBadge({ status, label, pulse, size, className }: StatusBadgeProps) {
  return <Badge status={status} label={label} pulse={pulse} size={size} className={className} />;
}

export { StatusBadge };
