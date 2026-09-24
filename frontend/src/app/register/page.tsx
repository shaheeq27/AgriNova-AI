"use client";

/**
 * AgriNova AI — Register Page
 */

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { AuthProvider, useAuth } from "@/lib/auth";

function RegisterForm() {
  const { register } = useAuth();
  const [form, setForm] = useState({ full_name: "", email: "", phone: "", password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field: string, value: string) => setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        phone: form.phone || undefined,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
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
        background: "radial-gradient(ellipse at 70% 20%, rgba(78, 232, 106, 0.06) 0%, transparent 50%), radial-gradient(ellipse at 30% 80%, rgba(45, 212, 168, 0.04) 0%, transparent 50%), var(--background)",
      }}
    >
      {/* Particles */}
      <div className="particle-bg">
        {Array.from({ length: 15 }).map((_, i) => (
          <div
            key={i}
            className="particle"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${4 + Math.random() * 4}s`,
            }}
          />
        ))}
      </div>

      <div
        className="glass-card animate-fade-in-up"
        style={{ width: "100%", maxWidth: "460px", padding: "40px", position: "relative", zIndex: 1 }}
      >
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <div style={{ position: "relative", marginBottom: "16px", display: "inline-flex", alignItems: "center", justifyItems: "center", margin: "0 auto 16px auto" }}>
            <div className="absolute inset-0 bg-[#ADFF00]/20 blur-xl rounded-full" />
            <div className="relative w-[72px] h-[72px] rounded-2xl bg-[#08120B] border border-[#ADFF00]/30 flex items-center justify-center p-2">
              <Image
                src="/logo_transparent.png"
                alt="AgriNova AI Logo"
                width={72}
                height={72}
                className="object-contain filter drop-shadow-[0_0_8px_rgba(173,255,0,0.6)]"
                priority
              />
            </div>
          </div>
          <h1 style={{ fontSize: "28px", fontWeight: 800, marginBottom: "8px" }}>Create Account</h1>
          <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
            Join AgriNova AI and start your smart farming journey
          </p>
        </div>

        {error && (
          <div style={{
            padding: "10px 16px", background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)", borderRadius: "var(--radius-md)",
            color: "var(--error)", fontSize: "13px", marginBottom: "20px",
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
          <div>
            <label className="input-label" htmlFor="full_name">Full Name</label>
            <input id="full_name" type="text" className="input-field" placeholder="John Doe"
              value={form.full_name} onChange={(e) => update("full_name", e.target.value)} required minLength={2} />
          </div>

          <div>
            <label className="input-label" htmlFor="reg-email">Email Address</label>
            <input id="reg-email" type="email" className="input-field" placeholder="farmer@example.com"
              value={form.email} onChange={(e) => update("email", e.target.value)} required />
          </div>

          <div>
            <label className="input-label" htmlFor="phone">Phone (Optional)</label>
            <input id="phone" type="tel" className="input-field" placeholder="+91 98765 43210"
              value={form.phone} onChange={(e) => update("phone", e.target.value)} />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <div>
              <label className="input-label" htmlFor="reg-password">Password</label>
              <input id="reg-password" type="password" className="input-field" placeholder="••••••••"
                value={form.password} onChange={(e) => update("password", e.target.value)} required minLength={8} />
            </div>
            <div>
              <label className="input-label" htmlFor="confirm-password">Confirm</label>
              <input id="confirm-password" type="password" className="input-field" placeholder="••••••••"
                value={form.confirmPassword} onChange={(e) => update("confirmPassword", e.target.value)} required minLength={8} />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}
            style={{ width: "100%", padding: "12px", fontSize: "15px", marginTop: "4px", opacity: loading ? 0.7 : 1 }}>
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p style={{ textAlign: "center", marginTop: "24px", fontSize: "13px", color: "var(--text-muted)" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--accent-primary)", textDecoration: "none", fontWeight: 600 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <AuthProvider>
      <RegisterForm />
    </AuthProvider>
  );
}
