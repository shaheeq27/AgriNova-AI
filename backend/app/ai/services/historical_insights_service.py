"""
AgriNova AI — Historical Insights Service.

Generates deterministic, lightweight insights from existing farm history
without executing a secondary LLM call.
"""

from collections import defaultdict
from app.ai.schemas.context import FarmHistoryContext, HistoricalInsights

class HistoricalInsightsService:
    """Extracts structured insights from FarmHistoryContext."""

    def generate_insights(self, history: FarmHistoryContext | None) -> HistoricalInsights:
        """
        Generate deterministic insights based on historical farm data.
        """
        insights = HistoricalInsights()

        if not history:
            return insights

        successful = []
        for crop in history.past_crops:
            if crop.status == "harvested" and crop.yield_amount is not None and crop.yield_amount > 0:
                name = crop.crop_name
                if crop.variety:
                    name += f" ({crop.variety})"
                successful.append(name)

        insights.successful_crops = list(dict.fromkeys(successful))

        disease_counts = defaultdict(int)
        for d in history.recent_diseases:
            name = d.split(" — ")[0].strip()
            disease_counts[name] += 1

        recurring = []
        for name, count in disease_counts.items():
            if count > 1:
                recurring.append(name)
        insights.recurring_diseases = recurring

        insights.seasonal_crop_patterns = history.seasonal_patterns.copy()

        yield_obs = defaultdict(list)
        for crop in history.past_crops:
            if crop.yield_amount is not None and crop.yield_amount > 0 and crop.yield_unit:
                obs = f"{crop.yield_amount} {crop.yield_unit}"
                yield_obs[crop.crop_name].append(obs)

        yield_summaries = []
        for crop_name, obs_list in yield_obs.items():
            yield_summaries.append(f"{crop_name}: {', '.join(obs_list)}")

        insights.historical_yield_observations = yield_summaries

        return insights

    async def compute_insights_context(self, db, farm_id: str):
        """Computes deterministic historical insights into Phase 2 models."""
        from app.repositories.history_repo import HistoryRepository
        from app.ai.schemas.historical_analysis import (
            CropPerformanceInsight, SeasonalPerformanceInsight,
            DiseasePatternInsight, InputUsageInsight, YieldTrendInsight,
            HistoricalInsightsContext
        )

        repo = HistoryRepository(db)
        ctx = HistoricalInsightsContext()

        crops = await repo.get_crop_history(farm_id)
        if not crops:
            return ctx

        def get_conf(n: int) -> float:
            if n >= 4: return 0.95
            if n == 3: return 0.8
            if n == 2: return 0.6
            if n == 1: return 0.3
            return 0.0

        diseases = await repo.get_disease_history(farm_id)
        ferts = await repo.get_fertilizer_history(farm_id)
        irrs = await repo.get_irrigation_history(farm_id)

        # Pre-compute input & disease counts per crop_id
        crop_disease_counts = defaultdict(int)
        crop_fert_counts = defaultdict(int)
        crop_irr_counts = defaultdict(int)

        for d in diseases:
            crop_disease_counts[d["crop_id"]] += 1
        for f in ferts:
            crop_fert_counts[f["crop_id"]] += 1
        for i in irrs:
            crop_irr_counts[i["crop_id"]] += 1

        # --- Crop Performance & Seasonal & Yield Trends ---
        crop_perf = defaultdict(lambda: {
            "seasons": set(), "observed": 0, "harvested": 0, "yields": [],
            "diseases": 0, "fertilizer": 0, "irrigation": 0
        })

        season_perf = defaultdict(lambda: {
            "observed": 0, "harvested": 0, "yields": []
        })

        trend_perf = defaultdict(list)

        for c in crops:
            key = (c.crop_name, c.variety, c.yield_unit)
            perf = crop_perf[key]
            perf["seasons"].add(c.season)
            perf["observed"] += 1
            perf["diseases"] += crop_disease_counts.get(c.id, 0)
            perf["fertilizer"] += crop_fert_counts.get(c.id, 0)
            perf["irrigation"] += crop_irr_counts.get(c.id, 0)

            if c.status == "harvested":
                perf["harvested"] += 1
                if c.yield_amount is not None and c.yield_amount > 0:
                    perf["yields"].append(c.yield_amount)
                    trend_date = c.actual_harvest_date or c.expected_harvest_date or c.planting_date
                    trend_perf[(c.crop_name, c.yield_unit)].append((trend_date, c.yield_amount))

            s_key = (c.season, c.yield_unit)
            s_perf = season_perf[s_key]
            s_perf["observed"] += 1
            if c.status == "harvested":
                s_perf["harvested"] += 1
                if c.yield_amount is not None and c.yield_amount > 0:
                    s_perf["yields"].append(c.yield_amount)

        for (c_name, var, unit), p in crop_perf.items():
            obs = p["observed"]
            y_arr = p["yields"]
            ctx.crop_performance.append(CropPerformanceInsight(
                crop_name=c_name,
                variety=var,
                seasons_observed=list(p["seasons"]),
                crops_observed=obs,
                harvested_count=p["harvested"],
                average_yield=sum(y_arr)/len(y_arr) if y_arr else None,
                yield_unit=unit if y_arr else None,
                best_yield=max(y_arr) if y_arr else None,
                worst_yield=min(y_arr) if y_arr else None,
                disease_records=p["diseases"],
                fertilizer_applications=p["fertilizer"],
                irrigation_applications=p["irrigation"],
                confidence=get_conf(obs)
            ))

        for (season, unit), p in season_perf.items():
            obs = p["observed"]
            y_arr = p["yields"]
            ctx.seasonal_performance.append(SeasonalPerformanceInsight(
                season=season,
                crops_observed=obs,
                harvested_crops=p["harvested"],
                average_yield=sum(y_arr)/len(y_arr) if y_arr else None,
                yield_unit=unit if y_arr else None,
                confidence=get_conf(obs)
            ))

        for (c_name, unit), obs_list in trend_perf.items():
            valid_obs = [x for x in obs_list if x[0] is not None]
            valid_obs.sort(key=lambda x: x[0])
            n = len(valid_obs)
            y_arr = [x[1] for x in valid_obs]

            trend_dir = None
            if n >= 2:
                mid = n // 2
                old_avg = sum(y_arr[:mid]) / mid
                new_avg = sum(y_arr[mid:]) / (n - mid)

                if old_avg > 0:
                    change = (new_avg - old_avg) / old_avg
                    if change > 0.05: trend_dir = "increasing"
                    elif change < -0.05: trend_dir = "decreasing"
                    else: trend_dir = "stable"
                else:
                    trend_dir = "stable"

            ctx.yield_trends.append(YieldTrendInsight(
                crop_name=c_name,
                yield_unit=unit,
                observations=n,
                average_yield=sum(y_arr)/n if n else None,
                highest_yield=max(y_arr) if n else None,
                lowest_yield=min(y_arr) if n else None,
                trend_direction=trend_dir,
                confidence=get_conf(n)
            ))

        # --- Disease Patterns ---
        d_perf = defaultdict(lambda: {
            "occ": 0, "res": 0, "act": 0, "severities": defaultdict(int), "treatments": defaultdict(int)
        })
        for d in diseases:
            c_name = d.get("crop_name", f"Crop-{d.get('crop_id')}")
            key = (d["disease_name"], c_name)
            p = d_perf[key]
            p["occ"] += 1
            if d.get("status") == "resolved": p["res"] += 1
            elif d.get("status") == "active": p["act"] += 1
            if d.get("severity"): p["severities"][d["severity"]] += 1
            if d.get("treatment_applied"): p["treatments"][d["treatment_applied"]] += 1

        for (d_name, c_name), p in d_perf.items():
            obs = p["occ"]
            com_sev = max(p["severities"].items(), key=lambda x: x[1])[0] if p["severities"] else None
            com_trt = max(p["treatments"].items(), key=lambda x: x[1])[0] if p["treatments"] else None
            ctx.disease_patterns.append(DiseasePatternInsight(
                disease_name=d_name,
                affected_crop=c_name,
                occurrence_count=obs,
                resolved_count=p["res"],
                active_count=p["act"],
                common_severity=com_sev,
                treatment_observed=com_trt,
                confidence=get_conf(obs)
            ))

        # --- Input Usage (Fertilizer & Irrigation) ---
        i_perf = defaultdict(lambda: {
            "count": 0, "qty": 0.0, "methods": defaultdict(int)
        })

        for f in ferts:
            c_name = f.get("crop_name", f"Crop-{f.get('crop_id')}")
            f_type = f.get("fertilizer_type", "Fertilizer")
            key = (f_type, c_name, f.get("unit"))
            p = i_perf[key]
            p["count"] += 1
            if f.get("quantity"): p["qty"] += f["quantity"]
            if f.get("application_method"): p["methods"][f["application_method"]] += 1

        for i in irrs:
            c_name = i.get("crop_name", f"Crop-{i.get('crop_id')}")
            # missing unit fallback
            unit = "liters"
            key = ("Irrigation", c_name, unit)
            p = i_perf[key]
            p["count"] += 1
            if i.get("water_amount_liters"): p["qty"] += i["water_amount_liters"]
            if i.get("method"): p["methods"][i["method"]] += 1

        for (itype, c_name, unit), p in i_perf.items():
            obs = p["count"]
            com_meth = max(p["methods"].items(), key=lambda x: x[1])[0] if p["methods"] else None
            ctx.input_usage.append(InputUsageInsight(
                input_type=itype,
                crop_name=c_name,
                application_count=obs,
                total_quantity=p["qty"] if p["qty"] > 0 else None,
                quantity_unit=unit if p["qty"] > 0 else None,
                common_application_method=com_meth,
                confidence=get_conf(obs)
            ))

        return ctx
