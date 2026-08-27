"""
AgriNova AI — Market Provider Factory (V5.1).

Instantiates the correct market provider based on environment config.
"""

from app.core.config import settings
from app.integrations.market.base import BaseMarketProvider
from app.integrations.market.data_gov_in import DataGovProvider
from app.integrations.market.demo import DemoMarketProvider


def get_market_provider() -> BaseMarketProvider:
    """Factory to get the configured market provider.
    
    Defaults to DemoMarketProvider if the configured provider fails
    to initialize (e.g., missing API keys) to ensure the application
    keeps running gracefully.
    """
    provider_name = settings.MARKET_DATA_PROVIDER.lower()
    
    if provider_name == "data_gov_in":
        try:
            return DataGovProvider()
        except Exception as exc:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "Failed to initialize DataGovProvider: %s. Falling back to DemoProvider.", 
                exc
            )
            return DemoMarketProvider()
            
    # Default to demo for "demo" or unknown
    return DemoMarketProvider()
