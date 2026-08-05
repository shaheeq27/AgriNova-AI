'use client';
import { useState, useEffect } from 'react';

export function useScroll() {
  const [scrollState, setScrollState] = useState({ scrollY: 0, scrollX: 0, isScrolled: false });

  useEffect(() => {
    const handleScroll = () => {
      setScrollState({
        scrollY: window.scrollY,
        scrollX: window.scrollX,
        isScrolled: window.scrollY > 10,
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return scrollState;
}
