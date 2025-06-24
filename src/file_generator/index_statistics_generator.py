"""Index statistics generator for comprehensive statistical analysis of scraped data."""
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

from src.scraper.multi_strategy_scraper import RestaurantData


class IndexStatisticsGenerator:
    """Generates comprehensive statistics for index files."""

    def calculate_entity_statistics(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Calculate entity statistics."""
        stats = {
            "total_entities": len(restaurant_data),
            "cuisine_breakdown": defaultdict(int),
            "source_breakdown": defaultdict(int),
            "completeness_metrics": {},
        }

        # Calculate cuisine breakdown
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            stats["cuisine_breakdown"][cuisine] += 1

        # Calculate source breakdown
        for restaurant in restaurant_data:
            for source in restaurant.sources:
                stats["source_breakdown"][source] += 1

        # Convert defaultdicts to regular dicts
        stats["cuisine_breakdown"] = dict(stats["cuisine_breakdown"])
        stats["source_breakdown"] = dict(stats["source_breakdown"])

        return stats

    def calculate_file_size_statistics(self, file_paths: List[str]) -> Dict[str, Any]:
        """Calculate file size statistics."""
        total_size = 0
        file_sizes = []

        for file_path in file_paths:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                total_size += size
                file_sizes.append(size)

        stats = {
            "total_size": total_size,
            "file_count": len(file_sizes),
            "average_size": total_size / len(file_sizes) if file_sizes else 0,
            "min_size": min(file_sizes) if file_sizes else 0,
            "max_size": max(file_sizes) if file_sizes else 0,
        }

        return stats

    def calculate_data_quality_metrics(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        total_entities = len(restaurant_data)
        if total_entities == 0:
            return {"completeness_score": 0, "field_coverage": {}}

        field_counts = {
            "name": 0,
            "address": 0,
            "phone": 0,
            "cuisine": 0,
            "menu_items": 0,
            "price_range": 0,
            "hours": 0,
        }

        for restaurant in restaurant_data:
            if restaurant.name:
                field_counts["name"] += 1
            if restaurant.address:
                field_counts["address"] += 1
            if restaurant.phone:
                field_counts["phone"] += 1
            if restaurant.cuisine:
                field_counts["cuisine"] += 1
            if restaurant.menu_items:
                field_counts["menu_items"] += 1
            if restaurant.price_range:
                field_counts["price_range"] += 1
            if restaurant.hours:
                field_counts["hours"] += 1

        field_coverage = {
            field: count / total_entities for field, count in field_counts.items()
        }
        completeness_score = sum(field_coverage.values()) / len(field_coverage)

        return {
            "completeness_score": completeness_score,
            "field_coverage": field_coverage,
            "total_entities_analyzed": total_entities,
        }

    def generate_generation_metadata(self) -> Dict[str, Any]:
        """Generate metadata about the generation process."""
        return {
            "generation_timestamp": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "schema_version": "1.0.0",
        }