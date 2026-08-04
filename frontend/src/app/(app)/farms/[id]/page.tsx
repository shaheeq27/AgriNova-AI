"use client";

/**
 * AgriNova AI — Farm Detail Page
 */

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { farmAPI, type FarmData } from "@/lib/api";

export default function FarmDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [farm, setFarm] = useState<FarmData | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (params.id) {
      farmAPI.get(params.id as string)
        .then(setFarm)
        .catch(() => router.push("/farms"))
        .finally(() => setLoading(false));
    }
  }, [params.id, router]);

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
      <div>
        <div className="skeleton" style={{ height: "32px", width: "200px", marginBottom: "8px" }} />
        <div className="skeleton" style={{ height: "16px", width: "300px", marginBottom: "32px" }} />
        <div className="skeleton" style={{ height: "300px" }} />
      </div>
    );
  }

  if (!farm) return null;

  return (
    <div>
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

      {/* Farm Details Card */}
      <div className="glass-card animate-fade-in-up delay-1" style={{ padding: "32px", marginBottom: "24px" }}>
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
      <div className="glass-card animate-fade-in-up delay-2" style={{
        padding: "40px", textAlign: "center",
        background: "radial-gradient(ellipse at center, var(--accent-glow), var(--surface-glass))",
      }}>
        <div style={{ fontSize: "48px", marginBottom: "16px" }}>🤖</div>
        <h3 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "8px" }}>Get AI Crop Recommendations</h3>
        <p style={{ color: "var(--text-muted)", fontSize: "14px", marginBottom: "24px", maxWidth: "400px", margin: "0 auto 24px" }}>
          Based on your farm&apos;s soil type, location, and weather data, our AI will recommend the best crops for you.
        </p>
        <button className="btn-primary" style={{ padding: "12px 32px", fontSize: "15px" }} disabled>
          🌱 Coming in Phase 2
        </button>
      </div>
    </div>
  );
}
