'use client';

import React from 'react';
import {
  useFarms,
  FarmHeader,
  FarmStats,
  FarmRegistration,
  FarmList,
} from '@/features/farms';

export default function FarmsPage() {
  const {
    stats,
    filteredFarms,
    loading,
    submitting,
    searchQuery,
    setSearchQuery,
    viewMode,
    setViewMode,
    registerFarm,
  } = useFarms();

  return (
    <>
      {/* 1. Header (Search, Profile, Title Banner + Farmhouse Image) */}
      <FarmHeader searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      {/* 2. Summary Statistics (4 Cards) */}
      <FarmStats stats={stats} />

      {/* 3. Farm Registration Bar */}
      <FarmRegistration onRegister={registerFarm} submitting={submitting} />

      {/* 4. My Farms List / Grid Section */}
      <FarmList
        farms={filteredFarms}
        loading={loading}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
        searchQuery={searchQuery}
      />
    </>
  );
}
