"""Unit tests demonstrating scraping and file generation integration failures."""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from src.scraper.restaurant_scraper import RestaurantScraper, ScrapingResult
from src.config.scraping_config import ScrapingConfig
from src.file_generator.file_generator_service import FileGeneratorService, FileGenerationRequest
from src.scraper.multi_strategy_scraper import RestaurantData


class TestScrapingFileGenerationIntegration:
    """Test suite demonstrating integration failures between scraping and file generation."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_restaurant_data(self):
        """Create sample restaurant data."""
        return RestaurantData(
            name="Test Restaurant",
            address="123 Test Street",
            phone="(555) 123-4567",
            sources=["test"]
        )

    @pytest.fixture
    def scraping_config(self, temp_output_dir):
        """Create scraping configuration."""
        return ScrapingConfig(
            urls=["https://example.com"],
            output_directory=temp_output_dir,
            file_mode="single"
        )

    def test_scraper_returns_metadata_not_file_paths(self, scraping_config, sample_restaurant_data):
        """Test that demonstrates scraper returns metadata instead of actual file paths."""
        scraper = RestaurantScraper()
        
        # Mock the multi-strategy scraper to return sample data
        with patch('src.scraper.restaurant_scraper.MultiStrategyScraper') as mock_scraper_class:
            mock_scraper_instance = MagicMock()
            mock_scraper_instance.scrape_url.return_value = sample_restaurant_data
            mock_scraper_class.return_value = mock_scraper_instance
            
            result = scraper.scrape_restaurants(scraping_config)
            
            # This demonstrates the problem: output_files contains descriptions, not file paths
            assert result.output_files["text"] == ["Extracted data for 1 restaurants"]
            
            # Verify no actual files were created
            output_dir = scraping_config.output_directory
            text_files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
            
            # THIS ASSERTION SHOULD PASS, demonstrating the problem
            assert len(text_files) == 0, "Scraper should not create files directly, but it returns success"

    def test_scraper_success_but_no_file_generation(self, scraping_config, sample_restaurant_data):
        """Test that scraper can succeed without triggering file generation."""
        scraper = RestaurantScraper()
        
        with patch('src.scraper.restaurant_scraper.MultiStrategyScraper') as mock_scraper_class:
            mock_scraper_instance = MagicMock()
            mock_scraper_instance.scrape_url.return_value = sample_restaurant_data
            mock_scraper_class.return_value = mock_scraper_instance
            
            result = scraper.scrape_restaurants(scraping_config)
            
            # Scraper reports success
            assert len(result.successful_extractions) == 1
            assert len(result.failed_urls) == 0
            
            # But no actual files exist
            output_dir = scraping_config.output_directory
            all_files = os.listdir(output_dir)
            output_files = [f for f in all_files if f.startswith('WebScrape_')]
            
            # THIS SHOULD PASS - demonstrating the integration gap
            assert len(output_files) == 0, "No output files should exist after scraping alone"

    def test_file_generation_service_works_independently(self, temp_output_dir, sample_restaurant_data):
        """Test that file generation service works when called directly."""
        service = FileGeneratorService()
        
        request = FileGenerationRequest(
            restaurant_data=[sample_restaurant_data],
            file_format="text",
            output_directory=temp_output_dir,
            allow_overwrite=True
        )
        
        result = service.generate_file(request)
        
        # File generation service works correctly
        assert result["success"] is True
        assert "file_path" in result
        assert os.path.exists(result["file_path"])
        
        # Verify file was actually created
        text_files = [f for f in os.listdir(temp_output_dir) if f.endswith('.txt')]
        assert len(text_files) == 1

    def test_missing_integration_between_scraper_and_file_generation(self, scraping_config, sample_restaurant_data):
        """Test demonstrating the missing integration between scraper and file generation."""
        scraper = RestaurantScraper()
        
        with patch('src.scraper.restaurant_scraper.MultiStrategyScraper') as mock_scraper_class:
            mock_scraper_instance = MagicMock()
            mock_scraper_instance.scrape_url.return_value = sample_restaurant_data
            mock_scraper_class.return_value = mock_scraper_instance
            
            # Scrape data
            scrape_result = scraper.scrape_restaurants(scraping_config)
            
            # Scraping succeeds
            assert len(scrape_result.successful_extractions) == 1
            
            # But there's no automatic file generation
            output_dir = scraping_config.output_directory
            files_before = set(os.listdir(output_dir))
            
            # File generation must be called separately
            service = FileGeneratorService()
            request = FileGenerationRequest(
                restaurant_data=scrape_result.successful_extractions,
                file_format="text",
                output_directory=output_dir,
                allow_overwrite=True
            )
            
            file_result = service.generate_file(request)
            
            # Now files exist
            files_after = set(os.listdir(output_dir))
            new_files = files_after - files_before
            
            # THIS DEMONSTRATES THE INTEGRATION GAP
            assert len(new_files) == 1, "File generation requires separate call"
            assert file_result["success"] is True

    def test_flask_scrape_endpoint_missing_file_generation(self, temp_output_dir):
        """Test demonstrating Flask scrape endpoint doesn't generate files."""
        from src.web_interface.app import create_app
        
        app = create_app(testing=True)
        client = app.test_client()
        
        # Mock successful scraping
        with patch('src.scraper.restaurant_scraper.RestaurantScraper') as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_result = ScrapingResult(
                successful_extractions=[RestaurantData(name="Test", sources=["test"])],
                failed_urls=[],
                total_processed=1,
                errors=[],
                processing_time=1.0
            )
            mock_result.output_files = {"text": ["Extracted data for 1 restaurants"]}
            mock_scraper.scrape_restaurants.return_value = mock_result
            mock_scraper_class.return_value = mock_scraper
            
            # Make scrape request
            response = client.post('/api/scrape', json={
                "urls": ["https://example.com"],
                "output_dir": temp_output_dir,
                "file_mode": "single"
            })
            
            # Request succeeds
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["processed_count"] == 1
            
            # But no files are actually created
            output_files = [f for f in os.listdir(temp_output_dir) if f.startswith('WebScrape_')]
            
            # THIS SHOULD PASS - demonstrating the problem
            assert len(output_files) == 0, "Flask scrape endpoint should create files but doesn't"

    def test_output_files_response_contains_descriptions_not_paths(self, temp_output_dir):
        """Test demonstrating that API responses contain descriptions, not file paths."""
        from src.web_interface.app import create_app
        
        app = create_app(testing=True)
        client = app.test_client()
        
        with patch('src.scraper.restaurant_scraper.RestaurantScraper') as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_result = ScrapingResult(
                successful_extractions=[RestaurantData(name="Test", sources=["test"])],
                failed_urls=[],
                total_processed=1,
                errors=[],
                processing_time=1.0
            )
            # This is the problematic part - descriptions instead of file paths
            mock_result.output_files = {"text": ["Extracted data for 1 restaurants"]}
            mock_scraper.scrape_restaurants.return_value = mock_result
            mock_scraper_class.return_value = mock_scraper
            
            response = client.post('/api/scrape', json={
                "urls": ["https://example.com"],
                "output_dir": temp_output_dir,
                "file_mode": "single"
            })
            
            data = response.get_json()
            output_files = data["output_files"]
            
            # THIS DEMONSTRATES THE PROBLEM
            assert len(output_files) == 1
            assert output_files[0] == "Extracted data for 1 restaurants"
            
            # The response doesn't contain actual file paths
            assert not output_files[0].startswith("/"), "Response should contain file paths, not descriptions"
            assert not os.path.exists(output_files[0]), "Response contains description, not actual file path"

    def test_separate_file_generation_endpoint_works(self, temp_output_dir):
        """Test that separate file generation endpoint works correctly."""
        from src.web_interface.app import create_app
        
        app = create_app(testing=True)
        client = app.test_client()
        
        # File generation endpoint works when called directly
        response = client.post('/api/generate-file', json={
            "restaurant_data": [
                {
                    "name": "Test Restaurant",
                    "address": "123 Test St",
                    "phone": "(555) 123-4567",
                    "sources": ["test"]
                }
            ],
            "file_format": "text",
            "output_directory": temp_output_dir,
            "allow_overwrite": True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "file_path" in data
        assert os.path.exists(data["file_path"])
        
        # This works correctly - demonstrating the separation
        text_files = [f for f in os.listdir(temp_output_dir) if f.endswith('.txt')]
        assert len(text_files) == 1

    def test_workflow_requires_two_separate_api_calls(self, temp_output_dir):
        """Test demonstrating that complete workflow requires two separate API calls."""
        from src.web_interface.app import create_app
        
        app = create_app(testing=True)
        client = app.test_client()
        
        # Step 1: Scrape data (doesn't create files)
        with patch('src.scraper.restaurant_scraper.RestaurantScraper') as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_result = ScrapingResult(
                successful_extractions=[RestaurantData(name="Test Restaurant", address="123 Test St", sources=["test"])],
                failed_urls=[],
                total_processed=1,
                errors=[],
                processing_time=1.0
            )
            mock_result.output_files = {"text": ["Extracted data for 1 restaurants"]}
            mock_scraper.scrape_restaurants.return_value = mock_result
            mock_scraper_class.return_value = mock_scraper
            
            scrape_response = client.post('/api/scrape', json={
                "urls": ["https://example.com"],
                "output_dir": temp_output_dir,
                "file_mode": "single"
            })
            
            assert scrape_response.status_code == 200
            scrape_data = scrape_response.get_json()
            assert scrape_data["success"] is True
            
            # No files created after scraping
            files_after_scrape = [f for f in os.listdir(temp_output_dir) if f.startswith('WebScrape_')]
            assert len(files_after_scrape) == 0
        
        # Step 2: Generate files (separate API call required)
        file_response = client.post('/api/generate-file', json={
            "restaurant_data": [
                {
                    "name": "Test Restaurant",
                    "address": "123 Test St", 
                    "phone": "",
                    "sources": ["test"]
                }
            ],
            "file_format": "text",
            "output_directory": temp_output_dir,
            "allow_overwrite": True
        })
        
        assert file_response.status_code == 200
        file_data = file_response.get_json()
        assert file_data["success"] is True
        
        # Files only created after separate file generation call
        files_after_generation = [f for f in os.listdir(temp_output_dir) if f.startswith('WebScrape_')]
        assert len(files_after_generation) == 1
        
        # THIS DEMONSTRATES THE INTEGRATION PROBLEM
        # User expects one API call (scrape) but needs two (scrape + generate-file)