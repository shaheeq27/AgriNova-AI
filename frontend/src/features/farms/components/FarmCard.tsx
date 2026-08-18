'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { MapPin, Sprout, ChevronRight, Compass } from 'lucide-react';
import { Farm } from '../types';
import { FarmsService } from '../services/farms.service';
import styles from './FarmCard.module.css';

interface FarmCardProps {
  farm: Farm;
  index: number;
}

export function FarmCard({ farm, index }: FarmCardProps) {
  const hasCrop = farm.crops && farm.crops.length > 0;
  const activeCrop = hasCrop ? farm.crops![0] : null;

  const bannerImage =
    farm.bannerImage ||
    (index % 3 === 0 ? '/farm_1.jpg' : index % 3 === 1 ? '/farm_2.jpg' : '/farm_3.jpg');

  const stageName = farm.stageName || (hasCrop ? 'Vegetative Stage' : undefined);
  const defaultDay = farm.defaultDay || 60;

  const { currentDay, totalDays } = FarmsService.calculateCropDays(
    undefined,
    activeCrop?.crop_name,
    defaultDay
  );

  return (
    <div className={styles.card}>
      <div>
        {/* Top Image Banner */}
        <div className={styles.bannerWrapper}>
          <Image
            src={bannerImage}
            alt={farm.name}
            fill
            className={styles.bannerImage}
          />
          <div className={styles.bannerOverlay} />

          {/* Active / Idle Badge */}
          {hasCrop ? (
            <span className={styles.badgeActive}>Active</span>
          ) : (
            <span className={styles.badgeIdle}>Idle</span>
          )}
        </div>

        {/* Card Body */}
        <div className={styles.cardBody}>
          <h3 className={styles.farmTitle}>
            <Sprout size={20} className={styles.sproutIcon} />
            {farm.name}
          </h3>
          <p className={styles.location}>
            <MapPin size={13} />
            {farm.location_city}
            {farm.location_state ? `, ${farm.location_state}` : ''}
          </p>

          <div className={styles.divider} />

          {/* Area & Soil Type */}
          <div className={styles.detailsGrid}>
            <div>
              <p className={styles.detailValue}>{farm.total_area_acres} Acres</p>
              <span className={styles.detailLabel}>Area</span>
            </div>
            <div>
              <p className={styles.detailValue}>{farm.soil_type}</p>
              <span className={styles.detailLabel}>Soil Type</span>
            </div>
          </div>

          {/* Current Crop / Status */}
          {hasCrop && activeCrop ? (
            <div className={styles.cropSection}>
              <span className={styles.sectionMetaLabel}>Current Crop</span>
              <div className={styles.cropRow}>
                <span className={styles.cropName}>{activeCrop.crop_name}</span>
                {stageName && (
                  <span className={styles.stageName}>
                    <Sprout size={13} className={styles.sproutIcon} />
                    {stageName}
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div className={styles.cropSection}>
              <span className={styles.sectionMetaLabel}>Status</span>
              <span className={styles.idleStatus}>No Crop Assigned</span>
            </div>
          )}
        </div>
      </div>

      {/* Card Footer Actions */}
      <div className={styles.cardFooter}>
        {hasCrop ? (
          <>
            <div className={styles.dayCounter}>
              <span>📅</span> Day {currentDay} / {totalDays}
            </div>
            <Link href={`/farms/${farm.id}`} className={styles.openButton}>
              <span>Open Farm</span>
              <ChevronRight size={14} />
            </Link>
          </>
        ) : (
          <>
            <Link href="/crops" style={{ flex: 1 }}>
              <button className={styles.recommendButton}>
                <Compass size={14} />
                <span>Recommend Crop</span>
              </button>
            </Link>
            <Link href={`/farms/${farm.id}`} className={styles.openButton}>
              <span>Open Farm</span>
              <ChevronRight size={14} />
            </Link>
          </>
        )}
      </div>
    </div>
  );
}

export default FarmCard;
