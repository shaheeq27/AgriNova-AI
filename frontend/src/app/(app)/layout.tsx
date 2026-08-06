"use client";

import { AuthProvider } from '@/providers/AuthProvider';
import { DashboardLayout } from '@/layouts/DashboardLayout';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <DashboardLayout>{children}</DashboardLayout>
    </AuthProvider>
  );
}
