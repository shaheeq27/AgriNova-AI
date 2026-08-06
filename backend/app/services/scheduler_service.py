import datetime
import calendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.farm import Farm
from app.models.crop import Crop
from app.models.timeline import CropTimeline, DailyTask

class SchedulerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily(self, user_id: str, date_str: str) -> dict:
        target_date = datetime.date.fromisoformat(date_str)
        
        # Get tasks — explicit select_from to avoid ambiguous JOIN
        tasks_query = (
            select(DailyTask, Crop, Farm)
            .select_from(DailyTask)
            .join(Crop, DailyTask.crop_id == Crop.id)
            .join(Farm, Crop.farm_id == Farm.id)
            .where(Farm.user_id == user_id, DailyTask.scheduled_date == target_date)
        )
        tasks_res = await self.db.execute(tasks_query)
        
        tasks = []
        for task, crop, farm in tasks_res:
            tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "crop_name": crop.crop_name,
                "farm_name": farm.name,
                "scheduled_date": task.scheduled_date.isoformat(),
                "priority": task.priority,
                "category": task.category,
                "is_completed": task.is_completed
            })
            
        # Get events
        all_events = await self.get_crop_events(user_id)
        events = [e for e in all_events if e['event_date'] == date_str]
        
        return {
            "date": date_str,
            "tasks": tasks,
            "crop_events": events
        }

    async def get_weekly(self, user_id: str, week_start_str: str) -> dict:
        start_date = datetime.date.fromisoformat(week_start_str)
        end_date = start_date + datetime.timedelta(days=6)
        
        days = []
        for i in range(7):
            curr_date = start_date + datetime.timedelta(days=i)
            day_schedule = await self.get_daily(user_id, curr_date.isoformat())
            days.append(day_schedule)
            
        return {
            "week_start": start_date.isoformat(),
            "week_end": end_date.isoformat(),
            "days": days
        }

    async def get_monthly(self, user_id: str, year: int, month: int) -> dict:
        _, num_days = calendar.monthrange(year, month)
        
        days = []
        today_str = datetime.date.today().isoformat()
        for d in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{d:02d}"
            day_schedule = await self.get_daily(user_id, date_str)
            
            tasks = day_schedule['tasks']
            events = day_schedule['crop_events']
            
            has_overdue = any(
                not t['is_completed'] and t['scheduled_date'] < today_str
                for t in tasks
            )
            
            days.append({
                "date": date_str,
                "task_count": len(tasks),
                "event_count": len(events),
                "has_overdue": has_overdue
            })
            
        return {
            "year": year,
            "month": month,
            "days": days
        }

    async def get_crop_events(self, user_id: str) -> list[dict]:
        events = []
        
        # Crop planting/harvest events
        crops_query = (
            select(Crop, Farm)
            .select_from(Crop)
            .join(Farm, Crop.farm_id == Farm.id)
            .where(Farm.user_id == user_id)
        )
        crops_res = await self.db.execute(crops_query)
        
        for crop, farm in crops_res:
            if crop.planting_date:
                events.append({
                    "crop_id": crop.id,
                    "crop_name": crop.crop_name,
                    "farm_name": farm.name,
                    "event_type": "planting",
                    "event_date": crop.planting_date.isoformat(),
                    "stage_name": None
                })
            if crop.expected_harvest_date:
                events.append({
                    "crop_id": crop.id,
                    "crop_name": crop.crop_name,
                    "farm_name": farm.name,
                    "event_type": "harvest",
                    "event_date": crop.expected_harvest_date.isoformat(),
                    "stage_name": None
                })
                
        # Timeline stage start events
        stages_query = (
            select(CropTimeline, Crop, Farm)
            .select_from(CropTimeline)
            .join(Crop, CropTimeline.crop_id == Crop.id)
            .join(Farm, Crop.farm_id == Farm.id)
            .where(Farm.user_id == user_id)
        )
        stages_res = await self.db.execute(stages_query)
        
        for stage, crop, farm in stages_res:
            if stage.start_date:
                events.append({
                    "crop_id": crop.id,
                    "crop_name": crop.crop_name,
                    "farm_name": farm.name,
                    "event_type": "stage_start",
                    "event_date": stage.start_date.isoformat(),
                    "stage_name": stage.stage_name
                })
                
        return events
