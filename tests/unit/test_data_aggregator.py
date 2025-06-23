"""Unit tests for multi-page data aggregation and conflict resolution."""
import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Dict, Any


class TestDataAggregator:
    """Test data aggregation from multiple pages."""

    def test_create_data_aggregator(self):
        """Test creation of data aggregator."""
        from src.scraper.data_aggregator import DataAggregator

        aggregator = DataAggregator()

        assert hasattr(aggregator, "page_data")
        assert hasattr(aggregator, "conflict_resolution_rules")

    def test_add_page_data(self):
        """Test adding data from individual pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        page_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Tony's Restaurant",
            menu_items={"Appetizers": ["Calamari", "Bruschetta"]},
            source="json-ld",
        )

        aggregator.add_page_data(page_data)

        assert len(aggregator.page_data) == 1
        assert aggregator.page_data[0].page_type == "menu"

    def test_aggregate_restaurant_data_from_multiple_pages(self):
        """Test aggregating restaurant data from multiple pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData
        from src.scraper.multi_strategy_scraper import RestaurantData

        aggregator = DataAggregator()

        # Add data from home page
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Tony's Italian Restaurant",
            cuisine="Italian",
            source="heuristic",
        )

        # Add data from menu page
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Tony's Restaurant",
            menu_items={"Appetizers": ["Calamari"], "Entrees": ["Pasta"]},
            price_range="$15-30",
            source="json-ld",
        )

        # Add data from contact page
        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            restaurant_name="Tony's Italian",
            phone="(503) 555-1234",
            address="123 Main St, Portland, OR",
            hours="Mon-Sun 11am-10pm",
            source="microdata",
        )

        aggregator.add_page_data(home_data)
        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(contact_data)

        result = aggregator.aggregate()

        assert isinstance(result, RestaurantData)
        assert result.name == "Tony's Italian Restaurant"  # From home page
        assert result.cuisine == "Italian"
        assert result.phone == "(503) 555-1234"
        assert result.address == "123 Main St, Portland, OR"
        assert result.hours == "Mon-Sun 11am-10pm"
        assert result.price_range == "$15-30"
        assert "Calamari" in result.menu_items.get("Appetizers", [])

    def test_resolve_conflicting_restaurant_names(self):
        """Test resolving conflicting restaurant names across pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # Different name variations across pages
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Tony's Italian Restaurant",
            source="heuristic",
        )

        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Tony's Restaurant",
            source="json-ld",
        )

        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            restaurant_name="Tony's Italian",
            source="microdata",
        )

        aggregator.add_page_data(home_data)
        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(contact_data)

        result = aggregator.aggregate()

        # Should prioritize JSON-LD source
        assert result.name == "Tony's Restaurant"

    def test_resolve_conflicting_contact_information(self):
        """Test resolving conflicting contact information."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # Conflicting phone numbers
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            phone="(503) 555-0000",
            source="heuristic",
        )

        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            phone="(503) 555-1234",
            address="123 Main St",
            hours="Mon-Sun 11am-10pm",
            source="microdata",
        )

        aggregator.add_page_data(home_data)
        aggregator.add_page_data(contact_data)

        result = aggregator.aggregate()

        # Contact page should have priority for contact fields
        assert result.phone == "(503) 555-1234"

    def test_merge_menu_items_from_multiple_pages(self):
        """Test merging menu items from multiple pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # Menu page with some items
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items={
                "Appetizers": ["Calamari", "Bruschetta"],
                "Entrees": ["Pasta", "Pizza"],
            },
            source="json-ld",
        )

        # About page with additional menu info
        about_data = PageData(
            url="http://example.com/about",
            page_type="about",
            menu_items={
                "Appetizers": ["Antipasto"],  # Additional item
                "Desserts": ["Tiramisu", "Gelato"],  # New section
            },
            source="heuristic",
        )

        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(about_data)

        result = aggregator.aggregate()

        # Should merge all menu items
        assert set(result.menu_items["Appetizers"]) == {
            "Calamari",
            "Bruschetta",
            "Antipasto",
        }
        assert set(result.menu_items["Entrees"]) == {"Pasta", "Pizza"}
        assert set(result.menu_items["Desserts"]) == {"Tiramisu", "Gelato"}

    def test_deduplicate_menu_items(self):
        """Test deduplicating menu items across pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # Two pages with overlapping menu items
        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items={"Appetizers": ["Calamari", "Bruschetta"]},
            source="json-ld",
        )

        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            menu_items={"Appetizers": ["Calamari", "Antipasto"]},  # Calamari duplicate
            source="heuristic",
        )

        aggregator.add_page_data(menu_data)
        aggregator.add_page_data(home_data)

        result = aggregator.aggregate()

        # Should not have duplicates
        appetizers = result.menu_items["Appetizers"]
        assert appetizers.count("Calamari") == 1
        assert set(appetizers) == {"Calamari", "Bruschetta", "Antipasto"}

    def test_track_data_sources_for_audit(self):
        """Test tracking data sources for audit trail."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Restaurant Name",
            source="heuristic",
        )

        menu_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items={"Entrees": ["Pasta"]},
            source="json-ld",
        )

        aggregator.add_page_data(home_data)
        aggregator.add_page_data(menu_data)

        result = aggregator.aggregate()

        # Should track all sources used
        assert "heuristic" in result.sources
        assert "json-ld" in result.sources
        assert len(result.sources) == 2

    def test_calculate_confidence_from_multiple_sources(self):
        """Test calculating confidence based on multiple sources."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # High confidence data from structured sources
        json_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Restaurant",
            source="json-ld",
            confidence="high",
        )

        microdata = PageData(
            url="http://example.com/contact",
            page_type="contact",
            phone="(503) 555-1234",
            source="microdata",
            confidence="medium",
        )

        aggregator.add_page_data(json_data)
        aggregator.add_page_data(microdata)

        result = aggregator.aggregate()

        # Should have high confidence due to multiple structured sources
        assert result.confidence == "high"

    def test_handle_empty_page_data(self):
        """Test handling case where no useful data is found."""
        from src.scraper.data_aggregator import DataAggregator

        aggregator = DataAggregator()

        result = aggregator.aggregate()

        assert result is None or result.name == ""

    def test_prioritize_structured_data_sources(self):
        """Test prioritizing structured data sources over heuristic."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # Heuristic data (lower priority)
        heuristic_data = PageData(
            url="http://example.com/",
            page_type="home",
            restaurant_name="Heuristic Name",
            phone="(000) 000-0000",
            source="heuristic",
        )

        # JSON-LD data (higher priority)
        structured_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            restaurant_name="Structured Name",
            phone="(503) 555-1234",
            source="json-ld",
        )

        aggregator.add_page_data(heuristic_data)
        aggregator.add_page_data(structured_data)

        result = aggregator.aggregate()

        # Should prioritize structured data
        assert result.name == "Structured Name"
        assert result.phone == "(503) 555-1234"

    def test_aggregate_social_media_links(self):
        """Test aggregating social media links from multiple pages."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            social_media=["https://facebook.com/restaurant"],
            source="heuristic",
        )

        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            social_media=[
                "https://instagram.com/restaurant",
                "https://twitter.com/restaurant",
            ],
            source="microdata",
        )

        aggregator.add_page_data(home_data)
        aggregator.add_page_data(contact_data)

        result = aggregator.aggregate()

        # Should combine all unique social media links
        expected_links = {
            "https://facebook.com/restaurant",
            "https://instagram.com/restaurant",
            "https://twitter.com/restaurant",
        }
        assert set(result.social_media) == expected_links

    def test_page_type_priority_for_contact_fields(self):
        """Test that contact page has priority for contact-related fields."""
        from src.scraper.data_aggregator import DataAggregator, PageData

        aggregator = DataAggregator()

        # Multiple pages with contact info
        home_data = PageData(
            url="http://example.com/",
            page_type="home",
            phone="(503) 555-0000",
            address="Wrong Address",
            hours="Wrong Hours",
            source="json-ld",  # Higher source priority
        )

        contact_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            phone="(503) 555-1234",
            address="123 Main St",
            hours="Mon-Sun 11am-10pm",
            source="heuristic",  # Lower source priority
        )

        aggregator.add_page_data(home_data)
        aggregator.add_page_data(contact_data)

        result = aggregator.aggregate()

        # Contact page should win for contact fields despite lower source priority
        assert result.phone == "(503) 555-1234"
        assert result.address == "123 Main St"
        assert result.hours == "Mon-Sun 11am-10pm"


