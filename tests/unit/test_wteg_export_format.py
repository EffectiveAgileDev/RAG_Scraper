"""Unit tests for WTEG export format for client RAG system.

Following TDD approach: Write failing tests first for RAG-ready export format.
"""
import pytest
import json
from datetime import datetime


class TestWTEGExportFormat:
    """Test WTEG export format for client RAG system."""
    
    def test_wteg_exporter_exists(self):
        """Test that WTEGExporter class exists."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            
            exporter = WTEGExporter()
            assert exporter is not None, "WTEGExporter should be instantiable"
            
        except ImportError:
            pytest.fail("WTEGExporter class not implemented yet")
    
    def test_rag_format_export(self):
        """Test export to RAG-optimized format for client ChatBot."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import WTEGRestaurantData, WTEGLocation, WTEGContactInfo
            
            exporter = WTEGExporter()
            
            # Create sample WTEG data
            sample_restaurant = WTEGRestaurantData(
                location=WTEGLocation(
                    street_address="123 Test St",
                    city="Portland",
                    state="OR",
                    zip_code="97201"
                ),
                cuisine="French",
                brief_description="Authentic French bistro with seasonal menu",
                click_to_call=WTEGContactInfo(primary_phone="(503) 555-0100"),
                source_url="https://mobimag.co/wteg/portland/21",
                confidence_score=0.85
            )
            
            # Export to RAG format
            rag_export = exporter.export_to_rag_format([sample_restaurant])
            
            # Verify RAG format structure
            assert "restaurants" in rag_export, "Should have restaurants section"
            assert "metadata" in rag_export, "Should have metadata section"
            assert len(rag_export["restaurants"]) == 1, "Should have one restaurant"
            
            restaurant = rag_export["restaurants"][0]
            assert "searchable_content" in restaurant, "Should have searchable content for embeddings"
            assert "location_summary" in restaurant, "Should have location summary"
            assert "contact_methods" in restaurant, "Should have contact methods"
            
        except ImportError:
            pytest.fail("RAG format export not implemented yet")
    
    def test_client_chatbot_format(self):
        """Test export format specifically for client ChatBot integration."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import WTEGRestaurantData, WTEGMenuItem
            
            exporter = WTEGExporter()
            
            # Create restaurant with menu items
            menu_items = [
                WTEGMenuItem(item_name="Duck Confit", price="$28", category="Entrees"),
                WTEGMenuItem(item_name="French Onion Soup", price="$12", category="Appetizers")
            ]
            
            sample_restaurant = WTEGRestaurantData(
                brief_description="French restaurant specializing in charcuterie",
                cuisine="French",
                menu_items=menu_items,
                confidence_score=0.9
            )
            
            # Export for ChatBot
            chatbot_export = exporter.export_for_chatbot([sample_restaurant])
            
            # Verify ChatBot format
            assert "conversation_ready_data" in chatbot_export, "Should have conversation-ready data"
            assert "query_responses" in chatbot_export, "Should have query responses"
            
            conv_data = chatbot_export["conversation_ready_data"][0]
            assert "natural_language_description" in conv_data, "Should have natural language description"
            assert "menu_summary" in conv_data, "Should have menu summary for food questions"
            assert "quick_facts" in conv_data, "Should have quick facts"
            
        except ImportError:
            pytest.fail("ChatBot format export not implemented yet")
    
    def test_preserve_raw_data_in_export(self):
        """Test that raw WTEG data is preserved in export without AI interpretation."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import WTEGRestaurantData
            
            exporter = WTEGExporter()
            
            # Raw data that should be preserved exactly
            raw_description = "Farm-to-table restaurant featuring locally sourced ingredients from Oregon farms"
            raw_cuisine = "Pacific Northwest"
            
            sample_restaurant = WTEGRestaurantData(
                brief_description=raw_description,
                cuisine=raw_cuisine,
                extraction_method="wteg_specific"
            )
            
            # Export preserving raw data
            preserved_export = exporter.export_with_raw_preservation([sample_restaurant])
            
            # Verify raw data preservation
            restaurant = preserved_export["restaurants"][0]
            assert restaurant["raw_data"]["brief_description"] == raw_description
            assert restaurant["raw_data"]["cuisine"] == raw_cuisine
            assert restaurant["raw_data"]["extraction_method"] == "wteg_specific"
            
            # Should not have AI-enhanced fields
            assert "ai_enhanced_description" not in restaurant["raw_data"]
            assert "ai_sentiment_analysis" not in restaurant["raw_data"]
            
        except ImportError:
            pytest.fail("Raw data preservation export not implemented yet")
    
    def test_client_specific_field_mapping(self):
        """Test mapping to client's specific field requirements."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import (
                WTEGRestaurantData, WTEGLocation, WTEGContactInfo, 
                WTEGWebLinks, WTEGServices, WTEGOnlineOrdering
            )
            
            exporter = WTEGExporter()
            
            # Complete WTEG data covering all client fields
            sample_restaurant = WTEGRestaurantData(
                location=WTEGLocation(street_address="123 Test St", city="Portland"),
                cuisine="Test Cuisine",
                brief_description="Test Description",
                click_to_call=WTEGContactInfo(primary_phone="(503) 555-0100"),
                click_for_website=WTEGWebLinks(official_website="https://test.com"),
                click_for_map=WTEGWebLinks(map_url="https://maps.google.com/test"),
                services_offered=WTEGServices(delivery_available=True, takeout_available=True),
                click_to_link=[WTEGOnlineOrdering(platform_name="DoorDash", ordering_url="https://doordash.com/test")]
            )
            
            # Export with client field mapping
            client_export = exporter.export_for_client([sample_restaurant])
            
            # Verify all client-required fields are present
            restaurant = client_export["restaurants"][0]
            
            # Client field requirements from specification
            required_client_fields = [
                "Location", "Cuisine", "Brief_Description", "Menu_items",
                "Click_to_Call", "Click_to_Link", "Services_Offered",
                "Click_for_Website", "Click_for_Map"
            ]
            
            for field in required_client_fields:
                assert field in restaurant, f"Missing required client field: {field}"
            
            # Verify field content is properly formatted
            assert restaurant["Location"] != "", "Location should not be empty"
            assert restaurant["Cuisine"] == "Test Cuisine", "Cuisine should match raw data"
            assert restaurant["Click_to_Call"] != "", "Phone should not be empty"
            
        except ImportError:
            pytest.fail("Client field mapping not implemented yet")
    
    def test_export_format_validation(self):
        """Test validation of export format structure."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import WTEGRestaurantData
            
            exporter = WTEGExporter()
            
            sample_restaurant = WTEGRestaurantData(
                brief_description="Test restaurant",
                confidence_score=0.8
            )
            
            # Test export validation
            export_data = exporter.export_to_rag_format([sample_restaurant])
            validation_result = exporter.validate_export_format(export_data)
            
            # Should have validation results
            assert "is_valid" in validation_result, "Should have validation status"
            assert "schema_errors" in validation_result, "Should have schema error list"
            assert "completeness_score" in validation_result, "Should have completeness score"
            
            # For complete data, should be valid
            assert validation_result["is_valid"] == True, "Complete export should be valid"
            assert len(validation_result["schema_errors"]) == 0, "Should have no schema errors"
            
        except ImportError:
            pytest.fail("Export format validation not implemented yet")
    
    def test_batch_export_for_multiple_restaurants(self):
        """Test batch export for multiple restaurants."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import WTEGRestaurantData
            
            exporter = WTEGExporter()
            
            # Create multiple restaurants (like client's URLs 21 and 16)
            restaurants = [
                WTEGRestaurantData(
                    brief_description="Canard - French bistro",
                    cuisine="French",
                    source_url="https://mobimag.co/wteg/portland/21"
                ),
                WTEGRestaurantData(
                    brief_description="Mamma Khouri's - Lebanese restaurant",
                    cuisine="Lebanese",
                    source_url="https://mobimag.co/wteg/portland/16"
                )
            ]
            
            # Batch export
            batch_export = exporter.export_batch_to_rag_format(restaurants)
            
            # Verify batch structure
            assert "restaurants" in batch_export, "Should have restaurants array"
            assert "batch_metadata" in batch_export, "Should have batch metadata"
            assert len(batch_export["restaurants"]) == 2, "Should have both restaurants"
            
            # Verify restaurants are different
            rest1 = batch_export["restaurants"][0]
            rest2 = batch_export["restaurants"][1]
            assert rest1["description"] != rest2["description"], "Should have different descriptions"
            
            # Verify batch metadata
            batch_meta = batch_export["batch_metadata"]
            assert batch_meta["restaurant_count"] == 2, "Should count restaurants correctly"
            assert "batch_timestamp" in batch_meta, "Should have timestamp"
            
        except ImportError:
            pytest.fail("Batch export not implemented yet")
    
    def test_export_quality_scoring(self):
        """Test quality scoring in export format."""
        try:
            from src.wteg.wteg_exporter import WTEGExporter
            from src.wteg.wteg_schema import WTEGRestaurantData, WTEGContactInfo
            
            exporter = WTEGExporter()
            
            # Complete restaurant (should have high quality)
            complete_restaurant = WTEGRestaurantData(
                brief_description="Complete restaurant data",
                cuisine="Italian",
                click_to_call=WTEGContactInfo(primary_phone="(503) 555-0100"),
                confidence_score=0.9
            )
            
            # Incomplete restaurant (should have lower quality)
            incomplete_restaurant = WTEGRestaurantData(
                brief_description="",  # Missing description
                confidence_score=0.3
            )
            
            # Export both with quality scoring
            complete_export = exporter.export_with_quality_scoring([complete_restaurant])
            incomplete_export = exporter.export_with_quality_scoring([incomplete_restaurant])
            
            # Verify quality scores
            complete_quality = complete_export["restaurants"][0]["quality_metrics"]
            incomplete_quality = incomplete_export["restaurants"][0]["quality_metrics"]
            
            assert complete_quality["completeness_score"] > incomplete_quality["completeness_score"]
            assert complete_quality["export_quality"] > incomplete_quality["export_quality"]
            assert complete_quality["rag_readiness"] > incomplete_quality["rag_readiness"]
            
        except ImportError:
            pytest.fail("Quality scoring not implemented yet")


if __name__ == "__main__":
    pytest.main([__file__])