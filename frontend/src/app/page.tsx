'use client';

import React from 'react';
import Link from 'next/link';
import Background from '@/background/Background/Background';
import LogoFloat from '@/effects/LogoFloat/LogoFloat';
import AuraPulse from '@/effects/AuraPulse/AuraPulse';
import FadeIn from '@/effects/FadeIn/FadeIn';
import SlideIn from '@/effects/SlideIn/SlideIn';
import PrimaryButton from '@/components/buttons/PrimaryButton';
import SecondaryButton from '@/components/buttons/SecondaryButton';
import Logo from '@/components/common/Logo';

export default function LandingPage() {
  return (
    <main
      style={{
        position: 'relative',
        minHeight: '100vh',
        width: '100vw',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        overflow: 'hidden',
      }}
    >
      {/* Step 10: Living Background with Fireflies, Ground Glow, Spores, Fog, Shader, Noise */}
      <Background
        shader={true}
        fog={true}
        groundGlow={true}
        noise={true}
        fireflies={true}
        fireflyCount={18}
        seeds={true}
        seedCount={20}
      />

      <div
        style={{
          position: 'relative',
          zIndex: 10,
          maxWidth: '720px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '24px',
        }}
      >
        {/* Step 10: Floating logo & Aura */}
        <FadeIn delay={100}>
          <AuraPulse size={140} color="rgba(78, 232, 106, 0.3)">
            <LogoFloat distance={14} duration={5}>
              <Logo size="lg" showGlow />
            </LogoFloat>
          </AuraPulse>
        </FadeIn>

        {/* Header & Tagline */}
        <SlideIn direction="up" delay={300}>
          <h1
            style={{
              fontFamily: 'var(--font-playfair)',
              fontSize: 'clamp(2.5rem, 6vw, 4.2rem)',
              fontWeight: 700,
              lineHeight: 1.15,
              background: 'linear-gradient(180deg, #FFFFFF 0%, #A8C4B0 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              margin: 0,
            }}
          >
            AgriNova AI
          </h1>
          <p
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '14px',
              letterSpacing: '0.15em',
              textTransform: 'uppercase',
              color: 'var(--color-accent)',
              marginTop: '12px',
            }}
          >
            Where Nature Meets Intelligence
          </p>
        </SlideIn>

        <SlideIn direction="up" delay={500}>
          <p
            style={{
              fontFamily: 'var(--font-inter)',
              fontSize: '17px',
              lineHeight: 1.6,
              color: 'var(--color-text-secondary)',
              maxWidth: '560px',
              margin: '0 auto',
            }}
          >
            An AI-powered precision agriculture OS guiding farmers through every stage of the crop lifecycle — from seed selection to yield optimization.
          </p>
        </SlideIn>

        {/* CTA Buttons */}
        <SlideIn direction="up" delay={700}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '16px',
              marginTop: '12px',
              flexWrap: 'wrap',
            }}
          >
            <Link href="/dashboard" style={{ textDecoration: 'none' }}>
              <PrimaryButton size="lg">
                Enter Platform
              </PrimaryButton>
            </Link>
            <Link href="/login" style={{ textDecoration: 'none' }}>
              <SecondaryButton size="lg">
                Sign In
              </SecondaryButton>
            </Link>
          </div>
        </SlideIn>

        {/* Telemetry Footer */}
        <FadeIn delay={900}>
          <div
            style={{
              marginTop: '40px',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--color-text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
            }}
          >
            <span>PLATFORM V1.1</span>
            <span>•</span>
            <span>SYSTEM OPTIMAL</span>
            <span>•</span>
            <span>SECURED BY AI</span>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}
