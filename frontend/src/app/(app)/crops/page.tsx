'use client';

import React, { useState } from 'react';
import { useCropRecommendationV6 } from '@/hooks/useCropRecommendationV6';
import { CropRecommendationRequestV6, FormContextData } from '@/lib/api';
import { InputState } from './components/InputState';
import { ReportState } from './components/ReportState';
import { useParticles } from '@/hooks/useParticles';

export default function CropRecommendationV6Page() {
  const { data, loading, fetchRecommendations, reset } = useCropRecommendationV6();
  const [formContext, setFormContext] = useState<FormContextData | null>(null);
  const particles = useParticles(10);

  const handleSubmit = async (formData: CropRecommendationRequestV6, context: FormContextData) => {
    setFormContext(context);
    try {
      await fetchRecommendations(formData);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReset = () => {
    setFormContext(null);
    reset();
  };

  // If data is not null, the API call completed successfully (even if recommendations array is empty)
  const isReportState = data !== null;

  return (
    <div
      className="relative min-h-[calc(100vh-80px)] w-full flex flex-col"
      style={{
        backgroundColor: '#050A05',
        fontFamily: 'var(--font-sans, system-ui, sans-serif)'
      }}
    >
      {/* PARTICLES BACKGROUND */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        {particles.map((p) => (
          <div
            key={p.id}
            className="absolute rounded-full pointer-events-none"
            style={{
              left: `${p.x}%`,
              top: `${p.y}%`,
              width: `${p.size}px`,
              height: `${p.size}px`,
              backgroundColor: '#4EE86A',
              opacity: 0.15,
              animation: `float-particle ${p.duration}s infinite linear`,
              animationDelay: `${p.delay}s`,
            }}
          />
        ))}
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes float-particle {
          0% { transform: translateY(0) rotate(0deg); opacity: 0; }
          10% { opacity: 0.2; }
          90% { opacity: 0.2; }
          100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
        }
      `}} />

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col justify-center px-6 py-12 relative z-10">
        <div className="w-full flex justify-center">
          {!isReportState ? (
            <InputState onSubmit={handleSubmit} isLoading={loading} />
          ) : (
            <ReportState data={data!} formContext={formContext} onReset={handleReset} />
          )}
        </div>
      </div>

    </div>
  );
}
