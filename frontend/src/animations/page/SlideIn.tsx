'use client';
import React from 'react';
import { useAnimation } from '../../hooks/useAnimation';

interface SlideInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  className?: string;
}

export default function SlideIn({ children, delay = 0, duration = 350, direction = 'left', className = '' }: SlideInProps) {
  const { ref, isVisible } = useAnimation();

  let transform = 'translateX(-100%)';
  if (direction === 'right') transform = 'translateX(100%)';
  if (direction === 'up') transform = 'translateY(100%)';
  if (direction === 'down') transform = 'translateY(-100%)';

  return (
    <div
      ref={ref}
      className={className}
      style={{
        transform: isVisible ? 'translate(0)' : transform,
        transition: `transform ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) ${delay}ms`,
        overflow: 'hidden'
      }}
    >
      {children}
    </div>
  );
}
