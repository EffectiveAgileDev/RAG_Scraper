"""Integration tests for multi-modal processing in the main scraper."""

import pytest
from unittest.mock import Mock, patch
from src.scraper.ai_enhanced_multi_strategy_scraper import AIEnhancedMultiStrategyScraper
from src.processors.multi_modal_processor import MultiModalProcessor


class TestMultiModalIntegration:
    """Test multi-modal processing integration with main scraper."""
    
    def test_scraper_initialization_with_multi_modal(self):
        """Test that scraper initializes with multi-modal processing enabled."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        assert scraper.enable_multi_modal is True
        assert scraper.multi_modal_processor is not None
        assert isinstance(scraper.multi_modal_processor, MultiModalProcessor)
        assert "multi_modal_extractions" in scraper.extraction_stats
    
    def test_scraper_initialization_without_multi_modal(self):
        """Test that scraper initializes with multi-modal processing disabled."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=False)
        
        assert scraper.enable_multi_modal is False
        assert scraper.multi_modal_processor is None
    
    def test_extract_media_from_html(self):
        """Test media extraction from HTML content."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        html_content = """
        <html>
            <body>
                <img src="/menu.jpg" alt="Restaurant Menu">
                <img src="/interior.png" alt="Dining Room Ambiance">
                <a href="/brochure.pdf">Services Brochure</a>
                <img src="/hours.jpg" alt="Business Hours">
            </body>
        </html>
        """
        
        media_files = scraper._extract_media_from_html(html_content)
        
        assert len(media_files) == 4
        
        # Check image categorization
        menu_img = next((m for m in media_files if m["url"] == "/menu.jpg"), None)
        assert menu_img is not None
        assert menu_img["category"] == "menu"
        assert menu_img["type"] == "image"
        
        ambiance_img = next((m for m in media_files if m["url"] == "/interior.png"), None)
        assert ambiance_img is not None
        assert ambiance_img["category"] == "ambiance"
        
        hours_img = next((m for m in media_files if m["url"] == "/hours.jpg"), None)
        assert hours_img is not None
        assert hours_img["category"] == "hours"
        
        # Check PDF categorization
        pdf_file = next((m for m in media_files if m["url"] == "/brochure.pdf"), None)
        assert pdf_file is not None
        assert pdf_file["category"] == "services"
        assert pdf_file["type"] == "pdf"
    
    def test_convert_multi_modal_to_data(self):
        """Test conversion of multi-modal results to standard data format."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        multi_modal_result = {
            "text_extraction": {
                "ocr_results": {
                    "menu_items": {
                        "appetizers": ["Caesar Salad - $12", "Soup - $8"],
                        "main_courses": ["Salmon - $24", "Pasta - $18"]
                    },
                    "business_hours": {
                        "monday": "9:00-21:00",
                        "tuesday": "9:00-21:00"
                    },
                    "contact_info": {
                        "phones": ["(555) 123-4567"],
                        "emails": ["info@restaurant.com"]
                    }
                },
                "pdf_results": {
                    "structured_data": {
                        "services": ["catering", "delivery"],
                        "pricing": {"catering": "$50/person"}
                    }
                }
            },
            "image_analysis": {
                "ambiance_description": "Warm, cozy atmosphere",
                "visual_elements": {
                    "lighting": ["warm", "intimate"],
                    "seating": ["wooden tables"]
                },
                "atmosphere_tags": ["romantic", "cozy"]
            },
            "source_attribution": {
                "menu_items": "OCR_menu_image",
                "services": "PDF_brochure"
            },
            "processing_stats": {
                "images_processed": 3,
                "pdfs_processed": 1,
                "total_time": 12.5,
                "success_rate": 0.95
            }
        }
        
        media_files = []
        converted_data = scraper._convert_multi_modal_to_data(multi_modal_result, media_files)
        
        # Check menu extraction
        assert "menu" in converted_data
        assert "appetizers" in converted_data["menu"]
        assert "Caesar Salad - $12" in converted_data["menu"]["appetizers"]
        
        # Check hours extraction
        assert "hours" in converted_data
        assert converted_data["hours"]["monday"] == "9:00-21:00"
        
        # Check contact extraction
        assert "contact" in converted_data
        assert "(555) 123-4567" in converted_data["contact"]["phones"]
        
        # Check services from PDF
        assert "services" in converted_data
        assert "catering" in converted_data["services"]
        
        # Check pricing from PDF
        assert "pricing" in converted_data
        assert converted_data["pricing"]["catering"] == "$50/person"
        
        # Check ambiance from image analysis
        assert "ambiance" in converted_data
        assert converted_data["ambiance"]["description"] == "Warm, cozy atmosphere"
        assert "romantic" in converted_data["ambiance"]["atmosphere_tags"]
        
        # Check metadata
        assert "_source_attribution" in converted_data
        assert "_processing_stats" in converted_data
        assert converted_data["_processing_stats"]["images_processed"] == 3
        assert converted_data["_processing_stats"]["success_rate"] == 0.95
    
    def test_multi_modal_extraction_method(self):
        """Test the multi-modal extraction method."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        html_content = """
        <html>
            <body>
                <img src="/menu.jpg" alt="Restaurant Menu">
                <p>Welcome to our restaurant</p>
            </body>
        </html>
        """
        
        config = {"industry": "Restaurant"}
        
        # Mock the multi-modal processor
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_process:
            mock_process.return_value = {
                "text_extraction": {
                    "ocr_results": {
                        "menu_items": {"appetizers": ["Salad - $12"]}
                    }
                },
                "processing_stats": {
                    "success_rate": 0.9,
                    "total_time": 5.0
                }
            }
            
            result = scraper._extract_multi_modal(html_content, config)
            
            assert result["success"] is True
            assert result["method"] == "multi_modal"
            assert result["confidence"] == 0.9
            assert "menu" in result["data"]
            assert mock_process.called
    
    def test_multi_modal_extraction_failure(self):
        """Test multi-modal extraction handles failures gracefully."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        html_content = "<html><body>Test</body></html>"
        config = {}
        
        # Mock the multi-modal processor to raise exception
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            
            result = scraper._extract_multi_modal(html_content, config)
            
            assert result["success"] is False
            assert result["method"] == "multi_modal"
            assert result["confidence"] == 0.0
            assert "error" in result
            assert "Processing failed" in result["error"]
    
    def test_multi_modal_disabled_extraction(self):
        """Test extraction when multi-modal is disabled."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=False)
        
        html_content = "<html><body>Test</body></html>"
        config = {}
        
        result = scraper._extract_multi_modal(html_content, config)
        
        assert result["success"] is False
        assert result["confidence"] == 0.0
        assert result["data"] == {}
    
    @patch('src.scraper.ai_enhanced_multi_strategy_scraper.AIEnhancedMultiStrategyScraper._extract_json_ld')
    @patch('src.scraper.ai_enhanced_multi_strategy_scraper.AIEnhancedMultiStrategyScraper._extract_microdata')
    @patch('src.scraper.ai_enhanced_multi_strategy_scraper.AIEnhancedMultiStrategyScraper._extract_heuristic')
    def test_parallel_extraction_includes_multi_modal(self, mock_heuristic, mock_microdata, mock_json_ld):
        """Test that parallel extraction includes multi-modal processing."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True, parallel_processing=True)
        
        # Mock traditional extractors to return success
        mock_json_ld.return_value = {"data": {"name": "Test"}, "success": True, "confidence": 0.9}
        mock_microdata.return_value = {"data": {"phone": "123"}, "success": True, "confidence": 0.8}
        mock_heuristic.return_value = {"data": {"address": "123 St"}, "success": True, "confidence": 0.7}
        
        html_content = """
        <html>
            <body>
                <img src="/menu.jpg" alt="Menu">
                <p>Restaurant content</p>
            </body>
        </html>
        """
        config = {}
        processing_stats = {}
        
        # Mock multi-modal processor
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_mm:
            mock_mm.return_value = {
                "text_extraction": {"ocr_results": {"menu_items": {"appetizers": ["Salad - $12"]}}},
                "processing_stats": {"success_rate": 0.85}
            }
            
            results = scraper._extract_parallel(html_content, config, processing_stats)
            
            # Should have 4 results: json_ld, microdata, heuristic, multi_modal
            assert len(results) == 4
            
            methods = [r["method"] for r in results]
            assert "json_ld" in methods
            assert "microdata" in methods
            assert "heuristic" in methods
            assert "multi_modal" in methods
            
            # Check multi-modal result
            mm_result = next(r for r in results if r["method"] == "multi_modal")
            assert mm_result["success"] is True
            assert "menu" in mm_result["data"]
    
    def test_extraction_statistics_includes_multi_modal(self):
        """Test that extraction statistics include multi-modal counts."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        # Simulate multi-modal extraction
        scraper.extraction_stats["multi_modal_extractions"] = 5
        
        stats = scraper.get_extraction_statistics()
        
        assert "multi_modal_extractions" in stats
        assert stats["multi_modal_extractions"] == 5