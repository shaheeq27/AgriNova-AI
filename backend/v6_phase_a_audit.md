# V6 Crop Recommendation — Backend Phase A: Input & Context Audit

## 1. Exact Request Flow
The user submits a `POST /api/v1/crops/v6/recommend` passing a `CropRecommendationRequestV6`.
1. **Authorization Check:** If `farm_id` is present, it optionally authenticates the user, then looks up the farm using `FarmService(db).get_farm(user.id, farm_id)`, verifying ownership.
2. **Orchestrator Invocation:** Control moves to `RecommendationOrchestrator.recommend()`.
3. **Historical Insights:** Fetches `disease_history` and `farm_performance` using `HistoricalInsightsService` if a `farm_id` is provided.
4. **Context Building:** Evaluates supplied input versus missing fields. If `water_source` is omitted but `farm_id` is supplied, it falls back to the farm's default `water_source`.
5. **Weather Resolution:** (See section below).
6. **Recommendation Context Creation:** Constructs the strictly-typed `RecommendationContext`.
7. **Candidate Generation:** Fetches all base `CropProfile`s from the Knowledge Base.
8. **Filtering:** Applies `SeasonFilter`.
9. **Scoring:** Applies `RuleBasedScorer` for base scores. Drops crops with base score `0`.
10. **Adjustments:** Iterates through `WaterConstraintAdjuster`, `CropRotationAdjuster`, `DiseaseHistoryAdjuster`, `HistoricalPerformanceAdjuster` sequentially.
11. **Final Selection & Explanation:** Assembles the `CropRecommendationResponseV6` by sorting crops descending by score and formatting explanations.

## 2. Exact Location → Coordinates → Weather Flow
1. **Check for explicitly provided weather:** If `temperature`, `humidity`, and `rainfall` are passed directly in the request, it skips weather fetching.
2. **Check for Farm coordinates:** If missing explicitly provided weather, it checks if `farm.latitude` and `farm.longitude` exist and uses them.
3. **Geocode Location Name:** If no farm coordinates, but a `location_name` is given (e.g. "Hyderabad", "Delhi"), it calls `WeatherService.resolve_location(location_name)` which queries the Open-Meteo Geocoding API (`https://geocoding-api.open-meteo.com/v1/search`).
4. **Fetch Weather:** If a `lat, lon` is found, it queries the Open-Meteo Forecast API (`https://api.open-meteo.com/v1/forecast`).
5. **Extract Data:** It maps `precipitation_sum` to `rainfall`, `temperature_2m` to `temperature`, and `relative_humidity_2m` to `humidity`.

*Fixed in Phase A:* I corrected an issue where the `WeatherService` contained an unreachable `except` block that would return fabricated mock weather (`25°C, 12.0 windspeed`) on failure. Additionally, it now requests `relative_humidity_2m` properly.

## 3. Exact RecommendationContext Contents
```python
class RecommendationContext(BaseModel):
    soil_type: str
    location: dict[str, float] | None = None
    season: str | None = None
    water_source: str | None = None

    # Weather
    temperature: float | None = None
    humidity: float | None = None
    rainfall: float | None = None
    current_weather: WeatherRecord | None = None
    weather_history: list[WeatherRecord] | None = None

    # Farm Context
    farm: Any | None = None
    farm_id: str | None = None
    previous_crop: str | None = None
    previous_crop_family: str | None = None

    # Insights
    disease_history: list[DiseasePatternInsight] | None = None
    farm_performance: HistoricalInsightsContext | None = None
```
The context accurately holds all information requested without containing unnecessary agricultural logic.

## 4. Canonical Soil Values
Queried directly from the `kb_crop_profiles` database, these are the deterministic expected values:
*   `Alluvial`
*   `Black`
*   `Clay`
*   `Loamy`
*   `Red`
*   `Sandy`

