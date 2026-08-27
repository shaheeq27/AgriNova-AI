'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { useCropRecommendation } from '@/hooks/useCropRecommendation';
import { farmAPI, FarmData } from '@/lib/api';
import Image from 'next/image';
import { Card, Badge, Button } from '@/ui';
import {
  Brain,
  Radio,
  ChevronDown,
  Droplets,
  Thermometer,
  TrendingDown,
  Loader2,
} from 'lucide-react';

/* ─────────────────────────────────────────────────────────────
   AgriNova AI — AI Crop Discovery / Diagnostic Consultation
   Stitch Screen: 4a8cd55482fb45b682fe435b51100d5b
   ───────────────────────────────────────────────────────────── */

const SOIL_OPTIONS = ['Silty Clay Loam', 'Sandy Loam', 'Peat / Histosols', 'Calcareous Soil'];
const CLIMATE_OPTIONS = [
  'Humid Subtropical (Cfa)',
  'Semi-Arid Steppe (Bsh)',
  'Marine West Coast (Cfb)',
  'Mediterranean (Csb)',
];
const WATER_OPTIONS = [
  'Automated Drip Irrigation',
  'Groundwater Aquifer',
  'Precision Pivot System',
  'Rain-fed / Natural',
];

export default function AdvisorPage() {
  const [soil, setSoil] = useState(SOIL_OPTIONS[0]);
  const [climate, setClimate] = useState(CLIMATE_OPTIONS[0]);
  const [acreage, setAcreage] = useState('');
  const [water, setWater] = useState(WATER_OPTIONS[0]);

  const [farms, setFarms] = useState<FarmData[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<string>('');

  useEffect(() => {
    farmAPI.list().then(res => setFarms(res.farms)).catch(() => {});
  }, []);

  const { fetchRecommendations, data: apiResult, loading, error } = useCropRecommendation();

  const [result, setResult] = useState<{
    crop: string;
    confidence: number;
    yield: string;
    cost: string;
    insight: string;
    historically_adjusted: boolean;
    rationale: string | null;
  } | null>(null);

  const runAnalysis = useCallback(async () => {
    setResult(null);
    try {
      const res = await fetchRecommendations({
        temperature: 24, // Mock values for UI since they aren't collected
        humidity: 60,
        rainfall: 400,
        soil_type: soil,
        farm_id: selectedFarmId || undefined
      });
      if (res.recommendations.length > 0) {
        const topRec = res.recommendations[0];
        setResult({
          crop: topRec.crop_name,
          confidence: topRec.confidence,
          yield: '184.2', // Mocked yield since API doesn't return it directly
          cost: '-12%', // Mocked cost
          insight: topRec.explanation,
          historically_adjusted: topRec.historically_adjusted,
          rationale: topRec.personalization_rationale
        });
      }
    } catch (e) {
      // Handle error natively in the UI or let the hook expose it
    }
  }, [fetchRecommendations, soil, selectedFarmId]);


  const isResultVisible = loading || result !== null;

  return (
    <div className="min-h-screen bg-surface text-on-surface font-sans relative overflow-x-hidden">
      {/* ── Inline Styles ── */}
      <style jsx>{`
        @keyframes pulseGlow {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
        .animate-pulse-glow {
          animation: pulseGlow 2s infinite;
        }
        .organic-shape {
          clip-path: polygon(2% 0%, 98% 2%, 100% 95%, 2% 100%, 0% 50%);
          border-radius: 40px;
        }
        select {
          -webkit-appearance: none;
          appearance: none;
        }
        input[type=number]::-webkit-inner-spin-button,
        input[type=number]::-webkit-outer-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        input[type=number] {
          -moz-appearance: textfield;
        }
      `}</style>

      {/* ── Main Content ── */}
      <main className="py-8 px-6 max-w-7xl mx-auto min-h-screen">
        <div className="grid lg:grid-cols-12 gap-10">
          {/* ══════════════════════════════════════════════
              LEFT: Consultation Form (Input Stage)
              ══════════════════════════════════════════════ */}
          <div className="lg:col-span-7 flex flex-col gap-8">
            {/* Header */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-4">
                <span className="w-2 h-2 rounded-full bg-neon-mint animate-pulse" />
                <p className="type-label-caps text-neon-mint uppercase">
                  Diagnostic Engine Active
                </p>
              </div>
              <h1 className="type-headline-lg leading-none">
                Environmental{' '}
                <br />
                <span className="text-neon-mint">Synthesis</span>
              </h1>
              <p className="type-body-md text-on-surface-variant max-w-md">
                Calibrating soil-to-satellite telemetry for optimized yield prediction. Input your
                local parameters below.
              </p>
            </div>

            {/* ── Organic Input Container ── */}
            <div
              className="organic-shape relative overflow-hidden group"
              style={{
                background: 'rgba(27,28,27,0.8)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(173,255,0,0.1)',
                padding: 'clamp(32px, 5vw, 56px)',
              }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10 relative z-10">
                {/* Soil Type */}
                <div className="space-y-4">
                  <label className="type-label-caps text-on-surface-variant block">
                    Target Farm (Optional)
                  </label>
                  <div className="relative mb-6">
                    <select
                      value={selectedFarmId}
                      onChange={(e) => setSelectedFarmId(e.target.value)}
                      className="w-full bg-soil-deep border-0 border-b-2 border-[#ADFF00]/20 focus:border-[#ADFF00] focus:ring-0 text-on-surface py-3 px-0 cursor-pointer transition-all font-sans"
                    >
                      <option value="">No Farm (Public Sandbox Mode)</option>
                      {farms.map((f) => (
                        <option key={f.id} value={f.id}>{f.name}</option>
                      ))}
                    </select>
                  </div>

                  <label className="type-label-caps text-on-surface-variant block">
                    Primary Soil Composition
                  </label>
                  <div className="relative">
                    <select
                      value={soil}
                      onChange={(e) => setSoil(e.target.value)}
                      className="w-full bg-soil-deep border-0 border-b-2 border-[#ADFF00]/20 focus:border-[#ADFF00] focus:ring-0 text-on-surface py-3 px-0 cursor-pointer transition-all font-sans"
                    >
                      {SOIL_OPTIONS.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                    <ChevronDown
                      size={18}
                      strokeWidth={1.75}
                      className="absolute right-0 top-3 pointer-events-none text-neon-mint/50"
                    />
                  </div>
                </div>

                {/* Climate Zone */}
                <div className="space-y-4">
                  <label className="type-label-caps text-on-surface-variant block">
                    Micro-Climate Profile
                  </label>
                  <div className="relative">
                    <select
                      value={climate}
                      onChange={(e) => setClimate(e.target.value)}
                      className="w-full bg-soil-deep border-0 border-b-2 border-[#ADFF00]/20 focus:border-[#ADFF00] focus:ring-0 text-on-surface py-3 px-0 cursor-pointer transition-all font-sans"
                    >
                      {CLIMATE_OPTIONS.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                    <Thermometer
                      size={18}
                      strokeWidth={1.75}
                      className="absolute right-0 top-3 pointer-events-none text-neon-mint/50"
                    />
                  </div>
                </div>

                {/* Acreage */}
                <div className="space-y-4">
                  <label className="type-label-caps text-on-surface-variant block">
                    Plot Dimensions (Acres)
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      placeholder="0.00"
                      value={acreage}
                      onChange={(e) => setAcreage(e.target.value)}
                      className="w-full bg-soil-deep border-0 border-b-2 border-[#ADFF00]/20 focus:border-[#ADFF00] focus:ring-0 text-on-surface py-3 px-0 transition-all font-mono"
                    />
                    <span className="absolute right-0 top-3 text-neon-mint/50 type-label-caps text-[10px]">
                      UNIT: AC
                    </span>
                  </div>
                </div>

                {/* Water Source */}
                <div className="space-y-4">
                  <label className="type-label-caps text-on-surface-variant block">
                    Hydration Infrastructure
                  </label>
                  <div className="relative">
                    <select
                      value={water}
                      onChange={(e) => setWater(e.target.value)}
                      className="w-full bg-soil-deep border-0 border-b-2 border-[#ADFF00]/20 focus:border-[#ADFF00] focus:ring-0 text-on-surface py-3 px-0 cursor-pointer transition-all font-sans"
                    >
                      {WATER_OPTIONS.map((w) => (
                        <option key={w} value={w}>
                          {w}
                        </option>
                      ))}
                    </select>
                    <Droplets
                      size={18}
                      strokeWidth={1.75}
                      className="absolute right-0 top-3 pointer-events-none text-neon-mint/50"
                    />
                  </div>
                </div>
              </div>

              {/* Footer: Telemetry + CTA */}
              <div className="mt-16 flex flex-col md:flex-row items-center justify-between gap-6 relative z-10">
                <div className="flex items-center gap-4">
                  <Radio
                    size={32}
                    strokeWidth={1.75}
                    className="text-neon-mint/40"
                  />
                  <div className="text-[10px] font-mono text-on-surface-variant tracking-widest leading-tight uppercase">
                    SATELLITE OVERPASS:{' '}
                    <span className="text-neon-mint">04m 12s</span>
                    <br />
                    TELEMETRY QUALITY:{' '}
                    <span className="text-neon-mint">OPTIMAL</span>
                  </div>
                </div>
                <button
                  onClick={runAnalysis}
                  disabled={loading}
                  className="group relative px-12 py-5 font-bold font-mono text-sm tracking-widest uppercase overflow-hidden transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-70"
                  style={{
                    background: '#ADFF00',
                    color: '#1A1412',
                  }}
                >
                  <span className="relative z-10">
                    {loading ? 'PROCESSING...' : 'INITIALIZE ANALYSIS'}
                  </span>
                  <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                </button>
              </div>
            </div>
          </div>

          {/* ══════════════════════════════════════════════
              RIGHT: Recommendation Result Pane
              ══════════════════════════════════════════════ */}
          <div
            className="lg:col-span-5 flex flex-col gap-6 transition-all duration-700"
            style={{
              opacity: isResultVisible ? 1 : 0.4,
              filter: isResultVisible ? 'none' : 'grayscale(1)',
            }}
          >
            <Card
              variant="glass"
              className="p-8 rounded-xl relative overflow-hidden h-full flex flex-col border border-[#ADFF00]/10"
              style={{ borderLeft: '4px solid #ADFF00' }}
            >
              {/* Loading Overlay */}
              {loading && (
                <div className="absolute inset-0 bg-surface/90 flex flex-col items-center justify-center z-20">
                  <Loader2
                    size={48}
                    strokeWidth={1.75}
                    className="text-neon-mint animate-spin"
                  />
                  <p className="mt-4 type-label-caps text-neon-mint">
                    SYNTHESIZING DATA...
                  </p>
                </div>
              )}

              {/* Header */}
              <div className="mb-8 flex justify-between items-start">
                <div>
                  <Badge variant="ai" pulse>
                    {result ? 'OPTIMAL MATCH FOUND' : 'AWAITING INPUT'}
                  </Badge>
                  {result?.historically_adjusted && (
                    <Badge variant="ai" className="ml-2 bg-purple-500/20 text-purple-300 border-purple-500/50">
                      HISTORICALLY ADJUSTED
                    </Badge>
                  )}
                  <h3 className="type-headline-md mt-4">
                    {result ? result.crop : '--- ---'}
                  </h3>
                </div>
                <div className="text-right">
                  <p className="type-label-caps text-[10px] text-on-surface-variant">
                    PROJECTION ID
                  </p>
                  <p className="font-mono text-xs text-neon-mint">#AN-8892-Z</p>
                </div>
              </div>

              {/* Crop Image */}
              <div className="relative w-full aspect-square mb-8 group">
                <div className="absolute inset-0 border border-[#ADFF00]/20 rounded-2xl group-hover:border-[#ADFF00]/50 transition-colors z-10" />
                <Image
                  src="/golden_maize.jpg"
                  alt="Golden Maize crop recommendation"
                  fill
                  className="object-cover rounded-2xl transition-all duration-500"
                  style={{
                    opacity: result ? 1 : 0.5,
                    filter: result ? 'none' : 'grayscale(1)',
                  }}
                />
                {/* Confidence Overlay */}
                <div className="absolute bottom-4 left-4 right-4 bg-surface/80 backdrop-blur-md p-4 rounded-xl border border-white/10 z-10">
                  <div className="flex items-center justify-between">
                    <span className="type-label-caps text-on-surface-variant">
                      AI CONFIDENCE
                    </span>
                    <span className="font-mono text-neon-mint text-xl">
                      {result ? `${result.confidence}%` : '--%'}
                    </span>
                  </div>
                  <div className="w-full h-1 bg-white/5 rounded-full mt-2 overflow-hidden">
                    <div
                      className="h-full bg-neon-mint transition-all duration-1000"
                      style={{ width: result ? `${result.confidence}%` : '0%' }}
                    />
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4 mt-auto">
                <div className="bg-soil-deep/50 p-4 rounded-lg border border-white/5">
                  <span className="type-label-caps text-[10px] text-on-surface-variant block mb-1">
                    PROJECTED YIELD
                  </span>
                  <div className="flex items-baseline gap-1">
                    <span className="font-mono text-2xl text-on-surface">
                      {result ? result.yield : '--.-'}
                    </span>
                    <span className="type-label-caps text-[10px] text-neon-mint">
                      BU/AC
                    </span>
                  </div>
                </div>
                <div className="bg-soil-deep/50 p-4 rounded-lg border border-white/5">
                  <span className="type-label-caps text-[10px] text-on-surface-variant block mb-1">
                    RESOURCE COST
                  </span>
                  <div className="flex items-baseline gap-1">
                    <TrendingDown
                      size={16}
                      strokeWidth={1.75}
                      className="text-neon-mint"
                    />
                    <span className="font-mono text-2xl text-on-surface">
                      {result ? result.cost : '--%'}
                    </span>
                  </div>
                </div>
              </div>

              {/* AI Insight Chip */}
              <div className="mt-6 flex flex-col gap-3">
                <div className="flex items-center gap-3 bg-[#ADFF00]/5 p-3 rounded-lg border border-[#ADFF00]/10">
                  <Brain
                    size={18}
                    strokeWidth={1.75}
                    className="text-neon-mint animate-pulse-glow flex-shrink-0"
                  />
                  <p className="type-body-md text-[13px] text-on-surface-variant italic">
                    {result
                      ? result.insight
                      : '"Awaiting environmental parameters for synthesis..."'}
                  </p>
                </div>
                {result?.rationale && (
                  <div className="flex items-center gap-3 bg-purple-500/5 p-3 rounded-lg border border-purple-500/10">
                    <Brain
                      size={18}
                      strokeWidth={1.75}
                      className="text-purple-400 flex-shrink-0"
                    />
                    <p className="type-body-md text-[13px] text-purple-200/80 italic">
                      {result.rationale}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
