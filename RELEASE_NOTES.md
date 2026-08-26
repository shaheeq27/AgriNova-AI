# 🌱 AgriNova AI — Release Notes

## v4.0.0-alpha.1 — V4 Phase 1 (Personalized Intelligence)
**Release Date:** August 24, 2026

### Step 1: Model + Database Foundation
- Added crop variety/yield tracking to Crop models and schemas
- Added irrigation growth-stage tracking to IrrigationLog models and schemas
- Added disease outcome tracking to DiseaseRecord models and schemas
- Added safe SQLite schema migration mechanism to preserve existing data during schema updates

### Step 2: Complete Farm Activity History
- Completed farm activity event coverage using existing ActivityLog
- Added tracking for fertilizer applications and irrigation events
- Added tracking for disease treatments and disease resolutions
- Added tracking for crop harvests
- Implemented robust duplicate-event prevention logic for idempotent updates

### Step 3: History Repository
- Added farm-level history repository (`HistoryRepository`)
- Added cross-entity historical retrieval spanning crops, fertilizer, irrigation, and diseases
- Added activity history retrieval scoped by farm
- Added farm performance aggregation for yield metrics
- Added strict farm isolation and SQL-level limit handling

### Step 4: AI History Context Schemas
- Created `CropHistoryEntry` and `FarmHistoryContext` Pydantic schemas.
- Extended `UnifiedContext` to seamlessly include backward-compatible `history` fields.
- Verified robust schema parsing and structure prior to context formatting.

### Step 5: FarmHistoryService
- Created `FarmHistoryService` to act as the AI transformation layer for historical farm data.
- Built context builders to map repository records to `FarmHistoryContext`.
- Extracted dynamic seasonal patterns automatically from historical crops.
- Produced formatted disease summaries and performance metrics explicitly scoped for LLM integration.
- Designed service carefully to support farm isolation and safely handle empty history boundaries without panicking.

### Step 6: AI Context Pipeline Integration
- Integrated `FarmHistoryService` into the existing `ContextService`.
- Context pipeline now retrieves and embeds farm history into `UnifiedContext`.
- Verified strict backward compatibility (all pre-existing context schemas and AI behavior remain entirely unaffected).
- Confirmed error resistance via fallback mechanisms for missing or unpopulated history data.

### Step 7: History Context Formatter
- Extended the `ContextFormatter` to seamlessly serialize the new `FarmHistoryContext`.
- Farm History is natively rendered for the LLM delimited by explicit `[FARM HISTORY]` boundaries.
- Adhered rigidly to pre-existing AI formatter conventions, preventing "JSON dumping" and skipping null objects cleanly.
- Added a robust formatter test suite safely proving optional variables format optimally without disrupting `UnifiedContext` strings.

### Step 8: AI History Consumption & Reasoning
- Extracted maximum reasoning value directly out of the primary LLM pipeline by instructing the AI via its System Prompts on exactly how to treat `[FARM HISTORY]`.
- Enforced constraint that `[FARM HISTORY]` operates as supporting, probabilistic evidence (rather than a deterministic absolute guarantee) when formulating guidance.
- Proved 100% stable integration passing cleanly through the `AIService` without requiring extraneous secondary agent calls, keeping latency optimally fast and LLM costs identical.

### Step 9: Deterministic Historical Insights
- Implemented `HistoricalInsightsService` to extract hard, deterministic signals (e.g., successful crops, recurring diseases) purely mathematically before AI reasoning begins.
- Executed synchronously over the pre-built `FarmHistoryContext` avoiding any N+1 secondary database traversals.
- Defined explicit rules isolating units natively to strictly prevent incompatible yield averaging, maintaining rigid numerical integrity.
- Formatted output organically into a distinct `[HISTORICAL INSIGHTS]` payload directly consumed by the AI System Prompt as absolute factual boundaries.

### Step 9: End-to-End History Pipeline Validation
- Added a comprehensive integration suite testing the full pipeline from database records to the final system prompt.
- Validated real data propagation (e.g., crops, yields, diseases, logs) through `HistoryRepository`, `FarmHistoryService`, and `ContextFormatter`.
- Verified strict farm isolation, ensuring Farm B's history never leaks into Farm A's context.
- Confirmed stable empty-state handling for new users without farms or farms without historical data.

### Step 4: Historical Insights Formatting & Prompt Grounding
- Extended  to seamlessly serialize the  into a clean, deterministic  block.
- Maintained exact yield/input unit integrity (, , ) during text serialization to prevent LLM hallucinations.
- Added strict grounding rules to  ensuring the AI accurately weighs computed historical conclusions against raw observational evidence from .
- Verified formatting edge cases (e.g., omitting the entire block when data is empty) through comprehensive unit testing.

