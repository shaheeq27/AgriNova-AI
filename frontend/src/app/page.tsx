'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { SeedShaderCanvas } from '@/background/Background/SeedShaderCanvas';

export default function WelcomePage() {
  const router = useRouter();
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    // Start exit transition at 7.2s
    const exitTimer = setTimeout(() => {
      setIsExiting(true);
    }, 7200);

    // Complete route transition at 8.0s (8 seconds total)
    const redirectTimer = setTimeout(() => {
      router.push('/login');
    }, 8000);

    return () => {
      clearTimeout(exitTimer);
      clearTimeout(redirectTimer);
    };
  }, [router]);

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        backgroundColor: '#030A04',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
      }}
    >
      <style>{`
        @keyframes auraBloom {
          0% {
            opacity: 0;
            transform: scale(0.65);
          }
          100% {
            opacity: 0.55;
            transform: scale(1);
          }
        }

        @keyframes logoEntranceSmooth {
          0% {
            opacity: 0;
            transform: translate3d(0, 36px, 0) scale(0.82);
            filter: drop-shadow(0 0 0px rgba(173, 255, 0, 0));
          }
          100% {
            opacity: 1;
            transform: translate3d(0, 0, 0) scale(1);
            filter: drop-shadow(0 0 16px rgba(173, 255, 0, 0.45));
          }
        }

        @keyframes floatSineSmooth {
          0% {
            transform: translate3d(0, 0, 0) scale(1);
            filter: drop-shadow(0 0 12px rgba(173, 255, 0, 0.35));
          }
          50% {
            transform: translate3d(0, -8px, 0) scale(1.02);
            filter: drop-shadow(0 0 22px rgba(173, 255, 0, 0.55));
          }
          100% {
            transform: translate3d(0, 0, 0) scale(1);
            filter: drop-shadow(0 0 12px rgba(173, 255, 0, 0.35));
          }
        }

        @keyframes textEntranceBlur {
          0% {
            opacity: 0;
            transform: translate3d(0, 24px, 0);
            filter: blur(10px);
          }
          100% {
            opacity: 1;
            transform: translate3d(0, 0, 0);
            filter: blur(0px);
          }
        }

        .welcome-aura {
          animation: auraBloom 1.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          will-change: transform, opacity;
        }

        .welcome-logo-wrapper {
          animation: logoEntranceSmooth 1.3s cubic-bezier(0.2, 0.9, 0.2, 1) forwards,
                     floatSineSmooth 5.5s ease-in-out 1.3s infinite;
          will-change: transform, opacity, filter;
        }

        .welcome-title-wrapper {
          animation: textEntranceBlur 1.1s cubic-bezier(0.2, 0.9, 0.2, 1) 0.35s forwards;
          will-change: transform, opacity, filter;
          opacity: 0;
        }

        .welcome-content-container {
          transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1),
                      opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1),
                      filter 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .welcome-content-exiting {
          opacity: 0 !important;
          transition: opacity 800ms ease-in-out !important;
        }

        .welcome-overlay-fade {
          position: fixed;
          inset: 0;
          background: #030A04; /* Keep the exact dark-green background */
          z-index: 100;
          pointer-events: none;
          opacity: 0;
          transition: opacity 800ms ease-in-out;
        }

        .welcome-overlay-fade-active {
          opacity: 1;
        }
      `}</style>

      {/* WebGL Seed Particles Canvas */}
      <SeedShaderCanvas isWelcomeMode={true} />

      {/* Dark Forest Curtain Dissolve Overlay for Transition to Dashboard */}
      <div
        className={`welcome-overlay-fade ${
          isExiting ? 'welcome-overlay-fade-active' : ''
        }`}
      />

      {/* Centered Content Container */}
      <div
        className={`welcome-content-container ${
          isExiting ? 'welcome-content-exiting' : ''
        }`}
        style={{
          position: 'relative',
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '24px',
          padding: '24px',
          textAlign: 'center',
        }}
      >
        {/* Soft Radial Neon Glow Aura */}
        <div
          className="welcome-aura"
          style={{
            position: 'absolute',
            width: '420px',
            height: '420px',
            background:
              'radial-gradient(circle, rgba(173, 255, 0, 0.18) 0%, rgba(34, 197, 94, 0.08) 50%, transparent 75%)',
            filter: 'blur(50px)',
            borderRadius: '50%',
            pointerEvents: 'none',
          }}
        />

        {/* Animated Logo Subject */}
        <div
          className="welcome-logo-wrapper"
          style={{
            position: 'relative',
            width: 'min(310px, 70vw)',
            height: 'min(310px, 70vw)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Image
            src="/logo_transparent.png"
            alt="AgriNova AI Glowing Leaf Circuit Logo"
            width={310}
            height={310}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'contain',
            }}
            priority
          />
        </div>

        {/* AgriNova AI Title & Tagline below Logo */}
        <div className="welcome-title-wrapper" style={{ position: 'relative', zIndex: 12 }}>
          <h1
            style={{
              fontSize: 'min(44px, 10vw)',
              fontWeight: 800,
              fontFamily: '"Source Serif 4", "Playfair Display", serif',
              letterSpacing: '0.03em',
              margin: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '2px',
              textShadow: '0 0 20px rgba(0,0,0,0.8)',
            }}
          >
            {/* Agri in Light Green */}
            <span style={{ color: '#ADFF00' }}>Agri</span>
            {/* Nova in Gold */}
            <span style={{ color: '#FFD700' }}>Nova</span>
            {/* AI Badge */}
            <span
              style={{
                fontFamily: '"JetBrains Mono", "Space Mono", monospace',
                fontSize: 'min(24px, 5vw)',
                fontWeight: 700,
                color: '#E0F2F1',
                background: 'rgba(173, 255, 0, 0.12)',
                border: '1px solid rgba(173, 255, 0, 0.35)',
                padding: '2px 10px',
                borderRadius: '8px',
                marginLeft: '12px',
                letterSpacing: '0.1em',
                boxShadow: '0 0 12px rgba(173, 255, 0, 0.25)',
              }}
            >
              AI
            </span>
          </h1>

          <p
            style={{
              fontSize: '13px',
              color: 'rgba(228, 226, 224, 0.75)',
              fontFamily: '"JetBrains Mono", monospace',
              letterSpacing: '0.18em',
              textTransform: 'uppercase',
              marginTop: '12px',
            }}
          >
            Where Nature Meets Technology
          </p>
        </div>
      </div>
    </div>
  );
}
