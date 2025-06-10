"""PDF generator for restaurant data using ReportLab."""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import black, blue, gray

from src.scraper.multi_strategy_scraper import RestaurantData
from src.config.file_permission_validator import FilePermissionValidator


@dataclass
class PDFConfig:
    """Configuration for PDF generation."""

    output_directory: str = "."
    allow_overwrite: bool = True
    font_family: str = "Helvetica"
    font_size: int = 12
    page_orientation: str = "portrait"
    margin_size: str = "standard"
    filename_pattern: str = "WebScrape_{timestamp}.pdf"

    def __post_init__(self):
        """Post-initialization validation."""
        if self.page_orientation not in ["portrait", "landscape"]:
            self.page_orientation = "portrait"
        if self.margin_size not in ["narrow", "standard", "wide"]:
            self.margin_size = "standard"


class PDFGenerator:
    """Generator for PDF documents from restaurant data."""

    def __init__(self, config: PDFConfig):
        """Initialize PDF generator with configuration.

        Args:
            config: PDF generation configuration
        """
        self.config = config
        self.permission_validator = FilePermissionValidator()

        # Set up page size based on orientation
        if config.page_orientation == "landscape":
            self.page_size = (letter[1], letter[0])  # Swap width and height
        else:
            self.page_size = letter

        # Set up margins based on size preference
        margin_settings = {
            "narrow": 0.5 * inch,
            "standard": 0.75 * inch,
            "wide": 1.0 * inch,
        }
        self.margin = margin_settings.get(config.margin_size, 0.75 * inch)

    def generate_file(self, restaurant_data: List[RestaurantData]) -> str:
        """Generate PDF file from restaurant data.

        Args:
            restaurant_data: List of restaurant data objects

        Returns:
            Path to generated PDF file

        Raises:
            ValueError: If no restaurant data provided
            PermissionError: If cannot write to output directory
            FileExistsError: If file exists and overwrite not allowed
        """
        if not restaurant_data:
            raise ValueError("No restaurant data available for PDF generation")

        # Validate directory permissions
        result = self.permission_validator.validate_directory_writable(
            self.config.output_directory
        )
        if not result.is_writable:
            raise PermissionError(
                f"No write permission for directory: {self.config.output_directory}"
            )

        # Generate filename with timestamp
        filename = self._generate_filename()
        file_path = os.path.join(self.config.output_directory, filename)

        # Check if file exists and handle overwrite settings
        if os.path.exists(file_path) and not self.config.allow_overwrite:
            raise FileExistsError(
                f"File already exists and overwrite is disabled: {file_path}"
            )

        # Create PDF document
        self._create_pdf_document(file_path, restaurant_data)

        return file_path

    def _generate_filename(self) -> str:
        """Generate filename with timestamp.

        Returns:
            Generated filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return self.config.filename_pattern.format(timestamp=timestamp)

    def _create_pdf_document(
        self, file_path: str, restaurant_data: List[RestaurantData]
    ) -> None:
        """Create PDF document with restaurant data.

        Args:
            file_path: Path where PDF should be saved
            restaurant_data: List of restaurant data to include
        """
        # Create document with specified page size and margins
        doc = SimpleDocTemplate(
            file_path,
            pagesize=self.page_size,
            topMargin=self.margin,
            bottomMargin=self.margin,
            leftMargin=self.margin,
            rightMargin=self.margin,
        )

        # Build document content
        story = []

        # Add document header
        story.extend(self._create_document_header(len(restaurant_data)))

        # Add restaurant data
        for i, restaurant in enumerate(restaurant_data):
            story.extend(self._create_restaurant_section(restaurant))

            # Add separator between restaurants (except for last one)
            if i < len(restaurant_data) - 1:
                story.append(Spacer(1, 20))

        # Build PDF
        doc.build(story)

    def _create_document_header(self, restaurant_count: int) -> List:
        """Create document header with title and metadata.

        Args:
            restaurant_count: Number of restaurants in document

        Returns:
            List of document elements for header
        """
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=16,
            spaceAfter=12,
            textColor=black,
        )

        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=20,
            textColor=gray,
        )

        elements = []

        # Document title
        title = Paragraph("Restaurant Data Report", title_style)
        elements.append(title)

        # Document metadata
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        metadata = (
            f"Generated on {timestamp} | {restaurant_count} restaurant(s) included"
        )
        subtitle = Paragraph(metadata, subtitle_style)
        elements.append(subtitle)

        return elements

    def _create_restaurant_section(self, restaurant: RestaurantData) -> List:
        """Create PDF section for a single restaurant.

        Args:
            restaurant: Restaurant data object

        Returns:
            List of document elements for restaurant section
        """
        styles = getSampleStyleSheet()

        # Create custom styles for restaurant sections
        restaurant_name_style = ParagraphStyle(
            "RestaurantName",
            parent=styles["Heading2"],
            fontSize=14,
            spaceAfter=6,
            textColor=blue,
        )

        field_style = ParagraphStyle(
            "FieldStyle", parent=styles["Normal"], fontSize=10, spaceAfter=4
        )

        source_style = ParagraphStyle(
            "SourceStyle",
            parent=styles["Normal"],
            fontSize=8,
            spaceAfter=8,
            textColor=gray,
            fontName="Helvetica-Oblique",
        )

        elements = []

        # Restaurant name
        name = Paragraph(f"<b>{restaurant.name}</b>", restaurant_name_style)
        elements.append(name)

        # Basic information
        if restaurant.address:
            address = Paragraph(f"<b>Address:</b> {restaurant.address}", field_style)
            elements.append(address)

        if restaurant.phone:
            phone = Paragraph(f"<b>Phone:</b> {restaurant.phone}", field_style)
            elements.append(phone)

        if restaurant.cuisine:
            cuisine = Paragraph(f"<b>Cuisine:</b> {restaurant.cuisine}", field_style)
            elements.append(cuisine)

        if restaurant.price_range:
            price = Paragraph(
                f"<b>Price Range:</b> {restaurant.price_range}", field_style
            )
            elements.append(price)

        if restaurant.hours:
            hours = Paragraph(f"<b>Hours:</b> {restaurant.hours}", field_style)
            elements.append(hours)

        # Menu items
        if restaurant.menu_items:
            menu_text = self._format_menu_items(restaurant.menu_items)
            menu = Paragraph(f"<b>Menu Items:</b><br/>{menu_text}", field_style)
            elements.append(menu)

        # Social media
        if restaurant.social_media:
            social_text = ", ".join(restaurant.social_media)
            social = Paragraph(f"<b>Social Media:</b> {social_text}", field_style)
            elements.append(social)

        # Data sources and confidence
        source_info = f"Data Sources: {', '.join(restaurant.sources)} | Confidence: {restaurant.confidence}"
        sources = Paragraph(source_info, source_style)
        elements.append(sources)

        return elements

    def _format_menu_items(self, menu_items: Dict[str, List[str]]) -> str:
        """Format menu items for PDF display.

        Args:
            menu_items: Dictionary of menu categories and items

        Returns:
            Formatted menu items string
        """
        if not menu_items:
            return "No menu items available"

        formatted_sections = []
        for category, items in menu_items.items():
            if items:
                category_title = category.replace("_", " ").title()
                items_list = ", ".join(items)
                formatted_sections.append(f"<b>{category_title}:</b> {items_list}")

        return "<br/>".join(formatted_sections)

    def validate_restaurant_data(
        self, restaurant_data: List[RestaurantData]
    ) -> List[str]:
        """Validate restaurant data for PDF generation.

        Args:
            restaurant_data: List of restaurant data to validate

        Returns:
            List of validation warnings (empty if all valid)
        """
        warnings = []

        if not restaurant_data:
            warnings.append("No restaurant data provided")
            return warnings

        for i, restaurant in enumerate(restaurant_data):
            if not restaurant.name:
                warnings.append(f"Restaurant {i+1}: Missing name")

            if not restaurant.sources:
                name_part = restaurant.name if restaurant.name else f"Restaurant {i+1}"
                warnings.append(
                    f"Restaurant {i+1} ({name_part}): No data sources specified"
                )

        return warnings
