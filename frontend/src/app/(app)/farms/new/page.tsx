"use client";

/**
 * AgriNova AI — Create Farm Page
 */

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { farmAPI } from "@/lib/api";

const SOIL_TYPES = ["Clay", "Loamy", "Sandy", "Black", "Red", "Alluvial", "Laterite"];
const WATER_SOURCES = ["Borewell", "Canal", "River", "Rainwater", "Pond/Tank", "Drip System", "Other"];

export default function CreateFarmPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "",
    location_city: "",
    location_state: "",
    total_area_acres: "",
    soil_type: "",
    water_source: "",
    description: "",
  });

  const update = (field: string, value: string) => setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await farmAPI.create({
        name: form.name,
        location_city: form.location_city,
        location_state: form.location_state || undefined,
        total_area_acres: parseFloat(form.total_area_acres),
        soil_type: form.soil_type,
        water_source: form.water_source || undefined,
        description: form.description || undefined,
      });
      router.push("/farms");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create farm");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "640px" }}>
      <div className="animate-fade-in-up" style={{ marginBottom: "32px" }}>
        <Link href="/farms" style={{ color: "var(--text-muted)", textDecoration: "none", fontSize: "13px", display: "inline-flex", alignItems: "center", gap: "6px", marginBottom: "16px" }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15,18 9,12 15,6" /></svg>
          Back to Farms
        </Link>
        <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "4px" }}>Create New Farm</h1>
        <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>Add a new farm to your agricultural portfolio</p>
      </div>

      {error && (
        <div style={{ padding: "10px 16px", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)", borderRadius: "var(--radius-md)", color: "var(--error)", fontSize: "13px", marginBottom: "20px" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-card animate-fade-in-up delay-1" style={{ padding: "32px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
          {/* Farm Name */}
          <div>
            <label className="input-label" htmlFor="farm-name">Farm Name *</label>
            <input id="farm-name" type="text" className="input-field" placeholder="e.g., Green Valley Farm"
              value={form.name} onChange={(e) => update("name", e.target.value)} required minLength={2} />
          </div>

          {/* Location */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div>
              <label className="input-label" htmlFor="city">City / Village *</label>
              <input id="city" type="text" className="input-field" placeholder="e.g., Pune"
                value={form.location_city} onChange={(e) => update("location_city", e.target.value)} required />
            </div>
            <div>
              <label className="input-label" htmlFor="state">State</label>
              <input id="state" type="text" className="input-field" placeholder="e.g., Maharashtra"
                value={form.location_state} onChange={(e) => update("location_state", e.target.value)} />
            </div>
          </div>

          {/* Area */}
          <div>
            <label className="input-label" htmlFor="area">Total Area (acres) *</label>
            <input id="area" type="number" className="input-field" placeholder="e.g., 5.5"
              step="0.1" min="0.1"
              value={form.total_area_acres} onChange={(e) => update("total_area_acres", e.target.value)} required />
          </div>

          {/* Soil Type */}
          <div>
            <label className="input-label">Soil Type *</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {SOIL_TYPES.map((soil) => (
                <button
                  key={soil}
                  type="button"
                  onClick={() => update("soil_type", soil)}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "var(--radius-full)",
                    border: form.soil_type === soil ? "2px solid var(--accent-primary)" : "1px solid var(--border)",
                    background: form.soil_type === soil ? "var(--accent-glow)" : "var(--surface)",
                    color: form.soil_type === soil ? "var(--accent-primary)" : "var(--text-secondary)",
                    fontSize: "13px",
                    fontWeight: form.soil_type === soil ? 600 : 400,
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  {soil}
                </button>
              ))}
            </div>
          </div>

          {/* Water Source */}
          <div>
            <label className="input-label">Water Source</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {WATER_SOURCES.map((source) => (
                <button
                  key={source}
                  type="button"
                  onClick={() => update("water_source", form.water_source === source ? "" : source)}
                  style={{
                    padding: "8px 16px",
                    borderRadius: "var(--radius-full)",
                    border: form.water_source === source ? "2px solid var(--accent-secondary)" : "1px solid var(--border)",
                    background: form.water_source === source ? "rgba(45, 212, 168, 0.1)" : "var(--surface)",
                    color: form.water_source === source ? "var(--accent-secondary)" : "var(--text-secondary)",
                    fontSize: "13px",
                    fontWeight: form.water_source === source ? 600 : 400,
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  {source}
                </button>
              ))}
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="input-label" htmlFor="description">Description (Optional)</label>
            <textarea
              id="description"
              className="input-field"
              placeholder="Any additional notes about your farm..."
              rows={3}
              style={{ resize: "vertical" }}
              value={form.description}
              onChange={(e) => update("description", e.target.value)}
            />
          </div>

          {/* Submit */}
          <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
            <button type="submit" className="btn-primary" disabled={loading} style={{ flex: 1, padding: "12px", fontSize: "15px", opacity: loading ? 0.7 : 1 }}>
              {loading ? "Creating..." : "🌱 Create Farm"}
            </button>
            <Link href="/farms" className="btn-secondary" style={{ padding: "12px 24px" }}>
              Cancel
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
