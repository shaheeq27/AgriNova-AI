'use client';

import React, { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import {
  ArrowRight,
  Play,
  Droplets,
  Thermometer,
  Leaf,
  TrendingUp,
  Sprout,
  ShieldCheck,
  MapPin,
  Cloud,
  BarChart3,
  ChevronDown,
  ArrowUpRight,
  MessageSquare,
} from 'lucide-react';
import { farmAPI } from '@/lib/api';
import styles from './page.module.css';

/* ───────── Types ───────── */
interface FarmCrop {
  crop_name: string;
  status?: string;
}

interface Farm {
  id: string;
  name: string;
  crops?: FarmCrop[];
  total_area_acres?: number;
}

/* ───────── Feature Data ───────── */
const FEATURES = [
  {
    icon: Sprout,
    title: 'Crop Advisory',
    desc: 'Get personalized crop recommendations based on your soil, climate and goals.',
    href: '/advisor',
  },
  {
    icon: ShieldCheck,
    title: 'Disease Detection',
    desc: 'Identify crop diseases instantly using AI and image analysis.',
    href: '/detect',
  },
  {
    icon: MapPin,
    title: 'Farm Management',
    desc: 'Track your farms, monitor crop health, and manage activities with ease.',
    href: '/farms',
  },
  {
    icon: Cloud,
    title: 'Weather Insights',
    desc: 'Stay ahead with real-time weather updates and intelligent alerts.',
    href: '/weather',
  },
  {
    icon: TrendingUp,
    title: 'Market Intelligence',
    desc: 'Get live market prices and trends for better selling decisions.',
    href: '/market',
  },
];

/* ───────── Aira Questions ───────── */
const AIRA_QUESTIONS = [
  'What crops are best for my soil?',
  'Is my plant showing signs of disease?',
  "What's the market price for tomatoes?",
  'Give me a farming tip for this season.',
];

/* ───────── Page Component ───────── */
export default function HomePage() {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loadingFarms, setLoadingFarms] = useState(true);

  const footerRef = useRef<HTMLElement>(null);
  const [footerVisible, setFooterVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setFooterVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    if (footerRef.current) {
      observer.observe(footerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    let mounted = true;
    farmAPI
      .list()
      .then((data: { farms?: Farm[] }) => {
        if (mounted && data.farms) {
          setFarms(data.farms);
        }
      })
      .catch(() => {
        // Silent — show 0 in metrics
      })
      .finally(() => {
        if (mounted) setLoadingFarms(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const totalFarms = farms.length;
  const cropsTracked = farms.reduce(
    (sum, f) => sum + (f.crops?.length || 0),
    0
  );

  return (
    <div className={styles.page}>
      {/* ═══════════ HERO ═══════════ */}
      <section className={styles.hero}>
        {/* Left — Text */}
        <div className={styles.heroText}>
          <p className={styles.tagline}>
            Where <span className={styles.taglineAccent}>Nature</span> Meets <span className={styles.taglineAccent}>Technology</span>
          </p>
          <h1 className={styles.heroHeading}>
            Smarter Farming
            <br />
            <span className={styles.heroHeadingAccent}>Starts Here.</span>
          </h1>
          <p className={styles.heroDescription}>
            AgriNova combines AI, real-world data, and agricultural insights to
            help you make better decisions, healthier crops, and higher yields
            — for a more sustainable future.
          </p>
          <div className={styles.heroCtas}>
            <Link href="/advisor" className={styles.ctaPrimary}>
              Get Crop Recommendations
              <ArrowRight size={16} strokeWidth={2} />
            </Link>
            <button type="button" className={styles.ctaSecondary}>
              <Play size={16} strokeWidth={2} />
              Watch How It Works
            </button>
          </div>
        </div>

        {/* Right — Visual */}
        <div className={styles.heroVisual}>
          {/* Crop Image */}
          <div className={styles.heroCropContainer}>
            <img src="/hero-crop.png" alt="Agriculture crop" className={styles.heroCropImage} />
            
            {/* Butterflies */}
            <div className={`${styles.butterfly} ${styles.butterfly1}`}>
              <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g className={styles.wingLeft} transform-origin="16 16">
                  <path d="M15 14C10 8 4 6 4 14C4 18 10 20 15 16Z" fill="#FDB813" />
                  <path d="M14 16C10 18 7 22 9 26C11 28 14 24 15 20Z" fill="#D47A11" />
                </g>
                <g className={styles.wingRight} transform-origin="16 16">
                  <path d="M17 14C22 8 28 6 28 14C28 18 22 20 17 16Z" fill="#FDB813" />
                  <path d="M18 16C22 18 25 22 23 26C21 28 18 24 17 20Z" fill="#D47A11" />
                </g>
                <path d="M15 12C15 10 17 10 17 12C17 15 16.5 22 16 22C15.5 22 15 15 15 12Z" fill="#4A3018" />
              </svg>
            </div>
            <div className={`${styles.butterfly} ${styles.butterfly2}`}>
              <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g className={styles.wingLeft} transform-origin="16 16">
                  <path d="M15 14C10 8 4 6 4 14C4 18 10 20 15 16Z" fill="#FDB813" />
                  <path d="M14 16C10 18 7 22 9 26C11 28 14 24 15 20Z" fill="#D47A11" />
                </g>
                <g className={styles.wingRight} transform-origin="16 16">
                  <path d="M17 14C22 8 28 6 28 14C28 18 22 20 17 16Z" fill="#FDB813" />
                  <path d="M18 16C22 18 25 22 23 26C21 28 18 24 17 20Z" fill="#D47A11" />
                </g>
                <path d="M15 12C15 10 17 10 17 12C17 15 16.5 22 16 22C15.5 22 15 15 15 12Z" fill="#4A3018" />
              </svg>
            </div>
            <div className={`${styles.butterfly} ${styles.butterfly3}`}>
              <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g className={styles.wingLeft} transform-origin="16 16">
                  <path d="M15 14C10 8 4 6 4 14C4 18 10 20 15 16Z" fill="#FDB813" />
                  <path d="M14 16C10 18 7 22 9 26C11 28 14 24 15 20Z" fill="#D47A11" />
                </g>
                <g className={styles.wingRight} transform-origin="16 16">
                  <path d="M17 14C22 8 28 6 28 14C28 18 22 20 17 16Z" fill="#FDB813" />
                  <path d="M18 16C22 18 25 22 23 26C21 28 18 24 17 20Z" fill="#D47A11" />
                </g>
                <path d="M15 12C15 10 17 10 17 12C17 15 16.5 22 16 22C15.5 22 15 15 15 12Z" fill="#4A3018" />
              </svg>
            </div>
          </div>

          {/* Floating Info Cards */}
          <div className={`${styles.infoCard} ${styles.cardSoilMoisture}`}>
            <Droplets size={16} className={styles.infoCardIcon} />
            <div className={styles.infoCardContent}>
              <span className={styles.infoCardLabel}>Soil Moisture</span>
              <span className={styles.infoCardValue}>68%</span>
            </div>
          </div>

          <div className={`${styles.infoCard} ${styles.cardTemperature}`}>
            <Thermometer size={16} className={styles.infoCardIcon} />
            <div className={styles.infoCardContent}>
              <span className={styles.infoCardLabel}>Temperature</span>
              <span className={styles.infoCardValue}>24°C</span>
            </div>
          </div>

          <div className={`${styles.infoCard} ${styles.cardCropHealth}`}>
            <Leaf size={16} className={styles.infoCardIcon} />
            <div className={styles.infoCardContent}>
              <span className={styles.infoCardLabel}>Crop Health</span>
              <span className={styles.infoCardValue}>Good</span>
            </div>
          </div>

          <div className={`${styles.infoCard} ${styles.cardExpectedYield}`}>
            <TrendingUp size={16} className={styles.infoCardIcon} />
            <div className={styles.infoCardContent}>
              <span className={styles.infoCardLabel}>Expected Yield</span>
              <span className={styles.infoCardValue}>+22%</span>
            </div>
          </div>

          {/* Decorative cursive text */}
          <div className={styles.decorativeText}>
            Better
            <br />
            Crops
            <br />
            Brighter
            <br />
            Tomorrows
          </div>
        </div>
      </section>

      {/* ═══════════ EXPLORE AGRINOVA ═══════════ */}
      <section className={styles.section} id="features">
        <div className={styles.sectionHeader}>
          <div className={styles.sectionHeaderLeft}>
            <h2 className={styles.sectionTitle}>Explore AgriNova</h2>
            <p className={styles.sectionSubtitle}>
              Everything you need for modern, data-driven farming.
            </p>
          </div>
          <Link 
            href="#features" 
            className={styles.sectionLink}
            onClick={(e) => {
              e.preventDefault();
              document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            View All Features
            <ArrowRight size={14} strokeWidth={2} />
          </Link>
        </div>

        <div className={styles.featureGrid}>
          {FEATURES.map((feature) => (
            <Link
              key={feature.href}
              href={feature.href}
              className={styles.featureCard}
            >
              <div className={styles.featureIconWrap}>
                <feature.icon size={20} strokeWidth={1.75} />
              </div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDesc}>{feature.desc}</p>
              <div className={styles.featureArrow}>
                <ArrowUpRight size={14} strokeWidth={2} />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ═══════════ YOUR FARM AT A GLANCE ═══════════ */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionHeaderLeft}>
            <h2 className={styles.sectionTitle}>Your Farm at a Glance</h2>
            <p className={styles.sectionSubtitle}>
              Key insights across all your farms.
            </p>
          </div>
          <div className={styles.farmDropdown}>
            All Farms
            <ChevronDown size={14} strokeWidth={2} />
          </div>
        </div>

        <div className={styles.metricsGrid}>
          {/* Total Farms */}
          <div className={styles.metricCard}>
            <div className={styles.metricIconWrap}>
              <Sprout size={22} strokeWidth={1.75} />
            </div>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>
                {loadingFarms ? '—' : totalFarms}
              </span>
              <span className={styles.metricLabel}>Total Farms</span>
            </div>
            <Link href="/farms" className={styles.metricViewLink}>
              View <ArrowRight size={12} strokeWidth={2} />
            </Link>
          </div>

          {/* Crops Tracked */}
          <div className={styles.metricCard}>
            <div className={styles.metricIconWrap}>
              <Leaf size={22} strokeWidth={1.75} />
            </div>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>
                {loadingFarms ? '—' : cropsTracked}
              </span>
              <span className={styles.metricLabel}>Crops Tracked</span>
            </div>
            <Link href="/farms" className={styles.metricViewLink}>
              View <ArrowRight size={12} strokeWidth={2} />
            </Link>
          </div>

          {/* Avg. Yield Increase */}
          <div className={styles.metricCard}>
            <div className={styles.metricIconWrap}>
              <BarChart3 size={22} strokeWidth={1.75} />
            </div>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>+18%</span>
              <span className={styles.metricLabel}>Avg. Yield Increase</span>
            </div>
            <Link href="/farms" className={styles.metricViewLink}>
              View <ArrowRight size={12} strokeWidth={2} />
            </Link>
          </div>

          {/* Overall Conditions */}
          <div className={styles.metricCard}>
            <div className={styles.metricIconWrap}>
              <Cloud size={22} strokeWidth={1.75} />
            </div>
            <div className={styles.metricContent}>
              <span className={styles.metricValue}>Good</span>
              <span className={styles.metricLabel}>Overall Conditions</span>
            </div>
            <Link href="/dashboard" className={styles.metricViewLink}>
              View <ArrowRight size={12} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>

      {/* ═══════════ MEET AIRA ═══════════ */}
      <section className={styles.section}>
        <div className={styles.airaSection}>
          <p className={styles.eyebrow}>Meet Aira</p>
          <h2 className={styles.sectionTitle}>Your AI Farming Assistant</h2>
          <div className={styles.airaContent}>
            <p className={styles.airaDescription}>
              Ask questions, get insights, and make better farming decisions —
              anytime, anywhere.
            </p>
            <div className={styles.airaChips}>
              {AIRA_QUESTIONS.map((q) => (
                <Link key={q} href="/aira" className={styles.airaChip}>
                  <MessageSquare size={12} strokeWidth={1.75} />
                  {q}
                </Link>
              ))}
            </div>
            <div className={styles.airaCtaRow}>
              <Link href="/aira" className={styles.ctaPrimary}>
                Open Aira
                <ArrowRight size={16} strokeWidth={2} />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ FOOTER ═══════════ */}
      <div className={styles.footerTrigger} />
      <footer 
        ref={footerRef} 
        className={`${styles.footer} ${footerVisible ? styles.footerVisible : ''}`}
      >
        <div className={styles.footerContent}>
          <div className={styles.footerLeft}>
            <div className={styles.footerLogo}>
              <Leaf size={18} className={styles.footerLogoIcon} />
              <span className={styles.footerLogoText}>AgriNova</span>
            </div>
            <p className={styles.footerTagline}>Where Nature Meets Technology</p>
          </div>
          <div className={styles.footerRight}>
            <div className={styles.footerLinks}>
              <Link href="#">Privacy Policy</Link>
              <Link href="#">Terms of Service</Link>
              <Link href="#">Contact Support</Link>
            </div>
            <p className={styles.footerCopyright}>&copy; {new Date().getFullYear()} AgriNova AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
