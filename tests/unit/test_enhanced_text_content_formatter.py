"""Unit tests for EnhancedTextContentFormatter class."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.enhanced_text_content_formatter import EnhancedTextContentFormatter


class TestEnhancedTextContentFormatter:
    """Test cases for EnhancedTextContentFormatter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = EnhancedTextContentFormatter()
        
        # Sample restaurant data for testing
        self.sample_restaurant = RestaurantData(
            name="Test Restaurant",
            address="123 Test Street",
            phone="(555) 123-4567",
            price_range="$15-$25",
            hours="Mon-Fri 9am-5pm",
            cuisine="Italian",
            menu_items={
                "appetizers": ["Bruschetta", "Calamari"],
                "entrees": ["Pasta", "Pizza"],
                "desserts": ["Tiramisu", "Gelato"]
            },
            sources=["json-ld", "heuristic"]
        )

    def test_init_with_default_params(self):
        """Test initialization with default parameters."""
        formatter = EnhancedTextContentFormatter()
        
        assert formatter.chunk_size_words == 500
        assert formatter.chunk_overlap_words == 50
        assert formatter.max_cross_references == 10
        assert formatter.semantic_chunker is not None

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        formatter = EnhancedTextContentFormatter(
            chunk_size_words=300,
            chunk_overlap_words=25,
            max_cross_references=5
        )
        
        assert formatter.chunk_size_words == 300
        assert formatter.chunk_overlap_words == 25
        assert formatter.max_cross_references == 5

    def test_generate_basic_content(self):
        """Test basic content generation."""
        content = self.formatter.generate_basic_content(self.sample_restaurant)
        
        assert "Test Restaurant" in content
        assert "123 Test Street" in content
        assert "(555) 123-4567" in content
        assert "$15-$25" in content
        assert "Hours: Mon-Fri 9am-5pm" in content
        assert "CUISINE: Italian" in content
        assert "APPETIZERS: Bruschetta, Calamari" in content
        assert "ENTREES: Pasta, Pizza" in content
        assert "DESSERTS: Tiramisu, Gelato" in content

    def test_generate_basic_content_minimal_data(self):
        """Test basic content generation with minimal data."""
        minimal_restaurant = RestaurantData(
            name="Minimal Restaurant",
            sources=["json-ld"]
        )
        
        content = self.formatter.generate_basic_content(minimal_restaurant)
        
        assert "Minimal Restaurant" in content
        assert content.strip() == "Minimal Restaurant"

    def test_format_menu_items(self):
        """Test menu items formatting."""
        menu_items = {
            "appetizers": ["Spring Rolls", "Soup"],
            "entrees": ["Chicken", "Beef"],
            "beverages": ["Coffee", "Tea"],
            "specials": ["Daily Special"]  # Should appear after standard sections
        }
        
        formatted = self.formatter.format_menu_items(menu_items)
        
        assert "APPETIZERS: Spring Rolls, Soup" in formatted
        assert "ENTREES: Chicken, Beef" in formatted
        assert "BEVERAGES: Coffee, Tea" in formatted
        assert "SPECIALS: Daily Special" in formatted
        
        # Check that standard sections appear before custom sections
        appetizers_index = formatted.index("APPETIZERS: Spring Rolls, Soup")
        specials_index = formatted.index("SPECIALS: Daily Special")
        assert appetizers_index < specials_index

    def test_format_menu_items_empty(self):
        """Test menu items formatting with empty data."""
        formatted = self.formatter.format_menu_items({})
        
        assert formatted == []

    def test_format_cross_references(self):
        """Test cross-references formatting."""
        relationships = [
            {"type": "parent", "target": "Parent Restaurant"},
            {"type": "sibling", "target": "Sister Restaurant"},
            {"type": "related", "target": "Related Restaurant"}
        ]
        
        formatted = self.formatter.format_cross_references(relationships)
        
        assert "- Parent: Parent Restaurant" in formatted
        assert "- Sibling: Sister Restaurant" in formatted
        assert "- Related: Related Restaurant" in formatted

    def test_format_cross_references_empty(self):
        """Test cross-references formatting with empty data."""
        formatted = self.formatter.format_cross_references([])
        
        assert formatted == "No related entities found."

    def test_format_cross_references_max_limit(self):
        """Test cross-references formatting respects max limit."""
        # Create more relationships than the max limit
        relationships = [
            {"type": f"type_{i}", "target": f"Target {i}"}
            for i in range(15)
        ]
        
        formatter = EnhancedTextContentFormatter(max_cross_references=5)
        formatted = formatter.format_cross_references(relationships)
        
        # Should only have 5 relationships
        lines = formatted.split("\n")
        assert len(lines) == 5

    def test_generate_hierarchical_content(self):
        """Test hierarchical content generation."""
        hierarchy_graph = {
            "Test Restaurant": {
                "parent": "Parent Restaurant",
                "children": ["Child Restaurant 1", "Child Restaurant 2"],
                "siblings": ["Sibling Restaurant"]
            }
        }
        
        content = self.formatter.generate_hierarchical_content(
            self.sample_restaurant, hierarchy_graph
        )
        
        assert "Test Restaurant" in content
        assert "Entity Hierarchy:" in content
        assert "Entity ID: Test Restaurant" in content
        assert "Parent Entity: Parent Restaurant" in content
        assert "Child Entities: Child Restaurant 1, Child Restaurant 2" in content
        assert "Related Entities: Sibling Restaurant" in content

    def test_generate_hierarchical_content_no_hierarchy(self):
        """Test hierarchical content generation with no hierarchy data."""
        content = self.formatter.generate_hierarchical_content(
            self.sample_restaurant, {}
        )
        
        # Should contain basic content but no hierarchy section
        assert "Test Restaurant" in content
        assert "Entity Hierarchy:" not in content

    def test_generate_entity_content(self):
        """Test entity content generation."""
        content = self.formatter.generate_entity_content(self.sample_restaurant)
        
        assert "Test Restaurant" in content
        assert "Entity Type: Restaurant" in content
        assert "Entity Category: Italian" in content
        assert "Extraction Sources: json-ld, heuristic" in content

    def test_generate_master_index(self):
        """Test master index generation."""
        restaurants = [
            RestaurantData(name="Restaurant 1", cuisine="Italian", address="Address 1", sources=["json-ld"]),
            RestaurantData(name="Restaurant 2", cuisine="Mexican", address="Address 2", sources=["json-ld"]),
            RestaurantData(name="Restaurant 3", cuisine="Italian", sources=["json-ld"])
        ]
        
        with patch('src.file_generator.enhanced_text_content_formatter.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2024-03-15 14:30:00"
            mock_datetime.now.return_value = mock_now
            
            index_content = self.formatter.generate_master_index(restaurants)
        
        assert "Master Index - All Restaurant Entities" in index_content
        assert "1. Restaurant 1" in index_content
        assert "   Category: Italian" in index_content
        assert "   Address: Address 1" in index_content
        assert "2. Restaurant 2" in index_content
        assert "   Category: Mexican" in index_content
        assert "3. Restaurant 3" in index_content
        assert "Total Entities: 3" in index_content
        assert "Generated:" in index_content

    def test_generate_category_index(self):
        """Test category index generation."""
        restaurants = [
            RestaurantData(name="Italian Place 1", address="Address 1", phone="111-111-1111", sources=["json-ld"]),
            RestaurantData(name="Italian Place 2", address="Address 2", phone="222-222-2222", sources=["json-ld"])
        ]
        
        with patch('src.file_generator.enhanced_text_content_formatter.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2024-03-15 14:30:00"
            mock_datetime.now.return_value = mock_now
            
            index_content = self.formatter.generate_category_index("Italian", restaurants)
        
        assert "Italian Category Index" in index_content
        assert "1. Italian Place 1" in index_content
        assert "   Address: Address 1" in index_content
        assert "   Phone: 111-111-1111" in index_content
        assert "2. Italian Place 2" in index_content
        assert "Total Italian Restaurants: 2" in index_content
        assert "Generated:" in index_content

    def test_extract_keywords_from_restaurant(self):
        """Test keyword extraction from restaurant data."""
        keywords = self.formatter.extract_keywords_from_restaurant(self.sample_restaurant)
        
        assert "italian" in keywords
        assert "test" in keywords
        assert "restaurant" in keywords
        assert "appetizers" in keywords
        assert "bruschetta" in keywords
        assert "pasta" in keywords
        # Should exclude short words
        assert "a" not in keywords
        assert "an" not in keywords

    def test_extract_keywords_from_restaurant_minimal(self):
        """Test keyword extraction with minimal restaurant data."""
        minimal_restaurant = RestaurantData(name="A B", sources=["json-ld"])  # Short words
        
        keywords = self.formatter.extract_keywords_from_restaurant(minimal_restaurant)
        
        # Should exclude words with length <= 2
        assert keywords == []

    def test_merge_multi_page_content(self):
        """Test merging content from multiple pages."""
        # Create entities with page metadata
        entities = []
        
        # Directory page
        directory = RestaurantData(name="Directory Info", sources=["heuristic"])
        directory.page_metadata = {"page_type": "directory"}
        entities.append(directory)
        
        # Detail page
        detail = RestaurantData(name="Detail Info", address="123 Main St", sources=["json-ld"])
        detail.page_metadata = {"page_type": "detail"}
        entities.append(detail)
        
        # Menu page
        menu = RestaurantData(name="Menu Info", menu_items={"entrees": ["Pasta"]}, sources=["json-ld"])
        menu.page_metadata = {"page_type": "menu"}
        entities.append(menu)
        
        merged_content = self.formatter.merge_multi_page_content(entities)
        
        # Should contain content from all pages in correct order
        assert "Directory Info" in merged_content
        assert "Detail Info" in merged_content
        assert "123 Main St" in merged_content
        assert "Menu Info" in merged_content
        assert "ENTREES: Pasta" in merged_content

    def test_add_cross_page_provenance(self):
        """Test adding cross-page provenance metadata."""
        entities = []
        
        # Create entities with page metadata
        entity1 = RestaurantData(name="Entity 1", sources=["json-ld"])
        entity1.page_metadata = {
            "page_type": "directory",
            "source_url": "http://example.com/page1",
            "entity_id": "entity_1"
        }
        entities.append(entity1)
        
        entity2 = RestaurantData(name="Entity 2", sources=["json-ld"])
        entity2.page_metadata = {
            "page_type": "detail",
            "source_url": "http://example.com/page2",
            "entity_id": "entity_2"
        }
        entities.append(entity2)
        
        chunk_with_provenance = self.formatter.add_cross_page_provenance(
            "Sample chunk content", entities, 0
        )
        
        assert "<!-- CHUNK_0_SOURCES: 2 pages -->" in chunk_with_provenance
        assert "Sample chunk content" in chunk_with_provenance

    def test_build_page_relationship_map(self):
        """Test building page relationship map."""
        restaurants = []
        
        # Create restaurants with page metadata
        restaurant1 = RestaurantData(name="Restaurant 1", sources=["json-ld"])
        restaurant1.page_metadata = {"entity_id": "rest_001"}
        restaurants.append(restaurant1)
        
        restaurant2 = RestaurantData(name="Restaurant 2", sources=["json-ld"])
        restaurant2.page_metadata = {"entity_id": "rest_002"}
        restaurants.append(restaurant2)
        
        # Restaurant without metadata
        restaurant3 = RestaurantData(name="Restaurant 3", sources=["json-ld"])
        restaurants.append(restaurant3)
        
        relationship_map = self.formatter.build_page_relationship_map(restaurants)
        
        assert "rest_001" in relationship_map
        assert "rest_002" in relationship_map
        assert relationship_map["rest_001"] == restaurant1
        assert relationship_map["rest_002"] == restaurant2
        assert len(relationship_map) == 2

    def test_extract_inheritable_context(self):
        """Test extracting inheritable context."""
        restaurant = RestaurantData(name="Test", sources=["json-ld"])
        restaurant.page_metadata = {
            "common_context": {
                "location_type": "downtown",
                "service_style": "casual dining"
            }
        }
        
        context = self.formatter.extract_inheritable_context(restaurant)
        
        assert "Location Type: downtown" in context
        assert "Service Style: casual dining" in context

    def test_extract_inheritable_context_no_context(self):
        """Test extracting inheritable context with no context data."""
        restaurant = RestaurantData(name="Test", sources=["json-ld"])
        
        context = self.formatter.extract_inheritable_context(restaurant)
        
        assert context == ""

    def test_calculate_adaptive_chunk_size(self):
        """Test calculating adaptive chunk size."""
        # Base size is 500
        assert self.formatter.calculate_adaptive_chunk_size(0) == 500
        assert self.formatter.calculate_adaptive_chunk_size(1) == 600
        assert self.formatter.calculate_adaptive_chunk_size(2) == 700

    def test_add_hierarchy_metadata(self):
        """Test adding hierarchy metadata to chunk."""
        chunk_with_metadata = self.formatter.add_hierarchy_metadata(
            "Sample chunk", self.sample_restaurant, 2, 1
        )
        
        assert "<!-- HIERARCHY_LEVEL_2_CHUNK_1 -->" in chunk_with_metadata
        assert "Sample chunk" in chunk_with_metadata

    def test_detect_temporal_conflicts(self):
        """Test detecting temporal conflicts."""
        # Create timeline with conflicts
        old_restaurant = RestaurantData(
            name="Restaurant",
            address="Old Address",
            phone="Old Phone",
            sources=["json-ld"]
        )
        
        new_restaurant = RestaurantData(
            name="Restaurant",
            address="New Address",
            phone="New Phone",
            sources=["json-ld"]
        )
        
        timeline = [
            ("2024-03-15T14:30:00Z", new_restaurant),  # Most recent
            ("2024-03-14T14:30:00Z", old_restaurant)   # Older
        ]
        
        conflicts = self.formatter.detect_temporal_conflicts(timeline)
        
        assert len(conflicts) == 2  # Address and phone conflicts
        
        address_conflict = next(c for c in conflicts if c["field"] == "address")
        assert address_conflict["latest"] == "New Address"
        assert address_conflict["older"] == "Old Address"
        
        phone_conflict = next(c for c in conflicts if c["field"] == "phone")
        assert phone_conflict["latest"] == "New Phone"
        assert phone_conflict["older"] == "Old Phone"

    def test_detect_temporal_conflicts_no_conflicts(self):
        """Test detecting temporal conflicts with no conflicts."""
        restaurant = RestaurantData(name="Restaurant", sources=["json-ld"])
        timeline = [("2024-03-15T14:30:00Z", restaurant)]
        
        conflicts = self.formatter.detect_temporal_conflicts(timeline)
        
        assert conflicts == []

    def test_generate_temporally_aware_content(self):
        """Test generating temporally aware content."""
        restaurant = RestaurantData(name="Restaurant", address="Address", sources=["json-ld"])
        timeline = [("2024-03-15T14:30:00Z", restaurant)]
        
        conflicts = [
            {"field": "address", "latest": "New Address", "older": "Old Address"},
            {"field": "phone", "latest": "New Phone", "older": "Old Phone"}
        ]
        
        content = self.formatter.generate_temporally_aware_content(timeline, conflicts)
        
        assert "Restaurant" in content
        assert "--- Data Evolution ---" in content
        assert "Address changed from 'Old Address' to 'New Address'" in content
        assert "Phone changed from 'Old Phone' to 'New Phone'" in content

    def test_add_temporal_metadata(self):
        """Test adding temporal metadata to chunk."""
        timeline = [("2024-03-15T14:30:00Z", self.sample_restaurant)]
        
        chunk_with_metadata = self.formatter.add_temporal_metadata(
            "Sample chunk", timeline, "entity_001", 0
        )
        
        assert "<!-- TEMPORAL_DATA: entity_001 updated 2024-03-15T14:30:00Z -->" in chunk_with_metadata
        assert "Sample chunk" in chunk_with_metadata

    def test_calculate_temporal_span(self):
        """Test calculating temporal span."""
        timeline = [
            ("2024-03-15T16:30:00Z", self.sample_restaurant),  # Latest
            ("2024-03-15T14:30:00Z", self.sample_restaurant)   # Earliest
        ]
        
        span_hours = self.formatter.calculate_temporal_span(timeline)
        
        assert span_hours == 2.0  # 2 hours difference

    def test_calculate_temporal_span_single_entry(self):
        """Test calculating temporal span with single entry."""
        timeline = [("2024-03-15T14:30:00Z", self.sample_restaurant)]
        
        span_hours = self.formatter.calculate_temporal_span(timeline)
        
        assert span_hours == 0

    def test_find_restaurant_by_entity_id(self):
        """Test finding restaurant by entity ID."""
        restaurants = []
        
        restaurant1 = RestaurantData(name="Restaurant 1", sources=["json-ld"])
        restaurant1.page_metadata = {"entity_id": "rest_001"}
        restaurants.append(restaurant1)
        
        restaurant2 = RestaurantData(name="Restaurant 2", sources=["json-ld"])
        restaurant2.page_metadata = {"entity_id": "rest_002"}
        restaurants.append(restaurant2)
        
        found = self.formatter.find_restaurant_by_entity_id(restaurants, "rest_001")
        assert found == restaurant1
        
        not_found = self.formatter.find_restaurant_by_entity_id(restaurants, "rest_999")
        assert not_found is None

    def test_add_retrieval_optimization_metadata(self):
        """Test adding retrieval optimization metadata."""
        related_entities = ["entity_1", "entity_2", "entity_3"]
        
        chunk_with_metadata = self.formatter.add_retrieval_optimization_metadata(
            "Sample chunk", self.sample_restaurant, related_entities, 0
        )
        
        assert "<!-- RETRIEVAL_OPTIMIZED: 3 related entities -->" in chunk_with_metadata
        assert "Sample chunk" in chunk_with_metadata

    def test_extract_primary_terms(self):
        """Test extracting primary terms."""
        terms = self.formatter.extract_primary_terms(self.sample_restaurant)
        
        assert "Test" in terms
        assert "Restaurant" in terms
        assert "Italian" in terms

    def test_extract_related_terms(self):
        """Test extracting related terms from content."""
        related_content = [
            "This is some restaurant content with keywords",
            "Another piece with dining and cuisine information"
        ]
        
        terms = self.formatter.extract_related_terms(related_content)
        
        assert "restaurant" in terms
        assert "content" in terms
        assert "keywords" in terms
        assert "dining" in terms
        assert "cuisine" in terms
        assert "information" in terms
        # Should exclude short words
        assert "is" not in terms
        assert "and" not in terms

    def test_generate_disambiguation_context(self):
        """Test generating disambiguation context."""
        restaurant = RestaurantData(
            name="Restaurant Name",
            address="123 Main St",
            sources=["json-ld"]
        )
        restaurant.page_metadata = {
            "page_type": "detail",
            "disambiguation_context": "downtown_location"
        }
        
        context = self.formatter.generate_disambiguation_context(restaurant, [])
        
        assert "Context: detail page" in context
        assert "Specific context: downtown_location" in context
        assert "Location: 123 Main St" in context

    def test_process_batch_with_optimization(self):
        """Test processing batch with optimization."""
        batch = [self.sample_restaurant, self.sample_restaurant]
        
        result = self.formatter.process_batch_with_optimization(batch)
        
        assert result["processed"] == 2

    def test_optimize_memory_usage(self):
        """Test memory usage optimization."""
        # This method calls gc.collect(), which should not raise an error
        self.formatter.optimize_memory_usage()
        # Test passes if no exception is raised