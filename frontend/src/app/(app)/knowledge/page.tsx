"use client";

/**
 * AgriNova AI — Knowledge Base Page
 */

import React, { useEffect, useState } from "react";
import { knowledgeAPI, type CropProfile } from "@/lib/api";

export default function KnowledgePage() {
  const [crops, setCrops] = useState<CropProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedCrop, setSelectedCrop] = useState<CropProfile | null>(null);

  useEffect(() => {
    knowledgeAPI.listCrops()
      .then(setCrops)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = crops.filter((c) =>
    c.crop_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      {/* Header */}
      <div className="animate-fade-in-up" style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "4px" }}>
          📚 Knowledge Base
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
          Agronomic reference data — crop profiles, growing conditions, and best practices
        </p>
      </div>

      {/* Search */}
      <div className="animate-fade-in-up delay-1" style={{ marginBottom: "24px" }}>
        <input
          type="text"
          className="input-field"
          placeholder="🔍 Search crops..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: "400px" }}
        />
      </div>

      {/* Content */}
      <div style={{ display: "flex", gap: "24px" }}>
        {/* Crop Grid */}
        <div style={{ flex: 1 }}>
          {loading ? (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "14px" }}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="skeleton" style={{ height: "140px" }} />
              ))}
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "14px" }}>
              {filtered.map((crop, i) => (
                <button
                  key={crop.id}
                  onClick={() => setSelectedCrop(crop)}
                  className="glass-card animate-fade-in-up"
                  style={{
                    padding: "20px",
                    textAlign: "left",
                    cursor: "pointer",
                    border: selectedCrop?.id === crop.id ? "1px solid var(--accent-primary)" : "1px solid var(--border)",
                    background: selectedCrop?.id === crop.id ? "var(--accent-glow)" : "var(--surface-glass)",
                    animationDelay: `${i * 0.03}s`,
                  }}
                >
                  <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "8px" }}>
                    🌱 {crop.crop_name}
                  </h3>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    <span className="badge badge-success">{crop.growing_season}</span>
                    <span className="badge" style={{ background: "var(--surface)", color: "var(--text-muted)" }}>
                      {crop.ideal_soil_types}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Detail Panel */}
        {selectedCrop && (
          <div
            className="glass-card animate-slide-in"
            style={{
              width: "360px",
              padding: "28px",
              position: "sticky",
              top: "calc(var(--navbar-height) + 32px)",
              alignSelf: "start",
              flexShrink: 0,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
              <h2 style={{ fontSize: "22px", fontWeight: 800 }}>🌾 {selectedCrop.crop_name}</h2>
              <button
                onClick={() => setSelectedCrop(null)}
                style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", fontSize: "18px" }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "20px" }}>
              {selectedCrop.description}
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              {[
                { label: "🌡️ Temperature", value: `${selectedCrop.temp_min}°C – ${selectedCrop.temp_max}°C` },
                { label: "🌧️ Rainfall", value: `${selectedCrop.rain_min} – ${selectedCrop.rain_max} mm` },
                { label: "💧 Humidity", value: `${selectedCrop.humidity_min}% – ${selectedCrop.humidity_max}%` },
                { label: "🪨 Soil Types", value: selectedCrop.ideal_soil_types },
                { label: "📅 Season", value: selectedCrop.growing_season },
                { label: "⏱️ Duration", value: selectedCrop.total_duration_days ? `${selectedCrop.total_duration_days} days` : "Varies" },
              ].map((item) => (
                <div key={item.label} style={{
                  padding: "10px 14px", background: "var(--surface)",
                  borderRadius: "var(--radius-md)",
                }}>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "2px" }}>{item.label}</p>
                  <p style={{ fontSize: "14px", fontWeight: 600 }}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
