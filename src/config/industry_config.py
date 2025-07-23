"""Industry configuration management for RAG Scraper."""
import json
import os
from typing import Dict, List, Optional, Any


class IndustryConfig:
    """Manages industry configurations and settings."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize with default industries and optional custom config."""
        self.industries = {}
        self.status_config = {}
        self._load_default_industries()
        self._load_status_config()

        if config_file:
            self._load_custom_config(config_file)

    def _load_default_industries(self):
        """Load the default 12 industries with their configurations."""
        self.industries = {
            "Restaurant": {
                "name": "Restaurant",
                "help_text": "Extracts menu items, hours, location, ambiance, and dining options",
                "extractor_class": "RestaurantScraper",
                "categories": [
                    "menu",
                    "hours",
                    "location",
                    "ambiance",
                    "dining_options",
                ],
            },
            "Real Estate": {
                "name": "Real Estate",
                "help_text": "Extracts property listings, agent info, prices, and features",
                "extractor_class": "RealEstateScraper",
                "categories": ["listings", "agents", "prices", "features", "location"],
            },
            "Medical": {
                "name": "Medical",
                "help_text": "Extracts services, insurance info, doctor profiles, and hours",
                "extractor_class": "MedicalScraper",
                "categories": [
                    "services",
                    "insurance",
                    "doctors",
                    "hours",
                    "appointments",
                ],
            },
            "Dental": {
                "name": "Dental",
                "help_text": "Extracts dental services, insurance, dentist profiles, and hours",
                "extractor_class": "DentalScraper",
                "categories": [
                    "services",
                    "insurance",
                    "dentists",
                    "hours",
                    "procedures",
                ],
            },
            "Furniture": {
                "name": "Furniture",
                "help_text": "Extracts product catalogs, prices, materials, and dimensions",
                "extractor_class": "FurnitureScraper",
                "categories": [
                    "products",
                    "prices",
                    "materials",
                    "dimensions",
                    "delivery",
                ],
            },
            "Hardware / Home Improvement": {
                "name": "Hardware / Home Improvement",
                "help_text": "Extracts tools, materials, prices, and project guides",
                "extractor_class": "HardwareScraper",
                "categories": ["tools", "materials", "prices", "guides", "services"],
            },
            "Vehicle Fuel": {
                "name": "Vehicle Fuel",
                "help_text": "Extracts fuel prices, station locations, and services",
                "extractor_class": "VehicleFuelScraper",
                "categories": [
                    "fuel_prices",
                    "locations",
                    "services",
                    "hours",
                    "payment",
                ],
            },
            "Vehicle Sales": {
                "name": "Vehicle Sales",
                "help_text": "Extracts vehicle inventory, prices, specs, and financing",
                "extractor_class": "VehicleSalesScraper",
                "categories": [
                    "inventory",
                    "prices",
                    "specifications",
                    "financing",
                    "dealers",
                ],
            },
            "Vehicle Repair / Towing": {
                "name": "Vehicle Repair / Towing",
                "help_text": "Extracts services, prices, coverage areas, and availability",
                "extractor_class": "VehicleRepairScraper",
                "categories": [
                    "services",
                    "prices",
                    "coverage",
                    "availability",
                    "certifications",
                ],
            },
            "Ride Services": {
                "name": "Ride Services",
                "help_text": "Extracts service areas, pricing, vehicle types, and availability",
                "extractor_class": "RideServicesScraper",
                "categories": [
                    "areas",
                    "pricing",
                    "vehicles",
                    "availability",
                    "drivers",
                ],
            },
            "Shop at Home": {
                "name": "Shop at Home",
                "help_text": "Extracts products, delivery options, prices, and policies",
                "extractor_class": "ShopAtHomeScraper",
                "categories": ["products", "delivery", "prices", "policies", "returns"],
            },
            "Fast Food": {
                "name": "Fast Food",
                "help_text": "Extracts menu items, prices, locations, and hours",
                "extractor_class": "FastFoodScraper",
                "categories": ["menu", "prices", "locations", "hours", "promotions"],
            },
        }

    def _load_custom_config(self, config_file: str):
        """Load custom configuration from JSON file."""
        with open(config_file, "r") as f:
            custom_config = json.load(f)

        # Update existing industries with custom settings
        for industry, settings in custom_config.items():
            if industry in self.industries:
                self.industries[industry].update(settings)

    def get_industry_list(self) -> List[str]:
        """Return sorted list of available industries."""
        return sorted(self.industries.keys())

    def get_industry_config(self, industry: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific industry."""
        return self.industries.get(industry)

    def get_help_text(self, industry: str) -> str:
        """Get help text for a specific industry."""
        config = self.get_industry_config(industry)
        if config:
            return config.get("help_text", "")
        return ""

    def validate_industry(self, industry: str) -> bool:
        """Check if an industry is valid."""
        if not industry:
            return False
        return industry in self.industries

    def get_extractor_class(self, industry: str) -> Optional[str]:
        """Get the extractor class name for an industry."""
        config = self.get_industry_config(industry)
        if config:
            return config.get("extractor_class")
        return None

    def get_industry_categories(self, industry: str) -> List[str]:
        """Get the categories for an industry."""
        config = self.get_industry_config(industry)
        if config:
            return config.get("categories", [])
        return []

    def _load_status_config(self):
        """Load industry status configuration from JSON file."""
        status_file = os.path.join(os.path.dirname(__file__), "industry_status.json")

        try:
            if os.path.exists(status_file):
                with open(status_file, "r") as f:
                    self.status_config = json.load(f)
            else:
                # Fallback to default status config if file doesn't exist
                self._create_default_status_config()
        except (json.JSONDecodeError, IOError):
            # Handle invalid JSON or file read errors gracefully
            self._create_default_status_config()

    def _create_default_status_config(self):
        """Create default status configuration when file is missing or invalid."""
        self.status_config = {
            "available_industries": [
                {
                    "name": industry_name,
                    "status": "coming_soon",
                    "description": industry_data.get("help_text", ""),
                    "eta": "TBD",
                }
                for industry_name, industry_data in self.industries.items()
            ],
            "status_definitions": {
                "available": "Fully functional",
                "beta": "Available with limited features",
                "coming_soon": "In development",
                "planned": "Future roadmap item",
            },
        }

    def get_all_industries_with_status(self) -> List[Dict[str, Any]]:
        """Get all industries with their status information."""
        return self.status_config.get("available_industries", [])

    def get_industries_by_status(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get industries grouped by their status."""
        industries_by_status = {
            "available": [],
            "beta": [],
            "coming_soon": [],
            "planned": [],
        }

        all_industries = self.get_all_industries_with_status()

        for industry in all_industries:
            status = industry.get("status", "coming_soon")
            if status in industries_by_status:
                industries_by_status[status].append(industry)

        return industries_by_status

    def filter_industries_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter industries by a specific status."""
        all_industries = self.get_all_industries_with_status()
        return [
            industry for industry in all_industries if industry.get("status") == status
        ]

    def get_status_definitions(self) -> Dict[str, str]:
        """Get the status definitions dictionary."""
        return self.status_config.get("status_definitions", {})

    def get_industry_status(self, industry_name: str) -> Optional[str]:
        """Get the status for a specific industry by name."""
        all_industries = self.get_all_industries_with_status()

        for industry in all_industries:
            if industry.get("name") == industry_name:
                return industry.get("status")

        return None
