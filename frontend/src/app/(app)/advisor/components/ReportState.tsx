import React, { useState, useEffect } from 'react';
import { farmAPI, cropsAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { CropRecommendationResponseV6, FormContextData } from '@/lib/api';

interface ReportStateProps {
  data: CropRecommendationResponseV6;
  formContext: FormContextData | null;
  onReset: () => void;
}

export function ReportState({ data, formContext, onReset }: ReportStateProps) {
  const recommendations = data.recommendations || [];
  const bestCrop = recommendations[0];
  const alternatives = recommendations.slice(1);
  const isEmpty = recommendations.length === 0;

    const [isPlanting, setIsPlanting] = useState(false);
  const [farms, setFarms] = useState<any[]>([]);
  const [selectedFarm, setSelectedFarm] = useState<string>('');
  const [showFarmSelect, setShowFarmSelect] = useState<string | null>(null); // crop name
  const router = useRouter();

  useEffect(() => {
    farmAPI.list().then(res => {
      if (res && res.farms) {
        setFarms(res.farms);
        if (res.farms.length > 0) setSelectedFarm(res.farms[0].id);
      }
    });
  }, []);

  const handlePlant = async (cropName: string) => {
    if (!selectedFarm) return;
    setIsPlanting(true);
    try {
      await cropsAPI.plant({
        farm_id: selectedFarm,
        crop_name: cropName,
        season: data.input_conditions_used?.season || formContext?.seasonText || "Kharif",
        area_acres: 1.0, // Default minimal area
        planting_date: new Date().toISOString().split('T')[0]
      });
      router.push('/timeline');
    } catch (e) {
      console.error(e);
      setIsPlanting(false);
    }
  };

  const formatScore = (score: number) => (score * 100).toFixed(2);

  const contextData = {
    location: formContext?.locationText || 'Not provided',
    soil: data.input_conditions_used?.soil_type || formContext?.soilText || 'Not provided',
    season: data.input_conditions_used?.season || formContext?.seasonText || 'Not provided',
    temp: data.input_conditions_used?.temperature,
    rainfall: data.input_conditions_used?.rainfall,
    humidity: data.input_conditions_used?.humidity,
  };

  return (
    <div
      style={{
        width: '100%',
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '2rem 1.5rem',
        fontFamily: 'var(--font-sans, system-ui, sans-serif)',
        display: 'flex',
        flexDirection: 'column',
        gap: '3rem'
      }}
    >
      {/* ─── PAGE TITLE ─── */}
      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <h1
          style={{
            fontSize: 'clamp(2.5rem, 5vw, 3.5rem)',
            fontWeight: 'bold',
            letterSpacing: '-0.02em',
            color: '#F3F4F6',
            margin: 0
          }}
        >
          Analysis Report
        </h1>
      </div>

      {isEmpty ? (
        /* ─── EMPTY STATE ─── */
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem' }}>
          <div
            style={{
              width: '100%',
              borderRadius: '24px',
              padding: '4rem 2rem',
              textAlign: 'center',
              backgroundColor: '#070C08',
              border: '1px solid #FBBF24',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
            }}
          >
            <span style={{ fontSize: '3rem', display: 'block', marginBottom: '1.5rem' }}>⚠️</span>
            <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', marginBottom: '1rem', color: '#FFFFFF' }}>
              No Suitable Crops Found
            </h2>
            <p style={{ fontSize: '1.125rem', color: '#9CA3AF', maxWidth: '32rem', margin: '0 auto' }}>
              No suitable crops were identified from the available conditions.
              Please adjust your farm details or season and try again.
            </p>
          </div>
          <button
            onClick={onReset}
            className="transition-transform hover:-translate-y-1"
            style={{
              backgroundColor: '#4EE86A',
              color: '#000000',
              padding: '1rem 2rem',
              borderRadius: '12px',
              fontWeight: 'bold',
              fontSize: '1rem',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            ← Start New Analysis
          </button>
        </div>
      ) : (
        <>
          {/* ════════════════════════════════════════════
              CLIMATE SUMMARY CARD
              ════════════════════════════════════════════ */}
          <div
            style={{
              width: '100%',
              borderRadius: '24px',
              padding: '2.5rem',
              backgroundColor: '#070B08',
              border: '1px solid #142417',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              display: 'flex',
              flexDirection: 'column',
              gap: '2.5rem'
            }}
          >
            {/* Header Area */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', alignItems: 'flex-start' }}>
              {/* Badge */}
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.625rem 1.25rem',
                  borderRadius: '9999px',
                  backgroundColor: 'rgba(78, 232, 106, 0.1)',
                  border: '1px solid rgba(78, 232, 106, 0.3)',
                  color: '#4EE86A'
                }}
              >
                <span style={{ fontSize: '14px' }}>✅</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', letterSpacing: '0.025em' }}>
                  Analysis Completed
                </span>
              </div>

              {/* Climate Summary Title & Description */}
              <div>
                <h3
                  style={{
                    fontSize: '1.5rem',
                    fontWeight: 'bold',
                    color: '#4EE86A',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    margin: '0 0 0.5rem 0'
                  }}
                >
                  <span>🌤️</span> Climate Summary
                </h3>
                <p style={{ fontSize: '0.9375rem', color: '#9CA3AF', margin: 0, lineHeight: 1.6 }}>
                  Historical weather conditions used by AgriNova to generate intelligent crop recommendations.
                </p>
              </div>
            </div>

            {/* Metrics Grid */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '1.5rem'
              }}
            >
              <MetricCard
                icon="📍"
                label="CITY"
                value={String(contextData.location)}
              />
              <MetricCard
                icon="🌡️"
                label="AVERAGE TEMPERATURE"
                value={
                  contextData.temp !== undefined && contextData.temp !== null
                    ? `${contextData.temp}°C`
                    : 'Unavailable'
                }
              />
              <MetricCard
                icon="🌧️"
                label="AVERAGE RAINFALL"
                value={
                  contextData.rainfall !== undefined &&
                  contextData.rainfall !== null
                    ? `${contextData.rainfall} mm`
                    : 'Unavailable'
                }
              />
              <MetricCard
                icon="💧"
                label="AVERAGE HUMIDITY"
                value={
                  contextData.humidity !== undefined &&
                  contextData.humidity !== null
                    ? `${contextData.humidity}%`
                    : 'Unavailable'
                }
              />
            </div>
          </div>

          {/* ════════════════════════════════════════════
              BEST RECOMMENDATION CARD
              ════════════════════════════════════════════ */}
          {bestCrop && (
            <div
              style={{
                width: '100%',
                borderRadius: '24px',
                padding: '4rem 2rem',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                background: 'linear-gradient(180deg, #1A4726 0%, #102E19 100%)',
                border: '1px solid #266336',
                boxShadow: '0 10px 40px rgba(78,232,106,0.1)',
                gap: '1.5rem'
              }}
            >
              <div
                style={{
                  fontSize: '0.8125rem',
                  fontWeight: 'bold',
                  textTransform: 'uppercase',
                  letterSpacing: '0.25em',
                  color: '#A7F3D0',
                  margin: 0
                }}
              >
                BEST RECOMMENDATION
              </div>

              <h2
                style={{
                  fontSize: 'clamp(2.5rem, 5vw, 3.25rem)',
                  fontWeight: 'bold',
                  color: '#FFFFFF',
                  margin: 0,
                  letterSpacing: '-0.02em',
                  lineHeight: 1.1
                }}
              >
                {bestCrop.crop_name}
              </h2>

              <div
                style={{
                  fontSize: '1.125rem',
                  fontWeight: 'bold',
                  color: '#6EE7B7',
                  margin: 0
                }}
              >
                Suitability Score: {formatScore(bestCrop.final_score)}%
              </div>

              <p
                style={{
                  fontSize: '1rem',
                  color: '#D1FAE5',
                  maxWidth: '42rem',
                  lineHeight: 1.6,
                  margin: 0
                }}
              >
                {bestCrop.explanation?.base_explanation ||
                  'The highest-ranked crop based on historical climate, soil type and season.'}
              </p>

              {showFarmSelect === bestCrop.crop_name ? (
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '1rem' }}>
                   <select
                     style={{ padding: '8px', borderRadius: '8px', background: '#0B120D', color: '#fff', border: '1px solid #162819' }}
                     value={selectedFarm}
                     onChange={e => setSelectedFarm(e.target.value)}
                   >
                     {farms.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                   </select>
                   <button
                     onClick={() => handlePlant(bestCrop.crop_name)}
                     disabled={isPlanting}
                     style={{ padding: '8px 16px', borderRadius: '8px', background: '#4EE86A', color: '#000', fontWeight: 'bold' }}
                   >
                     {isPlanting ? 'Adding...' : 'Confirm'}
                   </button>
                   <button
                     onClick={() => setShowFarmSelect(null)}
                     style={{ padding: '8px 16px', borderRadius: '8px', background: 'transparent', color: '#fff' }}
                   >
                     Cancel
                   </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowFarmSelect(bestCrop.crop_name)}
                  style={{
                    marginTop: '1rem',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    background: 'rgba(78, 232, 106, 0.1)',
                    border: '1px solid #4EE86A',
                    color: '#4EE86A',
                    fontWeight: 'bold',
                    cursor: 'pointer'
                  }}
                >
                  + Add to Farm
                </button>
              )}

            </div>
          )}

          {/* ════════════════════════════════════════════
              TOP 3 ALTERNATIVES — SIMPLE SCORE BAR CARDS
              ════════════════════════════════════════════ */}
          {alternatives.length > 0 && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '1.5rem'
              }}
            >
              {alternatives.map((crop, idx) => (
                <div
                  key={idx}
                  className="transition-all duration-300 hover:-translate-y-1 hover:border-[#1E3A24]"
                  style={{
                    backgroundColor: '#0B120D',
                    border: '1px solid #162819',
                    borderRadius: '20px',
                    padding: '2rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1.25rem'
                  }}
                >
                  <h4
                    style={{
                      fontSize: '1.25rem',
                      fontWeight: 'bold',
                      color: '#FFFFFF',
                      margin: 0
                    }}
                  >
                    {crop.crop_name}
                  </h4>

                  {/* Progress bar */}
                  <div
                    style={{
                      width: '100%',
                      height: '6px',
                      borderRadius: '3px',
                      backgroundColor: '#1A2E1F',
                      overflow: 'hidden'
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        borderRadius: '3px',
                        backgroundColor: '#4EE86A',
                        width: `${Number(formatScore(crop.final_score))}%`
                      }}
                    />
                  </div>

                  <div
                    style={{
                      fontSize: '0.9375rem',
                      fontWeight: 500,
                      color: '#D1D5DB',
                      margin: 0
                    }}
                  >
                    Suitability: {formatScore(crop.final_score)}%
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* ─── START NEW ANALYSIS BUTTON ─── */}
          <div style={{ display: 'flex', justifyContent: 'center', margin: '2rem 0 4rem 0' }}>
            <button
              onClick={onReset}
              className="transition-transform hover:-translate-y-1 shadow-lg"
              style={{
                backgroundColor: '#4EE86A',
                color: '#000000',
                padding: '1rem 2rem',
                borderRadius: '12px',
                fontWeight: 'bold',
                fontSize: '1rem',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              ← Start New Analysis
            </button>
          </div>
        </>
      )}
    </div>
  );
}

/* ─────────────────────────────────────
   MetricCard — Climate Summary metric
   ───────────────────────────────────── */
function MetricCard({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string;
}) {
  return (
    <div
      style={{
        backgroundColor: '#0A100C',
        border: '1px solid #162819',
        borderRadius: '16px',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        gap: '0.75rem'
      }}
    >
      <div
        style={{
          fontSize: '0.6875rem',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
          color: '#4EE86A',
          display: 'flex',
          alignItems: 'center',
          gap: '0.375rem',
          margin: 0
        }}
      >
        <span>{icon}</span> {label}
      </div>
      <div
        style={{
          fontSize: '1.125rem',
          fontWeight: 'bold',
          color: '#FFFFFF',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          margin: 0
        }}
      >
        {value}
      </div>
    </div>
  );
}
