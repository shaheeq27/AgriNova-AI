'use client';
import React from 'react';
import { useCounter } from '../../hooks/useCounter';
import { useAnimation } from '../../hooks/useAnimation';

interface CountUpProps {
  value: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  className?: string;
  style?: React.CSSProperties;
}

export default function CountUp({ value, duration = 1000, decimals = 0, suffix = '', prefix = '', className = '', style }: CountUpProps) {
  const { ref, isVisible } = useAnimation();
  const { value: displayValue } = useCounter({
    to: value,
    duration,
    decimals,
    suffix,
    enabled: isVisible,
  });

  return (
    <span ref={ref} className={className} style={style}>
      {prefix}{displayValue}
    </span>
  );
}
