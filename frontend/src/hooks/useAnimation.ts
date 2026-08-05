'use client';
import { useRef, useState, useEffect } from 'react';

interface UseAnimationOptions {
  threshold?: number;
  triggerOnce?: boolean;
  rootMargin?: string;
}

export function useAnimation(options?: UseAnimationOptions) {
  const { threshold = 0.1, triggerOnce = true, rootMargin = '0px' } = options || {};
  const ref = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true);
            setHasAnimated(true);
            if (triggerOnce && ref.current) {
              observer.unobserve(ref.current);
            }
          } else if (!triggerOnce) {
            setIsVisible(false);
          }
        });
      },
      { threshold, rootMargin }
    );

    const currentRef = ref.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [threshold, triggerOnce, rootMargin]);

  return { ref, isVisible, hasAnimated };
}
