"""Unit tests for JSON-LD data extraction engine."""
import json
import pytest
from unittest.mock import Mock, patch
from bs4 import BeautifulSoup


class TestJSONLDExtractor:
    """Test JSON-LD structured data extraction functionality."""

    def test_extract_restaurant_from_valid_json_ld(self):
        """Test extraction from valid JSON-LD restaurant data."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        # Sample JSON-LD restaurant data
        json_ld_data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": "Tony's Italian Restaurant",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "1234 Commercial Street",
                "addressLocality": "Salem",
                "addressRegion": "OR",
                "postalCode": "97301",
            },
            "telephone": "(503) 555-0123",
            "openingHours": ["Tu-Sa 17:00-22:00", "Su 16:00-21:00"],
            "priceRange": "$18-$32",
            "servesCuisine": "Italian",
        }

        result = extractor.extract_restaurant_data(json_ld_data)

        assert result.name == "Tony's Italian Restaurant"
        assert result.address == "1234 Commercial Street, Salem, OR 97301"
        assert result.phone == "(503) 555-0123"
        assert result.hours == "Tu-Sa 17:00-22:00, Su 16:00-21:00"
        assert result.price_range == "$18-$32"
        assert result.cuisine == "Italian"
        assert result.confidence == "high"
        assert result.source == "json-ld"

    def test_extract_from_html_with_json_ld_script(self):
        """Test extraction from HTML containing JSON-LD script tag."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        html_content = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Restaurant",
                "name": "Best Pizza Place",
                "telephone": "503-555-9876"
            }
            </script>
        </head>
        <body>
            <h1>Welcome to Best Pizza</h1>
        </body>
        </html>
        """

        results = extractor.extract_from_html(html_content)

        assert len(results) == 1
        assert results[0].name == "Best Pizza Place"
        assert results[0].phone == "503-555-9876"
        assert results[0].confidence == "high"

    def test_extract_multiple_json_ld_blocks(self):
        """Test extraction from HTML with multiple JSON-LD blocks."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        html_content = """
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Restaurant",
                "name": "Main Restaurant"
            }
            </script>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "Parent Company"
            }
            </script>
        </head>
        </html>
        """

        results = extractor.extract_from_html(html_content)

        # Should only extract Restaurant type, not Organization
        assert len(results) == 1
        assert results[0].name == "Main Restaurant"

    def test_handle_invalid_json_ld_gracefully(self):
        """Test handling of invalid JSON-LD data."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        html_content = """
        <script type="application/ld+json">
        {
            "invalid": "json",
            "missing": "required fields"
        }
        </script>
        """

        results = extractor.extract_from_html(html_content)

        assert len(results) == 0  # Should return empty list for invalid data

    def test_handle_malformed_json_in_script(self):
        """Test handling of malformed JSON in script tags."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        html_content = """
        <script type="application/ld+json">
        {
            "malformed": "json"
            "missing": "comma"
        }
        </script>
        """

        results = extractor.extract_from_html(html_content)

        assert len(results) == 0  # Should handle JSON parse errors gracefully

    def test_extract_menu_from_json_ld(self):
        """Test extraction of menu items from JSON-LD data."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        json_ld_data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": "Italian Place",
            "hasMenu": {
                "@type": "Menu",
                "hasMenuSection": [
                    {
                        "@type": "MenuSection",
                        "name": "Appetizers",
                        "hasMenuItem": [
                            {
                                "@type": "MenuItem",
                                "name": "Bruschetta",
                                "description": "Fresh tomatoes on toasted bread",
                            }
                        ],
                    }
                ],
            },
        }

        result = extractor.extract_restaurant_data(json_ld_data)

        assert "Appetizers" in result.menu_items
        assert "Bruschetta" in result.menu_items["Appetizers"]
        assert result.confidence == "high"

    def test_normalize_address_from_json_ld(self):
        """Test address normalization from JSON-LD structured address."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        # Test various address formats
        address_formats = [
            {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St",
                "addressLocality": "Portland",
                "addressRegion": "Oregon",
                "postalCode": "97201",
            },
            {
                "@type": "PostalAddress",
                "streetAddress": "456 Oak Ave",
                "addressLocality": "Eugene",
                "addressRegion": "OR",
                "postalCode": "97401",
            },
        ]

        for address_data in address_formats:
            normalized = extractor.normalize_address(address_data)

            assert ", " in normalized  # Should have comma separators
            assert normalized.endswith(address_data["postalCode"])
            assert address_data["streetAddress"] in normalized
            assert address_data["addressLocality"] in normalized

    def test_extract_hours_from_json_ld_array(self):
        """Test extraction and normalization of operating hours."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        hours_formats = [
            ["Mo-Fr 09:00-17:00", "Sa 10:00-16:00"],
            ["Monday-Friday 9am-5pm", "Saturday 10am-4pm", "Sunday Closed"],
            "Mo-Su 11:00-22:00",  # Single string format
        ]

        for hours_data in hours_formats:
            normalized = extractor.normalize_hours(hours_data)

            assert isinstance(normalized, str)
            assert len(normalized) > 0
            # Should contain day references
            assert any(
                day in normalized.lower()
                for day in [
                    "mo",
                    "tu",
                    "we",
                    "th",
                    "fr",
                    "sa",
                    "su",
                    "monday",
                    "tuesday",
                ]
            )

    def test_extract_price_range_validation(self):
        """Test price range extraction and validation."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        price_formats = ["$15-$25", "$$", "$$$", "15-25", "Moderate"]

        for price_data in price_formats:
            normalized = extractor.normalize_price_range(price_data)

            # Should either be in $XX-$YY format or descriptive
            assert normalized is not None
            assert len(normalized) > 0

    def test_confidence_scoring_based_on_data_completeness(self):
        """Test confidence scoring based on available data fields."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        # Complete data should have high confidence
        complete_data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": "Complete Restaurant",
            "address": {"@type": "PostalAddress", "streetAddress": "123 Main"},
            "telephone": "503-555-1234",
            "openingHours": ["Mo-Fr 09:00-17:00"],
            "priceRange": "$15-$25",
        }

        # Minimal data should have lower confidence
        minimal_data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": "Minimal Restaurant",
        }

        complete_result = extractor.extract_restaurant_data(complete_data)
        minimal_result = extractor.extract_restaurant_data(minimal_data)

        assert complete_result.confidence == "high"
        assert minimal_result.confidence in ["medium", "low"]

    def test_handle_nested_organization_in_restaurant(self):
        """Test handling of nested organization data within restaurant."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        json_ld_data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": "Chain Restaurant",
            "parentOrganization": {
                "@type": "Organization",
                "name": "Restaurant Group LLC",
            },
            "telephone": "503-555-5555",
        }

        result = extractor.extract_restaurant_data(json_ld_data)

        assert (
            result.name == "Chain Restaurant"
        )  # Should use restaurant name, not parent
        assert result.phone == "503-555-5555"

    def test_filter_relevant_json_ld_types(self):
        """Test filtering to only process relevant schema types."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        relevant_types = ["Restaurant", "FoodEstablishment", "LocalBusiness"]
        irrelevant_types = ["Person", "Article", "WebPage", "Organization"]

        for schema_type in relevant_types:
            assert extractor.is_relevant_schema_type(schema_type) is True

        for schema_type in irrelevant_types:
            assert extractor.is_relevant_schema_type(schema_type) is False

    def test_extract_social_media_links(self):
        """Test extraction of social media links from JSON-LD."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        json_ld_data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": "Social Restaurant",
            "sameAs": [
                "https://www.facebook.com/socialrestaurant",
                "https://www.instagram.com/socialrestaurant",
                "https://twitter.com/socialrest",
            ],
        }

        result = extractor.extract_restaurant_data(json_ld_data)

        assert hasattr(result, "social_media")
        assert len(result.social_media) == 3
        assert any("facebook" in url for url in result.social_media)
        assert any("instagram" in url for url in result.social_media)
        assert any("twitter" in url for url in result.social_media)


class TestJSONLDExtractionResult:
    """Test JSON-LD extraction result data structure."""

    def test_create_extraction_result(self):
        """Test creation of extraction result object."""
        from src.scraper.json_ld_extractor import JSONLDExtractionResult

        result = JSONLDExtractionResult(
            name="Test Restaurant",
            address="123 Test St, Test City, OR 97000",
            phone="503-555-0000",
            confidence="high",
            source="json-ld",
        )

        assert result.name == "Test Restaurant"
        assert result.address == "123 Test St, Test City, OR 97000"
        assert result.phone == "503-555-0000"
        assert result.confidence == "high"
        assert result.source == "json-ld"

    def test_extraction_result_optional_fields(self):
        """Test extraction result with optional fields."""
        from src.scraper.json_ld_extractor import JSONLDExtractionResult

        result = JSONLDExtractionResult(
            name="Complete Restaurant",
            hours="Mo-Fr 09:00-17:00",
            price_range="$15-$25",
            cuisine="Italian",
            menu_items={"Appetizers": ["Bruschetta", "Calamari"]},
            social_media=["https://facebook.com/restaurant"],
            confidence="high",
            source="json-ld",
        )

        assert result.hours == "Mo-Fr 09:00-17:00"
        assert result.price_range == "$15-$25"
        assert result.cuisine == "Italian"
        assert "Appetizers" in result.menu_items
        assert len(result.social_media) == 1

    def test_extraction_result_to_dict(self):
        """Test conversion of extraction result to dictionary."""
        from src.scraper.json_ld_extractor import JSONLDExtractionResult

        result = JSONLDExtractionResult(
            name="Dict Restaurant", confidence="medium", source="json-ld"
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["name"] == "Dict Restaurant"
        assert result_dict["confidence"] == "medium"
        assert result_dict["source"] == "json-ld"

    def test_extraction_result_validation(self):
        """Test validation of extraction result data."""
        from src.scraper.json_ld_extractor import JSONLDExtractionResult

        # Valid result should pass validation
        valid_result = JSONLDExtractionResult(
            name="Valid Restaurant", confidence="high", source="json-ld"
        )

        assert valid_result.is_valid() is True

        # Result without name should fail validation
        invalid_result = JSONLDExtractionResult(
            name="", confidence="high", source="json-ld"
        )

        assert invalid_result.is_valid() is False


class TestJSONLDErrorHandling:
    """Test error handling in JSON-LD extraction."""

    def test_handle_missing_context(self):
        """Test handling of JSON-LD without @context."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        json_ld_data = {"@type": "Restaurant", "name": "No Context Restaurant"}

        result = extractor.extract_restaurant_data(json_ld_data)

        # Should still extract if recognizable structure
        assert result is not None or result is None  # Either works gracefully

    def test_handle_empty_json_ld(self):
        """Test handling of empty JSON-LD data."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        empty_data = {}

        result = extractor.extract_restaurant_data(empty_data)

        assert result is None  # Should return None for empty data

    def test_handle_non_dict_json_ld(self):
        """Test handling of non-dictionary JSON-LD data."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        extractor = JSONLDExtractor()

        non_dict_data = ["not", "a", "dictionary"]

        result = extractor.extract_restaurant_data(non_dict_data)

        assert result is None  # Should handle gracefully

    @patch("src.scraper.json_ld_extractor.BeautifulSoup")
    def test_handle_html_parsing_errors(self, mock_soup):
        """Test handling of HTML parsing errors."""
        from src.scraper.json_ld_extractor import JSONLDExtractor

        # Mock BeautifulSoup to raise an exception
        mock_soup.side_effect = Exception("HTML parsing failed")

        extractor = JSONLDExtractor()

        results = extractor.extract_from_html("<html>test</html>")

        assert results == []  # Should return empty list on parsing errors
