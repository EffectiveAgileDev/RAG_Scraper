"""
JSON Export Generator for RAG_Scraper.
Generates structured JSON files from scraped restaurant data with field selection support.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union


class JSONExportGenerator:
    """
    Generates JSON files from restaurant data with comprehensive field support.

    Supports field categorization and selective export to allow customized
    JSON output based on user preferences.
    """

    # Class constants for better maintainability
    FORMAT_VERSION = "1.0"
    DEFAULT_FIELD_SELECTION = {
        "core_fields": True,
        "extended_fields": True,
        "additional_fields": True,
        "contact_fields": True,
        "descriptive_fields": True,
    }

    def __init__(self):
        """Initialize the JSON export generator with field category mappings."""
        self.format_version = self.FORMAT_VERSION

        # Define field category mappings for structured JSON output
        self.field_mappings = {
            "basic_info": {
                "category": "core_fields",
                "fields": ["name", "address", "phone", "hours", "website"],
            },
            "additional_details": {
                "category": "extended_fields",
                "fields": ["cuisine_types", "special_features", "parking"],
                "additional_category": "additional_fields",
                "additional_fields": ["reservations", "menu_items", "pricing"],
            },
            "contact_info": {
                "category": "contact_fields",
                "fields": ["email", "social_media", "delivery_options"],
            },
            "characteristics": {
                "category": "descriptive_fields",
                "fields": ["dietary_accommodations", "ambiance"],
            },
        }

    def format_restaurant_data(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format single restaurant data into structured JSON format.

        Args:
            restaurant_data: Dictionary containing restaurant information

        Returns:
            Formatted restaurant data with categorized fields
        """
        return {
            "basic_info": self._format_basic_info(restaurant_data),
            "additional_details": self._format_additional_details(restaurant_data),
            "contact_info": self._format_contact_info(restaurant_data),
            "characteristics": self._format_characteristics(restaurant_data),
        }

    def _format_basic_info(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format basic restaurant information."""
        return {
            "name": restaurant_data.get("name"),
            "address": restaurant_data.get("address"),
            "phone": restaurant_data.get("phone"),
            "hours": restaurant_data.get("hours"),
            "website": restaurant_data.get("website"),
        }

    def _format_additional_details(
        self, restaurant_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format additional restaurant details."""
        return {
            "cuisine_types": restaurant_data.get("cuisine_types", []),
            "special_features": restaurant_data.get("special_features", []),
            "parking": restaurant_data.get("parking"),
            "reservations": restaurant_data.get("reservations"),
            "menu_items": restaurant_data.get("menu_items", []),
            "pricing": restaurant_data.get("pricing"),
        }

    def _format_contact_info(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format contact information."""
        return {
            "email": restaurant_data.get("email"),
            "social_media": restaurant_data.get("social_media", []),
            "delivery_options": restaurant_data.get("delivery_options", []),
        }

    def _format_characteristics(
        self, restaurant_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format restaurant characteristics."""
        return {
            "dietary_accommodations": restaurant_data.get("dietary_accommodations", []),
            "ambiance": restaurant_data.get("ambiance"),
        }

    def generate_json_file(
        self,
        restaurant_list: List[Dict[str, Any]],
        output_path: str,
        field_selection: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Generate JSON file from restaurant data list.

        Args:
            restaurant_list: List of restaurant data dictionaries
            output_path: Path where JSON file should be saved
            field_selection: Optional field selection configuration

        Returns:
            Dictionary with generation results including success status
        """
        try:
            # Validate inputs
            if not self._validate_inputs(restaurant_list, output_path):
                return self._create_error_result("Invalid input parameters")

            # Use default field selection if none provided
            active_field_selection = field_selection or self.DEFAULT_FIELD_SELECTION

            # Validate field selection
            if not self.validate_field_selection(active_field_selection):
                return self._create_error_result(
                    "Invalid field selection configuration"
                )

            # Prepare output directory
            self._ensure_output_directory(output_path)

            # Process restaurant data
            formatted_restaurants = self._process_restaurant_list(
                restaurant_list, active_field_selection
            )

            # Generate and write JSON file
            json_data = self._create_json_structure(
                restaurant_list, formatted_restaurants
            )
            self._write_json_file(json_data, output_path)

            return self._create_success_result(output_path, len(restaurant_list))

        except (OSError, IOError, PermissionError) as e:
            return self._create_error_result(f"File system error: {str(e)}")
        except Exception as e:
            return self._create_error_result(f"Unexpected error: {str(e)}")

    def _validate_inputs(
        self, restaurant_list: List[Dict[str, Any]], output_path: str
    ) -> bool:
        """Validate input parameters."""
        return (
            isinstance(restaurant_list, list)
            and isinstance(output_path, str)
            and len(output_path.strip()) > 0
        )

    def _ensure_output_directory(self, output_path: str) -> None:
        """Create output directory if it doesn't exist."""
        directory = os.path.dirname(output_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _process_restaurant_list(
        self, restaurant_list: List[Dict[str, Any]], field_selection: Dict[str, bool]
    ) -> List[Dict[str, Any]]:
        """Process restaurant list with field selection applied."""
        formatted_restaurants = []
        for restaurant in restaurant_list:
            formatted_restaurant = self.format_restaurant_data(restaurant)
            formatted_restaurant = self._apply_field_selection(
                formatted_restaurant, field_selection
            )
            formatted_restaurants.append(formatted_restaurant)
        return formatted_restaurants

    def _create_json_structure(
        self,
        restaurant_list: List[Dict[str, Any]],
        formatted_restaurants: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Create the final JSON structure with metadata."""
        return {
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "restaurant_count": len(restaurant_list),
                "format_version": self.format_version,
            },
            "restaurants": formatted_restaurants,
        }

    def _write_json_file(self, json_data: Dict[str, Any], output_path: str) -> None:
        """Write JSON data to file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

    def _create_success_result(
        self, file_path: str, restaurant_count: int
    ) -> Dict[str, Any]:
        """Create success result dictionary."""
        return {
            "success": True,
            "file_path": file_path,
            "restaurant_count": restaurant_count,
        }

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result dictionary."""
        return {"success": False, "error": error_message}

    def _apply_field_selection(
        self, formatted_data: Dict[str, Any], field_selection: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Apply field selection to formatted restaurant data.

        Args:
            formatted_data: Formatted restaurant data
            field_selection: Field selection configuration

        Returns:
            Restaurant data with only selected fields
        """
        result = formatted_data.copy()

        # Define field selection rules for maintainable configuration
        selection_rules = {
            "core_fields": {"section": "basic_info", "action": "null_all"},
            "extended_fields": {
                "section": "additional_details",
                "fields": ["cuisine_types", "special_features", "parking"],
                "action": "selective_null",
            },
            "additional_fields": {
                "section": "additional_details",
                "fields": ["reservations", "menu_items", "pricing"],
                "action": "selective_null",
            },
            "contact_fields": {"section": "contact_info", "action": "selective_null"},
            "descriptive_fields": {
                "section": "characteristics",
                "action": "selective_null",
            },
        }

        # Apply field selection rules
        for category, enabled in field_selection.items():
            if not enabled and category in selection_rules:
                rule = selection_rules[category]
                self._apply_selection_rule(result, rule)

        return result

    def _apply_selection_rule(self, data: Dict[str, Any], rule: Dict[str, Any]) -> None:
        """Apply a specific field selection rule to the data."""
        section = rule["section"]
        action = rule["action"]

        if section not in data:
            return

        if action == "null_all":
            # Set all fields in section to None
            for key in data[section]:
                data[section][key] = None
        elif action == "selective_null":
            # Set specific fields to appropriate null values
            fields_to_process = rule.get("fields", data[section].keys())
            for field in fields_to_process:
                if field in data[section]:
                    data[section][field] = self._get_null_value_for_field(field)

    def _get_null_value_for_field(self, field_name: str) -> Union[None, List]:
        """Get appropriate null value for a field based on its expected type."""
        list_fields = {
            "cuisine_types",
            "special_features",
            "menu_items",
            "social_media",
            "delivery_options",
            "dietary_accommodations",
        }
        return [] if field_name in list_fields else None

    def validate_field_selection(self, field_selection: Dict[str, bool]) -> bool:
        """
        Validate field selection configuration.

        Args:
            field_selection: Field selection configuration to validate

        Returns:
            True if configuration is valid, False otherwise
        """
        valid_field_categories = {
            "core_fields",
            "extended_fields",
            "additional_fields",
            "contact_fields",
            "descriptive_fields",
        }

        # Check if all keys in field_selection are valid
        for key in field_selection.keys():
            if key not in valid_field_categories:
                return False

        # Check if all values are boolean
        for value in field_selection.values():
            if not isinstance(value, bool):
                return False

        return True
