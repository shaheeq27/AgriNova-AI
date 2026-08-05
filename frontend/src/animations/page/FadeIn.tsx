'use client';
import React from 'react';
import { useAnimation } from '../../hooks/useAnimation';

interface FadeInProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  direction?: 'up' | 'down' | 'left' | 'right' | 'none';
  className?: string;
}

export default function FadeIn({ children, delay = 0, duration = 500, direction = 'up', className = '' }: FadeInProps) {
  const { ref, isVisible } = useAnimation();

  let transform = 'translateY(20px)';
  if (direction === 'down') transform = 'translateY(-20px)';
  if (direction === 'left') transform = 'translateX(20px)';
  if (direction === 'right') transform = 'translateX(-20px)';
  if (direction === 'none') transform = 'none';

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translate(0)' : transform,
        transition: `opacity ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) ${delay}ms, transform ${duration}ms cubic-bezier(0.4, 0, 0.2, 1) ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}
