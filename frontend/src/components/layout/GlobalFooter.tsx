'use client';

import React, { useRef, useState, useEffect } from 'react';
import Link from 'next/link';
import { Leaf, Code, Globe, Mail } from 'lucide-react';
import styles from './GlobalFooter.module.css';
import { DEVELOPER_CONFIG } from '@/config/developer.config';

export default function GlobalFooter() {
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

  return (
    <>
      <div className={styles.footerTrigger} />
      <footer
        ref={footerRef}
        className={`${styles.footer} ${footerVisible ? styles.footerVisible : ''}`}
      >
        <div className={styles.footerGrid}>
          {/* 1. AgriNova Brand Column */}
          <div className={styles.brandColumn}>
            <div className={styles.brandLogo}>
              <Leaf size={22} className={styles.brandIcon} />
              <h2 className={styles.brandTitle}>AgriNova</h2>
            </div>
            <p className={styles.brandTagline}>Where Nature Meets Technology</p>
            <p className={styles.brandDesc}>
              AI-powered intelligence for smarter, data-driven farming.
            </p>
          </div>

          {/* 2. Platform Column */}
          <div className={styles.column}>
            <h3 className={styles.columnHeading}>PLATFORM</h3>
            <div className={styles.linkList}>
              <Link href="/home" className={styles.linkItem}>Home</Link>
              <Link href="/dashboard" className={styles.linkItem}>Dashboard</Link>
              <Link href="/farms" className={styles.linkItem}>My Farms</Link>
              <Link href="/advisor" className={styles.linkItem}>Crop Advisor</Link>
              <Link href="/weather" className={styles.linkItem}>Weather</Link>
              <Link href="/timeline" className={styles.linkItem}>Timeline</Link>
            </div>
          </div>

          {/* 3. Resources Column */}
          <div className={styles.column}>
            <h3 className={styles.columnHeading}>RESOURCES</h3>
            <div className={styles.linkList}>
              <Link href="/knowledge" className={styles.linkItem}>Knowledge Base</Link>
              <Link href="/market" className={styles.linkItem}>Market</Link>
              <Link href="/aira" className={styles.linkItem}>Aira</Link>
              <Link href="/settings" className={styles.linkItem}>Settings</Link>
            </div>
          </div>

          {/* 4. Developer Column */}
          <div className={styles.developerColumn}>
            <h3 className={styles.columnHeading}>DEVELOPER</h3>
            <div className={styles.developedByRow}>
              <span className={styles.devLabel}>Developed by</span>
              <span className={styles.devName}>{DEVELOPER_CONFIG.name}</span>
            </div>
            <p className={styles.devDesc}>
              Building AgriNova — an AI-powered precision agriculture platform.
            </p>
            <div className={styles.socialRow}>
              <a
                href={DEVELOPER_CONFIG.github}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.socialBtn}
                aria-label="GitHub Profile"
              >
                <Code size={18} />
              </a>
              <a
                href={DEVELOPER_CONFIG.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.socialBtn}
                aria-label="LinkedIn Profile"
              >
                <Globe size={18} />
              </a>
              <a
                href={DEVELOPER_CONFIG.email}
                className={styles.socialBtn}
                aria-label="Email Developer"
              >
                <Mail size={18} />
              </a>
            </div>
          </div>
        </div>

        {/* 6. Footer Divider */}
        <div className={styles.divider} />

        {/* 7. Bottom Footer Row */}
        <div className={styles.bottomRow}>
          <p className={styles.copyright}>
            &copy; {new Date().getFullYear()} AgriNova AI. All rights reserved.
          </p>
          <div className={styles.legalLinks}>
            <Link href="#">Privacy Policy</Link>
            <Link href="#">Terms of Service</Link>
            <Link href="#">Contact Support</Link>
          </div>
        </div>
      </footer>
    </>
  );
}
