import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json


class TestEntityRelationshipTracker:
    """Test suite for EntityRelationshipTracker class."""

    def test_tracker_initialization(self):
        """Test that the tracker initializes with empty relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        assert tracker.relationships == {}
        assert tracker.entities == {}
        assert tracker.relationship_index == {
            "parent-child": [],
            "sibling": [],
            "reference": [],
        }

    def test_create_entity_with_auto_id(self):
        """Test entity creation with automatic ID generation."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        entity_id = tracker.create_entity(
            url="/restaurants/italian-bistro", entity_type="restaurant"
        )

        assert entity_id is not None
        assert entity_id.startswith("rest_")
        assert len(entity_id) == 8  # rest_XXX format
        assert entity_id in tracker.entities
        assert tracker.entities[entity_id]["url"] == "/restaurants/italian-bistro"
        assert tracker.entities[entity_id]["type"] == "restaurant"

    def test_create_entity_with_custom_id(self):
        """Test entity creation with custom ID."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        entity_id = tracker.create_entity(
            url="/restaurants/directory", entity_type="directory", entity_id="dir_001"
        )

        assert entity_id == "dir_001"
        assert tracker.entities["dir_001"]["url"] == "/restaurants/directory"
        assert tracker.entities["dir_001"]["type"] == "directory"

    def test_unique_id_generation(self):
        """Test that generated IDs are unique."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        ids = set()

        for i in range(10):
            entity_id = tracker.create_entity(
                url=f"/restaurants/restaurant-{i}", entity_type="restaurant"
            )
            assert entity_id not in ids
            ids.add(entity_id)

    def test_track_parent_child_relationship(self):
        """Test tracking parent-child relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        parent_id = tracker.create_entity("/directory", "directory", "dir_001")
        child_id = tracker.create_entity("/restaurant", "restaurant", "rest_001")

        tracker.track_relationship(
            from_entity=parent_id, to_entity=child_id, relationship_type="parent-child"
        )

        assert child_id in tracker.relationships[parent_id]["children"]
        assert parent_id == tracker.relationships[child_id]["parent"]
        assert len(tracker.relationship_index["parent-child"]) == 1

    def test_track_sibling_relationships(self):
        """Test tracking sibling relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        rest1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        rest2 = tracker.create_entity("/rest2", "restaurant", "rest_002")

        tracker.track_relationship(
            from_entity=rest1, to_entity=rest2, relationship_type="sibling"
        )

        assert rest2 in tracker.relationships[rest1]["siblings"]
        assert rest1 in tracker.relationships[rest2]["siblings"]
        assert len(tracker.relationship_index["sibling"]) == 1

    def test_track_reference_relationship(self):
        """Test tracking reference relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        rest_id = tracker.create_entity("/restaurant", "restaurant", "rest_001")
        loc_id = tracker.create_entity("/location", "location", "loc_001")

        tracker.track_relationship(
            from_entity=rest_id,
            to_entity=loc_id,
            relationship_type="reference",
            metadata={"ref_type": "location"},
        )

        assert loc_id in tracker.relationships[rest_id]["references"]
        assert rest_id in tracker.relationships[loc_id]["referenced_by"]
        assert (
            tracker.relationships[rest_id]["reference_metadata"][loc_id]["ref_type"]
            == "location"
        )

    def test_relationship_with_metadata(self):
        """Test adding metadata to relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        parent = tracker.create_entity("/dir", "directory", "dir_001")
        child = tracker.create_entity("/rest", "restaurant", "rest_001")

        metadata = {"position": 1, "strength": "strong", "source_page": "/directory"}

        with patch("src.scraper.entity_relationship_tracker.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
            tracker.track_relationship(
                from_entity=parent,
                to_entity=child,
                relationship_type="parent-child",
                metadata=metadata,
            )

        rel_data = tracker.relationship_index["parent-child"][0]
        assert rel_data["metadata"]["position"] == 1
        assert rel_data["metadata"]["strength"] == "strong"
        assert rel_data["timestamp"] == "2024-01-01T12:00:00"

    def test_query_children(self):
        """Test querying all children of an entity."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        parent = tracker.create_entity("/dir", "directory", "dir_001")
        child1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        child2 = tracker.create_entity("/rest2", "restaurant", "rest_002")

        tracker.track_relationship(parent, child1, "parent-child")
        tracker.track_relationship(parent, child2, "parent-child")

        children = tracker.query_children(parent)
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_query_references(self):
        """Test querying all references from an entity."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        rest = tracker.create_entity("/rest", "restaurant", "rest_001")
        loc = tracker.create_entity("/loc", "location", "loc_001")
        menu = tracker.create_entity("/menu", "menu", "menu_001")

        tracker.track_relationship(rest, loc, "reference", {"ref_type": "location"})
        tracker.track_relationship(rest, menu, "reference", {"ref_type": "menu"})

        references = tracker.query_references(rest)
        assert len(references) == 2
        assert loc in references
        assert menu in references

    def test_query_relationships_by_type(self):
        """Test querying relationships by type."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        dir1 = tracker.create_entity("/dir", "directory", "dir_001")
        rest1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        rest2 = tracker.create_entity("/rest2", "restaurant", "rest_002")
        loc1 = tracker.create_entity("/loc", "location", "loc_001")

        tracker.track_relationship(dir1, rest1, "parent-child")
        tracker.track_relationship(dir1, rest2, "parent-child")
        tracker.track_relationship(rest1, rest2, "sibling")
        tracker.track_relationship(rest1, loc1, "reference")

        parent_child_rels = tracker.query_by_type("parent-child")
        assert len(parent_child_rels) == 2

        sibling_rels = tracker.query_by_type("sibling")
        assert len(sibling_rels) == 1

        reference_rels = tracker.query_by_type("reference")
        assert len(reference_rels) == 1

    def test_circular_reference_detection(self):
        """Test detection of circular references."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        rest1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        rest2 = tracker.create_entity("/rest2", "restaurant", "rest_002")

        # Create initial reference
        tracker.track_relationship(rest1, rest2, "reference")

        # Attempt circular reference
        result = tracker.track_relationship(rest2, rest1, "reference")

        # Should be marked as bidirectional
        assert (
            tracker.relationships[rest1]["reference_metadata"][rest2].get(
                "bidirectional"
            )
            is True
        )
        assert (
            tracker.relationships[rest2]["reference_metadata"][rest1].get(
                "bidirectional"
            )
            is True
        )

    def test_identify_siblings_from_parent(self):
        """Test automatic sibling identification from shared parent."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        parent = tracker.create_entity("/dir", "directory", "dir_001")
        child1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        child2 = tracker.create_entity("/rest2", "restaurant", "rest_002")
        child3 = tracker.create_entity("/rest3", "restaurant", "rest_003")

        tracker.track_relationship(parent, child1, "parent-child")
        tracker.track_relationship(parent, child2, "parent-child")
        tracker.track_relationship(parent, child3, "parent-child")

        tracker.identify_siblings()

        # All children should be siblings of each other
        assert child2 in tracker.relationships[child1]["siblings"]
        assert child3 in tracker.relationships[child1]["siblings"]
        assert child1 in tracker.relationships[child2]["siblings"]
        assert child3 in tracker.relationships[child2]["siblings"]
        assert child1 in tracker.relationships[child3]["siblings"]
        assert child2 in tracker.relationships[child3]["siblings"]

    def test_save_relationship_index(self):
        """Test saving relationship index to file."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        dir1 = tracker.create_entity("/dir", "directory", "dir_001")
        rest1 = tracker.create_entity("/rest1", "restaurant", "rest_001")

        tracker.track_relationship(dir1, rest1, "parent-child", {"position": 1})

        with patch("builtins.open", create=True) as mock_open:
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            tracker.save_index("output_dir")

            # Verify file was opened for writing
            mock_open.assert_called_with("output_dir/relationship_index.json", "w")

            # Verify JSON was written
            written_data = mock_file.write.call_args[0][0]
            data = json.loads(written_data)
            assert "entities" in data
            assert "relationships" in data
            assert "relationship_index" in data

    def test_load_relationship_index(self):
        """Test loading relationship index from file."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        saved_data = {
            "entities": {
                "dir_001": {"url": "/dir", "type": "directory"},
                "rest_001": {"url": "/rest", "type": "restaurant"},
            },
            "relationships": {
                "dir_001": {"children": ["rest_001"]},
                "rest_001": {"parent": "dir_001"},
            },
            "relationship_index": {
                "parent-child": [
                    {"from": "dir_001", "to": "rest_001", "metadata": {"position": 1}}
                ]
            },
        }

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = Mock(
                read=Mock(return_value=json.dumps(saved_data))
            )

            tracker = EntityRelationshipTracker()
            tracker.load_index("output_dir")

            assert "dir_001" in tracker.entities
            assert "rest_001" in tracker.entities
            assert "rest_001" in tracker.relationships["dir_001"]["children"]
            assert tracker.relationships["rest_001"]["parent"] == "dir_001"

    def test_entity_type_id_prefixes(self):
        """Test that different entity types get appropriate ID prefixes."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()

        rest_id = tracker.create_entity("/restaurant", "restaurant")
        assert rest_id.startswith("rest_")

        dir_id = tracker.create_entity("/directory", "directory")
        assert dir_id.startswith("dir_")

        loc_id = tracker.create_entity("/location", "location")
        assert loc_id.startswith("loc_")

        menu_id = tracker.create_entity("/menu", "menu")
        assert menu_id.startswith("menu_")

    def test_relationship_extraction_method_tracking(self):
        """Test tracking extraction method for relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        parent = tracker.create_entity("/dir", "directory", "dir_001")
        child = tracker.create_entity("/rest", "restaurant", "rest_001")

        tracker.track_relationship(
            from_entity=parent,
            to_entity=child,
            relationship_type="parent-child",
            metadata={
                "extraction_method": "page_discovery",
                "source_page": "/directory",
            },
        )

        rel_data = tracker.relationship_index["parent-child"][0]
        assert rel_data["metadata"]["extraction_method"] == "page_discovery"
        assert rel_data["metadata"]["source_page"] == "/directory"
