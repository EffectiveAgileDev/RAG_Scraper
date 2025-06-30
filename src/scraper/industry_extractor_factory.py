"""Factory for creating industry-specific extractors."""
from typing import Optional
from importlib import import_module
from src.config.industry_config import IndustryConfig


def get_industry_extractor(industry: str) -> Optional[object]:
    """Get the appropriate extractor instance for an industry.
    
    Args:
        industry: The industry name
        
    Returns:
        Extractor instance or None if industry is invalid
    """
    config = IndustryConfig()
    extractor_class_name = config.get_extractor_class(industry)
    
    if not extractor_class_name:
        return None
    
    try:
        # Map extractor classes to their modules
        # For now, RestaurantScraper exists, others will be added later
        if extractor_class_name == "RestaurantScraper":
            from src.scraper.restaurant_scraper import RestaurantScraper
            return RestaurantScraper()
        elif extractor_class_name == "RealEstateScraper":
            # Placeholder - will be implemented later
            class RealEstateScraper:
                pass
            return RealEstateScraper()
        elif extractor_class_name == "MedicalScraper":
            # Placeholder - will be implemented later
            class MedicalScraper:
                pass
            return MedicalScraper()
        else:
            # Try dynamic import for future extractors
            module_name = f"src.scraper.industries.{industry.lower().replace(' ', '_').replace('/', '_')}_scraper"
            module = import_module(module_name)
            extractor_class = getattr(module, extractor_class_name)
            return extractor_class()
    except (ImportError, AttributeError):
        return None