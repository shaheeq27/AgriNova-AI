'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Farm, CreateFarmInput, FarmStatsData, ViewMode } from '../types';
import { FarmsService } from '../services/farms.service';

export function useFarms() {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  useEffect(() => {
    FarmsService.getFarms()
      .then((data) => setFarms(data))
      .finally(() => setLoading(false));
  }, []);

  const stats: FarmStatsData = useMemo(() => {
    return FarmsService.calculateStats(farms);
  }, [farms]);

  const filteredFarms = useMemo(() => {
    if (!searchQuery.trim()) return farms;
    const q = searchQuery.toLowerCase();
    return farms.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        f.location_city.toLowerCase().includes(q) ||
        f.soil_type.toLowerCase().includes(q)
    );
  }, [farms, searchQuery]);

  const registerFarm = useCallback(async (input: CreateFarmInput) => {
    setSubmitting(true);
    try {
      const created = await FarmsService.createFarm(input);
      setFarms((prev) => [created, ...prev]);
      return created;
    } finally {
      setSubmitting(false);
    }
  }, []);

  return {
    farms,
    stats,
    filteredFarms,
    loading,
    submitting,
    searchQuery,
    setSearchQuery,
    viewMode,
    setViewMode,
    registerFarm,
  };
}
