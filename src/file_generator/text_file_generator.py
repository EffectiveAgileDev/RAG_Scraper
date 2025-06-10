"""Text file generator for RAG systems."""
import os
import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

from src.scraper.multi_strategy_scraper import RestaurantData
from src.config.file_permission_validator import FilePermissionValidator


@dataclass
class TextFileConfig:
    """Configuration for text file generation."""
    output_directory: str = "."
    allow_overwrite: bool = True
    encoding: str = "utf-8"
    filename_pattern: str = "WebScrape_{timestamp}.txt"
    
    def __post_init__(self):
        """Ensure output directory exists."""
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)


class TextFileGenerator:
    """Generates text files in RAG-compatible format from restaurant data."""
    
    def __init__(self, config: TextFileConfig):
        """Initialize text file generator.
        
        Args:
            config: Configuration for file generation
        """
        self.config = config
        self.permission_validator = FilePermissionValidator()
    
    def generate_file(self, restaurant_data: List[RestaurantData]) -> str:
        """Generate text file from restaurant data.
        
        Args:
            restaurant_data: List of RestaurantData objects to include in file
            
        Returns:
            Path to generated file
            
        Raises:
            ValueError: If no restaurant data provided
            PermissionError: If output directory lacks write permissions
            FileExistsError: If file exists and overwrite not allowed
        """
        if not restaurant_data:
            raise ValueError("No restaurant data available for file generation")
        
        # Validate directory permissions
        result = self.permission_validator.validate_directory_writable(self.config.output_directory)
        if not result.is_writable:
            raise PermissionError(f"No write permission for directory: {self.config.output_directory}")
        
        # Generate filename with timestamp
        filename = self._generate_filename()
        file_path = os.path.join(self.config.output_directory, filename)
        
        # Check for existing file
        if os.path.exists(file_path) and not self.config.allow_overwrite:
            raise FileExistsError(f"File already exists: {filename}")
        
        # Generate file content
        content = self._format_restaurants_for_rag(restaurant_data)
        
        # Write file
        with open(file_path, 'w', encoding=self.config.encoding) as f:
            f.write(content)
        
        return file_path
    
    def _generate_filename(self) -> str:
        """Generate filename with current timestamp.
        
        Returns:
            Filename string with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        return self.config.filename_pattern.format(timestamp=timestamp)
    
    def _format_restaurants_for_rag(self, restaurant_data: List[RestaurantData]) -> str:
        """Format restaurant data for RAG systems.
        
        Args:
            restaurant_data: List of restaurant data to format
            
        Returns:
            Formatted string content for RAG file
        """
        formatted_restaurants = []
        
        for restaurant in restaurant_data:
            formatted_restaurant = self._format_single_restaurant(restaurant)
            formatted_restaurants.append(formatted_restaurant)
        
        # Join restaurants with double carriage returns
        return "\n\n\n".join(formatted_restaurants)
    
    def _format_single_restaurant(self, restaurant: RestaurantData) -> str:
        """Format a single restaurant for RAG output.
        
        Args:
            restaurant: RestaurantData object to format
            
        Returns:
            Formatted string for single restaurant
        """
        lines = []
        
        # Required/core fields
        if restaurant.name:
            lines.append(restaurant.name)
        
        if restaurant.address:
            lines.append(restaurant.address)
        
        if restaurant.phone:
            lines.append(restaurant.phone)
        
        if restaurant.price_range:
            lines.append(restaurant.price_range)
        
        if restaurant.hours:
            lines.append(f"Hours: {restaurant.hours}")
        
        # Add blank line before menu sections if we have any
        if restaurant.menu_items:
            lines.append("")  # Blank line
            
            # Format menu sections
            menu_lines = self._format_menu_items(restaurant.menu_items)
            lines.extend(menu_lines)
        
        # Optional fields (add blank line before if we have them and previous content)
        optional_fields = []
        
        if restaurant.cuisine:
            optional_fields.append(f"CUISINE: {restaurant.cuisine}")
        
        # Add optional fields with blank line separator if we have them
        if optional_fields and lines:
            lines.append("")  # Blank line before optional fields
            lines.extend(optional_fields)
        
        return "\n".join(lines)
    
    def _format_menu_items(self, menu_items: dict) -> List[str]:
        """Format menu items for RAG output.
        
        Args:
            menu_items: Dictionary of menu sections and items
            
        Returns:
            List of formatted menu lines
        """
        menu_lines = []
        
        # Define section order and formatting
        section_map = {
            'appetizers': 'APPETIZERS',
            'entrees': 'ENTREES', 
            'mains': 'ENTREES',
            'main_courses': 'ENTREES',
            'desserts': 'DESSERTS',
            'drinks': 'DRINKS',
            'beverages': 'DRINKS'
        }
        
        # Process known sections in order
        for section_key in ['appetizers', 'entrees', 'mains', 'main_courses', 'desserts', 'drinks', 'beverages']:
            if section_key in menu_items and menu_items[section_key]:
                section_name = section_map[section_key]
                items = menu_items[section_key]
                if isinstance(items, list):
                    items_str = ", ".join(items)
                    menu_lines.append(f"{section_name}: {items_str}")
        
        # Process any other sections not in the standard map
        for section_key, items in menu_items.items():
            if section_key not in section_map and items:
                section_name = section_key.upper().replace('_', ' ')
                if isinstance(items, list):
                    items_str = ", ".join(items)
                    menu_lines.append(f"{section_name}: {items_str}")
        
        return menu_lines


class TextFileConfigManager:
    """Manages persistent configuration for text file generation."""
    
    def __init__(self, config_file: str = "text_generator_config.json"):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
    
    def save_config(self, config: TextFileConfig) -> None:
        """Save configuration to file.
        
        Args:
            config: Configuration to save
        """
        config_data = {
            'output_directory': config.output_directory,
            'allow_overwrite': config.allow_overwrite,
            'encoding': config.encoding,
            'filename_pattern': config.filename_pattern
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_config(self) -> Optional[TextFileConfig]:
        """Load configuration from file.
        
        Returns:
            Loaded configuration or None if file doesn't exist
        """
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            return TextFileConfig(**config_data)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def get_or_create_config(self, default_output_dir: str = ".") -> TextFileConfig:
        """Get existing configuration or create default.
        
        Args:
            default_output_dir: Default output directory if no config exists
            
        Returns:
            Configuration object
        """
        config = self.load_config()
        if config is None:
            config = TextFileConfig(output_directory=default_output_dir)
            self.save_config(config)
        
        return config