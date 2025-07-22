"""Incremental file handler for writing restaurant data as it's processed."""

import os
from typing import Optional, TextIO
from ..scraper.multi_strategy_scraper import RestaurantData
from .text_file_generator import TextFileGenerator, TextFileConfig


class IncrementalFileHandler:
    """Handler for writing restaurant data incrementally during processing."""
    
    def __init__(self, output_file_path: str, file_format: str = "text"):
        """Initialize incremental file handler.
        
        Args:
            output_file_path: Path to the output file
            file_format: Format of the file ("text", "json", "pdf")
        """
        self.output_file_path = output_file_path
        self.file_format = file_format.lower()
        self.file_handle: Optional[TextIO] = None
        self.is_first_entry = True
        
        # Create config for text generator
        text_config = TextFileConfig(
            output_directory=os.path.dirname(output_file_path),
            allow_overwrite=True
        )
        self.text_generator = TextFileGenerator(text_config)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        # Open the file for writing
        self._open_file()
    
    def _open_file(self):
        """Open the output file for writing."""
        try:
            if self.file_format == "text":
                self.file_handle = open(self.output_file_path, 'w', encoding='utf-8')
            elif self.file_format == "json":
                self.file_handle = open(self.output_file_path, 'w', encoding='utf-8')
                # Start JSON array
                self.file_handle.write('[\n')
            else:
                raise ValueError(f"Unsupported file format for incremental writing: {self.file_format}")
        except Exception as e:
            raise RuntimeError(f"Failed to open output file {self.output_file_path}: {str(e)}")
    
    def write_restaurant_data(self, restaurant_data: RestaurantData):
        """Write a single restaurant's data to the file immediately.
        
        Args:
            restaurant_data: RestaurantData object to write
        """
        if not self.file_handle:
            raise RuntimeError("File handler is not open")
        
        try:
            if self.file_format == "text":
                self._write_text_data(restaurant_data)
            elif self.file_format == "json":
                self._write_json_data(restaurant_data)
            
            # Flush to ensure data is written immediately
            self.file_handle.flush()
            
        except Exception as e:
            raise RuntimeError(f"Failed to write restaurant data: {str(e)}")
    
    def _write_text_data(self, restaurant_data: RestaurantData):
        """Write restaurant data in text format."""
        # Format the restaurant data using existing text generator logic
        formatted_text = self.text_generator._format_single_restaurant(restaurant_data)
        
        # Add separator if not the first entry
        if not self.is_first_entry:
            self.file_handle.write("\n\n\n")  # Triple newline separator
        
        self.file_handle.write(formatted_text)
        self.is_first_entry = False
    
    def _write_json_data(self, restaurant_data: RestaurantData):
        """Write restaurant data in JSON format."""
        import json
        
        # Convert restaurant data to dictionary
        restaurant_dict = restaurant_data.to_dict()
        
        # Add comma separator if not the first entry
        if not self.is_first_entry:
            self.file_handle.write(',\n')
        
        # Write JSON object with proper indentation
        json_str = json.dumps(restaurant_dict, indent=2, ensure_ascii=False)
        self.file_handle.write(json_str)
        self.is_first_entry = False
    
    def close(self):
        """Close the file handler."""
        if self.file_handle:
            try:
                # Finalize the file format if needed
                if self.file_format == "json":
                    self.file_handle.write('\n]')  # Close JSON array
                
                self.file_handle.close()
                self.file_handle = None
            except Exception as e:
                raise RuntimeError(f"Failed to close file {self.output_file_path}: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure file is closed."""
        if self.file_handle:
            try:
                self.close()
            except:
                pass  # Ignore errors in destructor