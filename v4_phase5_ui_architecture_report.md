# V4.5 UI Architecture Report

## 1. Current Frontend Architecture
The AgriNova frontend is built with Next.js (App Router), TypeScript, and Tailwind CSS. It uses a feature-based architecture (`src/features/*`), a custom design token system, and highly animated, glass-morphism components (`src/ui/*`).

## 2. Existing Components We Can Reuse
- **UI Primitives**: `Card` (glass/solid variants), `Badge`, `Button`, `Modal`, `Tooltip`.
- **Forms**: The existing environmental parameter inputs on the `/advisor` page.
- **Layouts**: `FarmDetailPage` header structure and grids.

## 3. Existing API/Service Architecture
- API requests are routed through a typed fetch wrapper in `src/lib/api.ts`.
- Components consume APIs either directly in `useEffect` or via custom hooks (`useAira.ts`, `useDiseaseDetection.ts`).
- **Observation**: Several core features (like `/advisor` and `/detect`) are currently using mocked states (`setTimeout` + static mock data) rather than calling their backend equivalents.

## 4. V4 Backend Endpoints Available
- **Available**: `GET /farms`, `GET /farms/{id}` (Farm Data).
- **Available**: `GET /crops/farm/{id}` (Crop History).
- **Available**: `GET /fertilizer/logs/{crop_id}`, `GET /irrigation/logs/{crop_id}` (Historical Logs).
- **Missing**: There is no direct REST endpoint to fetch `HistoricalInsightsContext` (e.g., `GET /farms/{id}/insights`).
- **Disconnected**: The Fertilizer, Irrigation, and Disease API routers do not accept a `farm_id` parameter to trigger personalization.

## 5. Backend → Frontend Data Contracts
Currently, `historically_adjusted` and `personalization_rationale` successfully flow into the **AI Agronomist Prompt** because `IntelligenceService` bypasses the REST APIs. However, for the **Frontend UI Component** consumption, there is a major contract mismatch (see Section 19).

## 6. V4.5 Proposed Information Architecture
- **Farm Detail Dashboard (`/farms/[id]`)**: Should evolve into a tabbed interface:
  1. **Overview**: Current farm stats and active crops.
  2. **History**: A timeline view of past crops, yields, and aggregated fertilizer/irrigation logs.
  3. **Insights**: A visual dashboard rendering the `HistoricalInsightsContext` (Yield Trends, Input Usage warnings, Disease Patterns).
- **Advisor (`/advisor`)**: Connect to the real `/crops/recommend` endpoint. Introduce a "Farm Context" selector to pass `farm_id`.
- **Disease Detect (`/detect`)**: Connect to the real `/disease/detect` endpoint. 

## 7. Proposed Component Tree
- `FarmDashboardTabs`
  - `FarmOverviewTab`
  - `FarmHistoryTab` (uses `HistoryTimeline`)
  - `FarmInsightsTab` (uses `InsightCard`)
- `RecommendationCard` (Extended)
  - `PersonalizationBadge`
  - `RationaleAlert`

## 8. Proposed Routes
- The existing `/farms/[id]` route will be expanded via internal state tabs (or Next.js parallel/intercepting routes if preferred) to handle History and Insights. No new top-level routes are necessary.

## 9. Proposed Hooks
- `useFarmInsights(farmId)`: Fetches historical insights.
- `useCropRecommendation(farmId)`: Wraps the recommendation API.
- `useFarmHistory(farmId)`: Aggregates logs and past crops.

## 10. Proposed API Services
- Extend `src/lib/api.ts` to include:
  - `historyAPI.getInsights(farmId)`
  - `cropsAPI.recommend(params, farmId)`
  - `fertilizerAPI.recommend(..., farmId)`
  - `diseaseAPI.detect(..., farmId)`

