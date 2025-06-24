"""Tests for MultiPageResultHandler - result collection and data aggregation."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.scraper.multi_page_result_handler import (
    MultiPageResultHandler,
    MultiPageScrapingResult,
    PageProcessingResult
)
from src.scraper.data_aggregator import DataAggregator, PageData
from src.scraper.multi_page_progress import MultiPageProgressNotifier
from src.scraper.multi_strategy_scraper import RestaurantData


class TestMultiPageResultHandler:
    """Test MultiPageResultHandler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.progress_notifier = Mock(spec=MultiPageProgressNotifier)
        self.data_aggregator = Mock(spec=DataAggregator)
        self.page_processor = Mock()
        
        self.result_handler = MultiPageResultHandler(
            progress_notifier=self.progress_notifier,
            data_aggregator=self.data_aggregator,
            page_processor=self.page_processor
        )

    def test_init_creates_handler_with_dependencies(self):
        """Test that MultiPageResultHandler initializes with required dependencies."""
        assert self.result_handler.progress_notifier is self.progress_notifier
        assert self.result_handler.data_aggregator is self.data_aggregator
        assert self.result_handler.page_processor is self.page_processor

    def test_create_empty_scraping_result(self):
        """Test creating empty MultiPageScrapingResult."""
        result = self.result_handler.create_scraping_result()
        
        assert isinstance(result, MultiPageScrapingResult)
        assert result.restaurant_name == ""
        assert result.pages_processed == []
        assert result.successful_pages == []
        assert result.failed_pages == []
        assert result.aggregated_data is None
        assert result.processing_time == 0.0
        assert result.data_sources_summary == {}

    def test_create_scraping_result_with_data(self):
        """Test creating MultiPageScrapingResult with initial data."""
        result = self.result_handler.create_scraping_result(
            restaurant_name="Test Restaurant",
            pages_processed=["page1.html", "page2.html"]
        )
        
        assert result.restaurant_name == "Test Restaurant"
        assert result.pages_processed == ["page1.html", "page2.html"]

    def test_process_discovered_pages_success(self):
        """Test processing discovered pages successfully."""
        pages = ["http://example.com/page1", "http://example.com/page2"]
        mock_callback = Mock()
        
        # Mock page processing results
        mock_data_1 = Mock()
        mock_data_1.sources = ["json-ld"]
        mock_data_1.name = "Test Restaurant"
        mock_data_1.address = "123 Main St"
        mock_data_1.phone = "555-1234"
        mock_data_1.hours = "9-5"
        mock_data_1.price_range = "$$"
        mock_data_1.cuisine = "Italian"
        mock_data_1.menu_items = {"appetizers": ["Bruschetta"]}
        mock_data_1.social_media = ["facebook.com/test"]
        mock_data_1.confidence = "high"
        
        page_result_1 = {
            "page_type": "menu",
            "data": mock_data_1
        }
        
        mock_data_2 = Mock()
        mock_data_2.sources = ["microdata"]
        mock_data_2.name = "Test Restaurant"
        mock_data_2.address = "123 Main St"
        mock_data_2.phone = "555-1234"
        mock_data_2.hours = "9-5"
        mock_data_2.price_range = ""
        mock_data_2.cuisine = ""
        mock_data_2.menu_items = {}
        mock_data_2.social_media = []
        mock_data_2.confidence = "medium"
        
        page_result_2 = {
            "page_type": "contact",
            "data": mock_data_2
        }
        
        self.page_processor._fetch_and_process_page.side_effect = [
            page_result_1, page_result_2
        ]
        
        # Mock data aggregator has some existing data
        self.data_aggregator.page_data = [
            Mock(restaurant_name="Test Restaurant")
        ]
        
        result = self.result_handler.process_discovered_pages(
            pages, progress_callback=mock_callback
        )
        
        assert isinstance(result, PageProcessingResult)
        assert result.successful_pages == pages
        assert result.failed_pages == []
        
        # Verify progress notifications
        self.progress_notifier.initialize_restaurant.assert_called_once()
        assert self.progress_notifier.notify_page_complete.call_count == 2
        
        # Verify data aggregation
        assert self.data_aggregator.add_page_data.call_count == 2

    def test_process_discovered_pages_with_failures(self):
        """Test processing pages with some failures."""
        pages = ["http://example.com/page1", "http://example.com/page2"]
        
        # First page succeeds, second fails
        mock_data_1 = Mock()
        mock_data_1.sources = ["json-ld"]
        mock_data_1.name = "Test Restaurant"
        mock_data_1.address = "123 Main St"
        mock_data_1.phone = "555-1234"
        mock_data_1.hours = "9-5"
        mock_data_1.price_range = "$$"
        mock_data_1.cuisine = "Italian"
        mock_data_1.menu_items = {"appetizers": ["Bruschetta"]}
        mock_data_1.social_media = ["facebook.com/test"]
        mock_data_1.confidence = "high"
        
        page_result_1 = {
            "page_type": "menu",
            "data": mock_data_1
        }
        
        self.page_processor._fetch_and_process_page.side_effect = [
            page_result_1, None  # Second page fails
        ]
        
        # Mock data aggregator
        self.data_aggregator.page_data = [
            Mock(restaurant_name="Test Restaurant")
        ]
        
        result = self.result_handler.process_discovered_pages(pages)
        
        assert result.successful_pages == ["http://example.com/page1"]
        assert result.failed_pages == ["http://example.com/page2"]

    def test_process_discovered_pages_with_exceptions(self):
        """Test processing pages when exceptions occur."""
        pages = ["http://example.com/page1"]
        
        self.page_processor._fetch_and_process_page.side_effect = Exception("Network error")
        
        # Mock data aggregator
        self.data_aggregator.page_data = [
            Mock(restaurant_name="Test Restaurant")
        ]
        
        result = self.result_handler.process_discovered_pages(pages)
        
        assert result.successful_pages == []
        assert result.failed_pages == ["http://example.com/page1"]

    def test_finalize_scraping_result(self):
        """Test finalizing scraping result with aggregated data."""
        result = MultiPageScrapingResult()
        result.successful_pages = ["page1", "page2"]
        result.failed_pages = ["page3"]
        
        # Mock aggregated data
        mock_aggregated_data = Mock(spec=RestaurantData)
        mock_data_summary = {"total_pages": 3, "sources": {"json-ld": 2}}
        
        self.data_aggregator.aggregate.return_value = mock_aggregated_data
        self.data_aggregator.get_data_sources_summary.return_value = mock_data_summary
        
        start_time = 1000.0
        end_time = 1005.0
        
        final_result = self.result_handler.finalize_scraping_result(
            result, start_time, end_time
        )
        
        assert final_result.aggregated_data is mock_aggregated_data
        assert final_result.data_sources_summary == mock_data_summary
        assert final_result.processing_time == 5.0

    def test_notify_completion(self):
        """Test completion notification."""
        mock_callback = Mock()
        
        self.result_handler.notify_completion(
            successful_count=5,
            failed_count=2,
            progress_callback=mock_callback
        )
        
        self.progress_notifier.notify_restaurant_complete.assert_called_once_with(
            5, 2, mock_callback
        )

    def test_extract_restaurant_name_from_page_data(self):
        """Test extracting restaurant name from page data for progress tracking."""
        page_data = [
            Mock(restaurant_name=""),
            Mock(restaurant_name="Test Restaurant"),
            Mock(restaurant_name="Another Name")
        ]
        
        self.data_aggregator.page_data = page_data
        
        name = self.result_handler._extract_restaurant_name_from_data()
        
        assert name == "Test Restaurant"  # First non-empty name

    def test_extract_restaurant_name_fallback(self):
        """Test restaurant name extraction with fallback."""
        self.data_aggregator.page_data = []
        
        name = self.result_handler._extract_restaurant_name_from_data()
        
        assert name == "Restaurant"  # Default fallback

    def test_create_page_data_from_result(self):
        """Test creating PageData from processing result."""
        url = "http://example.com/menu"
        
        # Create a mock data object with proper attribute access
        mock_data = Mock()
        mock_data.sources = ["json-ld"]
        mock_data.name = "Test Restaurant"
        mock_data.address = "123 Main St"
        mock_data.phone = "555-1234"
        mock_data.hours = "9-5"
        mock_data.price_range = "$$"
        mock_data.cuisine = "Italian"
        mock_data.menu_items = {"appetizers": ["Bruschetta"]}
        mock_data.social_media = ["facebook.com/test"]
        mock_data.confidence = "high"
        
        page_result = {
            "page_type": "menu",
            "data": mock_data
        }
        
        page_data = self.result_handler._create_page_data_from_result(url, page_result)
        
        assert isinstance(page_data, PageData)
        assert page_data.url == url
        assert page_data.page_type == "menu"
        assert page_data.source == "json-ld"
        assert page_data.restaurant_name == "Test Restaurant"
        assert page_data.address == "123 Main St"
        assert page_data.phone == "555-1234"
        assert page_data.hours == "9-5"
        assert page_data.price_range == "$$"
        assert page_data.cuisine == "Italian"
        assert page_data.menu_items == {"appetizers": ["Bruschetta"]}
        assert page_data.social_media == ["facebook.com/test"]
        assert page_data.confidence == "high"

    def test_create_page_data_with_empty_sources(self):
        """Test creating PageData when sources list is empty."""
        url = "http://example.com/menu"
        
        # Create a mock data object with proper attribute access
        mock_data = Mock()
        mock_data.sources = []  # Empty sources
        mock_data.name = "Test Restaurant"
        mock_data.address = ""
        mock_data.phone = ""
        mock_data.hours = ""
        mock_data.price_range = ""
        mock_data.cuisine = ""
        mock_data.menu_items = {}
        mock_data.social_media = []
        mock_data.confidence = "low"
        
        page_result = {
            "page_type": "menu",
            "data": mock_data
        }
        
        page_data = self.result_handler._create_page_data_from_result(url, page_result)
        
        assert page_data.source == "unknown"  # Fallback when no sources


