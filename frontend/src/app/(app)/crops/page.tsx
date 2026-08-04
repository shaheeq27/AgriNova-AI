"use client";

export default function CropsPage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "4px" }}>Crop Intelligence</h1>
        <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>AI-powered crop recommendations and management</p>
      </div>

      <div className="glass-card animate-fade-in-up delay-1" style={{
        padding: "60px", textAlign: "center",
        background: "radial-gradient(ellipse at center, var(--accent-glow), var(--surface-glass))",
      }}>
        <div className="animate-float" style={{ fontSize: "64px", marginBottom: "20px" }}>🌾</div>
        <h2 style={{ fontSize: "24px", fontWeight: 700, marginBottom: "8px" }}>Coming in Phase 2</h2>
        <p style={{ color: "var(--text-muted)", maxWidth: "450px", margin: "0 auto" }}>
          ML-powered crop recommendations, crop dashboards, templated timelines, and daily task management — all arriving in the next phase.
        </p>
      </div>
    </div>
  );
}
