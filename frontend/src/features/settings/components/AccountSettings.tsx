'use client';

import React from 'react';
import { useAuth } from '@/providers/AuthProvider';
import { LogOut } from 'lucide-react';

export function AccountSettings() {
  const { logout, user } = useAuth();

  return (
    <div style={{
      width: '100%',
      padding: '32px',
      borderRadius: '20px',
      border: '1px solid rgba(75, 85, 99, 0.4)',
      backgroundColor: 'rgba(17, 24, 39, 0.5)',
      boxSizing: 'border-box'
    }}>
      <h2 style={{
        fontFamily: 'Playfair Display, serif',
        fontSize: '24px',
        fontWeight: 600,
        margin: 0,
        color: '#ffffff'
      }}>Account Settings</h2>

      <div style={{ marginTop: '24px' }}>
        <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Signed In As</div>
        <div style={{ fontSize: '14px', color: '#9ca3af', marginTop: '6px' }}>{user?.email || 'Loading...'}</div>
      </div>

      <hr style={{
        border: 'none',
        borderTop: '1px solid rgba(75, 85, 99, 0.4)',
        marginTop: '24px',
        marginBottom: '24px'
      }} />

      <div>
        <div style={{ fontSize: '15px', fontWeight: 500, color: '#ffffff' }}>Account & Security</div>
        <div style={{ fontSize: '13px', color: '#9ca3af', marginTop: '6px' }}>Manage your current authentication session.</div>

        <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={logout}
            style={{
              height: '40px',
              paddingLeft: '18px',
              paddingRight: '18px',
              borderRadius: '10px',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: '#ef4444',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.2)')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)')}
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
