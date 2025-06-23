import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json


class TestEnhancedJSONLDExtractor:
    """Test suite for enhanced JSON-LD extractor with relationship awareness."""

    def test_extractor_with_extraction_context(self):
        """Test that extractor accepts and uses extraction context."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro",
            relationships={"parent": "dir_001", "siblings": ["rest_002"]},
        )

        extractor = JSONLDExtractor(extraction_context=context)
        assert extractor.extraction_context == context
        assert extractor.extraction_context.entity_id == "rest_001"

    def test_extraction_includes_entity_metadata(self):
        """Test that extraction results include entity relationship metadata."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        html = """
        <script type="application/ld+json">
        {
            "@context": "http://schema.org",
            "@type": "Restaurant",
            "name": "Italian Bistro",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St"
            }
        }
        </script>
        """

        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro",
        )

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert len(results) == 1
        result = results[0]
        assert hasattr(result, "extraction_metadata")
        assert result.extraction_metadata["entity_id"] == "rest_001"
        assert result.extraction_metadata["parent_id"] == "dir_001"
        assert result.extraction_metadata["source_url"] == "/restaurants/italian-bistro"

    def test_extraction_timestamp_tracking(self):
        """Test that extractions include timestamp."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Test Restaurant"}
        </script>
        """

        context = ExtractionContext(entity_id="rest_001")

        with patch("src.scraper.enhanced_json_ld_extractor.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 0)

            extractor = JSONLDExtractor(extraction_context=context)
            results = extractor.extract_from_html(html)

            assert results[0].extraction_metadata["timestamp"] == "2024-01-15T10:30:00"

    def test_extraction_method_recording(self):
        """Test that extraction method is recorded."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Test Restaurant"}
        </script>
        """

        context = ExtractionContext(entity_id="rest_001")
        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert results[0].extraction_metadata["method"] == "json-ld"

    def test_inherit_parent_context(self):
        """Test that child pages can inherit context from parent."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        parent_context = {
            "location_area": "Downtown District",
            "price_category": "Budget-Friendly",
        }

        context = ExtractionContext(
            entity_id="rest_001", parent_id="dir_001", parent_context=parent_context
        )

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Italian Bistro"}
        </script>
        """

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        result = results[0]
        assert result.extraction_metadata["inherited_context"] == parent_context

    def test_extraction_with_pattern_cache(self):
        """Test that extractor can use cached patterns from previous extractions."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
            PatternCache,
        )

        pattern_cache = PatternCache()
        pattern_cache.add_successful_pattern("json_ld_path", "Restaurant/@type")

        context = ExtractionContext(entity_id="rest_002", pattern_cache=pattern_cache)

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "French Cafe"}
        </script>
        """

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        # Should use cached pattern knowledge
        assert len(results) == 1
        assert (
            pattern_cache.get_pattern_stats()["json_ld_path"]["Restaurant/@type"][
                "uses"
            ]
            > 0
        )

    def test_extraction_confidence_with_context(self):
        """Test that confidence is adjusted based on context."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        # Test with sibling confirmation
        context = ExtractionContext(
            entity_id="rest_002",
            siblings_extracted=["rest_001"],
            sibling_patterns={"@type": "Restaurant"},
        )

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "French Cafe", "telephone": "555-0123"}
        </script>
        """

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        # Confidence should be boosted by matching sibling patterns
        base_confidence = results[0].confidence
        assert (
            results[0].extraction_metadata.get("confidence_boost")
            == "sibling_pattern_match"
        )

    def test_multiple_json_ld_with_relationship_priority(self):
        """Test handling multiple JSON-LD blocks with relationship context."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        html = """
        <script type="application/ld+json">
        {"@type": "Organization", "name": "Restaurant Group"}
        </script>
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Italian Bistro"}
        </script>
        """

        context = ExtractionContext(
            entity_id="rest_001",
            page_type="detail",  # Indicates this is a restaurant detail page
        )

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        # Should prioritize Restaurant type for detail page
        assert len(results) == 1
        assert results[0].name == "Italian Bistro"

    def test_extraction_history_tracking(self):
        """Test that extraction history is maintained."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
            ExtractionHistory,
        )

        history = ExtractionHistory()
        history.add_extraction(
            "rest_001", "json-ld", {"name": "Old Name"}, "2024-01-01T10:00:00"
        )

        context = ExtractionContext(entity_id="rest_001", extraction_history=history)

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Updated Italian Bistro"}
        </script>
        """

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert results[0].extraction_metadata["previous_extraction"] is not None
        assert results[0].extraction_metadata["is_update"] is True

    def test_cross_page_reference_detection(self):
        """Test detection of references to other pages."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        html = """
        <script type="application/ld+json">
        {
            "@type": "Restaurant",
            "name": "Italian Bistro",
            "menu": "https://example.com/restaurants/italian-bistro/menu",
            "hasMenu": {
                "@type": "Menu",
                "url": "/restaurants/italian-bistro/menu"
            }
        }
        </script>
        """

        context = ExtractionContext(entity_id="rest_001")
        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert "referenced_pages" in results[0].extraction_metadata
        assert (
            "/restaurants/italian-bistro/menu"
            in results[0].extraction_metadata["referenced_pages"]
        )

    def test_aggregated_extraction_by_entity(self):
        """Test aggregating multiple extractions for the same entity."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionAggregator,
        )

        aggregator = ExtractionAggregator()

        # First extraction
        result1 = Mock()
        result1.name = "Italian Bistro"
        result1.phone = None
        result1.extraction_metadata = {
            "entity_id": "rest_001",
            "timestamp": "2024-01-01T10:00:00",
            "confidence": "high",
        }

        # Second extraction with additional data
        result2 = Mock()
        result2.name = "Italian Bistro"
        result2.phone = "555-0123"
        result2.extraction_metadata = {
            "entity_id": "rest_001",
            "timestamp": "2024-01-01T11:00:00",
            "confidence": "high",
        }

        aggregator.add_extraction(result1)
        aggregator.add_extraction(result2)

        aggregated = aggregator.get_aggregated_data("rest_001")
        assert aggregated["name"] == "Italian Bistro"
        assert aggregated["phone"] == "555-0123"  # Newer data
        assert len(aggregated["extraction_history"]) == 2

    def test_conflict_detection_and_resolution(self):
        """Test detection and resolution of conflicting data."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionConflictResolver

        resolver = ExtractionConflictResolver()

        # Add conflicting data
        data1 = {
            "name": "Italian Bistro",
            "phone": "555-0123",
            "extraction_metadata": {
                "method": "json-ld",
                "confidence": "high",
                "timestamp": "2024-01-01T10:00:00",
            },
        }

        data2 = {
            "name": "Italian Restaurant",  # Different name
            "phone": "555-0123",
            "extraction_metadata": {
                "method": "heuristic",
                "confidence": "medium",
                "timestamp": "2024-01-01T11:00:00",
            },
        }

        resolved = resolver.resolve_conflicts([data1, data2])

        # Should prefer json-ld over heuristic
        assert resolved["name"] == "Italian Bistro"
        assert "conflicts" in resolved
        assert "name" in resolved["conflicts"]

    def test_extraction_coverage_metrics(self):
        """Test tracking of extraction coverage metrics."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionMetricsTracker

        tracker = ExtractionMetricsTracker()

        # Track various extractions
        tracker.record_extraction(
            "rest_001", "json-ld", success=True, confidence="high"
        )
        tracker.record_extraction(
            "rest_002", "json-ld", success=True, confidence="high"
        )
        tracker.record_extraction(
            "rest_003", "heuristic", success=True, confidence="medium"
        )
        tracker.record_extraction("rest_004", "json-ld", success=False)

        metrics = tracker.get_metrics()

        assert metrics["pages_with_structured_data"] == 3
        assert metrics["heuristic_only_pages"] == 1
        assert metrics["extraction_success_rate"] == 0.75  # 3/4
        assert metrics["average_confidence"] > 0

    def test_pattern_effectiveness_tracking(self):
        """Test tracking effectiveness of extraction patterns."""
        from src.scraper.enhanced_json_ld_extractor import PatternEffectivenessTracker

        tracker = PatternEffectivenessTracker()

        # Record pattern usage
        tracker.record_pattern_use("Restaurant/@type", success=True)
        tracker.record_pattern_use("Restaurant/@type", success=True)
        tracker.record_pattern_use("Restaurant/name", success=True)
        tracker.record_pattern_use("Restaurant/menu", success=False)

        effectiveness = tracker.get_pattern_effectiveness()

        assert effectiveness["Restaurant/@type"]["success_rate"] == 1.0
        assert effectiveness["Restaurant/@type"]["uses"] == 2
        assert effectiveness["Restaurant/menu"]["success_rate"] == 0.0
