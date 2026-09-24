'use client';

import React, { useState } from 'react';
import {
  Sprout,
  Plus,
  MapPin,
  Pencil,
  Droplets,
  ChevronDown,
} from 'lucide-react';
import { CreateFarmInput } from '../types';
import { SOIL_TYPES, WATER_SOURCES } from '../constants';
import styles from './FarmRegistration.module.css';

interface FarmRegistrationProps {
  onRegister: (input: CreateFarmInput) => Promise<unknown>;
  submitting: boolean;
}

export function FarmRegistration({ onRegister, submitting }: FarmRegistrationProps) {
  const [name, setName] = useState('');
  const [locationCity, setLocationCity] = useState('');
  const [areaAcres, setAreaAcres] = useState('');
  const [soilType, setSoilType] = useState<string>(SOIL_TYPES[0]);
  const [waterSource, setWaterSource] = useState<string>(WATER_SOURCES[0]);
  const [cropName, setCropName] = useState('');
  const [season, setSeason] = useState('Kharif');
  const [plantingDate, setPlantingDate] = useState(() => new Date().toISOString().split('T')[0]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !locationCity || !areaAcres) return;

    await onRegister({
      name,
      location_city: locationCity,
      total_area_acres: parseFloat(areaAcres),
      soil_type: soilType,
      water_source: waterSource,
      crop_name: cropName || undefined,
      season: season || undefined,
      planting_date: plantingDate || undefined,
    });

    setName('');
    setLocationCity('');
    setAreaAcres('');
    setCropName('');
  };

  return (
    <div className={styles.registrationCard}>
      <div className={styles.cardHeader}>
        <Sprout size={20} className={styles.headerIcon} />
        <h2 className={styles.headerTitle}>Register New Farm</h2>
      </div>

      <form onSubmit={handleSubmit} className={styles.formGrid}>
        {/* 1. Farm Name */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Farm Name</label>
          <div className={styles.inputWrapper}>
            <input
              type="text"
              placeholder="Enter farm name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className={styles.input}
            />
          </div>
        </div>

        {/* 2. Location */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Location</label>
          <div className={styles.inputWrapper}>
            <input
              type="text"
              placeholder="City / District / State"
              value={locationCity}
              onChange={(e) => setLocationCity(e.target.value)}
              required
              className={`${styles.input} ${styles.inputWithIcon}`}
            />
            <MapPin size={14} className={styles.inputIcon} />
          </div>
        </div>

        {/* 3. Farm Size (Acres) */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Farm Size (Acres)</label>
          <div className={styles.inputWrapper}>
            <input
              type="number"
              placeholder="Enter area in acres"
              step="0.1"
              min="0.1"
              value={areaAcres}
              onChange={(e) => setAreaAcres(e.target.value)}
              required
              className={`${styles.input} ${styles.inputWithIcon}`}
            />
            <Pencil size={14} className={styles.inputIcon} />
          </div>
        </div>

        {/* 4. Soil Type */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Soil Type</label>
          <div className={styles.inputWrapper}>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              className={styles.select}
            >
              {SOIL_TYPES.map((soil) => (
                <option key={soil} value={soil}>
                  {soil}
                </option>
              ))}
            </select>
            <Sprout size={14} className={styles.inputIcon} />
            <ChevronDown size={14} className={styles.chevronIcon} />
          </div>
        </div>

        {/* 5. Water Source */}
        <div className={styles.fieldGroup}>
          <label className={styles.fieldLabel}>Water Source</label>
          <div className={styles.inputWrapper}>
            <select
              value={waterSource}
              onChange={(e) => setWaterSource(e.target.value)}
              className={styles.select}
            >
              {WATER_SOURCES.map((source) => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
            <Droplets size={14} className={styles.inputIcon} />
            <ChevronDown size={14} className={styles.chevronIcon} />
          </div>
        </div>

        {/* Optional: Add Crop */}
        <div className={styles.fieldGroup} style={{ gridColumn: "1 / -1", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginTop: "8px", padding: "16px", backgroundColor: "rgba(255,255,255,0.02)", borderRadius: "8px", border: "1px dashed rgba(255,255,255,0.1)" }}>
          <div style={{ gridColumn: "1 / -1", fontSize: "14px", fontWeight: 600, color: "var(--neon-mint)", marginBottom: "4px" }}>
            Add Initial Crop (Optional)
          </div>
          <div>
            <label className={styles.fieldLabel}>Crop Name</label>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                placeholder="e.g. Rice, Wheat"
                value={cropName}
                onChange={(e) => setCropName(e.target.value)}
                className={styles.input}
              />
            </div>
          </div>
          <div>
            <label className={styles.fieldLabel}>Season</label>
            <div className={styles.inputWrapper}>
              <select value={season} onChange={(e) => setSeason(e.target.value)} className={styles.select}>
                <option value="Kharif">Kharif</option>
                <option value="Rabi">Rabi</option>
                <option value="Zaid">Zaid</option>
                <option value="Annual">Annual</option>
              </select>
              <ChevronDown size={14} className={styles.chevronIcon} />
            </div>
          </div>
          <div>
            <label className={styles.fieldLabel}>Sowing Date</label>
            <div className={styles.inputWrapper}>
              <input
                type="date"
                value={plantingDate}
                onChange={(e) => setPlantingDate(e.target.value)}
                className={styles.input}
              />
            </div>
          </div>
        </div>

        {/* 6. Register CTA Button */}
        <div style={{ gridColumn: "1 / -1" }}>
          <button type="submit" disabled={submitting} className={styles.submitButton}>
            <Plus size={18} strokeWidth={2.5} />
            <span>{submitting ? 'Registering...' : 'Register New Farm'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default FarmRegistration;
