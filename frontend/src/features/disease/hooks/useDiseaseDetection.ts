/* ══════════════════════════════════════════════════════════════
   AgriNova AI — Disease Detection State Machine Hook
   Manages the 5-stage workflow: DETECT → UNDERSTAND → TREAT → FOLLOW UP → RESOLVE
   ══════════════════════════════════════════════════════════════ */

'use client';

import { useState, useCallback, useEffect } from 'react';
import type {
  DiseaseDetectionState,
  FarmOption,
  TreatmentLogEntry,
  ResolutionOutcome,
  ImageAnalysisResponse
} from '../types';
import { STANDALONE_FARM } from '../constants';
import { farmAPI, diseaseAPI, ApiError } from '@/lib/api';

const initialState: DiseaseDetectionState = {
  stage: 'initial',
  selectedImage: null,
  imagePreviewUrl: null,
  selectedFarm: null,
  analysisResult: null,
  treatmentLog: null,
  showTreatmentForm: false,
  followUpImage: null,
  followUpImageUrl: null,
  resolutionOutcome: null,
  resolutionNotes: '',
  isAnalyzing: false,
  isSaving: false,
  detectionSaved: false,
  error: null,
};

export function useDiseaseDetection() {
  const [state, setState] = useState<DiseaseDetectionState>(initialState);
  const [farms, setFarms] = useState<FarmOption[]>([]);

  /* ── Load user's farms for dropdown ── */
  useEffect(() => {
    farmAPI
      .list()
      .then((data) => {
        const farmOptions: FarmOption[] = data.farms.map((f) => ({
          id: f.id,
          name: f.name,
          isStandalone: false,
        }));
        setFarms(farmOptions);
      })
      .catch(() => {
        // Silently fail — farms are optional
        setFarms([]);
      });
  }, []);

  /** All dropdown options: user farms + standalone */
  const farmOptions: FarmOption[] = [...farms, STANDALONE_FARM];

  /* ── Image Selection ── */
  const selectImage = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    setState((prev) => ({
      ...prev,
      selectedImage: file,
      imagePreviewUrl: url,
      error: null,
    }));
  }, []);

  const clearImage = useCallback(() => {
    setState((prev) => {
      if (prev.imagePreviewUrl) URL.revokeObjectURL(prev.imagePreviewUrl);
      return { ...prev, selectedImage: null, imagePreviewUrl: null, error: null };
    });
  }, []);

  /* ── Farm Selection ── */
  const selectFarm = useCallback((farm: FarmOption | null) => {
    setState((prev) => ({ ...prev, selectedFarm: farm, error: null }));
  }, []);

  /* ── Start Analysis ── */
  const startAnalysis = useCallback(async () => {
    if (!state.selectedImage) return;

    setState((prev) => ({ ...prev, stage: 'analyzing', isAnalyzing: true, error: null }));

    try {
      // Hit the ML image analysis endpoint
      const res: ImageAnalysisResponse = await diseaseAPI.analyzeImage(state.selectedImage);

      setState((prev) => ({
        ...prev,
        stage: 'result',
        isAnalyzing: false,
        error: null,
        analysisResult: res,
        detectionSaved: prev.selectedFarm != null && !prev.selectedFarm.isStandalone,
      }));
    } catch (err) {
      console.error("Disease detection failed", err);
      let errorMessage = 'Failed to analyze image. Please try again.';
      if (err instanceof ApiError) {
        errorMessage = err.message || errorMessage;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      setState((prev) => ({
        ...prev,
        stage: 'initial', // Revert to initial to show error and allow re-upload
        isAnalyzing: false,
        error: errorMessage,
      }));
    }
  }, [state.selectedImage, state.selectedFarm]);

  /* ── Treatment Form ── */
  const openTreatmentForm = useCallback(() => {
    setState((prev) => ({ ...prev, showTreatmentForm: true }));
  }, []);

  const closeTreatmentForm = useCallback(() => {
    setState((prev) => ({ ...prev, showTreatmentForm: false }));
  }, []);

  /* ── Log Treatment ── */
  const logTreatment = useCallback(async (entry: TreatmentLogEntry) => {
    setState((prev) => ({ ...prev, isSaving: true }));

    // Simulate API save
    await new Promise((resolve) => setTimeout(resolve, 800));

    setState((prev) => ({
      ...prev,
      stage: prev.selectedFarm?.isStandalone ? 'result' : 'followup',
      treatmentLog: entry,
      showTreatmentForm: false,
      isSaving: false,
    }));
  }, []);

  /* ── Follow-Up Image ── */
  const uploadFollowUp = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    setState((prev) => ({
      ...prev,
      followUpImage: file,
      followUpImageUrl: url,
    }));
  }, []);

  /* ── Proceed to Resolution ── */
  const proceedToResolve = useCallback(() => {
    setState((prev) => ({ ...prev, stage: 'resolved' }));
  }, []);

  /* ── Resolve Case ── */
  const resolveCase = useCallback(async (outcome: ResolutionOutcome, notes: string) => {
    setState((prev) => ({ ...prev, isSaving: true }));

    // Simulate API update
    await new Promise((resolve) => setTimeout(resolve, 800));

    setState((prev) => ({
      ...prev,
      resolutionOutcome: outcome,
      resolutionNotes: notes,
      isSaving: false,
    }));
  }, []);

  /* ── Reset to initial state ── */
  const resetDetection = useCallback(() => {
    setState((prev) => {
      if (prev.imagePreviewUrl) URL.revokeObjectURL(prev.imagePreviewUrl);
      if (prev.followUpImageUrl) URL.revokeObjectURL(prev.followUpImageUrl);
      return { ...initialState };
    });
  }, []);

  return {
    ...state,
    farms,
    farmOptions,
    selectImage,
    clearImage,
    selectFarm,
    startAnalysis,
    openTreatmentForm,
    closeTreatmentForm,
    logTreatment,
    uploadFollowUp,
    proceedToResolve,
    resolveCase,
    resetDetection,
  };
}
