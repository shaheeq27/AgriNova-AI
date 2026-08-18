'use client';

import React from 'react';
import Image from 'next/image';
import { Search, Bell, Sprout } from 'lucide-react';
import styles from './FarmHeader.module.css';

interface FarmHeaderProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export function FarmHeader({ searchQuery, onSearchChange }: FarmHeaderProps) {
  return (
    <>
      {/* Top Action Bar (Search, Bell, Profile Avatar) */}
      <div className={styles.headerActions}>
        <div className={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search farms..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className={styles.searchInput}
          />
          <Search size={16} className={styles.searchIcon} />
        </div>

        <button className={styles.iconButton} aria-label="Notifications">
          <Bell size={18} />
          <span className={styles.notificationDot} />
        </button>

        <div className={styles.avatar}>N</div>
      </div>

      {/* Page Title & Introduction Banner with Farmhouse Image */}
      <div className={styles.titleBanner}>
        {/* Left: Text Content */}
        <div className={styles.titleContent}>
          <div className={styles.titleRow}>
            <Sprout size={28} className={styles.sproutIcon} />
            <h1 className={styles.titleText}>My Farms</h1>
          </div>
          <p className={styles.description}>
            Manage all your agricultural lands from one place. Register new farms, organize your
            fields, and monitor every farm throughout its lifecycle.
          </p>
        </div>

        {/* Right: Decorative Farmhouse Landscape Image */}
        <div className={styles.bannerImageWrapper}>
          <Image
            src="/agri-background.png"
            alt="Farmhouse Landscape"
            fill
            unoptimized
            aria-hidden="true"
            className={styles.bannerImage}
            priority
          />
          {/* Gradient overlay — fades image into the dark background on the left */}
          <div className={styles.bannerImageOverlay} />
        </div>
      </div>
    </>
  );
}

export default FarmHeader;
