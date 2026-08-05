'use client';
import { useState, useEffect, useRef } from 'react';

interface UseCounterOptions {
  from?: number;
  to: number;
  duration?: number;
  delay?: number;
  decimals?: number;
  suffix?: string;
  enabled?: boolean;
}

export function useCounter({
  from = 0,
  to,
  duration = 1000,
  delay = 0,
  decimals = 0,
  suffix = '',
  enabled = true,
}: UseCounterOptions) {
  const [value, setValue] = useState<string>(from.toFixed(decimals) + suffix);
  const [rawValue, setRawValue] = useState<number>(from);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);
  
  const startTimeRef = useRef<number | null>(null);
  const rafRef = useRef<number | null>(null);
  const delayTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

  useEffect(() => {
    if (!enabled) return;

    const startAnimation = () => {
      setIsAnimating(true);
      startTimeRef.current = performance.now();

      const animate = (time: number) => {
        if (!startTimeRef.current) startTimeRef.current = time;
        const elapsed = time - startTimeRef.current;
        const progress = Math.min(elapsed / duration, 1);
        
        const easedProgress = easeOutCubic(progress);
        const currentRaw = from + (to - from) * easedProgress;
        
        setRawValue(currentRaw);
        setValue(currentRaw.toFixed(decimals) + suffix);

        if (progress < 1) {
          rafRef.current = requestAnimationFrame(animate);
        } else {
          setIsAnimating(false);
        }
      };

      rafRef.current = requestAnimationFrame(animate);
    };

    if (delay > 0) {
      delayTimeoutRef.current = setTimeout(startAnimation, delay);
    } else {
      startAnimation();
    }

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (delayTimeoutRef.current) clearTimeout(delayTimeoutRef.current);
    };
  }, [from, to, duration, delay, decimals, suffix, enabled]);

  return { value, rawValue, isAnimating };
}
