'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  Home,
  LayoutGrid,
  MapPin,
  Sprout,
  Cloud,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelLeftOpen,
  Bot,
  TrendingUp,
  Settings
} from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Home', href: '/home', Icon: Home },
  { label: 'Dashboard', href: '/dashboard', Icon: LayoutGrid },
  { label: 'My Farms', href: '/farms', Icon: MapPin },
  { label: 'Crops', href: '/crops', Icon: Sprout },
  { label: 'Weather', href: '/weather', Icon: Cloud },
  { label: 'Market', href: '/market', Icon: TrendingUp },
  { label: 'Aira', href: '/aira', Icon: Bot },
  { label: 'Knowledge Base', href: '/knowledge', Icon: BookOpen },
  { label: 'Settings', href: '/settings', Icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const handleToggle = () => {
      setCollapsed((prev) => !prev);
    };

    window.addEventListener('toggle-sidebar', handleToggle);
    return () => {
      window.removeEventListener('toggle-sidebar', handleToggle);
    };
  }, []);

  return (
    <aside
      className="hidden md:flex"
      style={{
        width: collapsed ? '72px' : '240px',
        minHeight: '100vh',
        background: '#131412',
        borderRight: '1px solid rgba(173,255,0,0.15)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'fixed',
        left: 0,
        top: 0,
        zIndex: 40,
        overflow: 'hidden',
      }}
    >
      {/* Logo Header: Clickable to expand when collapsed */}
      <div
        onClick={() => {
          if (collapsed) setCollapsed(false);
        }}
        title={collapsed ? 'Click to expand sidebar' : undefined}
        style={{
          padding: '16px',
          borderBottom: '1px solid rgba(173,255,0,0.12)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          minHeight: '72px',
          cursor: collapsed ? 'pointer' : 'default',
          transition: 'padding 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
          <div className="relative flex-shrink-0" style={{ width: 36, height: 36 }}>
            <Image
              src="/logo_transparent.png"
              alt="AgriNova AI"
              width={36}
              height={36}
              className="object-contain"
              style={{ filter: 'drop-shadow(0 0 8px rgba(173,255,0,0.5))' }}
              priority
            />
          </div>
          <div
            style={{
              opacity: collapsed ? 0 : 1,
              maxWidth: collapsed ? 0 : '140px',
              visibility: collapsed ? 'hidden' : 'visible',
              transition:
                'opacity 0.2s ease, max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              overflow: 'hidden',
              whiteSpace: 'nowrap',
            }}
          >
            <h1
              style={{
                fontSize: '18px',
                fontWeight: 700,
                lineHeight: 1.2,
                color: '#F2F0E8',
                fontFamily: 'Source Serif 4, serif',
                margin: 0,
              }}
            >
              AgriNova
            </h1>
            <p
              style={{
                fontSize: '10px',
                color: '#ADFF00',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                fontFamily: 'Hanken Grotesk, sans-serif',
                margin: 0,
              }}
            >
              AI Agriculture
            </p>
          </div>
        </div>

        {!collapsed ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setCollapsed(true);
            }}
            title="Collapse Sidebar"
            style={{
              background: 'none',
              border: 'none',
              color: 'rgba(242,240,232,0.6)',
              cursor: 'pointer',
              padding: '6px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = '#ADFF00';
              e.currentTarget.style.background = 'rgba(173,255,0,0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'rgba(242,240,232,0.6)';
              e.currentTarget.style.background = 'none';
            }}
          >
            <PanelLeftClose size={18} strokeWidth={1.75} />
          </button>
        ) : (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setCollapsed(false);
            }}
            title="Expand Sidebar"
            style={{
              display: 'none', // clean header on collapsed, clickable container expands
            }}
          />
        )}
      </div>

      {/* Nav Items */}
      <nav style={{ padding: '16px 12px', flex: 1 }}>
        <ul
          style={{
            listStyle: 'none',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
            margin: 0,
            padding: 0,
          }}
        >
          {NAV_ITEMS.map((item) => {
            const isActive =
              pathname === item.href || pathname?.startsWith(item.href + '/');
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  title={collapsed ? item.label : undefined}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: '12px',
                    color: isActive ? '#ADFF00' : 'rgba(242,240,232,0.5)',
                    background: isActive
                      ? 'rgba(173,255,0,0.08)'
                      : 'transparent',
                    textDecoration: 'none',
                    fontSize: '14px',
                    fontWeight: isActive ? 600 : 400,
                    fontFamily: 'Hanken Grotesk, sans-serif',
                    transition: 'all 0.2s ease',
                    whiteSpace: 'nowrap',
                    borderLeft: isActive
                      ? '2px solid #ADFF00'
                      : '2px solid transparent',
                  }}
                >
                  <item.Icon
                    size={20}
                    strokeWidth={1.75}
                    style={{
                      flexShrink: 0,
                      margin: collapsed ? '0 auto' : '0',
                    }}
                  />
                  <span
                    style={{
                      opacity: collapsed ? 0 : 1,
                      maxWidth: collapsed ? 0 : '140px',
                      visibility: collapsed ? 'hidden' : 'visible',
                      transition:
                        'opacity 0.2s ease, max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                      overflow: 'hidden',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {item.label}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* AI Engine Status Box */}
      <div style={{ padding: '16px 12px' }}>
        <div
          style={{
            padding: collapsed ? '12px 8px' : '12px 16px',
            background: 'rgba(173,255,0,0.04)',
            borderRadius: '12px',
            border: '1px solid rgba(173,255,0,0.1)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: collapsed ? 'center' : 'flex-start',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        >
          {collapsed ? (
            <span
              title="AI Engine: Optimizing Yield"
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: '#ADFF00',
                boxShadow: '0 0 8px #ADFF00',
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
          ) : (
            <>
              <p
                style={{
                  fontSize: '10px',
                  color: 'rgba(173,255,0,0.5)',
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  fontFamily: 'JetBrains Mono, monospace',
                  margin: '0 0 6px 0',
                  whiteSpace: 'nowrap',
                }}
              >
                AI ENGINE STATUS
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span
                  style={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: '#ADFF00',
                    boxShadow: '0 0 8px #ADFF00',
                    animation: 'pulse 2s ease-in-out infinite',
                  }}
                />
                <span
                  style={{
                    fontSize: '11px',
                    color: '#ADFF00',
                    fontFamily: 'JetBrains Mono, monospace',
                    whiteSpace: 'nowrap',
                  }}
                >
                  Optimizing Yield
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Bottom Collapse/Expand Toggle Button */}
      <div
        style={{
          padding: '12px',
          borderTop: '1px solid rgba(173,255,0,0.08)',
        }}
      >
        <button
          onClick={() => setCollapsed(!collapsed)}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          style={{
            width: '100%',
            padding: '8px',
            background: 'none',
            border: '1px solid rgba(173,255,0,0.12)',
            borderRadius: '10px',
            color: 'rgba(242,240,232,0.4)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#ADFF00';
            e.currentTarget.style.borderColor = 'rgba(173,255,0,0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'rgba(242,240,232,0.4)';
            e.currentTarget.style.borderColor = 'rgba(173,255,0,0.12)';
          }}
        >
          {collapsed ? (
            <ChevronRight size={16} strokeWidth={1.75} />
          ) : (
            <ChevronLeft size={16} strokeWidth={1.75} />
          )}
        </button>
      </div>
    </aside>
  );
}
