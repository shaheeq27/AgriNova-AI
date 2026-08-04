"use client";

/**
 * AgriNova AI — Farms List Page
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { farmAPI, type FarmData } from "@/lib/api";

export default function FarmsPage() {
  const [farms, setFarms] = useState<FarmData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    farmAPI.list()
      .then((data) => setFarms(data.farms))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="animate-fade-in-up" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "32px" }}>
        <div>
          <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "4px" }}>My Farms</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>Manage your farm properties and land parcels</p>
        </div>
        <Link href="/farms/new" className="btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New Farm
        </Link>
      </div>

      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "20px" }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: "220px" }} />
          ))}
        </div>
      ) : farms.length === 0 ? (
        <div className="glass-card animate-fade-in-up" style={{ padding: "80px 40px", textAlign: "center" }}>
          <div className="animate-float" style={{ fontSize: "64px", marginBottom: "20px" }}>🏡</div>
          <h3 style={{ fontSize: "24px", fontWeight: 700, marginBottom: "8px" }}>No farms registered</h3>
          <p style={{ color: "var(--text-muted)", maxWidth: "400px", margin: "0 auto 28px" }}>
            Add your first farm to get started with AI-powered crop recommendations.
          </p>
          <Link href="/farms/new" className="btn-primary" style={{ padding: "14px 36px", fontSize: "16px" }}>
            🌱 Add Your First Farm
          </Link>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "20px" }}>
          {farms.map((farm, i) => (
            <Link
              key={farm.id}
              href={`/farms/${farm.id}`}
              className="glass-card animate-fade-in-up"
              style={{
                padding: "28px",
                textDecoration: "none",
                color: "inherit",
                animationDelay: `${i * 0.06}s`,
              }}
            >
              <div style={{ display: "flex", alignItems: "start", justifyContent: "space-between", marginBottom: "18px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                  <div style={{
                    width: 48, height: 48, borderRadius: "var(--radius-lg)",
                    background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: "24px",
                  }}>
                    🏡
                  </div>
                  <div>
                    <h3 style={{ fontSize: "18px", fontWeight: 700 }}>{farm.name}</h3>
                    <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                      📍 {farm.location_city}{farm.location_state ? `, ${farm.location_state}` : ""}
                    </p>
                  </div>
                </div>
                <span className={`badge ${farm.is_active ? "badge-success" : "badge-error"}`}>
                  {farm.is_active ? "Active" : "Inactive"}
                </span>
              </div>

              <div style={{
                display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px",
                padding: "14px", background: "var(--surface)", borderRadius: "var(--radius-md)",
              }}>
                <div>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "2px" }}>Total Area</p>
                  <p style={{ fontSize: "15px", fontWeight: 700 }}>{farm.total_area_acres} <span style={{ fontSize: "12px", fontWeight: 400, color: "var(--text-muted)" }}>acres</span></p>
                </div>
                <div>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "2px" }}>Soil Type</p>
                  <p style={{ fontSize: "15px", fontWeight: 700 }}>{farm.soil_type}</p>
                </div>
                <div>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "2px" }}>Water Source</p>
                  <p style={{ fontSize: "15px", fontWeight: 600 }}>{farm.water_source || "—"}</p>
                </div>
                <div>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "2px" }}>Active Crops</p>
                  <p style={{ fontSize: "15px", fontWeight: 700, color: "var(--accent-primary)" }}>{farm.crops.length}</p>
                </div>
              </div>

              {farm.crops.length > 0 && (
                <div style={{ marginTop: "14px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
                  {farm.crops.slice(0, 4).map((crop) => (
                    <span key={crop.id} className="badge badge-success">{crop.crop_name}</span>
                  ))}
                  {farm.crops.length > 4 && (
                    <span className="badge" style={{ background: "var(--surface-hover)", color: "var(--text-muted)" }}>
                      +{farm.crops.length - 4} more
                    </span>
                  )}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
