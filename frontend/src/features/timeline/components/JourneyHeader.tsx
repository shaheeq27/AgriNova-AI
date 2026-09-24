'use client';

import React from 'react';
import styles from './JourneyHeader.module.css';

interface JourneyHeaderProps {
  cropName: string;
  farmName: string;
  season: string;
  farms: any[];
  crops: any[];
  selectedFarmId: string | null;
  selectedCropId: string | null;
  onSelectFarm: (id: string) => void;
  onSelectCrop: (id: string) => void;
  journey: any;
}

export default function JourneyHeader({
  cropName,
  farmName,
  season,
  farms,
  crops,
  selectedFarmId,
  selectedCropId,
  onSelectFarm,
  onSelectCrop,
  journey
}: JourneyHeaderProps) {

  const handleExport = () => {
    if (!journey) return;

    // Create a simple text report
    const lines = [
      `AgriNova Crop Journey Report`,
      `----------------------------`,
      `Farm: ${journey.farmName}`,
      `Crop: ${journey.cropName}`,
      `Season: ${journey.season}`,
      `Planting Date: ${journey.plantingDate}`,
      ``,
      `Progress: Day ${journey.currentDay} / ${journey.totalDays} (${journey.progressPercent}% Complete)`,
      `Current Stage: ${journey.currentPhaseName}`,
      ``,
      `SUMMARY`,
      `Important Events: ${journey.summary.totalEvents}`,
      `Health Issues: ${journey.summary.healthIssues}`,
      `Treatments Applied: ${journey.summary.treatmentsApplied}`,
      `AI Insights: ${journey.summary.aiInsights}`,
      ``,
      `TIMELINE STAGES`
    ];

    journey.phases.forEach((p: any) => {
      lines.push(`- [${p.status.toUpperCase()}] ${p.name} (${p.startDate} to ${p.endDate})`);
      if (p.events && p.events.length > 0) {
        p.events.forEach((e: any) => {
           lines.push(`    * ${e.date}: ${e.title}`);
        });
      }
    });

    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agrinova-${journey.farmName.replace(/\s+/g, '-').toLowerCase()}-${journey.cropName.replace(/\s+/g, '-').toLowerCase()}-timeline.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.header}>
      <div className={styles.titleSection}>
        <h1 className={styles.title}>Crop Journey</h1>
        <p className={styles.subtitle}>Track your crop's complete life cycle</p>
      </div>

      <div className={styles.selectors}>
        <div className={styles.pill} style={{ position: 'relative' }}>
          <span className={styles.icon}>🌾</span>
          <select
            value={selectedCropId || ""}
            onChange={(e) => onSelectCrop(e.target.value)}
            style={{ appearance: 'none', background: 'transparent', border: 'none', color: 'inherit', font: 'inherit', outline: 'none', cursor: 'pointer', paddingRight: '12px' }}
            disabled={crops.length === 0}
          >
            {crops.length > 0 ? crops.map(c => (
              <option key={c.id} value={c.id} style={{ color: '#000' }}>{c.crop_name}</option>
            )) : (
              <option value="">{cropName}</option>
            )}
          </select>
          <span className={styles.arrow} style={{ position: 'absolute', right: '12px', pointerEvents: 'none' }}>▼</span>
        </div>
        <div className={styles.pill} style={{ position: 'relative' }}>
          <span className={styles.icon}>🏡</span>
          <select
            value={selectedFarmId || ""}
            onChange={(e) => onSelectFarm(e.target.value)}
            style={{ appearance: 'none', background: 'transparent', border: 'none', color: 'inherit', font: 'inherit', outline: 'none', cursor: 'pointer', paddingRight: '12px' }}
            disabled={farms.length === 0}
          >
            {farms.length > 0 ? farms.map(f => (
              <option key={f.id} value={f.id} style={{ color: '#000' }}>{f.name}</option>
            )) : (
              <option value="">{farmName}</option>
            )}
          </select>
          <span className={styles.arrow} style={{ position: 'absolute', right: '12px', pointerEvents: 'none' }}>▼</span>
        </div>
        <div className={styles.pill} style={{ position: 'relative' }}>
          <span className={styles.icon}>📅</span>
          <select
            style={{ appearance: 'none', background: 'transparent', border: 'none', color: 'inherit', font: 'inherit', outline: 'none', cursor: 'pointer', paddingRight: '12px' }}
            disabled
          >
            <option value="">{season}</option>
          </select>
          <span className={styles.arrow} style={{ position: 'absolute', right: '12px', pointerEvents: 'none' }}>▼</span>
        </div>
      </div>

      <button className={styles.exportButton} onClick={handleExport}>
        Export Report ↓
      </button>
    </div>
  );
}
