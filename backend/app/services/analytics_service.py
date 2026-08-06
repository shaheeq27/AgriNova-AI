from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from app.models.farm import Farm
from app.models.crop import Crop
from app.models.timeline import CropTimeline, DailyTask

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, user_id: str) -> dict:
        overview = await self.get_farm_overview(user_id)
        crop_statistics = await self.get_crop_statistics(user_id)
        active_tasks = await self.get_active_tasks(user_id)
        crop_health = await self.get_crop_health(user_id)
        insights = await self.get_insights(user_id)

        return {
            "overview": overview,
            "crop_statistics": crop_statistics,
            "active_tasks": active_tasks,
            "crop_health": crop_health,
            "insights": insights
        }

    async def get_farm_overview(self, user_id: str, farm_id: str | None = None) -> dict:
        farm_query = select(func.count(Farm.id), func.sum(Farm.total_area_acres)).where(Farm.user_id == user_id)
        if farm_id:
            farm_query = farm_query.where(Farm.id == farm_id)
            
        farm_result = await self.db.execute(farm_query)
        total_farms, total_acres = farm_result.first()
        total_farms = total_farms or 0
        total_acres = float(total_acres or 0.0)

        crop_query = select(
            func.count(Crop.id),
            func.sum(case((Crop.status == 'active', 1), else_=0)),
            func.sum(case((Crop.status == 'harvested', 1), else_=0))
        ).join(Farm).where(Farm.user_id == user_id)
        
        if farm_id:
            crop_query = crop_query.where(Farm.id == farm_id)
            
        crop_result = await self.db.execute(crop_query)
        total_crops, active_crops, harvested_crops = crop_result.first()
        
        task_query = select(
            func.count(DailyTask.id),
            func.sum(case((DailyTask.is_completed == True, 1), else_=0))
        ).select_from(DailyTask).join(Crop).join(Farm).where(Farm.user_id == user_id)
        
        if farm_id:
            task_query = task_query.where(Farm.id == farm_id)
            
        task_result = await self.db.execute(task_query)
        total_tasks, completed_tasks = task_result.first()
        
        health_score = 100.0
        if total_tasks and total_tasks > 0:
            health_score = (completed_tasks / total_tasks) * 100.0

        return {
            "total_farms": total_farms,
            "total_acres": total_acres,
            "active_crops": active_crops or 0,
            "harvested_crops": harvested_crops or 0,
            "total_crops": total_crops or 0,
            "health_score": round(health_score, 2)
        }

    async def get_crop_statistics(self, user_id: str, farm_id: str | None = None) -> dict:
        status_query = select(Crop.status, func.count(Crop.id)).join(Farm).where(Farm.user_id == user_id)
        if farm_id:
            status_query = status_query.where(Crop.farm_id == farm_id)
        status_query = status_query.group_by(Crop.status)
        status_results = await self.db.execute(status_query)
        
        status_counts = {"planned": 0, "active": 0, "harvested": 0, "abandoned": 0}
        for status, count in status_results:
            if status in status_counts:
                status_counts[status] = count

        season_query = select(Crop.season, func.count(Crop.id)).join(Farm).where(Farm.user_id == user_id)
        if farm_id:
            season_query = season_query.where(Crop.farm_id == farm_id)
        season_query = season_query.group_by(Crop.season)
        season_results = await self.db.execute(season_query)
        
        by_season = [{"season_name": s, "count": c} for s, c in season_results]

        area_query = select(func.sum(Crop.area_acres)).join(Farm).where(Farm.user_id == user_id)
        if farm_id:
            area_query = area_query.where(Crop.farm_id == farm_id)
        area_result = await self.db.execute(area_query)
        total_area = float(area_result.scalar() or 0.0)

        return {
            "by_status": status_counts,
            "by_season": by_season,
            "total_area": total_area
        }

    async def get_active_tasks(self, user_id: str, limit: int = 10) -> list[dict]:
        query = (
            select(DailyTask, Crop, Farm)
            .select_from(DailyTask)
            .join(CropTimeline, DailyTask.timeline_id == CropTimeline.id)
            .join(Crop, DailyTask.crop_id == Crop.id)
            .join(Farm, Crop.farm_id == Farm.id)
            .where(Farm.user_id == user_id, DailyTask.is_completed == False)
            .order_by(DailyTask.scheduled_date.asc())
            .limit(limit)
        )
        results = await self.db.execute(query)
        
        tasks = []
        today = date.today()
        for task, crop, farm in results:
            tasks.append({
                "id": task.id,
                "title": task.title,
                "crop_name": crop.crop_name,
                "farm_name": farm.name,
                "scheduled_date": task.scheduled_date.isoformat(),
                "priority": task.priority,
                "is_overdue": task.scheduled_date < today
            })
        return tasks

    async def get_crop_health(self, user_id: str) -> list[dict]:
        crops_query = select(Crop, Farm).join(Farm).where(Farm.user_id == user_id, Crop.status == 'active')
        crops_result = await self.db.execute(crops_query)
        
        health_items = []
        for crop, farm in crops_result:
            task_query = select(
                func.count(DailyTask.id),
                func.sum(case((DailyTask.is_completed == True, 1), else_=0))
            ).where(DailyTask.crop_id == crop.id)
            task_res = await self.db.execute(task_query)
            total_tasks, completed_tasks = task_res.first()
            total_tasks = total_tasks or 0
            completed_tasks = completed_tasks or 0
            
            health_score = 100.0
            if total_tasks > 0:
                health_score = (completed_tasks / total_tasks) * 100.0
                
            stage_query = select(CropTimeline.stage_name).where(
                CropTimeline.crop_id == crop.id, CropTimeline.status == 'active'
            ).order_by(CropTimeline.stage_order.desc()).limit(1)
            stage_res = await self.db.execute(stage_query)
            current_stage = stage_res.scalar() or "Unknown"
            
            health_items.append({
                "crop_id": crop.id,
                "crop_name": crop.crop_name,
                "farm_name": farm.name,
                "health_score": round(health_score, 2),
                "current_stage": current_stage,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
                "disease_count": 0
            })
            
        return health_items

    async def get_insights(self, user_id: str) -> list[dict]:
        insights = []
        
        overdue_query = (
            select(func.count(DailyTask.id))
            .select_from(DailyTask)
            .join(Crop, DailyTask.crop_id == Crop.id)
            .join(Farm, Crop.farm_id == Farm.id)
            .where(
                Farm.user_id == user_id, 
                DailyTask.is_completed == False, 
                DailyTask.scheduled_date < date.today()
            )
        )
        overdue_res = await self.db.execute(overdue_query)
        overdue_count = overdue_res.scalar() or 0
        if overdue_count > 0:
            insights.append({
                "type": "overdue_tasks",
                "message": f"You have {overdue_count} overdue tasks",
                "severity": "warning",
                "action_url": "/scheduler"
            })
            
        health_data = await self.get_crop_health(user_id)
        for health in health_data:
            if health['total_tasks'] > 0 and health['completed_tasks'] == 0:
                insights.append({
                    "type": "needs_attention",
                    "message": f"Crop {health['crop_name']} needs attention",
                    "severity": "warning",
                    "action_url": f"/crops/{health['crop_id']}"
                })
        
        crops_query = select(Crop).join(Farm).where(
            Farm.user_id == user_id, 
            Crop.status == 'active',
            Crop.expected_harvest_date != None
        )
        crops_res = await self.db.execute(crops_query)
        today = date.today()
        for crop in crops_res.scalars():
            if crop.expected_harvest_date and (crop.expected_harvest_date - today).days <= 7:
                insights.append({
                    "type": "harvest_ready",
                    "message": f"Crop {crop.crop_name} is ready for harvest",
                    "severity": "info",
                    "action_url": f"/crops/{crop.id}"
                })
                
        return insights
