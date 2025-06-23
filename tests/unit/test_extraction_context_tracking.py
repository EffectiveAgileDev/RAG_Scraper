import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json


class TestExtractionContextTracking:
    """Test suite for comprehensive extraction context tracking."""

    def test_extraction_context_initialization(self):
        """Test that extraction context initializes correctly."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro",
            page_type="detail",
            relationships={"parent": "dir_001", "siblings": ["rest_002"]},
        )

        assert context.entity_id == "rest_001"
        assert context.parent_id == "dir_001"
        assert context.source_url == "/restaurants/italian-bistro"
        assert context.page_type == "detail"
        assert context.relationships["parent"] == "dir_001"

    def test_context_inheritance_from_parent(self):
        """Test that context can be inherited from parent pages."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        parent_context = {
            "location_area": "Downtown District",
            "price_range": "Mid-range",
            "cuisine_region": "Mediterranean",
        }

        context = ExtractionContext(
            entity_id="rest_001", parent_id="dir_001", parent_context=parent_context
        )

        assert context.parent_context["location_area"] == "Downtown District"
        assert context.parent_context["price_range"] == "Mid-range"
        assert context.parent_context["cuisine_region"] == "Mediterranean"

    def test_context_tracking_across_extractors(self):
        """Test that context is tracked consistently across all extractors."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )
        from src.scraper.enhanced_microdata_extractor import MicrodataExtractor
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor

        context = ExtractionContext(
            entity_id="rest_001", source_url="/restaurants/test"
        )

        # Test JSON-LD extractor
        json_extractor = JSONLDExtractor(extraction_context=context)
        assert json_extractor.extraction_context.entity_id == "rest_001"

        # Test Microdata extractor
        micro_extractor = MicrodataExtractor(extraction_context=context)
        assert micro_extractor.extraction_context.entity_id == "rest_001"

        # Test Heuristic extractor
        heuristic_extractor = HeuristicExtractor(extraction_context=context)
        assert heuristic_extractor.extraction_context.entity_id == "rest_001"

    def test_metadata_consistency_across_extractors(self):
        """Test that extraction metadata is consistent across all extractors."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )
        from src.scraper.enhanced_microdata_extractor import MicrodataExtractor
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor

        html_json_ld = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Test Restaurant"}
        </script>
        """

        html_microdata = """
        <div itemscope itemtype="http://schema.org/Restaurant">
            <span itemprop="name">Test Restaurant</span>
        </div>
        """

        html_heuristic = """
        <h1>Test Restaurant</h1>
        <p>Restaurant menu dining food</p>
        """

        context = ExtractionContext(
            entity_id="rest_001", parent_id="dir_001", source_url="/restaurants/test"
        )

        # Extract using all three methods
        json_extractor = JSONLDExtractor(extraction_context=context)
        json_results = json_extractor.extract_from_html(html_json_ld)

        micro_extractor = MicrodataExtractor(extraction_context=context)
        micro_results = micro_extractor.extract_from_html(html_microdata)

        heuristic_extractor = HeuristicExtractor(extraction_context=context)
        heuristic_results = heuristic_extractor.extract_from_html(html_heuristic)

        # All should have consistent metadata structure
        for results in [json_results, micro_results, heuristic_results]:
            if results:
                metadata = results[0].extraction_metadata
                assert "entity_id" in metadata
                assert "parent_id" in metadata
                assert "source_url" in metadata
                assert "method" in metadata
                assert "timestamp" in metadata
                assert metadata["entity_id"] == "rest_001"
                assert metadata["parent_id"] == "dir_001"
                assert metadata["source_url"] == "/restaurants/test"

    def test_source_page_tracking_accuracy(self):
        """Test that source page tracking is accurate and detailed."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Test Restaurant", "telephone": "555-0123"}
        </script>
        """

        context = ExtractionContext(
            entity_id="rest_001",
            source_url="/restaurants/detailed-page",
            page_type="detail",
            relationships={"parent": "dir_001"},
        )

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        assert len(results) == 1
        metadata = results[0].extraction_metadata

        # Verify detailed source tracking
        assert metadata["source_url"] == "/restaurants/detailed-page"
        assert metadata["entity_id"] == "rest_001"
        assert "timestamp" in metadata
        assert metadata["method"] == "json-ld"

    def test_timestamp_precision_and_consistency(self):
        """Test that timestamps are precise and consistent."""
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
            mock_dt = Mock()
            mock_dt.isoformat.return_value = "2024-01-15T10:30:45.123456"
            mock_datetime.now.return_value = mock_dt

            extractor = JSONLDExtractor(extraction_context=context)
            results = extractor.extract_from_html(html)

            timestamp = results[0].extraction_metadata["timestamp"]

            # Verify timestamp format and precision
            assert timestamp == "2024-01-15T10:30:45.123456"
            # Verify it's a valid ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_extraction_method_recording_accuracy(self):
        """Test that extraction methods are recorded accurately."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )
        from src.scraper.enhanced_microdata_extractor import MicrodataExtractor
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor

        context = ExtractionContext(entity_id="rest_001")

        # Test JSON-LD method recording
        json_html = """<script type="application/ld+json">{"@type": "Restaurant", "name": "Test"}</script>"""
        json_extractor = JSONLDExtractor(extraction_context=context)
        json_results = json_extractor.extract_from_html(json_html)
        if json_results:
            assert json_results[0].extraction_metadata["method"] == "json-ld"

        # Test Microdata method recording
        micro_html = """<div itemscope itemtype="http://schema.org/Restaurant"><span itemprop="name">Test</span></div>"""
        micro_extractor = MicrodataExtractor(extraction_context=context)
        micro_results = micro_extractor.extract_from_html(micro_html)
        if micro_results:
            assert micro_results[0].extraction_metadata["method"] == "microdata"

        # Test Heuristic method recording
        heuristic_html = """<h1>Test Restaurant</h1><p>Restaurant menu dining</p>"""
        heuristic_extractor = HeuristicExtractor(extraction_context=context)
        heuristic_results = heuristic_extractor.extract_from_html(heuristic_html)
        if heuristic_results:
            assert heuristic_results[0].extraction_metadata["method"] == "heuristic"

    def test_context_serialization_and_deserialization(self):
        """Test that extraction context can be serialized and deserialized."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        original_context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/test",
            page_type="detail",
            relationships={"parent": "dir_001", "siblings": ["rest_002"]},
            parent_context={"location": "Downtown"},
        )

        # Serialize to dict
        context_dict = {
            "entity_id": original_context.entity_id,
            "parent_id": original_context.parent_id,
            "source_url": original_context.source_url,
            "page_type": original_context.page_type,
            "relationships": original_context.relationships,
            "parent_context": original_context.parent_context,
        }

        # Serialize to JSON
        json_str = json.dumps(context_dict)

        # Deserialize
        loaded_dict = json.loads(json_str)
        restored_context = ExtractionContext(**loaded_dict)

        # Verify restoration
        assert restored_context.entity_id == original_context.entity_id
        assert restored_context.parent_id == original_context.parent_id
        assert restored_context.source_url == original_context.source_url
        assert restored_context.relationships == original_context.relationships

    def test_context_validation_and_error_handling(self):
        """Test validation and error handling for extraction context."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        # Test with minimal valid context
        minimal_context = ExtractionContext(entity_id="rest_001")
        assert minimal_context.entity_id == "rest_001"
        assert minimal_context.parent_id is None

        # Test with None values
        none_context = ExtractionContext(
            entity_id=None, parent_id=None, source_url=None
        )
        assert none_context.entity_id is None
        assert none_context.parent_id is None
        assert none_context.source_url is None

    def test_context_relationship_tracking(self):
        """Test comprehensive relationship tracking in context."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        relationships = {
            "parent": "dir_001",
            "siblings": ["rest_002", "rest_003"],
            "children": ["menu_001"],
            "references": ["loc_001"],
        }

        context = ExtractionContext(entity_id="rest_001", relationships=relationships)

        assert context.relationships["parent"] == "dir_001"
        assert len(context.relationships["siblings"]) == 2
        assert "rest_002" in context.relationships["siblings"]
        assert "rest_003" in context.relationships["siblings"]
        assert context.relationships["children"] == ["menu_001"]
        assert context.relationships["references"] == ["loc_001"]

    def test_context_pattern_learning_integration(self):
        """Test integration of pattern learning with context tracking."""
        from src.scraper.enhanced_heuristic_extractor import (
            PatternLearner,
            HeuristicExtractor,
            ExtractionContext,
        )

        learner = PatternLearner()
        learner.record_successful_pattern("name", "h1.title", success=True)
        learner.record_successful_pattern("name", "h1.title", success=True)

        context = ExtractionContext(entity_id="rest_001", pattern_learner=learner)

        html = """
        <h1 class="title">Restaurant Name</h1>
        <p>Restaurant menu dining food</p>
        """

        extractor = HeuristicExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        if results:
            assert "learned_pattern" in results[0].extraction_metadata
            assert results[0].extraction_metadata["learned_pattern"] is True

    def test_context_hierarchical_inheritance(self):
        """Test hierarchical inheritance of context across page levels."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        # Root context (directory level)
        root_context = {"location_area": "Downtown", "category": "Fine Dining"}

        # Parent context (restaurant level)
        parent_context = {
            **root_context,
            "cuisine_type": "Italian",
            "price_range": "$$",
        }

        # Child context (menu level)
        child_context = ExtractionContext(
            entity_id="menu_001",
            parent_id="rest_001",
            parent_context=parent_context,
            page_type="menu",
        )

        # Verify hierarchical inheritance
        assert child_context.parent_context["location_area"] == "Downtown"
        assert child_context.parent_context["category"] == "Fine Dining"
        assert child_context.parent_context["cuisine_type"] == "Italian"
        assert child_context.parent_context["price_range"] == "$$"

    def test_context_performance_tracking(self):
        """Test performance tracking within extraction context."""
        from src.scraper.enhanced_json_ld_extractor import (
            JSONLDExtractor,
            ExtractionContext,
        )

        context = ExtractionContext(entity_id="rest_001")

        html = """
        <script type="application/ld+json">
        {"@type": "Restaurant", "name": "Performance Test Restaurant"}
        </script>
        """

        start_time = datetime.now()

        extractor = JSONLDExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)

        end_time = datetime.now()
        extraction_duration = (end_time - start_time).total_seconds()

        # Verify extraction completed and was tracked
        assert len(results) == 1
        assert "timestamp" in results[0].extraction_metadata

        # Performance should be reasonable (under 1 second for simple extraction)
        assert extraction_duration < 1.0

    def test_context_multi_page_correlation(self):
        """Test context correlation across multiple related pages."""
        from src.scraper.enhanced_json_ld_extractor import ExtractionContext

        # Directory page context
        directory_context = ExtractionContext(
            entity_id="dir_001",
            page_type="directory",
            source_url="/restaurants/directory",
        )

        # Restaurant detail page contexts
        rest1_context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            page_type="detail",
            source_url="/restaurants/italian-bistro",
            relationships={"parent": "dir_001", "siblings": ["rest_002"]},
        )

        rest2_context = ExtractionContext(
            entity_id="rest_002",
            parent_id="dir_001",
            page_type="detail",
            source_url="/restaurants/french-cafe",
            relationships={"parent": "dir_001", "siblings": ["rest_001"]},
        )

        # Verify correlation
        assert rest1_context.parent_id == directory_context.entity_id
        assert rest2_context.parent_id == directory_context.entity_id
        assert "rest_002" in rest1_context.relationships["siblings"]
        assert "rest_001" in rest2_context.relationships["siblings"]
