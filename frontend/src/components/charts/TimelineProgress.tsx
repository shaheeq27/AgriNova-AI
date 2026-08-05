'use client';
import React, { useEffect, useState } from 'react';

interface TimelineProgressProps {
  progress: number; // 0-100
  height?: string; // e.g., '100%', '400px'
}

export default function TimelineProgress({ progress, height = '100%' }: TimelineProgressProps) {
  const [fill, setFill] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setFill(progress);
    }, 100);
    return () => clearTimeout(timer);
  }, [progress]);

  return (
    <div style={{ position: 'relative', width: '2px', height, background: 'var(--surface-hover, #122a1c)', borderRadius: '1px', overflow: 'hidden' }}>
      <div style={{ 
        position: 'absolute', 
        top: 0, left: 0, right: 0, 
        height: `${fill}%`, 
        background: 'var(--accent-primary, #4ee86a)',
        transition: 'height 1.5s cubic-bezier(0.4, 0, 0.2, 1)',
        boxShadow: '0 0 8px rgba(78, 232, 106, 0.5)'
      }} />
      
      {/* Travelling light effect overlay */}
      <div style={{
        position: 'absolute',
        top: 0, left: '-2px', right: '-2px', height: '20px',
        background: 'linear-gradient(to bottom, transparent, rgba(78, 232, 106, 0.8), transparent)',
        animation: 'travel 2s infinite linear'
      }} />

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes travel {
          0% { transform: translateY(-20px); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(100vh); opacity: 0; }
        }
      `}} />
    </div>
  );
}