### Step 5: End-to-End Pipeline Validation
- Added an exhaustive E2E integration suite mapping raw database fixtures entirely through the stack to the intercepted LLM prompt.
- Proved flawless coexistence between legacy  logs and modern  analytics.
- Validated rigorous cross-farm data isolation directly at the  provider boundary.
- Formally concluded V4 Phase 2.

---
## V4 Phase 2 — Farm-Specific Historical Intelligence
### Step 1: Historical Insight Contracts
- Created highly structured Pydantic models in `backend/app/ai/schemas/historical_analysis.py` representing deterministic historical insights (`CropPerformanceInsight`, `SeasonalPerformanceInsight`, `DiseasePatternInsight`, `InputUsageInsight`, `YieldTrendInsight`, `HistoricalInsightsContext`).
- Added strict validation rules, including confidence bound checks (`0.0 <= confidence <= 1.0`).
- Validated all models with robust unit tests mapping to edge cases (mixed units remain distinct, lists default safely to empty).
- Confirmed total backward compatibility with V4 Phase 1 schemas.

### Step 2: Historical Insights Computation Service
- Enhanced `HistoricalInsightsService` with a deterministic computation layer (`compute_insights_context`) processing raw historical records into detailed typed insights.
- Implemented isolated aggregation handling preserving separate metrics for incompatible units (e.g. tracking `kg` separate from `tons` organically).
- Engineered a deterministic confidence heuristic scaled organically by the frequency of observations (0 to 0.95).
- Created chronology-based simple-trend strategies tracking increasing/decreasing trends.
- Heavily tested isolated logic to ensure absolute zero data-bleeding across distinct farms, rigorously preventing N+1 queries by leveraging bulk query joins inside `HistoryRepository`.
- 100% backward compatible without mutating the existing Phase 1 logic.

### Step 3: Historical Insights Context Integration
- Successfully integrated the deterministic `HistoricalInsightsContext` into the AI's core `UnifiedContext` via `HistoricalInsightsService`.
- Engineered a fail-safe exception isolation mechanism guaranteeing core AI fallback features (weather, base farm rules, etc.) remain operational if insight computation fails.
- Confirmed missing or new farms without history dynamically default to empty structural representations rather than raising faults.
- Maintained strict isolation from the AI prompt formatting pipeline: the deterministic insights are successfully transported and prepared in memory, but consciously gated out of the LLM prompt pending integration in later steps.
- Retained full backward compatibility with the legacy Phase 1 integration without breaking pre-existing automated tests.

### Step 4: Historical Insights Formatting & Prompt Grounding
- Extended `ContextFormatter` to seamlessly serialize the `HistoricalInsightsContext` into a clean, deterministic `[HISTORICAL INSIGHTS]` block.
- Maintained exact yield/input unit integrity (`kg`, `tons`, `liters`) during text serialization to prevent LLM hallucinations.
- Added strict grounding rules to `AIRA_SYSTEM_PROMPT` ensuring the AI accurately weighs computed historical conclusions against raw observational evidence from `[FARM HISTORY]`.
- Verified formatting edge cases (e.g., omitting the entire block when data is empty) through comprehensive unit testing.

### Step 5: End-to-End Pipeline Validation
- Added an exhaustive E2E integration suite mapping raw database fixtures entirely through the stack to the intercepted LLM prompt.
- Proved flawless coexistence between legacy `[FARM HISTORY]` logs and modern `[HISTORICAL INSIGHTS]` analytics.
- Validated rigorous cross-farm data isolation directly at the `AIService` provider boundary.
- Formally concluded V4 Phase 2.

---
## v1.0.0 — Core Platform MVP
**Release Date:** August 5, 2026

### 🎯 Summary
First major release delivering the complete crop lifecycle platform with ML-powered recommendations, weather intelligence, fertilizer/irrigation engines, and disease detection.

---

### ✨ New Features

#### ML Crop Recommendation Engine
- RandomForest classifier (200 trees, 90.2% accuracy)
- Trained on 4,500 augmented samples across 30 Indian crops
- Returns top-5 recommendations with confidence + explanations
- Rule-based fallback system

#### Crop Lifecycle Management
- Plant crops on farms with full metadata
- Auto-generated growth timelines (6 stages per crop)
- Daily task generation and completion tracking

#### Weather Intelligence
- Real-time weather from Open-Meteo API (no API key required)
- 7-day forecast with daily min/max temps
- Smart alerts: frost, heat, heavy rain, high wind

#### Fertilizer Engine
- Stage-specific fertilizer recommendations from KB
- Application method guidance
- Fertilizer logging per crop

#### Irrigation Engine
- Water requirement calculations per crop/soil/stage
- Weather-adjusted frequency recommendations
- Irrigation activity logging

#### Disease Detection
- Symptom-based disease matching (Jaccard similarity)
- 8 diseases with treatments and prevention
- Image upload infrastructure
- Disease record tracking with workflow