class TestPageData:
    """Test PageData dataclass for individual page information."""

    def test_create_page_data_with_required_fields(self):
        """Test creating PageData with required fields."""
        from src.scraper.data_aggregator import PageData

        page_data = PageData(
            url="http://example.com/menu", page_type="menu", source="json-ld"
        )

        assert page_data.url == "http://example.com/menu"
        assert page_data.page_type == "menu"
        assert page_data.source == "json-ld"

    def test_page_data_with_restaurant_information(self):
        """Test PageData with restaurant information fields."""
        from src.scraper.data_aggregator import PageData

        page_data = PageData(
            url="http://example.com/contact",
            page_type="contact",
            restaurant_name="Tony's Restaurant",
            phone="(503) 555-1234",
            address="123 Main St",
            hours="Mon-Sun 11am-10pm",
            source="microdata",
        )

        assert page_data.restaurant_name == "Tony's Restaurant"
        assert page_data.phone == "(503) 555-1234"
        assert page_data.address == "123 Main St"
        assert page_data.hours == "Mon-Sun 11am-10pm"

    def test_page_data_with_menu_items(self):
        """Test PageData with menu items."""
        from src.scraper.data_aggregator import PageData

        menu_items = {
            "Appetizers": ["Calamari", "Bruschetta"],
            "Entrees": ["Pasta", "Pizza"],
        }

        page_data = PageData(
            url="http://example.com/menu",
            page_type="menu",
            menu_items=menu_items,
            source="json-ld",
        )

        assert page_data.menu_items == menu_items
        assert "Calamari" in page_data.menu_items["Appetizers"]

    def test_page_data_to_dict_conversion(self):
        """Test converting PageData to dictionary."""
        from src.scraper.data_aggregator import PageData

        page_data = PageData(
            url="http://example.com/about",
            page_type="about",
            restaurant_name="Restaurant Name",
            cuisine="Italian",
            source="heuristic",
        )

        data_dict = page_data.to_dict()

        assert data_dict["url"] == "http://example.com/about"
        assert data_dict["page_type"] == "about"
        assert data_dict["restaurant_name"] == "Restaurant Name"
        assert data_dict["cuisine"] == "Italian"
        assert data_dict["source"] == "heuristic"


