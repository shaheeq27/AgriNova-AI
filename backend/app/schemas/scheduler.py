from pydantic import BaseModel

class SchedulerTask(BaseModel):
    id: str
    title: str
    description: str | None
    crop_name: str
    farm_name: str
    scheduled_date: str
    priority: str
    category: str
    is_completed: bool

class CropEvent(BaseModel):
    crop_id: str
    crop_name: str
    farm_name: str
    event_type: str
    event_date: str
    stage_name: str | None

class DailySchedule(BaseModel):
    date: str
    tasks: list[SchedulerTask]
    crop_events: list[CropEvent]

class WeeklySchedule(BaseModel):
    week_start: str
    week_end: str
    days: list[DailySchedule]

class MonthlyCalendar(BaseModel):
    year: int
    month: int
    days: list[dict]
