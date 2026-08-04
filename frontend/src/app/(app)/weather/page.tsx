"use client";

export default function WeatherPage() {
  return (
    <div>
      <div className="animate-fade-in-up" style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "4px" }}>Weather Intelligence</h1>
        <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>Forecast, alerts, and climate data for your farms</p>
      </div>

      <div className="glass-card animate-fade-in-up delay-1" style={{
        padding: "60px", textAlign: "center",
        background: "radial-gradient(ellipse at center, rgba(59,130,246,0.08), var(--surface-glass))",
      }}>
        <div className="animate-float" style={{ fontSize: "64px", marginBottom: "20px" }}>☁️</div>
        <h2 style={{ fontSize: "24px", fontWeight: 700, marginBottom: "8px" }}>Coming in Phase 4</h2>
        <p style={{ color: "var(--text-muted)", maxWidth: "450px", margin: "0 auto" }}>
          Weather dashboards, 7-day forecasts, and smart alerts will be available once the core crop intelligence module is complete.
        </p>
      </div>
    </div>
  );
}
