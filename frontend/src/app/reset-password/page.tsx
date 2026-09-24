'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { authAPI } from '@/lib/api';
import Background from '@/background/Background/Background';
import { Button, Card, Badge, Input } from '@/ui';
import { Lock, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      setError('Invalid or missing recovery token. Please request a new password reset link.');
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await authAPI.resetPassword({ token, new_password: password });
      setSuccess(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
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

      <div className="relative z-10 w-full max-w-md">
        <Card variant="glass" className="p-8 md:p-10 rounded-3xl border border-[#ADFF00]/20 shadow-[0_0_30px_rgba(173,255,0,0.12)]">

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

            <Badge variant="ai" pulse={!success} className="mb-3">
              SYSTEM AUTHENTICATION
            </Badge>

            <h1 className="type-headline-md mb-2">
              {success ? 'Password Updated' : 'Create New Password'}
            </h1>
            <p className="type-body-sm text-on-surface-variant max-w-xs">
              {success
                ? 'Your authentication credentials have been successfully updated.'
                : 'Please enter your new access credentials.'}
            </p>
          </div>

          {error && (
            <div className="p-3 mb-6 rounded-xl bg-error/10 border border-error/30 text-error text-sm flex items-center gap-2">
              <ShieldCheck size={16} strokeWidth={1.75} />
              <span>{error}</span>
            </div>
          )}

          {success ? (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-neon-mint/20 flex items-center justify-center mb-6 text-neon-mint">
                <CheckCircle2 size={32} />
              </div>
              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={() => router.push('/login')}
                icon={<ArrowRight size={18} strokeWidth={1.75} />}
              >
                RETURN TO SIGN IN
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="password" className="type-label-caps text-[11px] text-on-surface-variant block mb-2">
                  NEW PASSCODE
                </label>
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
                    disabled={!token}
                    style={{ paddingLeft: '44px' }}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="confirmPassword" className="type-label-caps text-[11px] text-on-surface-variant block mb-2">
                  CONFIRM NEW PASSCODE
                </label>
                <div className="relative flex items-center">
                  <Lock size={18} strokeWidth={1.75} className="absolute left-4 text-on-surface-variant" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    variant="lens"
                    placeholder="••••••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    minLength={8}
                    disabled={!token}
                    style={{ paddingLeft: '44px' }}
                  />
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={loading}
                disabled={!token}
                className="w-full mt-2"
                icon={<ArrowRight size={18} strokeWidth={1.75} />}
              >
                RESET PASSWORD
              </Button>

              <div className="mt-4 text-center">
                <Link href="/login" className="type-label-caps text-[10px] text-on-surface-variant hover:text-white transition-colors">
                  CANCEL
                </Link>
              </div>
            </form>
          )}
        </Card>
      </div>
    </div>
  );
}
