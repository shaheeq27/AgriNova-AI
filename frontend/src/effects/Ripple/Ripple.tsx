'use client';

import React, { useState, type MouseEvent } from 'react';
import styles from './Ripple.module.css';

interface RipplePoint {
  x: number;
  y: number;
  id: number;
}

export function useRipple(): {
  onMouseDown: (e: MouseEvent<HTMLElement>) => void;
  ripples: React.ReactNode;
} {
  const [ripplesList, setRipplesList] = useState<RipplePoint[]>([]);

  const onMouseDown = (e: MouseEvent<HTMLElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newRipple = { x, y, id: Date.now() };

    setRipplesList((prev) => [...prev, newRipple]);

    setTimeout(() => {
      setRipplesList((prev) => prev.filter((r) => r.id !== newRipple.id));
    }, 600);
  };

  const ripples = (
    <div className={styles.container}>
      {ripplesList.map((ripple) => (
        <div
          key={ripple.id}
          className={styles.ripple}
          style={{ left: ripple.x - 10, top: ripple.y - 10 }}
        />
      ))}
    </div>
  );

  return { onMouseDown, ripples };
}

export default useRipple;
