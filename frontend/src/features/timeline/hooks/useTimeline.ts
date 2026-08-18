import { useState, useEffect, useCallback } from 'react';
import { MOCK_CROP_JOURNEY } from '../constants';
import type { CropJourney } from '../types';

export function useTimeline() {
  const [journey, setJourney] = useState<CropJourney | null>(null);
  const [expandedPhaseId, setExpandedPhaseId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setJourney(MOCK_CROP_JOURNEY);
      
      // Auto-expand current phase
      const currentPhase = MOCK_CROP_JOURNEY.phases.find(p => p.status === 'current');
      if (currentPhase) {
        setExpandedPhaseId(currentPhase.id);
      }
      
      setIsLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  const togglePhase = useCallback((phaseId: string) => {
    setExpandedPhaseId(prev => (prev === phaseId ? null : phaseId));
  }, []);

  return {
    journey,
    expandedPhaseId,
    togglePhase,
    isLoading,
  };
}