## 11. Personalization Metadata Flow
1. **API Response**: Returns `{ ..., historically_adjusted: true, personalization_rationale: "..." }`.
2. **React State**: Hook exposes these fields to the component.
3. **UI Rendering**: The `RecommendationCard` detects `historically_adjusted === true`, renders a glowing `PersonalizationBadge` ("Tailored for [Farm Name]"), and expands a `RationaleAlert` revealing the exact reasoning to the user.

## 12. Desktop Layout
- **Insights Tab**: 2-column grid of `InsightCard` components (e.g., Yield Trends on left, Disease Patterns on right).
- **Advisor**: Split screen (Parameters on left, dynamically adjusting recommendations on right).

## 13. Mobile Layout
- **Insights Tab**: Single column stacked cards.
- **Advisor**: Wizard-like flow or vertically stacked sections.
- **Rationale**: Accordions that default to collapsed to save vertical screen space.

## 14. Loading / Empty / Error States
- **Loading**: Animated skeleton representations of `InsightCard`.
- **Empty**: A beautifully styled empty state reading "Not enough historical data yet. Log more harvests to unlock AI insights."
- **Error**: Graceful fallback displaying standard non-personalized recommendations if the insights engine fails.

## 15. Accessibility Considerations
- `aria-live="polite"` regions for recommendation updates.
- Explicit text alternatives for glowing "Personalization" icons.
- Keyboard navigable tabs in the Farm Dashboard.

## 16. Components To Create
- `InsightCard`: Displays a specific historical insight (e.g., Seasonal Performance).
- `PersonalizationBadge`: A small, distinct marker for adjusted results.
- `RationaleAlert`: A stylized callout box explaining the adjustment.
- `HistoryTimeline`: Visualizing past crop cycles.

## 17. Components To Modify
- `FarmDetailPage` (convert to tabbed layout).
- `AdvisorPage` (remove static mock, wire real API, render personalization).
- `useDiseaseDetection` (remove static mock, wire real API, render personalization).

## 18. Components To Leave Untouched
- `Aira` (The chat interface requires no frontend changes to support V4, as the context is injected server-side).
- Authentication and User Profile views.
- Global navigation elements.

## 19. Backend/Frontend Contract Risks
**CRITICAL BLOCKERS IDENTIFIED:**
While the Intelligence Engines were upgraded in Phase 3, the **FastAPI Routers** were not fully wired for UI consumption:
1. **Missing Schema Fields**: `CropRecommendation`, `FertilizerRecommendation`, and `IrrigationRecommendation` Pydantic models in `backend/app/schemas/` lack `historically_adjusted` and `personalization_rationale` fields. FastAPI strips these fields from the response dicts before the frontend receives them.
2. **Missing Farm ID**: The `GET /fertilizer/recommend/{crop_name}` and `GET /irrigation/recommend/{crop_name}` routers do not accept a `farm_id` parameter, meaning they cannot trigger the `HistoricalInsightsService`.
3. **Missing Insights Endpoint**: There is no direct API route (e.g., `GET /farms/{id}/insights`) for the frontend to fetch the `HistoricalInsightsContext` for the new Dashboard Insights Tab.
4. **Mocked Frontend**: Key UI flows (`/advisor`, `/detect`) are entirely mocked in the frontend and do not connect to their backend counterparts.

## 20. Recommended Implementation Order
To successfully execute V4.5, we must follow this sequence:
1. **Backend Contract Patch**: Update schemas to include personalization fields. Update recommendation routers to accept `farm_id`. Create a new `GET /farms/{farm_id}/insights` endpoint.
2. **Frontend API Layer**: Implement the actual endpoints in `frontend/src/lib/api.ts`.
3. **Farm Detail UI**: Build the Tabbed Dashboard (Overview, History, Insights).
4. **Insights UI**: Build and populate the `InsightCard` components.
5. **Recommendations UI**: Un-mock the `/advisor` and `/detect` pages, hooking them up to the real backend and rendering the personalization rationale.
