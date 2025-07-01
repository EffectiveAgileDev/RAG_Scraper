"""Unit tests for ExportManager - manages export of structured data in various formats."""

import pytest
import json
from unittest.mock import Mock, patch, mock_open

# Import will fail until we implement - expected for RED phase
try:
    from src.semantic.export_manager import ExportManager
except ImportError:
    ExportManager = None


class TestExportManager:
    """Test the ExportManager class."""
    
    def test_export_manager_initialization(self):
        """Test ExportManager can be initialized."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        assert manager is not None
        assert hasattr(manager, 'config')
    
    def test_export_manager_custom_config(self):
        """Test ExportManager with custom configuration."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        config = {
            'default_format': 'json',
            'include_metadata': True,
            'pretty_print': True,
            'compression': 'gzip'
        }
        
        manager = ExportManager(config=config)
        assert manager.config['default_format'] == 'json'
        assert manager.config['include_metadata'] is True
        assert manager.config['pretty_print'] is True
        assert manager.config['compression'] == 'gzip'
    
    def test_export_json_format(self):
        """Test exporting data in JSON format."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [
                {"id": "chunk_1", "content": "Test content", "type": "text"},
                {"id": "chunk_2", "content": "More content", "type": "text"}
            ],
            "metadata": {"version": "1.0", "chunk_count": 2},
            "relationships": [
                {"from": "chunk_1", "to": "chunk_2", "type": "follows"}
            ]
        }
        
        result = manager.export(structured_data, format="json")
        
        # Should return valid JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert "chunks" in parsed
        assert "metadata" in parsed
        assert "relationships" in parsed
        assert len(parsed["chunks"]) == 2
    
    def test_export_jsonl_format(self):
        """Test exporting data in JSONL format."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [
                {"id": "chunk_1", "content": "First chunk"},
                {"id": "chunk_2", "content": "Second chunk"}
            ],
            "metadata": {"version": "1.0"}
        }
        
        result = manager.export(structured_data, format="jsonl")
        
        # Should return JSONL string (one JSON object per line)
        assert isinstance(result, str)
        lines = result.strip().split('\n')
        assert len(lines) >= 2  # At least one line per chunk
        
        # Each line should be valid JSON
        for line in lines:
            parsed = json.loads(line)
            assert isinstance(parsed, dict)
    
    def test_export_parquet_format(self):
        """Test exporting data in Parquet format."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [
                {"id": "chunk_1", "content": "Test", "metadata": {"score": 0.9}},
                {"id": "chunk_2", "content": "Data", "metadata": {"score": 0.8}}
            ]
        }
        
        result = manager.export(structured_data, format="parquet")
        
        # Should return bytes (simulated parquet data)
        assert isinstance(result, bytes)
        assert b"PARQUET" in result or len(result) > 0
    
    def test_export_csv_format(self):
        """Test exporting data in CSV format."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [
                {"id": "chunk_1", "content": "First chunk", "type": "text"},
                {"id": "chunk_2", "content": "Second chunk", "type": "text"}
            ]
        }
        
        result = manager.export(structured_data, format="csv")
        
        # Should return CSV string
        assert isinstance(result, str)
        lines = result.strip().split('\n')
        assert len(lines) >= 2  # Header + data rows
        
        # First line should be header
        headers = lines[0].split(',')
        assert "id" in headers
        assert "content" in headers
    
    def test_export_with_profile_chatbot(self):
        """Test exporting with chatbot profile."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [{"id": "chunk_1", "content": "Test content"}],
            "metadata": {"version": "1.0"}
        }
        
        result = manager.export(structured_data, format="json", profile="chatbot")
        
        parsed = json.loads(result)
        # Should optimize for chatbot use case
        assert "metadata" in parsed
        assert parsed["metadata"].get("profile") == "chatbot"
    
    def test_export_with_profile_search(self):
        """Test exporting with search profile."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [{"id": "chunk_1", "content": "Test content"}]
        }
        
        result = manager.export(structured_data, format="json", profile="search")
        
        parsed = json.loads(result)
        # Should optimize for search use case
        assert "metadata" in parsed
        assert parsed["metadata"].get("profile") == "search"
    
    def test_export_with_profile_analytics(self):
        """Test exporting with analytics profile."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [{"id": "chunk_1", "content": "Test content"}]
        }
        
        result = manager.export(structured_data, format="json", profile="analytics")
        
        parsed = json.loads(result)
        # Should optimize for analytics use case
        assert "metadata" in parsed
        assert parsed["metadata"].get("profile") == "analytics"
    
    def test_save_to_file(self):
        """Test saving exported data to file."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [{"id": "chunk_1", "content": "Test content"}]
        }
        
        with patch("builtins.open", mock_open()) as mock_file:
            file_path = manager.save_to_file(structured_data, "test_output.json", format="json")
            
            # Should call open with correct parameters
            mock_file.assert_called_once()
            assert file_path.endswith("test_output.json")
    
    def test_get_supported_formats(self):
        """Test getting list of supported export formats."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        formats = manager.get_supported_formats()
        
        assert isinstance(formats, list)
        assert "json" in formats
        assert "jsonl" in formats
        assert "parquet" in formats
        assert "csv" in formats
    
    def test_validate_export_data(self):
        """Test validating data before export."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        # Valid data
        valid_data = {
            "chunks": [{"id": "chunk_1", "content": "Test"}],
            "metadata": {"version": "1.0"}
        }
        
        assert manager.validate_export_data(valid_data) is True
        
        # Invalid data (missing chunks)
        invalid_data = {
            "metadata": {"version": "1.0"}
        }
        
        assert manager.validate_export_data(invalid_data) is False
    
    def test_add_export_metadata(self):
        """Test adding export-specific metadata."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        structured_data = {
            "chunks": [{"id": "chunk_1", "content": "Test"}]
        }
        
        enriched_data = manager.add_export_metadata(structured_data, format="json")
        
        assert "export_metadata" in enriched_data
        export_meta = enriched_data["export_metadata"]
        assert "export_format" in export_meta
        assert "export_timestamp" in export_meta
        assert export_meta["export_format"] == "json"
    
    def test_compress_output(self):
        """Test compressing export output."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager(config={'compression': 'gzip'})
        
        test_data = "This is test data for compression"
        
        compressed = manager.compress_output(test_data, compression="gzip")
        
        # Should return compressed bytes
        assert isinstance(compressed, bytes)
        # Note: Small texts might not compress to smaller size due to overhead
        assert len(compressed) > 0  # Should produce output
    
    def test_handle_large_datasets(self):
        """Test handling large datasets efficiently."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        # Create large dataset
        large_chunks = [
            {"id": f"chunk_{i}", "content": f"Content {i}" * 100}
            for i in range(1000)
        ]
        
        large_data = {
            "chunks": large_chunks,
            "metadata": {"chunk_count": 1000}
        }
        
        # Should handle large dataset without crashing
        result = manager.export(large_data, format="jsonl")
        assert isinstance(result, str)
        assert len(result) > 10000  # Should be substantial output
    
    def test_streaming_export(self):
        """Test streaming export for large datasets."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        large_data = {
            "chunks": [{"id": f"chunk_{i}", "content": f"Content {i}"} for i in range(100)]
        }
        
        # Should support streaming for large datasets
        stream_generator = manager.export_stream(large_data, format="jsonl")
        
        # Should return a generator or iterator
        assert hasattr(stream_generator, '__iter__') or hasattr(stream_generator, '__next__')
        
        # Should be able to iterate through chunks
        chunk_count = 0
        for chunk_data in stream_generator:
            chunk_count += 1
            if chunk_count >= 10:  # Just test first 10 items
                break
        
        assert chunk_count == 10
    
    def test_export_with_custom_serializer(self):
        """Test export with custom serialization."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        def custom_serializer(data):
            return f"CUSTOM:{json.dumps(data)}"
        
        structured_data = {
            "chunks": [{"id": "chunk_1", "content": "Test"}]
        }
        
        result = manager.export(structured_data, format="custom", serializer=custom_serializer)
        
        assert isinstance(result, str)
        assert result.startswith("CUSTOM:")
    
    def test_handle_export_errors_gracefully(self):
        """Test handling export errors gracefully."""
        if not ExportManager:
            pytest.skip("ExportManager not implemented yet")
        
        manager = ExportManager()
        
        # Test with invalid format
        try:
            result = manager.export({}, format="invalid_format")
            # Should either return error result or raise appropriate exception
            assert result is None or isinstance(result, str)
        except ValueError:
            # ValueError is acceptable for invalid format
            pass
        
        # Test with malformed data
        malformed_data = {"chunks": "not_a_list"}
        
        try:
            result = manager.export(malformed_data, format="json")
            # Should handle gracefully
            assert result is not None
        except (ValueError, TypeError):
            # These exceptions are acceptable
            pass