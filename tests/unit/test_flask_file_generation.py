"""Unit tests for Flask file generation endpoints."""
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

import pytest

from src.web_interface.app import create_app


class TestFlaskFileGeneration:
    """Test suite for Flask file generation endpoints."""

    @pytest.fixture
    def app(self):
        """Create Flask test app."""
        app = create_app(testing=True)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create Flask test client."""
        return app.test_client()

    @pytest.fixture
    def sample_restaurant_data(self):
        """Create sample restaurant data for testing."""
        return [
            {
                "name": "Tony's Italian Restaurant",
                "address": "1234 Commercial Street, Salem, OR 97301",
                "phone": "(503) 555-0123",
                "price_range": "$18-$32",
                "hours": "Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm",
                "menu_items": {
                    "appetizers": ["Fresh bruschetta", "calamari rings"],
                    "entrees": ["Homemade pasta", "wood-fired pizza"],
                    "desserts": ["Tiramisu", "cannoli"],
                },
                "cuisine": "Italian",
                "sources": ["json-ld", "heuristic"],
            },
            {
                "name": "Blue Moon Diner",
                "address": "5678 State Street",
                "phone": "(503) 555-4567",
                "cuisine": "American",
                "sources": ["heuristic"],
            },
        ]

    def test_generate_file_endpoint_success(self, client, sample_restaurant_data):
        """Test successful file generation via API."""
        with tempfile.TemporaryDirectory() as temp_dir:
            response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": sample_restaurant_data,
                    "output_directory": temp_dir,
                    "file_format": "text",
                    "allow_overwrite": True,
                },
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True
            assert "file_path" in data
            assert data["file_format"] == "text"
            assert data["restaurant_count"] == 2

            # Verify file was actually created
            assert os.path.exists(data["file_path"])

            # Verify file content
            with open(data["file_path"], "r", encoding="utf-8") as f:
                content = f.read()

            assert "Tony's Italian Restaurant" in content
            assert "Blue Moon Diner" in content

    def test_generate_file_endpoint_no_data(self, client):
        """Test file generation endpoint with no data."""
        response = client.post(
            "/api/generate-file", json={}, content_type="application/json"
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "restaurant data" in data["error"].lower()

    def test_generate_file_endpoint_empty_restaurant_data(self, client):
        """Test file generation endpoint with empty restaurant data."""
        response = client.post(
            "/api/generate-file",
            json={"restaurant_data": [], "file_format": "text"},
            content_type="application/json",
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is False
        assert "restaurant data" in data["error"].lower()

    def test_generate_file_endpoint_invalid_format(
        self, client, sample_restaurant_data
    ):
        """Test file generation endpoint with invalid format."""
        response = client.post(
            "/api/generate-file",
            json={
                "restaurant_data": sample_restaurant_data,
                "file_format": "invalid_format",
            },
            content_type="application/json",
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is False
        assert "format" in data["error"].lower()

    def test_generate_file_with_preferences_saving(
        self, client, sample_restaurant_data
    ):
        """Test file generation with preferences saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = os.path.join(temp_dir, "custom_output")
            os.makedirs(custom_dir)

            response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": sample_restaurant_data,
                    "output_directory": custom_dir,
                    "file_format": "text",
                    "save_preferences": True,
                },
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True

            # Verify preferences were saved by checking config
            config_response = client.get("/api/file-config")
            assert config_response.status_code == 200

            config_data = json.loads(config_response.data)
            assert config_data["success"] is True
            assert config_data["config"]["output_directory"] == custom_dir

    def test_get_file_config_endpoint(self, client):
        """Test getting file configuration."""
        response = client.get("/api/file-config")

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "config" in data
        assert "supported_formats" in data
        assert "directory_options" in data

        # Verify config structure
        config = data["config"]
        assert "output_directory" in config
        assert "allow_overwrite" in config
        assert "encoding" in config
        assert "filename_pattern" in config

        # Verify supported formats
        assert "text" in data["supported_formats"]

        # Verify directory options
        assert "current" in data["directory_options"]
        assert "suggestions" in data["directory_options"]

    def test_update_file_config_endpoint(self, client):
        """Test updating file configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_config = {
                "output_directory": temp_dir,
                "allow_overwrite": False,
                "filename_pattern": "Custom_{timestamp}.txt",
            }

            response = client.post(
                "/api/file-config", json=new_config, content_type="application/json"
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True

            # Verify config was updated
            get_response = client.get("/api/file-config")
            get_data = json.loads(get_response.data)

            assert get_data["config"]["output_directory"] == temp_dir
            assert get_data["config"]["allow_overwrite"] is False
            assert get_data["config"]["filename_pattern"] == "Custom_{timestamp}.txt"

    def test_update_file_config_invalid_directory(self, client):
        """Test updating file config with invalid directory."""
        new_config = {"output_directory": "/root/invalid_directory"}

        response = client.post(
            "/api/file-config", json=new_config, content_type="application/json"
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is False
        assert "directory" in data["error"].lower()

    def test_validate_directory_endpoint_valid(self, client):
        """Test directory validation endpoint with valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            response = client.post(
                "/api/validate-directory",
                json={"directory_path": temp_dir},
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True
            assert data["validation"]["valid"] is True

    def test_validate_directory_endpoint_invalid(self, client):
        """Test directory validation endpoint with invalid directory."""
        response = client.post(
            "/api/validate-directory",
            json={"directory_path": "/root"},
            content_type="application/json",
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["validation"]["valid"] is False
        assert "error" in data["validation"]

    def test_validate_directory_endpoint_no_path(self, client):
        """Test directory validation endpoint without path."""
        response = client.post(
            "/api/validate-directory", json={}, content_type="application/json"
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "directory path" in data["error"].lower()

    def test_create_directory_endpoint_success(self, client):
        """Test creating custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            response = client.post(
                "/api/create-directory",
                json={
                    "parent_directory": temp_dir,
                    "directory_name": "restaurant_data",
                },
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True
            assert "directory_path" in data

            # Verify directory was created
            assert os.path.exists(data["directory_path"])
            assert os.path.isdir(data["directory_path"])

    def test_create_directory_endpoint_invalid_parent(self, client):
        """Test creating directory with invalid parent."""
        response = client.post(
            "/api/create-directory",
            json={"parent_directory": "/root", "directory_name": "test_dir"},
            content_type="application/json",
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is False
        assert "cannot create" in data["error"].lower()

    def test_create_directory_endpoint_missing_params(self, client):
        """Test creating directory with missing parameters."""
        response = client.post(
            "/api/create-directory",
            json={"parent_directory": "/tmp"},
            content_type="application/json",
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "directory name required" in data["error"].lower()

    def test_file_generation_endpoints_error_handling(self, client):
        """Test error handling in file generation endpoints."""
        # Test with no JSON data
        response = client.post("/api/generate-file")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "json" in data["error"].lower()

        # Test with malformed JSON
        response = client.post(
            "/api/generate-file", data="invalid json", content_type="application/json"
        )
        assert response.status_code == 400

        # Test config endpoints with no JSON
        response = client.post("/api/file-config")
        assert response.status_code == 400

        response = client.post("/api/validate-directory")
        assert response.status_code == 400

        response = client.post("/api/create-directory")
        assert response.status_code == 400


class TestFileGenerationIntegration:
    """Integration tests for file generation with Flask app."""

    @pytest.fixture
    def app(self):
        """Create Flask test app."""
        app = create_app(testing=True)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create Flask test client."""
        return app.test_client()

    def test_full_workflow_generate_and_download(self, client):
        """Test complete workflow: generate file and download."""
        restaurant_data = [
            {
                "name": "Integration Test Restaurant",
                "address": "123 Test Street",
                "phone": "555-TEST",
                "cuisine": "Test Cuisine",
                "sources": ["integration_test"],
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate file
            generate_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": restaurant_data,
                    "output_directory": temp_dir,
                    "file_format": "text",
                },
                content_type="application/json",
            )

            assert generate_response.status_code == 200

            generate_data = json.loads(generate_response.data)
            assert generate_data["success"] is True

            # Verify file was created
            file_path = generate_data["file_path"]
            assert os.path.exists(file_path)

            # Verify file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "Integration Test Restaurant" in content
            assert "123 Test Street" in content
            assert "555-TEST" in content
            assert "Test Cuisine" in content

    def test_configuration_persistence_across_requests(self, client):
        """Test that configuration persists across requests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = os.path.join(temp_dir, "persistent_config")
            os.makedirs(custom_dir)

            # Update configuration
            update_response = client.post(
                "/api/file-config",
                json={"output_directory": custom_dir, "allow_overwrite": False},
                content_type="application/json",
            )

            assert update_response.status_code == 200

            # Get configuration to verify it was saved
            get_response = client.get("/api/file-config")
            get_data = json.loads(get_response.data)

            assert get_data["config"]["output_directory"] == custom_dir
            assert get_data["config"]["allow_overwrite"] is False

            # Generate file using saved configuration
            restaurant_data = [{"name": "Test", "sources": ["test"]}]

            generate_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": restaurant_data,
                    "file_format": "text"
                    # Note: not specifying output_directory, should use saved config
                },
                content_type="application/json",
            )

            assert generate_response.status_code == 200

            generate_data = json.loads(generate_response.data)
            assert generate_data["success"] is True

            # Verify file was created in the configured directory
            assert generate_data["file_path"].startswith(custom_dir)
