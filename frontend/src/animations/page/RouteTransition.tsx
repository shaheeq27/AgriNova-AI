'use client';
import React from 'react';
import { usePathname } from 'next/navigation';
import PageTransition from './PageTransition';

export default function RouteTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  return (
    <div key={pathname}>
      <PageTransition>{children}</PageTransition>
    </div>
  );
}