### 📊 Backend Modules Added
| Module | Files |
|--------|-------|
| Crop Recommendation | Service, Schema, ML Training |
| Crop Lifecycle | Service, Repository, Schema, API |
| Timeline & Tasks | Service, Schema |
| Weather Intelligence | Service, Repository, Schema, API |
| Fertilizer Engine | Service, Schema, API |
| Irrigation Engine | Service, Schema, API |
| Disease Detection | Service, Repository, Schema, API |

### 🎨 Frontend Architecture
- **95 component files** across 16 categories
- Complete CSS design system (7 token files)
- TypeScript theme tokens (7 files)
- 10 animation wrappers, 5 custom hooks
- Dark forest aesthetic with neon green accents

### 🗄️ Database
- 16 tables (user data + knowledge base)
- 30 crop profiles, 180 growth stages, 8 diseases
- 30 fertilizer guidelines, 120 irrigation guidelines

### 📈 Test Results
- 27/29 E2E API tests passing
- All 11 modules verified
- 16 database tables validated
- Swagger + ReDoc documentation live

---

## v0.0.0 — Foundation
**Release Date:** August 2, 2026

### Features
- JWT authentication (register/login/profile)
- Farm management (CRUD)
- Knowledge Base with seeded data
- Database models and migrations
- Project structure (service/repo/schema pattern)

---
## V4 Phase 3 — Deterministic Recommendation Personalization
### Step 1: Engine Interface Expansion
- Upgraded the deterministic intelligence engines (`FertilizerEngine`, `IrrigationEngine`, `CropRecommendationService`, `DiseaseService`) to optionally accept `HistoricalInsightsContext`.
- Ensured strict backward compatibility: passing `None` yields the exact same recommendations as before.

### Step 2: ContextService Wiring
- Connected the `HistoricalInsightsContext` generated by `HistoricalInsightsService` directly into `IntelligenceService` and the `UnifiedContext`.
- Preserved strict execution order ensuring historical insights are computed BEFORE engine context is built.

### Step 3: Personalized Fertilizer & Irrigation
- Implemented bounded deterministic adjustment logic for `FertilizerEngine` and `IrrigationEngine`.
- If historical application of an input on a crop is excessive (e.g. >= 3 for fertilizer, >= 5 for irrigation) with high confidence (>= 0.6), the engine deterministically reduces the recommended quantity by up to 10%.
- Surfaced boolean flags (`historically_adjusted`) and text rationales (`personalization_rationale`) so the LLM knows why a number changed without deciding the number itself.

### Step 4: Personalized Crop & Disease
- Implemented yield-trend-based personalization for `CropRecommendationService`: crops with increasing yield trends receive up to a 5% baseline score boost; declining trends receive up to a 5% score penalty.
- Implemented recurrence-based personalization for `DiseaseService`: if a disease frequently recurred on a specific crop in the past, its symptom match confidence is boosted by up to 5%.
- Maintained the architectural boundary: history modifies base scores, and re-ranking happens *before* exposing the final candidates to the LLM.

### Step 5: End-to-End Personalization Validation
- Added an exhaustive E2E integration test proving the entire Phase 3 pipeline.
- Verified that heavy farm history triggers deterministic personalization in all 4 engines.
- Proved that the modified outputs successfully bubble up through the `UnifiedContext` to the final AI prompt.
- Passed full regression suite (0 regressions).

---
## V4 Phase 4 — AI Integration
### Step 1: Architecture Inspection
- Mapped the full V3 AI Agronomist pipeline from `AIService` -> `ContextService` -> `IntelligenceService` -> `ContextFormatter`.
- Pinpointed the exact architectural boundary where `historically_adjusted` and `personalization_rationale` were being dropped before reaching the LLM's system prompt.

### Step 2: Historical Personalization Context Formatting
- Upgraded `ContextFormatter` to properly append `Personalization: Adjusted based on farm history - <rationale>` exactly when the deterministic engine outputs flag `historically_adjusted`.
- Expanded the AI system instructions (`AIRA_SYSTEM_PROMPT`) mandating the LLM only narrate these provided adjustments, explicitly forbidding it from inventing, overriding, or calculating its own personalizations.

### Step 3: AI Behavior Validation
- Added 6 critical AI behavior validation scenarios ensuring the AI narrator obeys the deterministic boundaries.
- Verified exact numerical output authority, no-personalization transparency, and irrelevant-history ignorance without executing real external LLM API calls.

### Step 4: Full V4 Personalization Integration
- Built and validated a comprehensive E2E integration test proving the complete end-to-end V4 architecture: `Farm History -> Insights -> Deterministic Engines -> Unified Context -> Formatter -> AI Prompt`.
- Proved identical inputs yield uniquely personalized prompts for heavily historical farms while maintaining baseline integrity for normal farms.
- Passed full backend regression suite with 130 successful tests and 0 regressions.
