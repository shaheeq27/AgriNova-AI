import React, { useState } from 'react';
import { CropRecommendationRequestV6, FormContextData } from '@/lib/api';
import { AutocompleteInput } from './AutocompleteInput';

const SOIL_OPTIONS = [
  { value: 'clay', label: 'Clay Soil' },
  { value: 'sandy', label: 'Sandy Soil' },
  { value: 'loamy', label: 'Loamy Soil' },
  { value: 'silt', label: 'Silty Soil' },
  { value: 'black', label: 'Black Soil' },
  { value: 'red', label: 'Red Soil' },
  { value: 'laterite', label: 'Laterite Soil' },
];

const SEASON_OPTIONS = [
  { value: 'kharif', label: 'Kharif (Monsoon)' },
  { value: 'rabi', label: 'Rabi (Winter)' },
  { value: 'zaid', label: 'Zaid (Summer)' },
  { value: 'annual', label: 'Annual / All Season' },
];

const IRRIGATION_OPTIONS = [
  { value: 'rainfed', label: 'Rainfed (No Irrigation)' },
  { value: 'canal', label: 'Canal Irrigation' },
  { value: 'borewell', label: 'Borewell / Tube Well' },
  { value: 'drip', label: 'Drip Irrigation' },
  { value: 'sprinkler', label: 'Sprinkler System' },
];

interface InputStateProps {
  onSubmit: (data: CropRecommendationRequestV6, context: FormContextData) => void;
  isLoading: boolean;
}

