"use client";

/**
 * AgriNova AI — Authenticated App Layout
 *
 * Wraps all authenticated routes with sidebar + navbar.
 * Redirects to /login if not authenticated.
 */

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthProvider, useAuth } from "@/lib/auth";
import Sidebar from "@/components/layout/Sidebar";
import Navbar from "@/components/layout/Navbar";

function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [sidebarWidth, setSidebarWidth] = useState("var(--sidebar-width)");

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  // Watch for sidebar width changes
  useEffect(() => {
    const observer = new MutationObserver(() => {
      const sidebar = document.querySelector("aside");
      if (sidebar) {
        setSidebarWidth(sidebar.style.width || "var(--sidebar-width)");
      }
    });

    const sidebar = document.querySelector("aside");
    if (sidebar) {
      observer.observe(sidebar, { attributes: true, attributeFilter: ["style"] });
    }

    return () => observer.disconnect();
  }, [isLoading]);

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "var(--background)",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            className="animate-float"
            style={{ fontSize: "48px", marginBottom: "16px" }}
          >
            🌱
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>Loading AgriNova AI...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <div
        style={{
          flex: 1,
          marginLeft: sidebarWidth,
          transition: "margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
          display: "flex",
          flexDirection: "column",
          minHeight: "100vh",
        }}
      >
        <Navbar />
        <main
          style={{
            flex: 1,
            padding: "32px",
            background: "var(--background)",
          }}
        >
          {children}
        </main>
      </div>
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AuthenticatedLayout>{children}</AuthenticatedLayout>
    </AuthProvider>
  );
}
