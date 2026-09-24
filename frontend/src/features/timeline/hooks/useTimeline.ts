import { useState, useEffect, useCallback } from 'react';
import { farmAPI, cropsAPI, diseaseAPI, fertilizerAPI, irrigationAPI, activityAPI } from '@/lib/api';
import { parseDateString } from '@/utils/date';
import { FarmsService } from '@/features/farms/services/farms.service';
import { MOCK_CROP_JOURNEY } from '../constants';
import type { CropJourney, CropJourneyPhase, PhaseEvent, EventCategory, PhaseStatus } from '../types';

export function useTimeline() {
  const [journey, setJourney] = useState<CropJourney | null>(null);
  const [expandedPhaseId, setExpandedPhaseId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Selection state
  const [farms, setFarms] = useState<any[]>([]);
  const [crops, setCrops] = useState<any[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(null);
  const [selectedCropId, setSelectedCropId] = useState<string | null>(null);

  // Load farms once
  useEffect(() => {
    let isMounted = true;
    farmAPI.list().then(res => {
      if (!isMounted) return;
      if (res && res.farms && res.farms.length > 0) {
        setFarms(res.farms);
        setSelectedFarmId(res.farms[0].id);
      } else {
        setFarms([]);
        setJourney(MOCK_CROP_JOURNEY);
        const currentPhase = MOCK_CROP_JOURNEY.phases.find(p => p.status === 'current');
        if (currentPhase) setExpandedPhaseId(currentPhase.id);
        setIsLoading(false);
      }
    }).catch(err => {
      if (isMounted) setIsLoading(false);
    });
    return () => { isMounted = false; };
  }, []);

  // When selectedFarmId changes, load its crops
  useEffect(() => {
    if (!selectedFarmId) return;
    let isMounted = true;
    setIsLoading(true);

    cropsAPI.listByFarm(selectedFarmId).then(res => {
      if (!isMounted) return;
      if (res && res.crops && res.crops.length > 0) {
        setCrops(res.crops);
        // Try to pick an active crop
        let activeCrop = res.crops.find((c: any) => c.status === "active" || c.status === "planned");
        if (!activeCrop) activeCrop = res.crops[0];
        setSelectedCropId(activeCrop.id);
      } else {
        setCrops([]);
        setSelectedCropId(null);
        setJourney(null);
        setIsLoading(false);
      }
    }).catch(err => {
      if (isMounted) { setCrops([]); setSelectedCropId(null); setIsLoading(false); }
    });
    return () => { isMounted = false; };
  }, [selectedFarmId]);

  // When selectedCropId changes, load timeline and stats
  useEffect(() => {
    if (!selectedCropId) return;
    let isMounted = true;
    setIsLoading(true);

    async function loadTimeline() {
      try {
        const targetFarm = farms.find(f => f.id === selectedFarmId);
        const activeCrop = crops.find(c => c.id === selectedCropId);
        if (!targetFarm || !activeCrop) return;

        const timelineRes = await cropsAPI.getTimeline(activeCrop.id);
        const tasksRes = await cropsAPI.getTasks(activeCrop.id);

        let diseaseRecords: any[] = [];
        try { const dRes = await diseaseAPI.getRecords(activeCrop.id); diseaseRecords = dRes.data || []; } catch(e) {}

        let fertilizerLogs: any[] = [];
        try { const fRes = await fertilizerAPI.getLogs(activeCrop.id); fertilizerLogs = fRes.data || []; } catch(e) {}

        let irrigationLogs: any[] = [];
        try { const iRes = await irrigationAPI.getLogs(activeCrop.id); irrigationLogs = iRes.data || []; } catch(e) {}

        let activityRecords: any[] = [];
        try { const aRes = await activityAPI.getForCrop(activeCrop.id); activityRecords = aRes.data?.items || []; } catch(e) {}

        const stages = timelineRes.stages || [];
        const tasks = tasksRes.tasks || [];

        const today = new Date();
        today.setHours(0, 0, 0, 0); // Normalize today to start of day for accurate day counts

        // USE THE EXACT SAME LOGIC AS FARM CARD
        const { currentDay, totalDays } = FarmsService.calculateCropDays(
            activeCrop.planting_date,
            activeCrop.crop_name,
            activeCrop.created_at
        );
        let plantingDate = parseDateString(activeCrop.planting_date || activeCrop.created_at) || today;
        let progressPercent = 0;

        if (currentDay > 0) {
            progressPercent = Math.min(100, Math.max(0, Math.round(((currentDay - 1) / (Math.max(1, totalDays - 1))) * 100)));
        }


        const phases: CropJourneyPhase[] = stages.map((s: any) => {
           const startDate = parseDateString(s.start_date) || today;
           const endDate = parseDateString(s.end_date) || today;

           const sDiff = startDate.getTime() - plantingDate!.getTime();
           const dayStart = Math.round(sDiff / (1000 * 60 * 60 * 24)) + 1;

           const eDiff = endDate.getTime() - plantingDate!.getTime();
           const dayEnd = Math.round(eDiff / (1000 * 60 * 60 * 24)) + 1;

           let status: PhaseStatus = 'upcoming';
           if (today >= startDate && today <= endDate) status = 'current';
           else if (today > endDate) status = 'completed';

           let icon = "🌱";
           if (s.stage_name.toLowerCase().includes("veg")) icon = "🌿";
           if (s.stage_name.toLowerCase().includes("flower")) icon = "🌸";
           if (s.stage_name.toLowerCase().includes("fruit")) icon = "🍎";
           if (s.stage_name.toLowerCase().includes("mature")) icon = "🌾";
           if (s.stage_name.toLowerCase().includes("harvest")) icon = "🚜";

           const phaseTasks = tasks.filter((t: any) => {
              const tDate = parseDateString(t.scheduled_date);
              if (!tDate) return false;
              return tDate >= startDate && tDate <= endDate;
           });

           const events: PhaseEvent[] = phaseTasks.map((t: any) => {
              let category: EventCategory = 'milestone';
              let tIcon = "📌";
              if (t.category === 'monitoring') { category = 'health'; tIcon = "🔎"; }
              else if (t.category === 'watering' || t.category === 'fertilizer' || t.category === 'weeding') { category = 'treatment'; tIcon = "💧"; }
              else if (t.category === 'ai') { category = 'ai'; tIcon = "✨"; }

              if (t.is_completed) tIcon = "✅";

              return {
                 id: t.id,
                 // Pass the RAW string (YYYY-MM-DD) so the component can parse it securely
                 date: t.scheduled_date,
                 category,
                 title: t.title,
                 description: t.description || "",
                 icon: tIcon
              };
           });

           return {
              id: s.id,
              name: s.stage_name,
              stageOrder: s.stage_order,
              // Pass the raw strings
              startDate: s.start_date,
              endDate: s.end_date,
              dayStart,
              dayEnd,
              status,
              icon,
              events
           };
        });

        // Ensure "Important Events" only counts completed/real events
        const summary = {
          totalEvents: activityRecords.length,
          healthIssues: diseaseRecords.length,
          treatmentsApplied: fertilizerLogs.length + irrigationLogs.length,
          aiInsights: 0
        };

        const pd = parseDateString(activeCrop.planting_date);
        // Will format it properly later, for now pass raw to not break structure, but journey expects a string.
        const pStr = pd ? pd.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : "Date unavailable";

        const journeyData: CropJourney = {
           cropName: activeCrop.crop_name,
           farmName: targetFarm.name,
           season: activeCrop.season,
           plantingDate: pStr,
           totalDays,
           currentDay,
           progressPercent,
           currentPhaseName: timelineRes.current_stage || (phases.length > 0 ? phases[0].name : ""),
           phases,
           summary
        };

        if (isMounted) {
           setJourney(journeyData);
           const currentPhase = phases.find(p => p.status === 'current');
           if (currentPhase) setExpandedPhaseId(currentPhase.id);
           setIsLoading(false);
        }
      } catch (err) {
        console.error("Timeline error:", err);
        if (isMounted) {
           setJourney(null);
           setIsLoading(false);
        }
      }
    }

    loadTimeline();
    return () => { isMounted = false; };
  }, [selectedCropId]);

  const togglePhase = useCallback((phaseId: string) => {
    setExpandedPhaseId(prev => (prev === phaseId ? null : phaseId));
  }, []);

  return {
    journey,
    expandedPhaseId,
    togglePhase,
    isLoading,
    farms,
    crops,
    selectedFarmId,
    selectedCropId,
    setSelectedFarmId,
    setSelectedCropId
  };
}
