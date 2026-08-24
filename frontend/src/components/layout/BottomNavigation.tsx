'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutGrid, Calendar, Scan, Brain, Bot } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Dashboard', href: '/dashboard', Icon: LayoutGrid },
  { label: 'Timeline', href: '/timeline', Icon: Calendar },
  { label: 'Detect', href: '/detect', Icon: Scan },
  { label: 'Advisor', href: '/advisor', Icon: Brain },
  { label: 'Aira', href: '/aira', Icon: Bot },
];

export default function BottomNavigation() {
  const pathname = usePathname();

  return (
    <footer
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: '72px',
        background: 'rgba(19,20,18,0.92)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        borderTop: '1px solid rgba(173,255,0,0.1)',
        display: 'flex',
        justifyContent: 'space-around',
        alignItems: 'center',
        zIndex: 50,
        padding: '0 16px',
      }}
    >
      {NAV_ITEMS.map((item) => {
        const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
        return (
          <Link
            key={item.href}
            href={item.href}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              color: isActive ? '#ADFF00' : 'rgba(242,240,232,0.4)',
              textDecoration: 'none',
              padding: '8px 16px',
              borderRadius: '12px',
              background: isActive ? 'rgba(173,255,0,0.08)' : 'transparent',
              transition: 'all 0.2s ease',
            }}
          >
            <item.Icon size={20} strokeWidth={1.75} />
            <span style={{ fontSize: '10px', fontFamily: 'Hanken Grotesk, sans-serif', letterSpacing: '0.08em', textTransform: 'uppercase' as const }}>
              {item.label}
            </span>
          </Link>
        );
      })}
    </footer>
  );
}