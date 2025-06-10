"""Unit tests for Flask PDF integration endpoints."""
import os
import json
import tempfile

import pytest

from src.web_interface.app import create_app


class TestFlaskPDFIntegration:
    """Test suite for Flask PDF integration endpoints."""

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

    def test_generate_pdf_endpoint_success(self, client, sample_restaurant_data):
        """Test successful PDF generation via API."""
        with tempfile.TemporaryDirectory() as temp_dir:
            response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": sample_restaurant_data,
                    "output_directory": temp_dir,
                    "file_format": "pdf",
                    "allow_overwrite": True,
                },
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True
            assert "file_path" in data
            assert data["file_format"] == "pdf"
            assert data["restaurant_count"] == 2

            # Verify PDF file was actually created
            assert os.path.exists(data["file_path"])
            assert data["file_path"].endswith(".pdf")

            # Verify file has content
            file_size = os.path.getsize(data["file_path"])
            assert file_size > 0

    def test_generate_pdf_endpoint_no_data(self, client):
        """Test PDF generation endpoint with no data."""
        response = client.post(
            "/api/generate-file",
            json={"file_format": "pdf"},
            content_type="application/json",
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data["success"] is False
        assert "restaurant data" in data["error"].lower()

    def test_generate_pdf_endpoint_empty_restaurant_data(self, client):
        """Test PDF generation endpoint with empty restaurant data."""
        response = client.post(
            "/api/generate-file",
            json={"restaurant_data": [], "file_format": "pdf"},
            content_type="application/json",
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is False
        assert "restaurant data" in data["error"].lower()

    def test_generate_pdf_endpoint_invalid_directory(
        self, client, sample_restaurant_data
    ):
        """Test PDF generation endpoint with invalid directory."""
        response = client.post(
            "/api/generate-file",
            json={
                "restaurant_data": sample_restaurant_data,
                "output_directory": "/root/invalid_directory",
                "file_format": "pdf",
            },
            content_type="application/json",
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is False
        assert "permission" in data["error"].lower()

    def test_generate_pdf_with_preferences_saving(self, client, sample_restaurant_data):
        """Test PDF generation with preferences saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = os.path.join(temp_dir, "custom_pdf_output")
            os.makedirs(custom_dir)

            response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": sample_restaurant_data,
                    "output_directory": custom_dir,
                    "file_format": "pdf",
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

    def test_pdf_format_in_supported_formats(self, client):
        """Test that PDF format is included in supported formats."""
        response = client.get("/api/file-config")

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "supported_formats" in data

        # Verify PDF is in supported formats
        assert "pdf" in data["supported_formats"]
        assert "text" in data["supported_formats"]  # Should still support text

    def test_generate_pdf_with_special_characters(self, client):
        """Test PDF generation with special characters in restaurant data."""
        special_restaurant_data = [
            {
                "name": "José's Café & Bistro",
                "address": "123 Rue de la Paix, Montréal, QC H3G 1A1",
                "phone": "(514) 555-CAFÉ",
                "price_range": "€15-€30",
                "hours": "Lundi-Dimanche 7h-22h",
                "menu_items": {
                    "entrées": ["Salade niçoise", "Soupe à l'oignon"],
                    "plats_principaux": ["Coq au vin", "Ratatouille"],
                    "desserts": ["Crème brûlée", "Tarte tatin"],
                },
                "cuisine": "French",
                "sources": ["json-ld", "heuristic"],
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": special_restaurant_data,
                    "output_directory": temp_dir,
                    "file_format": "pdf",
                    "allow_overwrite": True,
                },
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True
            assert "file_path" in data
            assert data["file_format"] == "pdf"

            # Verify PDF file was created with special characters
            assert os.path.exists(data["file_path"])
            file_size = os.path.getsize(data["file_path"])
            assert file_size > 0

    def test_generate_pdf_large_dataset(self, client):
        """Test PDF generation with large dataset via API."""
        # Create large dataset
        large_dataset = []
        for i in range(50):
            restaurant = {
                "name": f"Restaurant {i+1}",
                "address": f"{1000+i} Test Street, Salem, OR 9730{i%10}",
                "phone": f"(503) 555-{1000+i:04d}",
                "price_range": "$10-$25",
                "hours": "Daily 11am-10pm",
                "cuisine": f"Cuisine Type {i%5}",
                "sources": ["heuristic"],
            }
            large_dataset.append(restaurant)

        with tempfile.TemporaryDirectory() as temp_dir:
            response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": large_dataset,
                    "output_directory": temp_dir,
                    "file_format": "pdf",
                    "allow_overwrite": True,
                },
                content_type="application/json",
            )

            assert response.status_code == 200

            data = json.loads(response.data)
            assert data["success"] is True
            assert data["restaurant_count"] == 50

            # Verify PDF file was created
            assert os.path.exists(data["file_path"])
            file_size = os.path.getsize(data["file_path"])
            assert file_size > 0

    def test_pdf_generation_error_handling(self, client):
        """Test error handling in PDF generation endpoints."""
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

        # Test with invalid restaurant data format
        response = client.post(
            "/api/generate-file",
            json={
                "restaurant_data": "invalid_format",  # Should be a list
                "file_format": "pdf",
            },
            content_type="application/json",
        )
        assert response.status_code == 500  # Should trigger exception handling


class TestDualFormatEndpointIntegration:
    """Test suite for dual format generation via Flask endpoints."""

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
    def sample_restaurant(self):
        """Create sample restaurant data."""
        return {
            "name": "Dual Format Test Restaurant",
            "address": "123 Test Street",
            "phone": "555-TEST",
            "cuisine": "Test Cuisine",
            "sources": ["integration_test"],
        }

    def test_generate_both_text_and_pdf_via_api(self, client, sample_restaurant):
        """Test generating both text and PDF formats via API."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate text file
            text_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": [sample_restaurant],
                    "output_directory": temp_dir,
                    "file_format": "text",
                },
                content_type="application/json",
            )

            assert text_response.status_code == 200
            text_data = json.loads(text_response.data)
            assert text_data["success"] is True

            # Generate PDF file
            pdf_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": [sample_restaurant],
                    "output_directory": temp_dir,
                    "file_format": "pdf",
                },
                content_type="application/json",
            )

            assert pdf_response.status_code == 200
            pdf_data = json.loads(pdf_response.data)
            assert pdf_data["success"] is True

            # Verify both files were created
            assert os.path.exists(text_data["file_path"])
            assert os.path.exists(pdf_data["file_path"])

            assert text_data["file_path"].endswith(".txt")
            assert pdf_data["file_path"].endswith(".pdf")

            # Verify same restaurant count
            assert text_data["restaurant_count"] == pdf_data["restaurant_count"]

    def test_dual_format_with_configuration_persistence(
        self, client, sample_restaurant
    ):
        """Test dual format generation with configuration persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Update configuration for PDF generation
            config_response = client.post(
                "/api/file-config",
                json={"output_directory": temp_dir, "allow_overwrite": False},
                content_type="application/json",
            )

            assert config_response.status_code == 200

            # Generate text file using saved configuration
            text_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": [sample_restaurant],
                    "file_format": "text"
                    # Note: not specifying output_directory, should use saved config
                },
                content_type="application/json",
            )

            assert text_response.status_code == 200
            text_data = json.loads(text_response.data)
            assert text_data["success"] is True

            # Generate PDF file using saved configuration
            pdf_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": [sample_restaurant],
                    "file_format": "pdf"
                    # Note: not specifying output_directory, should use saved config
                },
                content_type="application/json",
            )

            assert pdf_response.status_code == 200
            pdf_data = json.loads(pdf_response.data)
            assert pdf_data["success"] is True

            # Verify both files were created in the configured directory
            assert text_data["file_path"].startswith(temp_dir)
            assert pdf_data["file_path"].startswith(temp_dir)

    def test_dual_format_file_size_comparison(self, client, sample_restaurant):
        """Test file size comparison between text and PDF formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate text file
            text_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": [sample_restaurant],
                    "output_directory": temp_dir,
                    "file_format": "text",
                },
                content_type="application/json",
            )

            # Generate PDF file
            pdf_response = client.post(
                "/api/generate-file",
                json={
                    "restaurant_data": [sample_restaurant],
                    "output_directory": temp_dir,
                    "file_format": "pdf",
                },
                content_type="application/json",
            )

            # Both should succeed
            assert text_response.status_code == 200
            assert pdf_response.status_code == 200

            text_data = json.loads(text_response.data)
            pdf_data = json.loads(pdf_response.data)

            # Get file sizes
            text_size = os.path.getsize(text_data["file_path"])
            pdf_size = os.path.getsize(pdf_data["file_path"])

            # Both files should have content
            assert text_size > 0
            assert pdf_size > 0

            # PDF should be larger but not excessively so (basic performance check)
            assert pdf_size > text_size  # PDF typically larger due to formatting
            # For minimal data, PDF overhead is significant, so allow up to 50x for single restaurant
            assert (
                pdf_size < text_size * 50
            )  # But not more than 50x larger for single restaurant