export function InputState({ onSubmit, isLoading }: InputStateProps) {
  const [locationName, setLocationName] = useState('');
  const [selectedFarmId, setSelectedFarmId] = useState('');

  const [soilType, setSoilType] = useState('');
  const [soilText, setSoilText] = useState('');

  const [season, setSeason] = useState('');
  const [seasonText, setSeasonText] = useState('');

  const [waterSource, setWaterSource] = useState('');
  const [waterText, setWaterText] = useState('');

  const [errorMsg, setErrorMsg] = useState('');

  const handleLocationChange = (val: string) => {
    setLocationName(val);
    setSelectedFarmId('');
    setErrorMsg('');
  };

  const handleGenerate = () => {
    if (!locationName.trim()) {
      setErrorMsg('Please enter a Location to generate recommendations.');
      return;
    }
    setErrorMsg('');
    onSubmit({
      location_name: locationName.trim(),
      farm_id: selectedFarmId || undefined,
      soil_type: soilType,
      season: season || undefined,
      water_source: waterSource || undefined,
    }, {
      locationText: locationName || 'Not provided',
      soilText: soilText || soilType || 'Not provided',
      seasonText: seasonText || season || 'Not provided',
      waterText: waterText || waterSource || 'Not provided'
    });
  };

  const isLocationProvided = locationName && locationName.trim() !== '';

  return (
    <div className="flex flex-col w-[calc(100%-32px)] md:w-[calc(100%-48px)] max-w-[1200px] mx-auto items-center" style={{ fontFamily: 'var(--font-sans, system-ui, sans-serif)' }}>
      {/* Page Title / Header */}
      <div className="text-center w-full" style={{ marginTop: '32px', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '40px', fontWeight: 700, color: '#E4E2E0', lineHeight: 1.1, letterSpacing: '-0.02em', marginBottom: '8px' }}>
          Crop Advisor
        </h1>
        <p style={{ fontSize: '16px', color: '#88929E' }}>
          AI-powered crop recommendations tailored to your farm&apos;s unique conditions.
        </p>
      </div>

      <div
        className="grid grid-cols-1 md:grid-cols-2 items-start w-full gap-[20px] md:gap-[24px]"
      >

      {/* ══════════════════════════════════════════════
          LEFT PANEL: FARM DETAILS
          ══════════════════════════════════════════════ */}
      <div
        className="flex flex-col relative overflow-visible transition-all duration-300 group hover:-translate-y-1 h-auto"
        style={{
          backgroundColor: 'rgba(7, 12, 8, 0.95)',
          border: '1px solid #192B1D',
          borderRadius: '20px',
          padding: '32px',
          boxSizing: 'border-box'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-[#4EE86A]/5 to-transparent pointer-events-none group-hover:from-[#4EE86A]/10 transition-colors duration-500" />

        <div className="relative z-10 flex flex-col">
          <h2 style={{ fontSize: '36px', fontWeight: 700, lineHeight: 1.1, color: '#4EE86A', marginBottom: '8px', letterSpacing: '-0.02em' }}>
            Farm Details
          </h2>
          <p style={{ fontSize: '16px', fontWeight: 400, color: '#88929E', marginBottom: '28px' }}>
            Provide your farm information to begin climate-based crop analysis.
          </p>

          <div className="flex flex-col gap-[24px] mb-10">
            <AutocompleteInput
              label="Location"
              icon="📍"
              subtitle="Enter your city or region"
              placeholder="e.g. Hyderabad"
              value={locationName}
              onChange={handleLocationChange}
              options={[]}
              allowFreeText={true}
            />

            <AutocompleteInput
              label="Soil Type"
              icon="🌱"
              subtitle="Select the dominant soil type"
              placeholder="Select Soil Type"
              value={soilType}
              onChange={(val) => { setSoilType(val); setSoilText(val); }}
              options={SOIL_OPTIONS}
              onSelectOption={(opt) => setSoilText(opt.label)}
            />

            <AutocompleteInput
              label="Growing Season"
              icon="🌤️"
              subtitle="Select the intended cultivation season"
              placeholder="Select Season"
              value={season}
              onChange={(val) => { setSeason(val); setSeasonText(val); }}
              options={SEASON_OPTIONS}
              onSelectOption={(opt) => setSeasonText(opt.label)}
            />

            <AutocompleteInput
              label="Irrigation"
              icon="💧"
              subtitle="Select water source availability"
              placeholder="Select Water Source"
              value={waterSource}
              onChange={(val) => { setWaterSource(val); setWaterText(val); }}
              options={IRRIGATION_OPTIONS}
              onSelectOption={(opt) => setWaterText(opt.label)}
            />
          </div>

          <div className="mt-2">
            {errorMsg && (
              <div className="mb-6 border p-5 rounded-[12px] text-[16px] font-medium" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.2)', color: '#ef4444' }}>
                {errorMsg}
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="w-full transition-all flex items-center justify-center gap-3 border shadow-lg"
            style={{
              height: '64px',
              borderRadius: '16px',
              fontSize: '18px',
              fontWeight: 700,
              backgroundColor: isLoading ? '#1E3A24' : '#4EE86A',
              color: isLoading ? '#9CA3AF' : '#050A05',
              borderColor: isLoading ? '#2A422F' : '#4EE86A'
            }}
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Generating recommendations...
              </>
            ) : (
              'Generate Recommendations'
            )}
          </button>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════
          RIGHT PANEL: CROP INTELLIGENCE
          Matches the reference screenshot exactly:
          - "Climate Intelligence" heading
          - Vertically stacked dark-green info cards
          - Each card: emoji + bold green label + muted value
          ══════════════════════════════════════════════ */}
      <div
        className="flex flex-col relative overflow-visible transition-all duration-300 group hover:-translate-y-1 h-auto"
        style={{
          backgroundColor: 'rgba(7, 12, 8, 0.95)',
          border: '1px solid #192B1D',
          borderRadius: '20px',
          padding: '32px',
          boxSizing: 'border-box',
          fontFamily: 'var(--font-sans, system-ui, sans-serif)'
        }}
      >
        <div className="absolute inset-0 bg-gradient-to-bl from-[#4EE86A]/5 to-transparent pointer-events-none group-hover:from-[#4EE86A]/10 transition-colors duration-500" />

        <div className="relative z-10 flex flex-col">
        {/* HEADING */}
        <h2 style={{
          fontSize: '36px',
          fontWeight: 700,
          fontStyle: 'italic',
          lineHeight: 1.1,
          color: '#4EE86A',
          marginBottom: '24px',
          letterSpacing: '-0.01em'
        }}>
          Climate Intelligence
        </h2>

        {/* STACKED INFO CARDS */}
        <div className="flex flex-col gap-[16px]">

          {/* LOCATION */}
          <InfoCard
            icon="📍"
            label="Location"
            value={isLocationProvided ? locationName : 'Not provided'}
            muted={!isLocationProvided}
          />

          {/* SOIL TYPE */}
          <InfoCard
            icon="🌱"
            label="Soil Type"
            value={soilText || soilType || 'Not provided'}
            muted={!soilText && !soilType}
          />

          {/* GROWING SEASON */}
          <InfoCard
            icon="🌤️"
            label="Growing Season"
            value={seasonText || season || 'Not provided'}
            muted={!seasonText && !season}
          />

          {/* HISTORICAL CLIMATE */}
          <InfoCard
            icon="🌡️"
            label="Historical Climate"
            value={isLocationProvided ? 'Will be analysed automatically' : 'Waiting for location...'}
            muted={!isLocationProvided}
          />

          {/* RECOMMENDATION ENGINE */}
          <InfoCard
            icon="⚡"
            label="Recommendation Engine"
            value={isLoading ? 'Generating recommendations...' : 'Ready'}
            muted={false}
            highlight={isLoading}
          />

          {/* ESTIMATED TIME */}
          <InfoCard
            icon="⏱️"
            label="Estimated Time"
            value="< 5 seconds"
            muted={false}
          />

        </div>
        </div>
      </div>

    </div>
    </div>
  );
}


/* ─────────────────────────────────────────────────
   InfoCard — matches the reference screenshot:
   dark-green translucent rounded rectangle
   with emoji + bold green label + muted value
   ───────────────────────────────────────────────── */
function InfoCard({
  icon,
  label,
  value,
  muted = false,
  highlight = false
}: {
  icon: string;
  label: string;
  value: string;
  muted?: boolean;
  highlight?: boolean;
}) {
  return (
    <div
      className="transition-all duration-200 hover:border-[#2A4530] flex flex-col justify-center"
      style={{
        backgroundColor: 'rgba(12, 22, 14, 0.85)',
        border: '1px solid #1A2E1E',
        borderRadius: '16px',
        padding: '16px 24px',
        minHeight: '90px'
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span style={{ fontSize: '18px' }}>{icon}</span>
        <span style={{
          fontSize: '18px',
          fontWeight: 700,
          color: '#4EE86A',
        }}>
          {label}
        </span>
      </div>
      <div style={{
        fontSize: '20px',
        fontWeight: 400,
        color: highlight ? '#4EE86A' : (muted ? '#6B7280' : '#D1D5DB'),
        marginLeft: '2px'
      }}>
        {value}
      </div>
    </div>
  );
}
