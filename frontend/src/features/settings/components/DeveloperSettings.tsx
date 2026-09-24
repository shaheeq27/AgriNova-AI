'use client';

import React from 'react';
import { DEVELOPER_CONFIG } from '@/config/developer.config';
import { Mail, Globe } from 'lucide-react';

const GithubIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
  </svg>
);

const LinkedinIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
    <rect x="2" y="9" width="4" height="12"></rect>
    <circle cx="4" cy="4" r="2"></circle>
  </svg>
);

export function DeveloperSettings() {
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
      }}>Developer / About</h2>

      <div className="flex flex-col md:flex-row md:justify-between md:items-start" style={{ marginTop: '24px', gap: '24px' }}>
        {/* Left Side: Developer Info */}
        <div className="flex flex-col gap-2">
          <div style={{ fontSize: '13px', color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            Built and maintained by
          </div>
          <div style={{ fontSize: '18px', fontWeight: 500, color: '#ffffff' }}>
            {DEVELOPER_CONFIG.name}
          </div>
          <div style={{ fontSize: '14px', color: '#9ca3af', marginTop: '4px' }}>
            Computer Science • AI • Full Stack
          </div>
          <div style={{ fontSize: '14px', color: '#d1d5db', marginTop: '16px' }}>
            Building AgriNova — Precision Agriculture Platform
          </div>
        </div>

        {/* Right Side: Links */}
        <div className="flex flex-row md:flex-col flex-wrap gap-4 md:gap-3">
          {DEVELOPER_CONFIG.github && (
            <a href={DEVELOPER_CONFIG.github} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors">
              <GithubIcon size={16} />
              <span>GitHub</span>
            </a>
          )}
          {DEVELOPER_CONFIG.linkedin && (
            <a href={DEVELOPER_CONFIG.linkedin} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors">
              <LinkedinIcon size={16} />
              <span>LinkedIn</span>
            </a>
          )}
          {DEVELOPER_CONFIG.email && (
            <a href={`mailto:${DEVELOPER_CONFIG.email}`}
               className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors">
              <Mail size={16} />
              <span>Email</span>
            </a>
          )}
          {DEVELOPER_CONFIG.portfolio && (
            <a href={DEVELOPER_CONFIG.portfolio} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors">
              <Globe size={16} />
              <span>Portfolio</span>
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
