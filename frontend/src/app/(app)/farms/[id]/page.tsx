"use client";

/**
 * AgriNova AI — Farm Detail Page (Tabbed)
 */

import React, { useEffect, useState, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { farmAPI, cropsAPI, type FarmData, type CropResponse } from "@/lib/api";
import { useFarmInsights } from "@/hooks/useFarmInsights";
import { TrendingUp, TrendingDown, AlertTriangle, ShieldAlert, Droplet, Sprout, Activity, ArrowRight, Minus } from "lucide-react";
import { Card, Badge, Button } from "@/ui"; // Assuming these exist from earlier steps, if not we'll use raw HTML matching existing style

type TabState = "overview" | "history" | "insights";

export default function FarmDetailPage() {
  const params = useParams();
  const router = useRouter();
  const farmId = params.id as string;

  const [farm, setFarm] = useState<FarmData | null>(null);
  const [cropsHistory, setCropsHistory] = useState<CropResponse[]>([]);

  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [activeTab, setActiveTab] = useState<TabState>("overview");

  const { data: insights, loading: insightsLoading, error: insightsError } = useFarmInsights(activeTab === "insights" ? farmId : undefined);

  // Compute derived metrics from insights arrays
  const bestPerformingCrop = useMemo(() => {
    if (!insights?.crop_performance?.length) return null;
    return insights.crop_performance.reduce((prev, curr) => (curr.average_yield || 0) > (prev.average_yield || 0) ? curr : prev);
  }, [insights]);

  const worstPerformingCrop = useMemo(() => {
    if (!insights?.crop_performance?.length) return null;
    return insights.crop_performance.reduce((prev, curr) => {
      if ((curr.average_yield || 0) === 0) return prev; // Ignore zero yields if they exist
      return (curr.average_yield || 0) < (prev.average_yield || Infinity) ? curr : prev;
    });
  }, [insights]);

  const mostCommonDisease = useMemo(() => {
    if (!insights?.disease_patterns?.length) return null;
    return insights.disease_patterns.reduce((prev, curr) => curr.occurrence_count > prev.occurrence_count ? curr : prev);
  }, [insights]);


  useEffect(() => {
    if (farmId) {
      farmAPI.get(farmId)
        .then(setFarm)
        .catch(() => router.push("/farms"))
        .finally(() => setLoading(false));
    }
  }, [farmId, router]);

  // Fetch history when history tab is selected
  useEffect(() => {
    if (activeTab === "history" && farmId && cropsHistory.length === 0) {
      setHistoryLoading(true);
      cropsAPI.listByFarm(farmId)
        .then(res => {
          // Filter for non-active crops
          const pastCrops = res.crops.filter(c => c.status !== "active");
          // Sort by planting date descending
          pastCrops.sort((a, b) => {
             if (!a.planting_date) return 1;
             if (!b.planting_date) return -1;
             return new Date(b.planting_date).getTime() - new Date(a.planting_date).getTime();
          });
          setCropsHistory(pastCrops);
        })
        .catch(console.error)
        .finally(() => setHistoryLoading(false));
    }
  }, [activeTab, farmId, cropsHistory.length]);

  const handleDelete = async () => {
    if (!farm || !confirm("Are you sure you want to delete this farm?")) return;
    setDeleting(true);
    try {
      await farmAPI.delete(farm.id);
      router.push("/farms");
    } catch { setDeleting(false); }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="skeleton" style={{ height: "32px", width: "200px", marginBottom: "8px" }} />
        <div className="skeleton" style={{ height: "16px", width: "300px", marginBottom: "32px" }} />
        <div className="skeleton" style={{ height: "300px" }} />
      </div>
    );
  }

  if (!farm) return null;

  return (
    <div className="pb-12">
      {/* Header */}
      <div className="animate-fade-in-up" style={{ marginBottom: "32px" }}>
        <Link href="/farms" style={{ color: "var(--text-muted)", textDecoration: "none", fontSize: "13px", display: "inline-flex", alignItems: "center", gap: "6px", marginBottom: "16px" }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6" /></svg>
          Back to Farms
        </Link>
        <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "4px" }}>{farm.name}</h1>
            <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
              📍 {farm.location_city}{farm.location_state ? `, ${farm.location_state}` : ""}
            </p>
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            <button onClick={handleDelete} className="btn-secondary" disabled={deleting}
              style={{ color: "var(--error)", borderColor: "rgba(239,68,68,0.3)", fontSize: "13px", padding: "8px 16px" }}>
              {deleting ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 border-b border-white/10 mb-8 animate-fade-in-up delay-1">
        {(["overview", "history", "insights"] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-4 px-2 text-sm font-medium tracking-wide transition-colors uppercase ${
              activeTab === tab
                ? "text-neon-mint border-b-2 border-neon-mint"
                : "text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {tab.replace("_", " ")}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in-up delay-2">
        {activeTab === "overview" && (
          <div className="flex flex-col gap-6">
            {/* Farm Details Card */}
            <div className="glass-card" style={{ padding: "32px" }}>
              <h2 style={{ fontSize: "18px", fontWeight: 700, marginBottom: "20px" }}>Farm Details</h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "24px" }}>
                {[
                  { label: "Total Area", value: `${farm.total_area_acres} acres`, icon: "📐" },
                  { label: "Soil Type", value: farm.soil_type, icon: "🪨" },
                  { label: "Water Source", value: farm.water_source || "Not specified", icon: "💧" },
                  { label: "Active Crops", value: `${farm.crops.length}`, icon: "🌾" },
                  { label: "Status", value: farm.is_active ? "Active" : "Inactive", icon: "✅" },
                  { label: "Created", value: new Date(farm.created_at).toLocaleDateString(), icon: "📅" },
                ].map((detail) => (
                  <div key={detail.label}>
                    <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>
                      {detail.icon} {detail.label}
                    </p>
                    <p style={{ fontSize: "16px", fontWeight: 600 }}>{detail.value}</p>
                  </div>
                ))}
              </div>
              {farm.description && (
                <div style={{ marginTop: "20px", padding: "14px", background: "var(--surface)", borderRadius: "var(--radius-md)" }}>
                  <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Description</p>
                  <p style={{ fontSize: "14px" }}>{farm.description}</p>
                </div>
              )}
            </div>

            {/* Crop Recommendations CTA */}
            <div className="glass-card" style={{
              padding: "40px", textAlign: "center",
              background: "radial-gradient(ellipse at center, var(--accent-glow), var(--surface-glass))",
            }}>
              <div style={{ fontSize: "48px", marginBottom: "16px" }}>🤖</div>
              <h3 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "8px" }}>Get AI Crop Recommendations</h3>
              <p style={{ color: "var(--text-muted)", fontSize: "14px", marginBottom: "24px", maxWidth: "400px", margin: "0 auto 24px" }}>
                Based on your farm&apos;s soil type, location, and weather data, our AI will recommend the best crops for you.
              </p>
              <Link href="/advisor" className="btn-primary" style={{ padding: "12px 32px", fontSize: "15px", display: "inline-block" }}>
                🌱 Launch Advisor
              </Link>
            </div>
          </div>
        )}

        {activeTab === "history" && (
          <div className="flex flex-col gap-4">
            {historyLoading ? (
              <div className="p-12 text-center text-on-surface-variant flex flex-col items-center">
                <div className="w-6 h-6 border-2 border-neon-mint border-t-transparent rounded-full animate-spin mb-4" />
                <p>Loading timeline...</p>
              </div>
            ) : cropsHistory.length === 0 ? (
              <div className="glass-card p-12 text-center border-dashed border-white/20">
                <span className="text-4xl mb-4 block opacity-50">🌾</span>
                <h3 className="type-headline-md mb-2">No Historical Data Logged Yet</h3>
                <p className="type-body-sm text-on-surface-variant max-w-sm mx-auto">
                  Harvest a crop to build your farm&apos;s history and unlock powerful AI insights for future planting seasons.
                </p>
              </div>
            ) : (
              <div className="relative border-l-2 border-white/10 ml-4 md:ml-6 space-y-8 pb-8">
                {cropsHistory.map(crop => (
                  <div key={crop.id} className="relative pl-8 md:pl-10">
                    <div className="absolute w-4 h-4 bg-surface border-2 border-neon-mint rounded-full -left-[9px] top-4 shadow-[0_0_10px_rgba(173,255,0,0.5)]" />

                    <div className="glass-card p-6 flex flex-col md:flex-row justify-between gap-6 hover:border-white/20 transition-colors">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-on-surface">{crop.crop_name}</h3>
                          <span className="px-2.5 py-1 text-[10px] uppercase tracking-wider font-mono bg-white/5 border border-white/10 rounded-full text-on-surface-variant">
                            {crop.status}
                          </span>
                        </div>
                        <p className="text-sm text-on-surface-variant mb-4">
                          {crop.variety ? `${crop.variety} · ` : ""}{crop.season} Season
                        </p>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <span className="block text-[10px] text-on-surface-variant uppercase tracking-wide mb-1">Planted</span>
                            <span className="font-mono text-sm text-on-surface">
                              {crop.planting_date ? new Date(crop.planting_date).toLocaleDateString() : "--"}
                            </span>
                          </div>
                          <div>
                            <span className="block text-[10px] text-on-surface-variant uppercase tracking-wide mb-1">Harvested</span>
                            <span className="font-mono text-sm text-on-surface">
                              {crop.actual_harvest_date ? new Date(crop.actual_harvest_date).toLocaleDateString() : "--"}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="md:w-48 bg-soil-deep/50 rounded-xl p-4 flex flex-col justify-center items-center text-center border border-white/5">
                        <span className="block text-[10px] text-on-surface-variant uppercase tracking-wide mb-2">Total Yield</span>
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-mono text-neon-mint">{crop.yield_amount || "--"}</span>
                          <span className="text-xs text-neon-mint/60">{crop.yield_unit || "kg"}</span>
                        </div>
                        <span className="block text-[10px] text-on-surface-variant mt-3 border-t border-white/10 pt-2 w-full">
                          {crop.area_acres} Acres Planted
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

                {activeTab === "insights" && (
          <div className="flex flex-col gap-6">
            {insightsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="skeleton h-[200px] w-full" />
                <div className="skeleton h-[200px] w-full" />
                <div className="skeleton h-[200px] w-full" />
                <div className="skeleton h-[200px] w-full" />
              </div>
            ) : insightsError ? (
              <div className="glass-card p-12 text-center border-dashed border-red-500/20">
                <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4 opacity-50" />
                <h3 className="type-headline-md mb-2 text-red-400">Failed to load AI Insights</h3>
                <p className="type-body-sm text-on-surface-variant max-w-sm mx-auto">
                  {insightsError.message || "An unexpected error occurred while analyzing historical data."}
                </p>
              </div>
            ) : !insights || (insights.crop_performance.length === 0 && insights.disease_patterns.length === 0) ? (
               <div className="glass-card p-12 text-center border-dashed border-white/20">
                <Sprout className="mx-auto h-12 w-12 text-neon-mint mb-4 opacity-50" />
                <h3 className="type-headline-md mb-2">Insufficient Data for Analysis</h3>
                <p className="type-body-sm text-on-surface-variant max-w-sm mx-auto">
                  Not enough historical data yet. Log more harvests and crop details to unlock personalized AI insights for this farm.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Crop Performance */}
                <div className="glass-card p-6 border border-white/5 hover:border-neon-mint/30 transition-colors">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-neon-mint/10 text-neon-mint">
                      <Sprout size={20} />
                    </div>
                    <h3 className="text-lg font-bold text-on-surface">Crop Performance</h3>
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                      <span className="text-sm text-on-surface-variant">Best Performing</span>
                      <span className="font-medium text-neon-mint flex items-center gap-2">
                        {bestPerformingCrop?.crop_name || "—"}
                        {bestPerformingCrop && <TrendingUp size={14} />}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                      <span className="text-sm text-on-surface-variant">Needs Attention</span>
                      <span className="font-medium text-orange-400 flex items-center gap-2">
                        {worstPerformingCrop?.crop_name || "—"}
                        {worstPerformingCrop && <TrendingDown size={14} />}
                      </span>
                    </div>
                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                      <span className="text-sm text-on-surface-variant">Reliability Score</span>
                      <span className="font-mono text-on-surface">
                        {bestPerformingCrop?.confidence ? `${(bestPerformingCrop.confidence * 100).toFixed(0)}%` : "—"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Yield Trends */}
                <div className="glass-card p-6 border border-white/5 hover:border-neon-mint/30 transition-colors">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                      <Activity size={20} />
                    </div>
                    <h3 className="text-lg font-bold text-on-surface">Yield Trends</h3>
                  </div>

                  <div className="space-y-4">
                    {insights.yield_trends.length > 0 ? insights.yield_trends.slice(0, 3).map((trend, i) => (
                      <div key={i} className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                        <span className="text-sm text-on-surface-variant">{trend.crop_name}</span>
                        <div className="flex items-center gap-2">
                           <span className="text-xs text-on-surface-variant">{trend.average_yield} {trend.yield_unit}</span>
                           {trend.trend_direction === "increasing" ? (
                             <Badge className="bg-neon-mint/20 text-neon-mint border-neon-mint/50"><TrendingUp size={12} className="mr-1"/> Up</Badge>
                           ) : trend.trend_direction === "decreasing" ? (
                             <Badge className="bg-red-500/20 text-red-400 border-red-500/50"><TrendingDown size={12} className="mr-1"/> Down</Badge>
                           ) : (
                             <Badge className="bg-white/10 text-on-surface border-white/20"><Minus size={12} className="mr-1"/> Stable</Badge>
                           )}
                        </div>
                      </div>
                    )) : (
                      <div className="p-3 text-center text-on-surface-variant text-sm">No yield trends available.</div>
                    )}
                  </div>
                </div>

                {/* Disease Patterns */}
                <div className="glass-card p-6 border border-white/5 hover:border-orange-500/30 transition-colors">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-orange-500/10 text-orange-400">
                      <ShieldAlert size={20} />
                    </div>
                    <h3 className="text-lg font-bold text-on-surface">Disease Patterns</h3>
                  </div>

                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                      <span className="text-sm text-on-surface-variant">Most Common</span>
                      <span className="font-medium text-orange-400">
                        {mostCommonDisease ? `${mostCommonDisease.disease_name} (${mostCommonDisease.occurrence_count})` : "—"}
                      </span>
                    </div>
                                        {insights.disease_patterns.length > 0 ? (
                      <>
                        {insights.disease_patterns.filter(d => d.occurrence_count > 1).map((d, i) => (
                           <div key={i} className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20 mb-2">
                             <div className="flex items-start gap-2">
                               <AlertTriangle size={14} className="text-orange-400 mt-0.5" />
                               <p className="text-xs text-orange-200">
                                 <strong>High Risk:</strong> Recurrent cases of {d.disease_name} ({d.occurrence_count} times) observed in {d.affected_crop}. Preventative measures recommended.
                               </p>
                             </div>
                           </div>
                        ))}
                      </>
                    ) : (
                       <div className="p-3 rounded-lg bg-neon-mint/10 border border-neon-mint/20">
                         <div className="flex items-start gap-2">
                           <Sprout size={14} className="text-neon-mint mt-0.5" />
                           <p className="text-xs text-neon-mint/80">
                             No significant disease patterns detected in historical logs.
                           </p>
                         </div>
                       </div>
                    )}
                  </div>
                </div>

                {/* Input Usage */}
                <div className="glass-card p-6 border border-white/5 hover:border-blue-500/30 transition-colors">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                      <Droplet size={20} />
                    </div>
                    <h3 className="text-lg font-bold text-on-surface">Input Usage</h3>
                  </div>

                  <div className="space-y-4">
                    {insights.input_usage.length > 0 ? insights.input_usage.slice(0, 3).map((input, i) => (
                      <div key={i} className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                        <span className="text-sm text-on-surface-variant">{input.input_type} ({input.crop_name})</span>
                        <div className="text-right">
                          <span className="block text-sm font-medium text-on-surface">{input.total_quantity || "—"} {input.quantity_unit}</span>
                          <span className="block text-[10px] text-on-surface-variant">{input.application_count} applications</span>
                        </div>
                      </div>
                    )) : (
                      <div className="p-3 text-center text-on-surface-variant text-sm">No input usage data available.</div>
                    )}
                  </div>
                </div>

              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
