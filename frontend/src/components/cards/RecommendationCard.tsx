'use client';
import React, { useEffect, useState } from 'react';
import GlassCard from './GlassCard';

interface RecommendationCardProps {
  cropName: string;
  confidence: number;
  explanation: string;
}

export default function RecommendationCard({ cropName, confidence, explanation }: RecommendationCardProps) {
  const [fill, setFill] = useState(0);

  useEffect(() => {
    // Slight delay before animation starts for better visual impact
    const timer = setTimeout(() => {
      setFill(confidence);
    }, 100);
    return () => clearTimeout(timer);
  }, [confidence]);

  return (
    <GlassCard hover glow>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h4 style={{ fontFamily: 'var(--font-serif, "Playfair Display")', color: 'var(--text-primary, #e8f5ec)', margin: 0, fontSize: '1.4rem', fontWeight: 500 }}>
          {cropName}
        </h4>
        <div style={{ fontFamily: 'var(--font-mono, "Space Mono")', color: 'var(--accent-primary, #4ee86a)', fontSize: '1.2rem' }}>
          {confidence}%
        </div>
      </div>
      
      <p style={{ color: 'var(--text-secondary, #8fb89e)', fontSize: '0.85rem', margin: '0 0 20px 0', lineHeight: 1.5 }}>
        {explanation}
      </p>

      <div style={{ position: 'relative', height: '6px', background: 'var(--background-subtle, #081410)', borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{ 
          position: 'absolute',
          top: 0, left: 0, bottom: 0,
          width: `${fill}%`, 
          background: 'linear-gradient(90deg, var(--accent-muted, #1a5a3a) 0%, var(--accent-primary, #4ee86a) 100%)',
          transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 0 8px rgba(78, 232, 106, 0.4)'
        }} />
      </div>
    </GlassCard>
  );
}
