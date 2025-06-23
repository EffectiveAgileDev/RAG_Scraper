import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json


class TestEnhancedMicrodataExtractor:
    """Test suite for enhanced microdata extractor with entity correlation."""

    def test_extractor_with_extraction_context(self):
        """Test that extractor accepts and uses extraction context."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro",
        )

        extractor = MicrodataExtractor(extraction_context=context)
        assert extractor.extraction_context == context
        assert extractor.extraction_context.entity_id == "rest_001"

    def test_extraction_includes_entity_metadata(self):
        """Test that extraction results include entity relationship metadata."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h1 itemprop="name">Italian Bistro</h1>
            <div itemprop="address" itemscope itemtype="http://schema.org/PostalAddress">
                <span itemprop="streetAddress">123 Main St</span>
            </div>
        </div>
        """

        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro",
        )

        extractor = MicrodataExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert len(results) == 1
        result = results[0]
        assert hasattr(result, "extraction_metadata")
        assert result.extraction_metadata["entity_id"] == "rest_001"
        assert result.extraction_metadata["parent_id"] == "dir_001"
        assert result.extraction_metadata["source_url"] == "/restaurants/italian-bistro"

    def test_correlate_data_across_parent_child_pages(self):
        """Test correlation of data between parent and child pages."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        # Parent directory page
        parent_html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h2 itemprop="name">Italian Bistro</h2>
            <span itemprop="description">Authentic Italian cuisine</span>
        </div>
        """

        # Child detail page with additional data
        child_html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h1 itemprop="name">Italian Bistro</h1>
            <span itemprop="telephone">555-0123</span>
            <div itemprop="address" itemscope itemtype="http://schema.org/PostalAddress">
                <span itemprop="streetAddress">123 Main St</span>
            </div>
        </div>
        """

        # Extract from parent
        parent_context = ExtractionContext(entity_id="dir_001", page_type="directory")
        parent_extractor = MicrodataExtractor(extraction_context=parent_context)
        parent_results = parent_extractor.extract_from_html(parent_html)

        # Extract from child with parent context
        child_context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            page_type="detail",
            parent_data=parent_results[0] if parent_results else None,
        )

        child_extractor = MicrodataExtractor(extraction_context=child_context)
        child_results = child_extractor.extract_from_html(child_html)

        assert len(child_results) == 1
        result = child_results[0]

        # Child should have detailed data
        assert result.name == "Italian Bistro"
        assert result.phone == "555-0123"
        assert result.address == "123 Main St"

        # Should indicate data correlation
        assert "parent_correlation" in result.extraction_metadata

    def test_deduplicate_with_child_precedence(self):
        """Test that child data takes precedence over parent in deduplication."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
            DataCorrelator,
        )

        parent_data = {
            "name": "Italian Restaurant",  # Less specific
            "cuisine": "Italian",
        }

        child_data = {
            "name": "Authentic Italian Bistro",  # More specific
            "phone": "555-0123",
        }

        correlator = DataCorrelator()
        merged = correlator.merge_parent_child_data(parent_data, child_data)

        # Child name should override parent
        assert merged["name"] == "Authentic Italian Bistro"
        # Child-only data should be preserved
        assert merged["phone"] == "555-0123"
        # Parent-only data should be preserved
        assert merged["cuisine"] == "Italian"

    def test_extraction_timestamp_tracking(self):
        """Test that extractions include timestamp."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Test Restaurant</span>
        </div>
        """

        context = ExtractionContext(entity_id="rest_001")

        with patch(
            "src.scraper.enhanced_microdata_extractor.datetime"
        ) as mock_datetime:
            mock_dt = Mock()
            mock_dt.isoformat.return_value = "2024-01-15T10:30:00"
            mock_datetime.now.return_value = mock_dt

            extractor = MicrodataExtractor(extraction_context=context)
            results = extractor.extract_from_html(html)

            assert results[0].extraction_metadata["timestamp"] == "2024-01-15T10:30:00"

    def test_extraction_method_recording(self):
        """Test that extraction method is recorded."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Test Restaurant</span>
        </div>
        """

        context = ExtractionContext(entity_id="rest_001")
        extractor = MicrodataExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert results[0].extraction_metadata["method"] == "microdata"

    def test_correlation_confidence_boost(self):
        """Test that correlation with parent data boosts confidence."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        # Minimal child data that would normally have medium confidence
        html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Bistro</span>
        </div>
        """

        # Parent data provides additional context
        parent_data = Mock()
        parent_data.cuisine = "Italian"
        parent_data.address = "Downtown District"

        context = ExtractionContext(
            entity_id="rest_001", parent_id="dir_001", parent_data=parent_data
        )

        extractor = MicrodataExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        # Confidence should be boosted by parent correlation
        assert "correlation_boost" in results[0].extraction_metadata

    def test_multiple_microdata_blocks_correlation(self):
        """Test correlation across multiple microdata blocks on same page."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h1 itemprop="name">Italian Bistro</h1>
        </div>
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Italian Bistro</span>
            <span itemprop="telephone">555-0123</span>
        </div>
        """

        context = ExtractionContext(entity_id="rest_001")
        extractor = MicrodataExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        # Should merge into single result with all data
        assert len(results) == 1
        result = results[0]
        assert result.name == "Italian Bistro"
        assert result.phone == "555-0123"
        assert "block_correlation" in result.extraction_metadata

    def test_inherit_context_from_parent(self):
        """Test inheriting context information from parent page."""
        from src.scraper.enhanced_microdata_extractor import (
            MicrodataExtractor,
            ExtractionContext,
        )

        parent_context = {
            "location_area": "Downtown District",
            "price_category": "Mid-range",
            "cuisine_region": "Mediterranean",
        }

        html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Olive Garden</span>
        </div>
        """

        context = ExtractionContext(
            entity_id="rest_001", parent_id="dir_001", parent_context=parent_context
        )

        extractor = MicrodataExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        result = results[0]
        assert result.extraction_metadata["inherited_context"] == parent_context

    def test_cross_page_entity_correlation(self):
        """Test correlation of entities across multiple pages."""
        from src.scraper.enhanced_microdata_extractor import EntityCorrelationTracker

        tracker = EntityCorrelationTracker()

        # Add restaurant from directory page
        tracker.add_entity_mention(
            "Italian Bistro",
            "dir_001",
            {"name": "Italian Bistro", "description": "Authentic cuisine"},
        )

        # Add same restaurant from detail page
        tracker.add_entity_mention(
            "Italian Bistro",
            "rest_001",
            {"name": "Italian Bistro", "phone": "555-0123", "address": "123 Main St"},
        )

        # Should correlate the entities
        correlations = tracker.get_correlations("Italian Bistro")
        assert len(correlations) == 2
        assert "dir_001" in [c["page_id"] for c in correlations]
        assert "rest_001" in [c["page_id"] for c in correlations]

    def test_microdata_pattern_recognition(self):
        """Test recognition of microdata patterns across pages."""
        from src.scraper.enhanced_microdata_extractor import MicrodataPatternRecognizer

        recognizer = MicrodataPatternRecognizer()

        # Register successful pattern
        recognizer.record_successful_extraction(
            pattern="Restaurant/name", selector="h1[itemprop='name']", success=True
        )

        # Same pattern on another page
        recognizer.record_successful_extraction(
            pattern="Restaurant/name", selector="h1[itemprop='name']", success=True
        )

        patterns = recognizer.get_reliable_patterns()
        assert "Restaurant/name" in patterns
        assert patterns["Restaurant/name"]["confidence"] > 0.8

    def test_structured_data_validation(self):
        """Test validation of structured data against schema."""
        from src.scraper.enhanced_microdata_extractor import MicrodataValidator

        validator = MicrodataValidator()

        # Valid restaurant data
        valid_data = {
            "name": "Italian Bistro",
            "address": "123 Main St",
            "telephone": "555-0123",
        }

        # Invalid data (missing required name)
        invalid_data = {"address": "123 Main St", "telephone": "555-0123"}

        assert validator.validate_restaurant_data(valid_data) == True
        assert validator.validate_restaurant_data(invalid_data) == False

    def test_correlation_scoring(self):
        """Test scoring of correlations between entities."""
        from src.scraper.enhanced_microdata_extractor import CorrelationScorer

        scorer = CorrelationScorer()

        entity1 = {"name": "Italian Bistro", "cuisine": "Italian"}

        entity2 = {"name": "Italian Bistro", "phone": "555-0123"}

        # Exact name match should have high score
        score = scorer.calculate_correlation_score(entity1, entity2)
        assert score >= 0.7  # Exact name match gives 0.7 base score

    def test_directory_listing_correlation(self):
        """Test correlation of restaurant listings in directory pages."""
        from src.scraper.enhanced_microdata_extractor import DirectoryListingCorrelator

        correlator = DirectoryListingCorrelator()

        directory_html = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h3 itemprop="name">Bistro One</h3>
            <span itemprop="url">/restaurants/bistro-one</span>
        </div>
        <div itemscope itemtype="http://schema.org/Restaurant">
            <h3 itemprop="name">Cafe Two</h3>
            <span itemprop="url">/restaurants/cafe-two</span>
        </div>
        """

        listings = correlator.extract_restaurant_listings(directory_html)

        assert len(listings) == 2
        assert listings[0]["name"] == "Bistro One"
        assert listings[0]["detail_url"] == "/restaurants/bistro-one"
        assert listings[1]["name"] == "Cafe Two"
        assert listings[1]["detail_url"] == "/restaurants/cafe-two"
