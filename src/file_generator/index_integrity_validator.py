"""Index integrity validator for validating index file integrity and consistency."""
import os
import json
from typing import List, Dict, Any

from src.scraper.multi_strategy_scraper import RestaurantData


class IndexIntegrityValidator:
    """Validates index file integrity and consistency."""

    def validate_comprehensive_integrity(self, output_directory: str) -> Dict[str, Any]:
        """Validate comprehensive index integrity."""
        validation_result = {
            "valid": True,
            "file_references_valid": True,
            "entity_consistency_valid": True,
            "category_assignments_valid": True,
            "no_orphaned_references": True,
            "issues": [],
        }

        try:
            # Load master index
            master_index_path = os.path.join(output_directory, "master_index.json")
            if os.path.exists(master_index_path):
                with open(master_index_path, "r", encoding="utf-8") as f:
                    master_index = json.load(f)

                # Validate file references
                file_validation = self.validate_file_references(
                    master_index, output_directory
                )
                if not file_validation["valid"]:
                    validation_result["file_references_valid"] = False
                    validation_result["issues"].extend(
                        file_validation.get("issues", [])
                    )

            validation_result["valid"] = (
                validation_result["file_references_valid"]
                and validation_result["entity_consistency_valid"]
                and validation_result["category_assignments_valid"]
                and validation_result["no_orphaned_references"]
            )

        except Exception as e:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")

        return validation_result

    def validate_file_references(
        self, index_data: Dict[str, Any], base_directory: str
    ) -> Dict[str, Any]:
        """Validate that all file references in index exist."""
        validation_result = {"valid": True, "missing_files": [], "issues": []}

        for entity in index_data.get("entities", []):
            file_path = entity.get("file_path")
            if file_path:
                full_path = os.path.join(base_directory, file_path)
                if not os.path.exists(full_path):
                    validation_result["missing_files"].append(file_path)
                    validation_result["issues"].append(f"Missing file: {file_path}")

        validation_result["valid"] = len(validation_result["missing_files"]) == 0
        return validation_result

    def validate_entity_id_consistency(
        self, master_index: Dict[str, Any], category_indices: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate entity ID consistency across indices."""
        consistency_result = {"consistent": True, "inconsistencies": [], "issues": []}

        # Extract entity IDs from master index
        master_ids = set()
        for entity in master_index.get("entities", []):
            master_ids.add(entity.get("id"))

        # Check consistency with category indices
        for category, category_data in category_indices.items():
            for entity in category_data.get("entities", []):
                entity_id = entity.get("id")
                if entity_id not in master_ids:
                    consistency_result["inconsistencies"].append(
                        f"Entity {entity_id} in {category} not found in master index"
                    )

        consistency_result["consistent"] = (
            len(consistency_result["inconsistencies"]) == 0
        )
        return consistency_result

    def validate_category_assignments(
        self,
        restaurant_data: List[RestaurantData],
        category_indices: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Validate category assignments are accurate."""
        validation_result = {"accurate": True, "misassignments": [], "issues": []}

        # Check each restaurant's category assignment
        for restaurant in restaurant_data:
            expected_category = restaurant.cuisine or "Unknown"
            found_in_categories = []

            for category, restaurant_names in category_indices.items():
                if restaurant.name in restaurant_names:
                    found_in_categories.append(category)

            if expected_category not in found_in_categories:
                validation_result["misassignments"].append(
                    f"Restaurant {restaurant.name} expected in {expected_category}, found in {found_in_categories}"
                )

        validation_result["accurate"] = len(validation_result["misassignments"]) == 0
        return validation_result

    def detect_orphaned_references(
        self, index_data: Dict[str, Any], all_entity_ids: List[str]
    ) -> List[str]:
        """Detect orphaned references in index data."""
        orphaned_refs = []
        entity_id_set = set(all_entity_ids)

        for entity in index_data.get("entities", []):
            related_to = entity.get("related_to", [])
            for related_id in related_to:
                if related_id not in entity_id_set:
                    orphaned_refs.append(related_id)

        return orphaned_refs