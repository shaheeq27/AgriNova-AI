from pydantic import BaseModel

class FarmOverview(BaseModel):
    total_farms: int
    total_acres: float
    active_crops: int
    harvested_crops: int
    total_crops: int
    health_score: float

class CropStatsByStatus(BaseModel):
    planned: int
    active: int
    harvested: int
    abandoned: int

class CropStatsBySeason(BaseModel):
    season_name: str
    count: int

class CropStatistics(BaseModel):
    by_status: CropStatsByStatus
    by_season: list[CropStatsBySeason]
    total_area: float

class ActiveTaskItem(BaseModel):
    id: str
    title: str
    crop_name: str
    farm_name: str
    scheduled_date: str
    priority: str
    is_overdue: bool

class CropHealthItem(BaseModel):
    crop_id: str
    crop_name: str
    farm_name: str
    health_score: float
    current_stage: str
    completed_tasks: int
    total_tasks: int
    disease_count: int

class QuickInsight(BaseModel):
    type: str
    message: str
    severity: str
    action_url: str | None

class DashboardResponse(BaseModel):
    overview: FarmOverview
    crop_statistics: CropStatistics
    active_tasks: list[ActiveTaskItem]
    crop_health: list[CropHealthItem]
    insights: list[QuickInsight]
