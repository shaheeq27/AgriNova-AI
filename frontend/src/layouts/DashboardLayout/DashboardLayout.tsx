'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/providers/AuthProvider';
import Sidebar from '@/components/layout/Sidebar';
import Navbar from '@/components/layout/Navbar';
import BottomNavigation from '@/components/layout/BottomNavigation';
import MobileHeader from '@/components/layout/MobileHeader';
import { cn } from '@/utils/cn';
import styles from './DashboardLayout.module.css';

export interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [sidebarWidth, setSidebarWidth] = useState('var(--sidebar-width)');

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      const sidebar = document.querySelector('aside');
      if (sidebar) {
        setSidebarWidth(sidebar.style.width || 'var(--sidebar-width)');
      }
    });

    const sidebar = document.querySelector('aside');
    if (sidebar) {
      observer.observe(sidebar, { attributes: true, attributeFilter: ['style'] });
    }

    return () => observer.disconnect();
  }, [isLoading]);

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingContent}>
          <div className={cn(styles.loadingIcon, 'anim-float')}>🌱</div>
          <p className={styles.loadingText}>Loading AgriNova AI...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className={styles.shell}>
      <Sidebar />
      <div className={styles.content} style={{ marginLeft: sidebarWidth }}>
        <MobileHeader />
        <Navbar />
        <main className={styles.main}>{children}</main>
      </div>
      <BottomNavigation />
    </div>
  );
}

export default DashboardLayout;
