'use client';
import React, { useEffect, useState } from 'react';
import Label from '../typography/Label';

export interface SyncStatusProps {
  isSyncing?: boolean;
  lastSynced?: string;
  className?: string;
  style?: React.CSSProperties;
}

const SyncStatus: React.FC<SyncStatusProps> = ({
  isSyncing = false,
  lastSynced,
  className = '',
  style,
}) => {
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    ...style,
  };

  const iconStyle: React.CSSProperties = {
    color: isSyncing ? 'var(--accent-primary)' : 'var(--text-muted)',
    animation: isSyncing ? 'spin 2s linear infinite' : 'none',
    display: 'flex',
    alignItems: 'center',
  };

  return (
    <div style={containerStyle} className={className}>
      <div style={iconStyle}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="23 4 23 10 17 10"></polyline>
          <polyline points="1 20 1 14 7 14"></polyline>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
      </div>
      <Label style={{ color: isSyncing ? 'var(--accent-primary)' : 'var(--text-muted)' }}>
        {isSyncing ? 'SYNCING...' : (lastSynced ? `SYNCED ${lastSynced}` : 'AUTO-SYNC')}
      </Label>
    </div>
  );
};

export default SyncStatus;
