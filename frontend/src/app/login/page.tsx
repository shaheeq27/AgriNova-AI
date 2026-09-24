'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { AuthProvider, useAuth } from '@/lib/auth';
import { authAPI } from '@/lib/api';
import Background from '@/background/Background/Background';
import { Button, Card, Badge, Input } from '@/ui';
import { Mail, Lock, ArrowRight, ShieldCheck, KeyRound, ArrowLeft } from 'lucide-react';

function LoginForm() {
  const { login } = useAuth();
  const [mode, setMode] = useState<'login' | 'forgot_password'>('login');

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const handleLoginSubmit = async (e: React.FormEvent) => {
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

  const handleForgotSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    setLoading(true);
    try {
      await authAPI.forgotPassword(email);
      setSuccessMsg('If an account exists with this email, a password recovery link has been sent.');
      setEmail('');
    } catch (err: unknown) {
      // Don't leak whether email exists
      setSuccessMsg('If an account exists with this email, a password recovery link has been sent.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface text-on-surface relative overflow-hidden flex items-center justify-center p-6 font-sans">
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

      <style>{`
        @keyframes loginEntrance {
          0% {
            opacity: 0;
            transform: translateY(10px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
      <div
        className="relative z-10 w-full md:w-[520px] max-w-[calc(100vw-32px)] md:max-w-[calc(100vw-48px)] mx-auto"
        style={{
          animation: "loginEntrance 700ms ease-out forwards",
        }}
      >
        <Card variant="glass" className="p-[24px] md:p-[32px] rounded-[18px] border border-[#ADFF00]/20 shadow-[0_0_30px_rgba(173,255,0,0.12)]">

          <div className="flex flex-col items-center text-center" style={{ marginBottom: "36px" }}>
            <div className="relative mb-[14px] flex items-center justify-center">
              <div className="absolute inset-0 bg-[#ADFF00]/20 blur-xl rounded-full" />
              <div className="relative w-[68px] h-[68px] md:w-[72px] md:h-[72px] rounded-2xl bg-surface-container border border-neon-mint/30 flex items-center justify-center p-2">
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

            <Badge variant="ai" pulse className="text-[12px] tracking-[0.08em] px-[12px] py-[7px] rounded-full" style={{ marginBottom: "28px" }}>
              SYSTEM AUTHENTICATION
            </Badge>

            <h1 className="text-[38px] font-[700] md:font-[800] leading-[1.1] text-[#ADFF00] tracking-[-0.025em] text-center mb-[6px]" style={{ marginTop: "12px" }}>
              {mode === 'login' ? 'Agrinova AI' : 'Recover Access'}
            </h1>
            {mode === 'login' && (
              <h2 className="text-[22px] font-[500] md:font-[600] leading-[1.2] text-[#E5E7E5] tracking-normal text-center mb-[16px]">
                Sign In
              </h2>
            )}
            <p className="text-[16px] leading-[1.4] text-on-surface-variant max-w-[380px] text-center mx-auto">
              {mode === 'login'
                ? 'Access precision telemetry and AI-driven environmental control.'
                : 'Enter your email address to receive a secure recovery link.'}
            </p>
          </div>

          {error && (
            <div className="p-3 mb-6 rounded-xl bg-error/10 border border-error/30 text-error text-sm flex items-center gap-2">
              <ShieldCheck size={16} strokeWidth={1.75} />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="p-3 mb-6 rounded-xl bg-neon-mint/10 border border-neon-mint/30 text-neon-mint text-sm flex items-start gap-2">
              <ShieldCheck size={16} strokeWidth={1.75} className="mt-0.5 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {mode === 'login' ? (
            <form onSubmit={handleLoginSubmit} className="flex flex-col gap-[20px]">
              <div className="flex flex-col" style={{ gap: "8px" }}>
                <label htmlFor="email" className="font-mono text-[13px] font-medium tracking-[0.10em] uppercase text-on-surface-variant block leading-[18px]">
                  WORK EMAIL ADDRESS
                </label>
                <div className="relative flex items-center">
                  <Mail size={20} strokeWidth={1.75} className="absolute left-[16px] top-1/2 -translate-y-1/2 text-on-surface-variant" />
                  <Input
                    id="email"
                    type="email"
                    variant="lens"
                    placeholder="agronomist@agrinova.ai"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full h-[52px] md:h-[54px] rounded-[10px] text-[16px] leading-[1.4]"
                    style={{ paddingLeft: "46px", paddingRight: "16px" }}
                  />
                </div>
              </div>

              <div className="flex flex-col" style={{ gap: "8px" }}>
                <div className="flex justify-between items-center h-[18px]">
                  <label htmlFor="password" className="font-mono text-[13px] font-medium tracking-[0.10em] uppercase text-on-surface-variant leading-[18px]">
                    PASSCODE
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setMode('forgot_password');
                      setError('');
                      setSuccessMsg('');
                    }}
                    className="font-mono text-[13px] font-medium tracking-[0.10em] uppercase text-[#ADFF00] hover:underline text-decoration-none"
                  >
                    FORGOT?
                  </button>
                </div>
                <div className="relative flex items-center">
                  <Lock size={20} strokeWidth={1.75} className="absolute left-[16px] top-1/2 -translate-y-1/2 text-on-surface-variant" />
                  <Input
                    id="password"
                    type="password"
                    variant="lens"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength={8}
                    className="w-full h-[52px] md:h-[54px] rounded-[10px] text-[16px] leading-[1.4]"
                    style={{ paddingLeft: "46px", paddingRight: "16px" }}
                  />
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={loading}
                className="w-full h-[54px] md:h-[56px] rounded-[10px] text-[17px] font-[600] md:font-[700]"
                icon={<ArrowRight size={18} strokeWidth={1.75} />}
              >
                INITIALIZE SESSION
              </Button>
            </form>
          ) : (
            <form onSubmit={handleForgotSubmit} className="flex flex-col gap-[20px]">
              <div className="flex flex-col" style={{ gap: "8px" }}>
                <label htmlFor="reset-email" className="font-mono text-[13px] font-medium tracking-[0.10em] uppercase text-on-surface-variant block leading-[18px]">
                  WORK EMAIL ADDRESS
                </label>
                <div className="relative flex items-center">
                  <Mail size={20} strokeWidth={1.75} className="absolute left-[16px] top-1/2 -translate-y-1/2 text-on-surface-variant" />
                  <Input
                    id="reset-email"
                    type="email"
                    variant="lens"
                    placeholder="agronomist@agrinova.ai"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full h-[52px] md:h-[54px] rounded-[10px] text-[16px] leading-[1.4]"
                    style={{ paddingLeft: "46px", paddingRight: "16px" }}
                  />
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={loading}
                className="w-full h-[54px] md:h-[56px] rounded-[10px] text-[17px] font-[600] md:font-[700]"
              >
                SEND RECOVERY LINK
              </Button>

              <button
                type="button"
                onClick={() => {
                  setMode('login');
                  setError('');
                  setSuccessMsg('');
                }}
                className="w-full mt-4 flex items-center justify-center gap-2 type-label-caps text-[11px] text-on-surface-variant hover:text-white transition-colors"
              >
                <ArrowLeft size={14} strokeWidth={1.75} />
                BACK TO SIGN IN
              </button>
            </form>
          )}

          {mode === 'login' && (
            <div className="flex items-center justify-between" style={{ marginTop: "24px" }}>
              <span className="font-mono text-[13px] leading-[18px] tracking-[0.08em] text-on-surface-variant opacity-60 uppercase">
                NEW AGRO-OPERATOR?
              </span>
              <Link
                href="/register"
                className="font-mono text-[13px] leading-[18px] tracking-[0.08em] text-[#ADFF00] font-bold hover:underline text-decoration-none flex items-center gap-1 uppercase"
              >
                <KeyRound size={14} strokeWidth={1.75} />
                CREATE ACCOUNT
              </Link>
            </div>
          )}
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
