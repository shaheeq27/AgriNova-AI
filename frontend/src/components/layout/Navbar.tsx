'use client';

/**
 * AgriNova AI — Top Navbar
 */

import React from 'react';
import { useAuth } from '@/lib/auth';
import { PanelLeft } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();

  const handleToggleSidebar = () => {
    window.dispatchEvent(new CustomEvent('toggle-sidebar'));
  };

  return (
    <header
      style={{
        height: 'var(--navbar-height)',
        background: '#131412',
        borderBottom: '1px solid rgba(173,255,0,0.12)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        position: 'sticky',
        top: 0,
        zIndex: 30,
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Left: Sidebar toggle button + Breadcrumb area */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={handleToggleSidebar}
          title="Toggle Sidebar"
          style={{
            background: 'none',
            border: '1px solid rgba(173,255,0,0.15)',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '6px 8px',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#ADFF00';
            e.currentTarget.style.borderColor = 'rgba(173,255,0,0.4)';
            e.currentTarget.style.background = 'rgba(173,255,0,0.08)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-muted)';
            e.currentTarget.style.borderColor = 'rgba(173,255,0,0.15)';
            e.currentTarget.style.background = 'none';
          }}
        >
          <PanelLeft size={18} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '14px', color: 'rgba(242,240,232,0.4)' }}>
            AgriNova AI
          </span>
          <span style={{ color: 'rgba(242,240,232,0.5)', fontSize: '12px' }}>
            /
          </span>
          <span
            style={{ fontSize: '14px', color: '#F2F0E8', fontWeight: 500 }}
          >
            Dashboard
          </span>
        </div>
      </div>

      {/* Right: User section */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Notification bell */}
        <button
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '8px',
            borderRadius: 'var(--radius-md)',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = 'var(--text-primary)';
            e.currentTarget.style.background = 'var(--surface-hover)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-muted)';
            e.currentTarget.style.background = 'none';
          }}
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 01-3.46 0" />
          </svg>
        </button>

        {/* User avatar & name */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: 'var(--radius-full)',
              background: 'linear-gradient(135deg, #ADFF00, #7AB800)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '13px',
              fontWeight: 700,
              color: '#0E0E0D',
            }}
          >
            {user?.full_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <p style={{ fontSize: '13px', fontWeight: 500, lineHeight: 1.2 }}>
              {user?.full_name || 'User'}
            </p>
            <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Farmer
            </p>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={logout}
          style={{
            background: 'none',
            border: '1px solid var(--border)',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '6px 12px',
            borderRadius: 'var(--radius-md)',
            fontSize: '12px',
            fontWeight: 500,
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--error)';
            e.currentTarget.style.color = 'var(--error)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.color = 'var(--text-muted)';
          }}
        >
          Logout
        </button>
      </div>
    </header>
  );
}
