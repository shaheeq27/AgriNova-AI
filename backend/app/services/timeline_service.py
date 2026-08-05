"""
AgriNova AI — Timeline Service.

Generates crop timelines from Knowledge Base growth stages
and creates daily tasks for each stage.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import GrowthStage
from app.models.timeline import CropTimeline, DailyTask
from app.repositories.crop_repo import CropRepository
from app.schemas.crop import TimelineStageResponse, TimelineResponse, DailyTaskResponse


# Task templates per growth stage
STAGE_TASKS = {
    "germination": [
        {"title": "Monitor seed germination", "category": "monitoring", "priority": "high"},
        {"title": "Ensure adequate soil moisture", "category": "watering", "priority": "high"},
        {"title": "Check for pest activity", "category": "monitoring", "priority": "medium"},
    ],
    "vegetative": [
        {"title": "Apply fertilizer (as per schedule)", "category": "fertilizer", "priority": "high"},
        {"title": "Regular watering", "category": "watering", "priority": "high"},
        {"title": "Weeding and soil loosening", "category": "weeding", "priority": "medium"},
        {"title": "Monitor plant growth", "category": "monitoring", "priority": "medium"},
    ],
    "flowering": [
        {"title": "Reduce nitrogen fertilizer", "category": "fertilizer", "priority": "high"},
        {"title": "Monitor for pest and disease", "category": "monitoring", "priority": "high"},
        {"title": "Maintain consistent watering", "category": "watering", "priority": "high"},
    ],
    "fruiting": [
        {"title": "Apply potassium-rich fertilizer", "category": "fertilizer", "priority": "high"},
        {"title": "Support heavy fruit/grain heads", "category": "general", "priority": "medium"},
        {"title": "Monitor for disease symptoms", "category": "monitoring", "priority": "high"},
        {"title": "Adjust irrigation as needed", "category": "watering", "priority": "medium"},
    ],
    "maturation": [
        {"title": "Reduce watering gradually", "category": "watering", "priority": "medium"},
        {"title": "Monitor crop maturity indicators", "category": "monitoring", "priority": "high"},
        {"title": "Prepare harvesting equipment", "category": "general", "priority": "medium"},
    ],
    "harvest": [
        {"title": "Harvest at optimal maturity", "category": "general", "priority": "high"},
        {"title": "Post-harvest handling and storage", "category": "general", "priority": "high"},
        {"title": "Record yield and quality data", "category": "monitoring", "priority": "medium"},
    ],
}

DEFAULT_TASKS = [
    {"title": "Monitor crop health", "category": "monitoring", "priority": "medium"},
    {"title": "Check soil moisture", "category": "watering", "priority": "medium"},
]


async def generate_timeline(
    db: AsyncSession,
    crop_id: str,
    crop_name: str,
    planting_date: date,
) -> list[TimelineStageResponse]:
    """Generate a crop timeline from KB growth stages and create daily tasks.

    Args:
        db: Database session
        crop_id: The crop record ID
        crop_name: Name of the crop (to look up KB stages)
        planting_date: When the crop was planted

    Returns:
        List of created timeline stages
    """
    repo = CropRepository(db)

    # Fetch growth stages from Knowledge Base
    result = await db.execute(
        select(GrowthStage)
        .where(GrowthStage.crop_name == crop_name)
        .order_by(GrowthStage.stage_order)
    )
    kb_stages = list(result.scalars().all())

    if not kb_stages:
        # Fallback: create generic stages
        kb_stages = _generic_stages(crop_name)

    stages = []
    current_date = planting_date

    for kb_stage in kb_stages:
        duration = kb_stage.duration_days if hasattr(kb_stage, "duration_days") else kb_stage["duration_days"]
        stage_name = kb_stage.stage_name if hasattr(kb_stage, "stage_name") else kb_stage["stage_name"]
        stage_order = kb_stage.stage_order if hasattr(kb_stage, "stage_order") else kb_stage["stage_order"]

        end_date = current_date + timedelta(days=duration)

        # Create timeline stage
        timeline_stage = CropTimeline(
            crop_id=crop_id,
            stage_name=stage_name,
            stage_order=stage_order,
            start_date=current_date,
            end_date=end_date,
            status="active" if stage_order == 1 else "upcoming",
        )
        timeline_stage = await repo.create_timeline_stage(timeline_stage)

        # Create daily tasks for this stage
        stage_key = stage_name.lower().strip()
        task_templates = STAGE_TASKS.get(stage_key, DEFAULT_TASKS)

        # Spread tasks across the stage duration
        task_interval = max(1, duration // len(task_templates))
        for i, tmpl in enumerate(task_templates):
            task_date = current_date + timedelta(days=i * task_interval)
            if task_date > end_date:
                task_date = end_date

            task = DailyTask(
                timeline_id=timeline_stage.id,
                crop_id=crop_id,
                title=tmpl["title"],
                description=f"{tmpl['title']} during {stage_name} stage of {crop_name}",
                scheduled_date=task_date,
                priority=tmpl["priority"],
                category=tmpl["category"],
            )
            await repo.create_task(task)

        stages.append(TimelineStageResponse.model_validate(timeline_stage))
        current_date = end_date

    await repo.commit()
    return stages


async def get_timeline(db: AsyncSession, crop_id: str) -> TimelineResponse:
    """Get the full timeline for a crop."""
    repo = CropRepository(db)
    stages = await repo.get_timeline(crop_id)

    stage_responses = [TimelineStageResponse.model_validate(s) for s in stages]

    total_days = 0
    current_stage = None
    today = date.today()

    for s in stages:
        total_days += (s.end_date - s.start_date).days
        if s.start_date <= today <= s.end_date:
            current_stage = s.stage_name

    return TimelineResponse(
        stages=stage_responses,
        total_days=total_days,
        current_stage=current_stage,
    )


def _generic_stages(crop_name: str) -> list[dict]:
    """Fallback generic stages if KB has no data for this crop."""
    return [
        {"stage_name": "Germination", "stage_order": 1, "duration_days": 14},
        {"stage_name": "Vegetative", "stage_order": 2, "duration_days": 30},
        {"stage_name": "Flowering", "stage_order": 3, "duration_days": 21},
        {"stage_name": "Fruiting", "stage_order": 4, "duration_days": 28},
        {"stage_name": "Maturation", "stage_order": 5, "duration_days": 21},
        {"stage_name": "Harvest", "stage_order": 6, "duration_days": 7},
    ]
