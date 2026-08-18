'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { AuthProvider, useAuth } from '@/lib/auth';
import Background from '@/background/Background/Background';
import { Button, Card, Badge, Input } from '@/ui';
import { Mail, Lock, ArrowRight, ShieldCheck, KeyRound } from 'lucide-react';

function LoginForm() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface text-on-surface relative overflow-hidden flex items-center justify-center p-6 font-sans">
      {/* ── Active Ambient WebGL Seed Shader Background ── */}
      <Background
        shader={true}
        fog={true}
        groundGlow={true}
        noise={true}
        fireflies={true}
        fireflyCount={12}
        seeds={true}
        seedCount={15}
      />

      <div className="relative z-10 w-full max-w-md">
        <Card variant="glass" className="p-8 md:p-10 rounded-3xl border border-[#ADFF00]/20 shadow-[0_0_30px_rgba(173,255,0,0.12)]">
          {/* Header Brand Cutout */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="relative mb-4 flex items-center justify-center">
              <div className="absolute inset-0 bg-[#ADFF00]/20 blur-xl rounded-full" />
              <div className="relative w-16 h-16 rounded-2xl bg-surface-container border border-neon-mint/30 flex items-center justify-center p-2">
                <Image
                  src="/logo_transparent.png"
                  alt="AgriNova AI Logo"
                  width={48}
                  height={48}
                  className="object-contain filter drop-shadow-[0_0_8px_rgba(173,255,0,0.6)]"
                  priority
                />
              </div>
            </div>

            <Badge variant="ai" pulse className="mb-3">
              SYSTEM AUTHENTICATION
            </Badge>

            <h1 className="type-headline-md mb-2">Agronomist Sign In</h1>
            <p className="type-body-sm text-on-surface-variant max-w-xs">
              Access precision telemetry and AI-driven environmental control.
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="p-3 mb-6 rounded-xl bg-error/10 border border-error/30 text-error text-sm flex items-center gap-2">
              <ShieldCheck size={16} strokeWidth={1.75} />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="type-label-caps text-[11px] text-on-surface-variant block mb-2">
                WORK EMAIL ADDRESS
              </label>
              <div className="relative flex items-center">
                <Mail size={18} strokeWidth={1.75} className="absolute left-4 text-on-surface-variant" />
                <Input
                  id="email"
                  type="email"
                  variant="lens"
                  placeholder="agronomist@agrinova.ai"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  style={{ paddingLeft: '44px' }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label htmlFor="password" className="type-label-caps text-[11px] text-on-surface-variant">
                  PASSCODE
                </label>
                <Link href="#" className="type-label-caps text-[10px] text-neon-mint hover:underline text-decoration-none">
                  FORGOT?
                </Link>
              </div>
              <div className="relative flex items-center">
                <Lock size={18} strokeWidth={1.75} className="absolute left-4 text-on-surface-variant" />
                <Input
                  id="password"
                  type="password"
                  variant="lens"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  style={{ paddingLeft: '44px' }}
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={loading}
              className="w-full mt-2"
              icon={<ArrowRight size={18} strokeWidth={1.75} />}
            >
              INITIALIZE SESSION
            </Button>
          </form>

          {/* Telemetry Footer */}
          <div className="mt-8 pt-6 border-t border-white/5 flex items-center justify-between text-xs">
            <span className="type-label-caps text-[10px] text-on-surface-variant opacity-60">
              NEW AGRO-OPERATOR?
            </span>
            <Link
              href="/register"
              className="type-label-caps text-[11px] text-neon-mint font-bold hover:underline text-decoration-none flex items-center gap-1"
            >
              <KeyRound size={14} strokeWidth={1.75} />
              CREATE ACCOUNT
            </Link>
          </div>
        </Card>
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
