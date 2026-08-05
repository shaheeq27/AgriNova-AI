'use client';
import React from 'react';

export default function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <div 
      className="anim-page-enter"
      style={{
        animation: 'page-enter-anim 500ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        opacity: 0,
      }}
    >
      <style>{`
        @keyframes page-enter-anim {
          0% { opacity: 0; transform: translateY(10px); }
          100% { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      {children}
    </div>
  );
}
