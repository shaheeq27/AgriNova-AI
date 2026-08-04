"use client";

/**
 * AgriNova AI — Top Navbar
 */

import React from "react";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header
      style={{
        height: "var(--navbar-height)",
        background: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 32px",
        position: "sticky",
        top: 0,
        zIndex: 30,
        backdropFilter: "blur(12px)",
      }}
    >
      {/* Left: Breadcrumb area */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{ fontSize: "14px", color: "var(--text-muted)" }}>AgriNova AI</span>
        <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>/</span>
        <span style={{ fontSize: "14px", color: "var(--text-primary)", fontWeight: 500 }}>
          Dashboard
        </span>
      </div>

      {/* Right: User section */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {/* Notification bell */}
        <button
          style={{
            background: "none",
            border: "none",
            color: "var(--text-muted)",
            cursor: "pointer",
            padding: "8px",
            borderRadius: "var(--radius-md)",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = "var(--text-primary)";
            e.currentTarget.style.background = "var(--surface-hover)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = "var(--text-muted)";
            e.currentTarget.style.background = "none";
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 01-3.46 0" />
          </svg>
        </button>

        {/* User avatar & name */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: "var(--radius-full)",
              background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "13px",
              fontWeight: 700,
              color: "var(--text-inverse)",
            }}
          >
            {user?.full_name?.[0]?.toUpperCase() || "U"}
          </div>
          <div>
            <p style={{ fontSize: "13px", fontWeight: 500, lineHeight: 1.2 }}>
              {user?.full_name || "User"}
            </p>
            <p style={{ fontSize: "11px", color: "var(--text-muted)" }}>Farmer</p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={logout}
          style={{
            background: "none",
            border: "1px solid var(--border)",
            color: "var(--text-muted)",
            cursor: "pointer",
            padding: "6px 12px",
            borderRadius: "var(--radius-md)",
            fontSize: "12px",
            fontWeight: 500,
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--error)";
            e.currentTarget.style.color = "var(--error)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--border)";
            e.currentTarget.style.color = "var(--text-muted)";
          }}
        >
          Logout
        </button>
      </div>
    </header>
  );
}
