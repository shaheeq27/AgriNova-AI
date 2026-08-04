"use client";

/**
 * AgriNova AI — Login Page
 */

import React, { useState } from "react";
import Link from "next/link";
import { AuthProvider, useAuth } from "@/lib/auth";

function LoginForm() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        background: "radial-gradient(ellipse at 30% 20%, rgba(78, 232, 106, 0.06) 0%, transparent 50%), radial-gradient(ellipse at 70% 80%, rgba(45, 212, 168, 0.04) 0%, transparent 50%), var(--background)",
      }}
    >
      {/* Floating particles */}
      <div className="particle-bg">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${4 + Math.random() * 4}s`,
              width: `${2 + Math.random() * 4}px`,
              height: `${2 + Math.random() * 4}px`,
              opacity: 0.1 + Math.random() * 0.2,
            }}
          />
        ))}
      </div>

      <div
        className="glass-card animate-fade-in-up"
        style={{
          width: "100%",
          maxWidth: "420px",
          padding: "40px",
          position: "relative",
          zIndex: 1,
        }}
      >
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: "var(--radius-lg)",
              background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "28px",
              marginBottom: "16px",
            }}
          >
            🌱
          </div>
          <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "8px" }}>
            Welcome back
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            Sign in to your AgriNova AI account
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              padding: "10px 16px",
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "var(--radius-md)",
              color: "var(--error)",
              fontSize: "13px",
              marginBottom: "20px",
            }}
          >
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div>
            <label className="input-label" htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              className="input-field"
              placeholder="farmer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="input-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              fontSize: "15px",
              marginTop: "4px",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "24px",
            fontSize: "13px",
            color: "var(--text-muted)",
          }}
        >
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            style={{ color: "var(--accent-primary)", textDecoration: "none", fontWeight: 600 }}
          >
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <AuthProvider>
      <LoginForm />
    </AuthProvider>
  );
}
