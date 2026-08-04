"use client";

/**
 * AgriNova AI — Dashboard Page
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { farmAPI, type FarmData } from "@/lib/api";

export default function DashboardPage() {
  const { user } = useAuth();
  const [farms, setFarms] = useState<FarmData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    farmAPI.list()
      .then((data) => setFarms(data.farms))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalArea = farms.reduce((sum, f) => sum + f.total_area_acres, 0);
  const totalCrops = farms.reduce((sum, f) => sum + f.crops.length, 0);

  const stats = [
    { label: "Total Farms", value: farms.length, icon: "🏡", color: "var(--accent-primary)" },
    { label: "Total Area", value: `${totalArea.toFixed(1)} acres`, icon: "📐", color: "var(--accent-secondary)" },
    { label: "Active Crops", value: totalCrops, icon: "🌾", color: "var(--warning)" },
    { label: "AI Insights", value: "Coming Soon", icon: "🤖", color: "var(--info)" },
  ];

  return (
    <div>
      {/* Welcome Header */}
      <div className="animate-fade-in-up" style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "32px", fontWeight: 800, marginBottom: "8px" }}>
          Welcome back, <span className="gradient-text">{user?.full_name?.split(" ")[0] || "Farmer"}</span> 👋
        </h1>
        <p style={{ color: "var(--text-muted)", fontSize: "15px" }}>
          Here&apos;s an overview of your farming operations
        </p>
      </div>

      {/* Stats Grid */}
      <div
        className="animate-fade-in-up delay-1"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: "16px",
          marginBottom: "32px",
        }}
      >
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="glass-card"
            style={{ padding: "24px" }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
              <span style={{ fontSize: "28px" }}>{stat.icon}</span>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: stat.color,
                  boxShadow: `0 0 8px ${stat.color}`,
                }}
              />
            </div>
            <p style={{ fontSize: "24px", fontWeight: 700, marginBottom: "4px" }}>{stat.value}</p>
            <p style={{ fontSize: "13px", color: "var(--text-muted)" }}>{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Farms Section */}
      <div className="animate-fade-in-up delay-2" style={{ marginBottom: "32px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px" }}>
          <h2 style={{ fontSize: "20px", fontWeight: 700 }}>Your Farms</h2>
          <Link href="/farms/new" className="btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Add Farm
          </Link>
        </div>

        {loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "16px" }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: "180px" }} />
            ))}
          </div>
        ) : farms.length === 0 ? (
          /* Empty State */
          <div
            className="glass-card"
            style={{
              padding: "60px 40px",
              textAlign: "center",
              background: "radial-gradient(ellipse at center, var(--accent-glow), var(--surface-glass))",
            }}
          >
            <div className="animate-float" style={{ fontSize: "56px", marginBottom: "20px" }}>🌾</div>
            <h3 style={{ fontSize: "22px", fontWeight: 700, marginBottom: "8px" }}>No farms yet</h3>
            <p style={{ color: "var(--text-muted)", fontSize: "14px", marginBottom: "24px", maxWidth: "400px", margin: "0 auto 24px" }}>
              Create your first farm to start receiving AI-powered crop recommendations and manage your agricultural operations.
            </p>
            <Link href="/farms/new" className="btn-primary" style={{ padding: "12px 32px", fontSize: "15px" }}>
              🌱 Create Your First Farm
            </Link>
          </div>
        ) : (
          /* Farm Cards Grid */
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "16px" }}>
            {farms.map((farm, i) => (
              <Link
                key={farm.id}
                href={`/farms/${farm.id}`}
                className="glass-card"
                style={{
                  padding: "24px",
                  textDecoration: "none",
                  color: "inherit",
                  animationDelay: `${i * 0.05}s`,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
                  <div
                    style={{
                      width: 40, height: 40, borderRadius: "var(--radius-md)",
                      background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
                      display: "flex", alignItems: "center", justifyContent: "center", fontSize: "20px",
                    }}
                  >
                    🏡
                  </div>
                  <div>
                    <h3 style={{ fontSize: "16px", fontWeight: 600 }}>{farm.name}</h3>
                    <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>{farm.location_city}{farm.location_state ? `, ${farm.location_state}` : ""}</p>
                  </div>
                </div>

                <div style={{ display: "flex", gap: "16px", fontSize: "13px" }}>
                  <div>
                    <span style={{ color: "var(--text-muted)" }}>Area: </span>
                    <span style={{ fontWeight: 600 }}>{farm.total_area_acres} acres</span>
                  </div>
                  <div>
                    <span style={{ color: "var(--text-muted)" }}>Soil: </span>
                    <span style={{ fontWeight: 600 }}>{farm.soil_type}</span>
                  </div>
                </div>

                {farm.crops.length > 0 && (
                  <div style={{ marginTop: "12px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
                    {farm.crops.map((crop) => (
                      <span key={crop.id} className="badge badge-success">{crop.crop_name}</span>
                    ))}
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="animate-fade-in-up delay-3">
        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "16px" }}>Quick Actions</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "12px" }}>
          {[
            { icon: "🌱", label: "Get Crop Recommendation", desc: "AI-powered crop analysis", href: "/crops" },
            { icon: "📚", label: "Knowledge Base", desc: "Agronomic reference data", href: "/knowledge" },
            { icon: "☁️", label: "Weather Dashboard", desc: "Forecast & alerts", href: "/weather" },
          ].map((action) => (
            <Link
              key={action.label}
              href={action.href}
              className="glass-card"
              style={{
                padding: "20px",
                textDecoration: "none",
                color: "inherit",
                display: "flex",
                alignItems: "center",
                gap: "14px",
              }}
            >
              <span style={{ fontSize: "28px" }}>{action.icon}</span>
              <div>
                <p style={{ fontWeight: 600, fontSize: "14px" }}>{action.label}</p>
                <p style={{ fontSize: "12px", color: "var(--text-muted)" }}>{action.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
