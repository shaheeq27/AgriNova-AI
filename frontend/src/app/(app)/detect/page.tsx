'use client';

import React from 'react';
import { useDiseaseDetection } from '@/features/disease/hooks/useDiseaseDetection';
import { DetectionHeader } from '@/features/disease/components/DetectionHeader';
import { ImageUpload } from '@/features/disease/components/ImageUpload';
import { AnalyzingState } from '@/features/disease/components/AnalyzingState';
import { WorkflowStepper } from '@/features/disease/components/WorkflowStepper';
import { DiagnosisResult } from '@/features/disease/components/DiagnosisResult';
import { TreatmentPlan } from '@/features/disease/components/TreatmentPlan';
import { FollowUpTracker } from '@/features/disease/components/FollowUpTracker';
import { ResolutionPanel } from '@/features/disease/components/ResolutionPanel';

/* ─────────────────────────────────────────────────────────────
   AgriNova AI — Crop Disease Detection
   5-stage workflow: DETECT → UNDERSTAND → TREAT → FOLLOW UP → RESOLVE
   Progressive disclosure: complexity appears only after analysis.
   ───────────────────────────────────────────────────────────── */

export default function DetectPage() {
  const {
    stage,
    imagePreviewUrl,
    farmOptions,
    selectedFarm,
    diagnosis,
    treatmentLog,
    showTreatmentForm,
    followUpImageUrl,
    resolutionOutcome,
    isAnalyzing,
    isSaving,
    detectionSaved,
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
  } = useDiseaseDetection();

  return (
    <>


      {/* Page content wrapper */}
      <div style={{
        maxWidth: '1040px',
        margin: '0 auto',
        padding: '0 16px 48px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
      }}>

        {/* ═══════════════════════════════════════════════════
            STAGE: INITIAL — Upload + Farm dropdown only
            ═══════════════════════════════════════════════════ */}
        {stage === 'initial' && (
          <div style={{
            background: 'rgba(20, 26, 20, 0.45)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            borderRadius: '24px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px'
          }}>
            <DetectionHeader />
            <ImageUpload
              imagePreviewUrl={imagePreviewUrl}
              farmOptions={farmOptions}
              selectedFarm={selectedFarm}
              onImageSelect={selectImage}
              onImageClear={clearImage}
              onFarmSelect={selectFarm}
              onStartAnalysis={startAnalysis}
            />
          </div>
        )}

        {/* ═══════════════════════════════════════════════════
            STAGE: ANALYZING — Scanning animation
            ═══════════════════════════════════════════════════ */}
        {stage === 'analyzing' && imagePreviewUrl && (
          <AnalyzingState imagePreviewUrl={imagePreviewUrl} />
        )}

        {/* ═══════════════════════════════════════════════════
            STAGE: RESULT — Diagnosis + Treatment + Log
            Stepper: DETECT ✓, UNDERSTAND ✓, TREAT ●
            ═══════════════════════════════════════════════════ */}
        {stage === 'result' && diagnosis && (
          <>
            <WorkflowStepper currentStage={stage} />
            <DiagnosisResult
              diagnosis={diagnosis}
              detectionSaved={detectionSaved}
              imagePreviewUrl={imagePreviewUrl}
              farmName={selectedFarm?.isStandalone ? undefined : selectedFarm?.name}
            />
            <TreatmentPlan
              diagnosis={diagnosis}
              showTreatmentForm={showTreatmentForm}
              isSaving={isSaving}
              onOpenForm={openTreatmentForm}
              onCloseForm={closeTreatmentForm}
              onLogTreatment={logTreatment}
              isStandalone={selectedFarm?.isStandalone}
              onReset={resetDetection}
            />
          </>
        )}

        {/* ═══════════════════════════════════════════════════
            STAGE: FOLLOW UP — Upload follow-up image
            Stepper: DETECT ✓, UNDERSTAND ✓, TREAT ✓, FOLLOW UP ●
            ═══════════════════════════════════════════════════ */}
        {stage === 'followup' && (
          <>
            <WorkflowStepper currentStage={stage} />
            <FollowUpTracker
              treatmentLog={treatmentLog}
              followUpImageUrl={followUpImageUrl}
              onUploadFollowUp={uploadFollowUp}
              onProceedToResolve={proceedToResolve}
            />
          </>
        )}

        {/* ═══════════════════════════════════════════════════
            STAGE: RESOLVED — Mark resolution + New detection
            Stepper: All ✓ or RESOLVE ●
            ═══════════════════════════════════════════════════ */}
        {stage === 'resolved' && (
          <>
            <WorkflowStepper currentStage={stage} />
            <ResolutionPanel
              isSaving={isSaving}
              resolutionOutcome={resolutionOutcome}
              onResolve={resolveCase}
              onNewDetection={resetDetection}
            />
          </>
        )}
      </div>
    </>
  );
}
