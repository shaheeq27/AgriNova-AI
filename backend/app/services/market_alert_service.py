"""
AgriNova AI — Market Alert Service (V5.3.4).

Triggers market alerts when an active crop's price changes by ±10% or more.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.farm import Farm
from app.services.market_service import MarketService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

MARKET_ALERT_THRESHOLD_PERCENT = 10.0


class MarketAlertService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.market_service = MarketService(db)
        self.notification_service = NotificationService()

    async def check_alerts_for_user(self, user_id: str) -> int:
        """
        Check for market price changes for a user's active crops.
        Generates alerts for changes >= 10% in either direction.
        Returns the number of alerts generated.
        """
        # 1. Fetch user's active crops
        query = select(Farm).options(selectinload(Farm.crops)).where(Farm.user_id == user_id)
        result = await self.db.execute(query)
        farms = result.scalars().all()
        
        active_crop_names = set()
        for farm in farms:
            for crop in farm.crops:
                if crop.status in ("active", "planned"):
                    active_crop_names.add(crop.crop_name.lower())
                    
        if not active_crop_names:
            logger.info("No active crops for user %s, skipping market alerts.", user_id)
            return 0
            
        # 2. Get market summary for these crops
        try:
            summary = await self.market_service.get_dashboard_summary(list(active_crop_names))
        except Exception as e:
            logger.error("Failed to fetch market summary for user %s: %s", user_id, str(e))
            return 0

        if not summary.items:
            return 0
            
        # 3. Check thresholds and trigger alerts
        alerts_created = 0
        for item in summary.items:
            if item.price_change_pct is None:
                continue
                
            if abs(item.price_change_pct) >= MARKET_ALERT_THRESHOLD_PERCENT:
                try:
                    n = await self.notification_service.create_market_alert(
                        db=self.db,
                        user_id=user_id,
                        commodity=item.commodity,
                        market_name=item.market_name,
                        modal_price=item.modal_price,
                        price_change_pct=item.price_change_pct,
                    )
                    if n is not None:
                        alerts_created += 1
                except Exception as e:
                    logger.error("Failed to create market alert for %s: %s", item.commodity, str(e))
                    
        return alerts_created