class TestEnhancedDataAggregator:
    """Test enhanced data aggregation functionality for multi-page entities."""

    @pytest.fixture
    def aggregator(self):
        """Create DataAggregator instance for testing."""
        from src.scraper.data_aggregator import DataAggregator

        return DataAggregator()

    @pytest.fixture
    def sample_entities(self):
        """Create sample restaurant entities for testing."""
        from src.scraper.data_aggregator import RestaurantEntity

        return [
            RestaurantEntity(
                entity_id="rest_1",
                name="Mario's Pizza",
                url="https://restaurant1.com",
                entity_type="restaurant",
                data={
                    "address": "123 Main St",
                    "phone": "555-0001",
                    "cuisine": "Italian",
                },
            ),
            RestaurantEntity(
                entity_id="menu_1",
                name="Mario's Pizza Menu",
                url="https://restaurant1.com/menu",
                entity_type="menu",
                data={"items": ["Pizza", "Pasta", "Salads"]},
            ),
            RestaurantEntity(
                entity_id="contact_1",
                name="Mario's Pizza Contact",
                url="https://restaurant1.com/contact",
                entity_type="contact",
                data={"email": "info@marios.com", "hours": "Mon-Sun 11am-10pm"},
            ),
        ]

    @pytest.fixture
    def sample_relationships(self):
        """Create sample entity relationships."""
        from src.scraper.data_aggregator import EntityRelationship

        return [
            EntityRelationship(
                parent_id="rest_1",
                child_id="menu_1",
                relationship_type="has_menu",
                strength=0.9,
            ),
            EntityRelationship(
                parent_id="rest_1",
                child_id="contact_1",
                relationship_type="has_contact",
                strength=0.8,
            ),
        ]

    def test_create_enhanced_data_aggregator(self, aggregator):
        """Test creating enhanced DataAggregator instance."""
        assert aggregator is not None
        assert hasattr(aggregator, "aggregate_entities")
        assert hasattr(aggregator, "deduplicate_entities")
        assert hasattr(aggregator, "create_hierarchical_structure")

    def test_aggregate_entities_by_restaurant_name(self, aggregator):
        """Test aggregating entities with same restaurant name."""
        from src.scraper.data_aggregator import RestaurantEntity

        entities = [
            RestaurantEntity(
                entity_id="page_1",
                name="Mario's Pizza",
                url="https://restaurant1.com",
                entity_type="main",
                data={"address": "123 Main St", "phone": "555-0001"},
            ),
            RestaurantEntity(
                entity_id="page_2",
                name="Mario's Pizza",
                url="https://restaurant1.com/menu",
                entity_type="menu",
                data={"items": ["Pizza", "Pasta"]},
            ),
            RestaurantEntity(
                entity_id="page_3",
                name="Mario's Pizza",
                url="https://restaurant1.com/contact",
                entity_type="contact",
                data={"email": "info@marios.com"},
            ),
        ]

        result = aggregator.aggregate_entities(entities)

        # Should consolidate entities with same name
        assert len(result) == 1
        aggregated_entity = result[0]
        assert aggregated_entity.name == "Mario's Pizza"

        # Should merge data from all entities
        assert "address" in aggregated_entity.data
        assert "phone" in aggregated_entity.data
        assert "items" in aggregated_entity.data
        assert "email" in aggregated_entity.data

    def test_aggregate_with_relationships(
        self, aggregator, sample_entities, sample_relationships
    ):
        """Test aggregating entities with relationship information."""
        result = aggregator.aggregate_with_relationships(
            sample_entities, sample_relationships
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Check that relationships are preserved in result
        main_entity = next((e for e in result if e.entity_type == "restaurant"), None)
        assert main_entity is not None

        # Should have relationship metadata
        assert (
            hasattr(main_entity, "relationships") or "relationships" in main_entity.data
        )

    def test_deduplicate_entities_by_url_similarity(self, aggregator):
        """Test deduplicating entities by URL similarity."""
        from src.scraper.data_aggregator import RestaurantEntity

        entities = [
            RestaurantEntity(
                entity_id="dup_1",
                name="Mario's Pizza",
                url="https://restaurant1.com",
                entity_type="restaurant",
                data={"address": "123 Main St"},
            ),
            RestaurantEntity(
                entity_id="dup_2",
                name="Mario's Pizzeria",  # Slightly different name
                url="https://restaurant1.com",  # Same URL
                entity_type="restaurant",
                data={"phone": "555-0001"},
            ),
            RestaurantEntity(
                entity_id="unique_1",
                name="Luigi's Pasta",
                url="https://restaurant2.com",
                entity_type="restaurant",
                data={"address": "456 Oak Ave"},
            ),
        ]

        result = aggregator.deduplicate_entities(entities)

        # Should have 2 unique entities (by URL)
        assert len(result) == 2

        # Check that duplicate data was merged
        merged_entity = next(
            (e for e in result if e.url == "https://restaurant1.com"), None
        )
        assert merged_entity is not None
        assert "address" in merged_entity.data
        assert "phone" in merged_entity.data

    def test_merge_entities_with_priority_rules(self, aggregator):
        """Test merging entities with data priority rules."""
        from src.scraper.data_aggregator import RestaurantEntity

        entities = [
            RestaurantEntity(
                entity_id="merge_1",
                name="Mario's Pizza",
                url="https://main-site.com",
                entity_type="restaurant",
                data={"address": "123 Main St", "phone": "555-0001", "rating": 4.2},
            ),
            RestaurantEntity(
                entity_id="merge_2",
                name="Mario's Pizzeria",
                url="https://review-site.com",
                entity_type="restaurant",
                data={
                    "address": "123 Main Street",  # More detailed
                    "phone": "(555) 000-1",  # Different format
                    "rating": 4.5,  # Higher rating
                    "cuisine": "Italian",  # Additional info
                },
            ),
        ]

        result = aggregator.merge_entities(entities)

        assert result is not None
        assert isinstance(result, RestaurantEntity)

        # Should keep most detailed/accurate information
        assert result.data["address"] == "123 Main Street"  # More detailed
        assert result.data["rating"] == 4.5  # Higher rating
        assert "cuisine" in result.data  # Additional info preserved

    def test_create_hierarchical_structure_with_levels(self, aggregator):
        """Test creating hierarchical data structure with multiple levels."""
        from src.scraper.data_aggregator import RestaurantEntity

        entities = [
            RestaurantEntity(
                entity_id="dir_1",
                name="Restaurant Directory",
                url="https://directory.com",
                entity_type="directory",
                data={"level": 0},
            ),
            RestaurantEntity(
                entity_id="rest_1",
                name="Mario's Pizza",
                url="https://restaurant1.com",
                entity_type="restaurant",
                data={"level": 1, "parent": "dir_1"},
            ),
            RestaurantEntity(
                entity_id="menu_1",
                name="Mario's Menu",
                url="https://restaurant1.com/menu",
                entity_type="menu",
                data={"level": 2, "parent": "rest_1"},
            ),
        ]

        result = aggregator.create_hierarchical_structure(entities)

        assert isinstance(result, list)
        assert len(result) > 0

        # Should maintain hierarchical relationships
        root_entities = [e for e in result if e.data.get("level") == 0]
        assert len(root_entities) > 0

    def test_entity_relationship_creation_and_validation(self):
        """Test creating and validating EntityRelationship objects."""
        from src.scraper.data_aggregator import EntityRelationship

        relationship = EntityRelationship(
            parent_id="parent_1",
            child_id="child_1",
            relationship_type="has_menu",
            strength=0.9,
        )

        assert relationship.parent_id == "parent_1"
        assert relationship.child_id == "child_1"
        assert relationship.relationship_type == "has_menu"
        assert relationship.strength == 0.9
        assert relationship.is_valid()

    def test_restaurant_entity_similarity_calculation(self):
        """Test RestaurantEntity similarity calculation."""
        from src.scraper.data_aggregator import RestaurantEntity

        entity1 = RestaurantEntity(
            entity_id="e1",
            name="Mario's Pizza",
            url="https://marios.com",
            entity_type="restaurant",
            data={"address": "123 Main St"},
        )

        entity2 = RestaurantEntity(
            entity_id="e2",
            name="Mario's Pizzeria",  # Similar name
            url="https://marios-pizza.com",  # Similar URL
            entity_type="restaurant",
            data={"address": "123 Main Street"},  # Similar address
        )

        entity3 = RestaurantEntity(
            entity_id="e3",
            name="Luigi's Pasta",  # Different name
            url="https://luigis.com",  # Different URL
            entity_type="restaurant",
            data={"address": "456 Oak Ave"},  # Different address
        )

        similarity_12 = entity1.calculate_similarity(entity2)
        similarity_13 = entity1.calculate_similarity(entity3)

        assert similarity_12 > similarity_13
        assert 0 <= similarity_12 <= 1
        assert 0 <= similarity_13 <= 1

    def test_cross_reference_mapping_creation(
        self, aggregator, sample_entities, sample_relationships
    ):
        """Test creating cross-reference mapping between entities."""
        cross_refs = aggregator.create_cross_reference_mapping(
            sample_entities, sample_relationships
        )

        assert isinstance(cross_refs, dict)
        assert len(cross_refs) > 0

        # Should map entity IDs to related entity IDs
        for entity_id, related_ids in cross_refs.items():
            assert isinstance(related_ids, list)

    def test_data_merging_strategies(self, aggregator):
        """Test different data merging strategies."""
        from src.scraper.data_aggregator import RestaurantEntity

        entities = [
            RestaurantEntity(
                entity_id="strategy_1",
                name="Restaurant A",
                url="https://resta.com",
                entity_type="restaurant",
                data={"phone": "555-0001", "rating": 4.0, "reviews": 100},
            ),
            RestaurantEntity(
                entity_id="strategy_2",
                name="Restaurant A",
                url="https://resta.com",
                entity_type="restaurant",
                data={
                    "phone": "555-0001",
                    "rating": 4.5,  # Different rating
                    "reviews": 150,  # Different review count
                    "cuisine": "Italian",  # Additional field
                },
            ),
        ]

        # Test max value strategy
        result_max = aggregator.merge_entities(entities, strategy="max_value")
        assert result_max.data["rating"] == 4.5  # Should take max
        assert result_max.data["reviews"] == 150  # Should take max

        # Test latest strategy
        result_latest = aggregator.merge_entities(entities, strategy="latest")
        # Should prefer data from later entity
        assert "cuisine" in result_latest.data

    def test_preserve_source_information_during_aggregation(self, aggregator):
        """Test preserving source information during aggregation."""
        from src.scraper.data_aggregator import RestaurantEntity

        entities = [
            RestaurantEntity(
                entity_id="source_1",
                name="Mario's Pizza",
                url="https://main-site.com",
                entity_type="restaurant",
                data={"address": "123 Main St"},
                source_info={"site": "main", "timestamp": "2024-01-01"},
            ),
            RestaurantEntity(
                entity_id="source_2",
                name="Mario's Pizza",
                url="https://review-site.com",
                entity_type="restaurant",
                data={"rating": 4.5},
                source_info={"site": "reviews", "timestamp": "2024-01-02"},
            ),
        ]

        result = aggregator.aggregate_entities(entities)

        # Should preserve source information
        assert len(result) > 0
        aggregated_entity = result[0]
        assert (
            hasattr(aggregated_entity, "source_info")
            or "sources" in aggregated_entity.data
        )


class TestHierarchicalNode:
    """Test HierarchicalNode functionality."""

    def test_hierarchical_node_creation(self):
        """Test creating HierarchicalNode objects."""
        from src.scraper.data_aggregator import RestaurantEntity, HierarchicalNode

        entity = RestaurantEntity(
            entity_id="test_1",
            name="Test Restaurant",
            url="https://test.com",
            entity_type="restaurant",
            data={"address": "123 Test St"},
        )

        node = HierarchicalNode(entity=entity, parent=None, children=[])

        assert node.entity == entity
        assert node.parent is None
        assert node.children == []
        assert node.get_depth() == 0

    def test_hierarchical_node_depth_calculation(self):
        """Test hierarchical node depth calculation."""
        from src.scraper.data_aggregator import RestaurantEntity, HierarchicalNode

        # Create parent node
        parent_entity = RestaurantEntity(
            entity_id="parent_1",
            name="Directory",
            url="https://dir.com",
            entity_type="directory",
            data={},
        )
        parent_node = HierarchicalNode(parent_entity, None, [])

        # Create child node
        child_entity = RestaurantEntity(
            entity_id="child_1",
            name="Restaurant",
            url="https://rest.com",
            entity_type="restaurant",
            data={},
        )
        child_node = HierarchicalNode(child_entity, parent_node, [])
        parent_node.children.append(child_node)

        assert parent_node.get_depth() == 0
        assert child_node.get_depth() == 1