class TestMultiPageScrapingResult:
    """Test MultiPageScrapingResult dataclass."""

    def test_empty_result_initialization(self):
        """Test empty result initialization."""
        result = MultiPageScrapingResult()
        
        assert result.restaurant_name == ""
        assert result.pages_processed == []
        assert result.successful_pages == []
        assert result.failed_pages == []
        assert result.aggregated_data is None
        assert result.processing_time == 0.0
        assert result.data_sources_summary == {}

    def test_result_with_data(self):
        """Test result with data."""
        mock_data = Mock(spec=RestaurantData)
        
        result = MultiPageScrapingResult(
            restaurant_name="Test Restaurant",
            pages_processed=["page1", "page2"],
            successful_pages=["page1"],
            failed_pages=["page2"],
            aggregated_data=mock_data,
            processing_time=5.5,
            data_sources_summary={"total": 2}
        )
        
        assert result.restaurant_name == "Test Restaurant"
        assert result.pages_processed == ["page1", "page2"]
        assert result.successful_pages == ["page1"]
        assert result.failed_pages == ["page2"]
        assert result.aggregated_data is mock_data
        assert result.processing_time == 5.5
        assert result.data_sources_summary == {"total": 2}


class TestPageProcessingResult:
    """Test PageProcessingResult dataclass."""

    def test_empty_processing_result(self):
        """Test empty processing result initialization."""
        result = PageProcessingResult()
        
        assert result.successful_pages == []
        assert result.failed_pages == []

    def test_processing_result_with_data(self):
        """Test processing result with data."""
        result = PageProcessingResult()
        result.successful_pages = ["page1", "page2"]
        result.failed_pages = ["page3"]
        
        assert result.successful_pages == ["page1", "page2"]
        assert result.failed_pages == ["page3"]