"use client";

/**
 * AgriNova AI — Sidebar Navigation
 */

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    label: "My Farms",
    href: "/farms",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
        <polyline points="9,22 9,12 15,12 15,22" />
      </svg>
    ),
  },
  {
    label: "Crops",
    href: "/crops",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 20h10" />
        <path d="M10 20c5.5-2.5.8-6.4 3-10" />
        <path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z" />
        <path d="M14.1 6a7 7 0 00-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z" />
      </svg>
    ),
  },
  {
    label: "Weather",
    href: "/weather",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17.5 19H9a7 7 0 110-14h.5" />
        <path d="M17 7a5 5 0 110 10h-1.5" />
      </svg>
    ),
  },
  {
    label: "Knowledge Base",
    href: "/knowledge",
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
      </svg>
    ),
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      style={{
        width: collapsed ? "var(--sidebar-collapsed)" : "var(--sidebar-width)",
        minHeight: "100vh",
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        position: "fixed",
        left: 0,
        top: 0,
        zIndex: 40,
        overflow: "hidden",
      }}
    >
      {/* Logo */}
      <div
        style={{
          padding: collapsed ? "20px 16px" : "20px 24px",
          borderBottom: "1px solid var(--border)",
          display: "flex",
          alignItems: "center",
          gap: "12px",
          minHeight: "var(--navbar-height)",
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: "var(--radius-md)",
            background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "18px",
            flexShrink: 0,
          }}
        >
          🌱
        </div>
        {!collapsed && (
          <div style={{ overflow: "hidden", whiteSpace: "nowrap" }}>
            <h1 style={{ fontSize: "18px", fontWeight: 700, lineHeight: 1.2 }}>
              <span className="gradient-text">AgriNova</span>
            </h1>
            <p style={{ fontSize: "11px", color: "var(--text-muted)", letterSpacing: "0.05em" }}>
              AI Agriculture
            </p>
          </div>
        )}
      </div>

      {/* Nav Items */}
      <nav style={{ padding: "16px 12px", flex: 1 }}>
        <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "4px" }}>
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    padding: collapsed ? "10px 14px" : "10px 16px",
                    borderRadius: "var(--radius-md)",
                    color: isActive ? "var(--accent-primary)" : "var(--text-secondary)",
                    background: isActive ? "var(--accent-glow)" : "transparent",
                    textDecoration: "none",
                    fontSize: "14px",
                    fontWeight: isActive ? 600 : 400,
                    transition: "all 0.2s ease",
                    whiteSpace: "nowrap",
                    justifyContent: collapsed ? "center" : "flex-start",
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = "var(--surface-hover)";
                      e.currentTarget.style.color = "var(--text-primary)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = "transparent";
                      e.currentTarget.style.color = "var(--text-secondary)";
                    }
                  }}
                >
                  <span style={{ flexShrink: 0 }}>{item.icon}</span>
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Collapse Toggle */}
      <div style={{ padding: "16px 12px", borderTop: "1px solid var(--border)" }}>
        <button
          onClick={() => setCollapsed(!collapsed)}
          style={{
            width: "100%",
            padding: "8px",
            background: "none",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-md)",
            color: "var(--text-muted)",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--border-hover)";
            e.currentTarget.style.color = "var(--text-primary)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border)";
            e.currentTarget.style.color = "var(--text-muted)";
          }}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              transform: collapsed ? "rotate(180deg)" : "none",
              transition: "transform 0.3s ease",
            }}
          >
            <polyline points="15,18 9,12 15,6" />
          </svg>
        </button>
      </div>
    </aside>
  );
}