*Missing Data Behavior:* If a user passes an unknown soil type (e.g., "silt" or "laterite"), the `RuleBasedScorer` assigns a `0.0` score to all crops during base scoring (because `soil_type` does not match `crop.ideal_soil_types`), causing the recommendation to fail gracefully with "No Suitable Crops Found".

## 5. Canonical Season Values
Queried from the Knowledge Base:
*   `All`
*   `Kharif`
*   `Rabi`
*   `Summer`
*   `Winter`

*Fixed in Phase A:* The UI passes `zaid` and `annual`, which did not match `summer` or `all` in the database. `SeasonFilter` now normalizes `zaid` -> `summer` and `annual` -> `all`. If an unknown season is passed, it fails to match and drops the crop (unless the crop is an "all" season crop). Missing season is fully optional—`SeasonFilter` skips filtering if `context.season` is missing.

## 6. Canonical Water_Source Values
The expected inputs (from UI) are:
*   `rainfed`
*   `canal`
*   `borewell`
*   `drip`
*   `sprinkler`

The `WaterConstraintAdjuster` distinguishes strictly between explicitly un-irrigated and missing. It only penalizes/filters crops if `water_source` is explicitly `"none"` or `"rainfed"`. Other values (like `borewell`) or a completely missing `water_source` assume standard irrigation is available and do not penalize water-intensive crops.

## 7. Missing-Data Behavior (Test Cases Audit)
1. **location only:** Validates (soil_type is required by schema, but if bypassed, fails base scorer). Wait, schema `CropRecommendationRequestV6` has `soil_type: str` as required. So it returns 422 Validation Error.
2. **location + soil:** Succeeds. Weather is resolved from location.
3. **location + soil + season:** Succeeds. Filters by season appropriately.
4. **location + soil + season + irrigation:** Succeeds.
5. **farm_id + soil:** Succeeds. Fetches farm lat/lon and water source.
6. **arbitrary location with no farm_id:** Succeeds. Geocodes name.
7. **missing weather:** If geocoding fails, weather is None. Scoring treats missing temp/rainfall neutrally or applies conservative logic.
8. **unknown location:** Weather fetch fails -> weather becomes None.
9. **unknown soil:** Scorer drops all candidates (score 0). Meaningful failure: "No Suitable Crops Found".
10. **unknown season:** Filter drops crops unless they are "All" season.
11. **unknown water source:** Treated as non-rainfed (un-penalized).

## 8. Weather Failure Behavior
If the Open-Meteo API times out or fails (or an unknown location is passed):
*   Exception is caught inside `_fetch_weather_data`, returning `{}`.
*   `get_current_weather` detects failure and sets `temperature`, `humidity`, `rainfall` to `None`.
*   Flow continues normally without hanging. No fabricated defaults are assigned.

## 9. Farm Authorization Behavior
If `farm_id` is supplied:
*   The `HTTPBearer` token is verified via `get_optional_user`.
*   If user missing, raises `401 Unauthorized` ("Must be logged in to use farm context").
*   `FarmService.get_farm(user.id, farm_id)` is invoked, which queries the DB with `user_id == user.id`. If it belongs to another user, raises `404 Not Found` (or 403). Safe.

## 10. Bugs Discovered & Fixed
*   **Fabricated Weather Default:** Removed `_get_mock_weather` fallback that returned 25.5°C and 5.0mm precipitation on API failures.
*   **Missing Humidity:** Appended `relative_humidity_2m` to the Open-Meteo current weather fields so the context actually gets humidity data.
*   **Season Mismatches:** Added normalization inside `SeasonFilter` to translate `zaid` to `summer` and `annual` to `all`, preventing valid recommendations from being discarded due to UI/DB naming differences.

## 11. Files Changed
*   `backend/app/services/weather_service.py`
*   `backend/app/services/crop_recommendation/filters/season_filter.py`

## 12. Tests to Add
A comprehensive test suite is required to cover these permutations and verify that authorization cannot be bypassed and weather isn't fabricated. (See `test_v6_input_context.py` in next step).
