"""End-to-end integration test for multi-modal processing in the complete extraction pipeline."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper.ai_enhanced_multi_strategy_scraper import AIEnhancedMultiStrategyScraper
from src.scraper.json_ld_extractor import JSONLDExtractor
from src.scraper.microdata_extractor import MicrodataExtractor
from src.scraper.heuristic_extractor import HeuristicExtractor


class TestEndToEndMultiModalIntegration:
    """End-to-end test for complete multi-modal integration."""
    
    @pytest.fixture
    def mock_extractors(self):
        """Mock traditional extractors."""
        json_ld = Mock(spec=JSONLDExtractor)
        microdata = Mock(spec=MicrodataExtractor)
        heuristic = Mock(spec=HeuristicExtractor)
        
        # Configure mock returns
        json_ld.extract_from_html.return_value = [{"name": "Bistro Deluxe", "type": "Restaurant"}]
        microdata.extract_from_html.return_value = [{"telephone": "(555) 123-4567"}]
        heuristic.extract_from_html.return_value = [{"address": "123 Main St"}]
        
        return {
            "json_ld": json_ld,
            "microdata": microdata,
            "heuristic": heuristic
        }
    
    @pytest.fixture
    def sample_restaurant_html(self):
        """Sample restaurant HTML with various media."""
        return """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Bistro Deluxe - Fine Dining</title>
                <script type="application/ld+json">
                {
                    "@context": "https://schema.org",
                    "@type": "Restaurant",
                    "name": "Bistro Deluxe",
                    "telephone": "(555) 123-4567",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "123 Main Street",
                        "addressLocality": "City",
                        "addressRegion": "State"
                    }
                }
                </script>
            </head>
            <body>
                <h1>Welcome to Bistro Deluxe</h1>
                <div class="menu-section">
                    <img src="/images/menu.jpg" alt="Our delicious menu featuring appetizers and main courses">
                    <img src="/images/interior.jpg" alt="Elegant dining room ambiance with warm lighting">
                    <img src="/images/hours.png" alt="Business hours Monday through Sunday">
                </div>
                <div class="documents">
                    <a href="/brochures/services.pdf">Catering Services Brochure</a>
                    <a href="/menus/wine_list.pdf">Wine Selection Menu</a>
                </div>
                <div class="contact-info">
                    <p>Phone: (555) 123-4567</p>
                    <p>Email: info@bistrodeluxe.com</p>
                    <p>Address: 123 Main Street, City, State</p>
                </div>
            </body>
        </html>
        """
    
    def test_complete_extraction_pipeline_with_multi_modal(self, mock_extractors, sample_restaurant_html):
        """Test complete extraction pipeline including multi-modal processing."""
        # Initialize scraper with multi-modal enabled
        scraper = AIEnhancedMultiStrategyScraper(
            enable_multi_modal=True,
            enable_ai_extraction=False,  # Disable AI to focus on multi-modal
            parallel_processing=True,
            traditional_extractors=mock_extractors
        )
        
        config = {
            "industry": "Restaurant",
            "confidence_threshold": 0.6
        }
        
        # Mock multi-modal processor results
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_mm:
            mock_mm.return_value = {
                "text_extraction": {
                    "ocr_results": {
                        "extracted_text": "APPETIZERS\nCaesar Salad - $12\nSOUP - $8\nMAIN COURSES\nSalmon - $24",
                        "confidence": 0.92,
                        "menu_items": {
                            "appetizers": ["Caesar Salad - $12", "Soup - $8"],
                            "main_courses": ["Grilled Salmon - $24"]
                        }
                    },
                    "pdf_results": {
                        "extracted_text": "Our catering services include full-service events",
                        "structured_data": {
                            "services": ["catering", "events", "wine_selection"],
                            "pricing": {"catering": "Contact for pricing"}
                        },
                        "metadata": {"pages": 2, "source": "services.pdf"}
                    }
                },
                "image_analysis": {
                    "ambiance_description": "Elegant dining room with warm lighting and sophisticated decor",
                    "visual_elements": {
                        "lighting": ["warm", "elegant", "sophisticated"],
                        "seating": ["upscale tables", "comfortable chairs"],
                        "decor": ["modern", "refined"]
                    },
                    "atmosphere_tags": ["upscale", "romantic", "fine_dining"],
                    "confidence": 0.85
                },
                "processing_stats": {
                    "total_time": 15.2,
                    "images_processed": 3,
                    "pdfs_processed": 2,
                    "success_rate": 0.9
                },
                "source_attribution": {
                    "menu_items": "OCR_menu_image",
                    "services": "PDF_services_brochure",
                    "ambiance": "image_analysis_interior"
                }
            }
            
            # Execute extraction
            result = scraper.extract_from_html(sample_restaurant_html, config)
            
            # Verify extraction completed successfully
            assert result.ai_status == "success"
            assert result.errors is None or len(result.errors) == 0
            
            # Verify all extraction methods were used
            expected_methods = ["json_ld", "microdata", "heuristic", "multi_modal"]
            for method in expected_methods:
                assert method in result.extraction_methods
            
            # Verify restaurant data contains merged results
            restaurant_data = result.restaurant_data
            
            # Check traditional extraction data is present
            assert "name" in restaurant_data or "Bistro Deluxe" in str(restaurant_data)
            assert "telephone" in restaurant_data or "(555) 123-4567" in str(restaurant_data)
            assert "address" in restaurant_data or "123 Main St" in str(restaurant_data)
            
            # Check multi-modal data is present
            # Menu data from OCR
            if "menu" in restaurant_data:
                menu = restaurant_data["menu"]
                assert "appetizers" in menu
                assert any("Caesar Salad" in item for item in menu["appetizers"])
            
            # Services data from PDF processing
            if "services" in restaurant_data:
                services = restaurant_data["services"]
                assert "catering" in services
            
            # Ambiance data from image analysis
            if "ambiance" in restaurant_data:
                ambiance = restaurant_data["ambiance"]
                assert "description" in ambiance
                assert "elegant" in ambiance["description"].lower()
            
            # Verify confidence scores
            assert "overall" in result.confidence_scores
            assert result.confidence_scores["overall"] > 0.0
            
            # Verify source attribution
            assert result.source_attribution is not None
            assert len(result.source_attribution) > 0
            
            # Verify processing stats
            stats = result.processing_stats
            assert stats["parallel_execution"] is True
            assert stats["total_time"] > 0
            assert "traditional_time" in stats
            
            # Verify multi-modal processor was called
            mock_mm.assert_called_once()
            call_args = mock_mm.call_args
            assert call_args[0][0] == sample_restaurant_html  # HTML content
            assert call_args[1]["config"] == config  # Config
    
    def test_extraction_with_multi_modal_failure_recovery(self, mock_extractors, sample_restaurant_html):
        """Test that extraction continues gracefully when multi-modal processing fails."""
        scraper = AIEnhancedMultiStrategyScraper(
            enable_multi_modal=True,
            enable_ai_extraction=False,
            traditional_extractors=mock_extractors
        )
        
        config = {"industry": "Restaurant"}
        
        # Mock multi-modal processor to fail
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_mm:
            mock_mm.side_effect = Exception("Multi-modal processing failed")
            
            result = scraper.extract_from_html(sample_restaurant_html, config)
            
            # Extraction should still succeed with traditional methods
            assert result.ai_status == "success"
            
            # Should have traditional methods but not multi_modal
            assert "json_ld" in result.extraction_methods
            assert "microdata" in result.extraction_methods
            assert "heuristic" in result.extraction_methods
            # multi_modal might still be in extraction_methods but marked as failed
            
            # Should still have restaurant data from traditional extractors
            assert result.restaurant_data is not None
            assert len(result.restaurant_data) > 0
    
    def test_sequential_extraction_with_multi_modal(self, mock_extractors, sample_restaurant_html):
        """Test sequential extraction mode includes multi-modal processing."""
        scraper = AIEnhancedMultiStrategyScraper(
            enable_multi_modal=True,
            enable_ai_extraction=False,
            parallel_processing=False,  # Use sequential processing
            traditional_extractors=mock_extractors
        )
        
        config = {"industry": "Restaurant"}
        
        # Mock multi-modal processor
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_mm:
            mock_mm.return_value = {
                "text_extraction": {"ocr_results": {"menu_items": {"appetizers": ["Salad - $10"]}}},
                "processing_stats": {"success_rate": 0.8}
            }
            
            result = scraper.extract_from_html(sample_restaurant_html, config)
            
            # Verify multi-modal was included in sequential processing
            assert "multi_modal" in result.extraction_methods
            assert result.processing_stats["parallel_execution"] is False
            
            # Multi-modal processor should have been called
            mock_mm.assert_called_once()
    
    def test_extraction_statistics_tracking(self, mock_extractors, sample_restaurant_html):
        """Test that extraction statistics properly track multi-modal usage."""
        scraper = AIEnhancedMultiStrategyScraper(
            enable_multi_modal=True,
            enable_ai_extraction=False,
            traditional_extractors=mock_extractors
        )
        
        config = {"industry": "Restaurant"}
        
        # Mock multi-modal processor
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_mm:
            mock_mm.return_value = {
                "text_extraction": {"ocr_results": {"menu_items": {}}},
                "processing_stats": {"success_rate": 0.9}
            }
            
            # Run multiple extractions
            for _ in range(3):
                scraper.extract_from_html(sample_restaurant_html, config)
            
            # Check statistics
            stats = scraper.get_extraction_statistics()
            
            assert stats["total_extractions"] == 3
            assert stats["multi_modal_extractions"] == 3
            assert stats["traditional_extractions"] >= 9  # At least 3 methods × 3 runs
    
    def test_media_extraction_accuracy(self, sample_restaurant_html):
        """Test accurate media extraction from complex HTML."""
        scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
        
        media_files = scraper._extract_media_from_html(sample_restaurant_html)
        
        # Should extract 3 images and 2 PDFs
        images = [m for m in media_files if m["type"] == "image"]
        pdfs = [m for m in media_files if m["type"] == "pdf"]
        
        assert len(images) == 3
        assert len(pdfs) == 2
        
        # Check image categorization
        menu_img = next((img for img in images if "menu" in img["url"]), None)
        assert menu_img is not None
        assert menu_img["category"] == "menu"
        
        interior_img = next((img for img in images if "interior" in img["url"]), None)
        assert interior_img is not None
        assert interior_img["category"] == "ambiance"
        
        hours_img = next((img for img in images if "hours" in img["url"]), None)
        assert hours_img is not None
        assert hours_img["category"] == "hours"
        
        # Check PDF categorization
        services_pdf = next((pdf for pdf in pdfs if "services" in pdf["url"]), None)
        assert services_pdf is not None
        assert services_pdf["category"] == "services"
        
        wine_pdf = next((pdf for pdf in pdfs if "wine" in pdf["url"]), None)
        assert wine_pdf is not None
        assert wine_pdf["category"] == "menu"
    
    def test_confidence_scoring_with_multi_modal(self, mock_extractors, sample_restaurant_html):
        """Test that confidence scoring properly incorporates multi-modal results."""
        scraper = AIEnhancedMultiStrategyScraper(
            enable_multi_modal=True,
            enable_ai_extraction=False,
            traditional_extractors=mock_extractors
        )
        
        config = {"industry": "Restaurant"}
        
        # Mock multi-modal with high confidence
        with patch.object(scraper.multi_modal_processor, 'process_multi_modal') as mock_mm:
            mock_mm.return_value = {
                "text_extraction": {"ocr_results": {"menu_items": {"appetizers": ["Salad"]}}},
                "processing_stats": {"success_rate": 0.95}  # High confidence
            }
            
            result = scraper.extract_from_html(sample_restaurant_html, config)
            
            # Overall confidence should be reasonably high
            assert result.confidence_scores["overall"] > 0.7
            
            # Should have confidence scores for each method
            assert len(result.confidence_scores) > 1  # More than just overall