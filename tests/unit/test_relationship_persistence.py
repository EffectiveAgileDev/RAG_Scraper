import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime


class TestRelationshipPersistence:
    """Test suite for relationship persistence functionality."""

    def test_save_index_creates_directory(self, tmp_path):
        """Test that save_index creates output directory if it doesn't exist."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        tracker.create_entity("/test", "restaurant", "rest_001")

        output_dir = tmp_path / "new_directory"
        tracker.save_index(str(output_dir))

        assert output_dir.exists()
        assert (output_dir / "relationship_index.json").exists()

    def test_save_empty_tracker(self, tmp_path):
        """Test saving an empty tracker."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        tracker.save_index(str(tmp_path))

        with open(tmp_path / "relationship_index.json", "r") as f:
            data = json.load(f)

        assert data["entities"] == {}
        assert data["relationships"] == {}
        assert data["relationship_index"] == {
            "parent-child": [],
            "sibling": [],
            "reference": [],
        }

    def test_save_complex_relationships(self, tmp_path):
        """Test saving tracker with complex relationships."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()

        # Create entities
        dir1 = tracker.create_entity("/dir", "directory", "dir_001")
        rest1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        rest2 = tracker.create_entity("/rest2", "restaurant", "rest_002")
        loc1 = tracker.create_entity("/loc", "location", "loc_001")

        # Create relationships
        tracker.track_relationship(dir1, rest1, "parent-child", {"position": 1})
        tracker.track_relationship(dir1, rest2, "parent-child", {"position": 2})
        tracker.track_relationship(rest1, rest2, "sibling")
        tracker.track_relationship(rest1, loc1, "reference", {"ref_type": "location"})

        # Save
        tracker.save_index(str(tmp_path))

        # Load and verify
        with open(tmp_path / "relationship_index.json", "r") as f:
            data = json.load(f)

        assert len(data["entities"]) == 4
        assert len(data["relationship_index"]["parent-child"]) == 2
        assert len(data["relationship_index"]["sibling"]) == 1
        assert len(data["relationship_index"]["reference"]) == 1

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file raises appropriate error."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()

        with pytest.raises(FileNotFoundError):
            tracker.load_index("/nonexistent/directory")

    def test_save_load_roundtrip(self, tmp_path):
        """Test that data survives save/load roundtrip."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        # Create and populate tracker
        tracker1 = EntityRelationshipTracker()
        dir1 = tracker1.create_entity("/dir", "directory", "dir_001")
        rest1 = tracker1.create_entity("/rest1", "restaurant", "rest_001")
        tracker1.track_relationship(dir1, rest1, "parent-child", {"position": 1})

        # Save
        tracker1.save_index(str(tmp_path))

        # Load into new tracker
        tracker2 = EntityRelationshipTracker()
        tracker2.load_index(str(tmp_path))

        # Verify
        assert tracker2.entities == tracker1.entities
        assert tracker2.relationships == tracker1.relationships
        assert tracker2.relationship_index == tracker1.relationship_index

    def test_save_with_special_characters(self, tmp_path):
        """Test saving entities with special characters in metadata."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        rest1 = tracker.create_entity("/café", "restaurant", "rest_001")
        rest2 = tracker.create_entity("/restaurant/björk", "restaurant", "rest_002")

        tracker.track_relationship(
            rest1, rest2, "reference", {"note": "Special chars: café, björk, 中文"}
        )

        tracker.save_index(str(tmp_path))

        # Load and verify
        with open(tmp_path / "relationship_index.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["entities"]["rest_001"]["url"] == "/café"
        assert data["entities"]["rest_002"]["url"] == "/restaurant/björk"
        assert "中文" in data["relationship_index"]["reference"][0]["metadata"]["note"]

    def test_save_preserves_timestamps(self, tmp_path):
        """Test that timestamps are preserved in saved data."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        mock_dt = Mock()
        mock_dt.isoformat.return_value = "2024-01-15T10:30:00"

        with patch("src.scraper.entity_relationship_tracker.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_dt

            tracker = EntityRelationshipTracker()
            rest1 = tracker.create_entity("/rest1", "restaurant")
            rest2 = tracker.create_entity("/rest2", "restaurant")
            tracker.track_relationship(rest1, rest2, "sibling")

        tracker.save_index(str(tmp_path))

        with open(tmp_path / "relationship_index.json", "r") as f:
            data = json.load(f)

        # Check relationship timestamp
        assert (
            data["relationship_index"]["sibling"][0]["timestamp"]
            == "2024-01-15T10:30:00"
        )

    def test_save_handles_io_error(self):
        """Test that save handles IO errors gracefully."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        tracker.create_entity("/test", "restaurant")

        with patch("builtins.open", side_effect=IOError("Disk full")):
            with pytest.raises(IOError):
                tracker.save_index("/some/path")

    def test_load_handles_corrupt_json(self, tmp_path):
        """Test that load handles corrupt JSON files."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        # Create corrupt JSON file
        corrupt_file = tmp_path / "relationship_index.json"
        corrupt_file.write_text('{"entities": "not valid JSON}')

        tracker = EntityRelationshipTracker()

        with pytest.raises(json.JSONDecodeError):
            tracker.load_index(str(tmp_path))

    def test_save_load_preserves_bidirectional_references(self, tmp_path):
        """Test that bidirectional references are preserved."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker

        tracker = EntityRelationshipTracker()
        rest1 = tracker.create_entity("/rest1", "restaurant", "rest_001")
        rest2 = tracker.create_entity("/rest2", "restaurant", "rest_002")

        # Create bidirectional reference
        tracker.track_relationship(rest1, rest2, "reference")
        tracker.track_relationship(
            rest2, rest1, "reference"
        )  # This creates bidirectional

        tracker.save_index(str(tmp_path))

        # Load and verify
        new_tracker = EntityRelationshipTracker()
        new_tracker.load_index(str(tmp_path))

        # Check bidirectional flag is preserved
        assert (
            new_tracker.relationships[rest1]["reference_metadata"][rest2].get(
                "bidirectional"
            )
            is True
        )
        assert (
            new_tracker.relationships[rest2]["reference_metadata"][rest1].get(
                "bidirectional"
            )
            is True
        )

    def test_concurrent_save_operations(self, tmp_path):
        """Test that concurrent saves don't corrupt data."""
        from src.scraper.entity_relationship_tracker import EntityRelationshipTracker
        import threading

        tracker = EntityRelationshipTracker()
        for i in range(10):
            tracker.create_entity(f"/rest{i}", "restaurant", f"rest_{i:03d}")

        def save_tracker():
            tracker.save_index(str(tmp_path))

        # Simulate concurrent saves
        threads = []
        for _ in range(3):
            t = threading.Thread(target=save_tracker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify file is valid
        with open(tmp_path / "relationship_index.json", "r") as f:
            data = json.load(f)

        assert len(data["entities"]) == 10
