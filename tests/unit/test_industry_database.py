"""Unit tests for industry knowledge database functionality."""
import pytest
from unittest.mock import Mock, patch, mock_open
import json
import tempfile
import os


class TestIndustryDatabase:
    """Test cases for the core IndustryDatabase class."""

    def test_database_initialization_with_default_config(self):
        """Test database initializes with default industry configurations."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        
        assert db is not None
        assert hasattr(db, 'industries')
        assert hasattr(db, 'categories')
        assert hasattr(db, 'term_mappings')

    def test_database_initialization_with_custom_config_file(self):
        """Test database initializes with custom configuration file."""
        from src.knowledge.industry_database import IndustryDatabase
        
        config_data = {
            "restaurant": {
                "categories": ["Menu Items", "Cuisine Type"],
                "term_mappings": {}
            }
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(config_data))):
            db = IndustryDatabase(config_file="custom_config.json")
            
        assert db.config_file == "custom_config.json"
        assert "restaurant" in db.industries

    def test_get_industry_categories_returns_correct_list(self):
        """Test getting categories for a specific industry."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        categories = db.get_categories("Restaurant")
        
        expected_categories = [
            "Menu Items", "Cuisine Type", "Dining Options", 
            "Amenities", "Hours", "Location"
        ]
        
        assert isinstance(categories, list)
        assert len(categories) == 6
        for category in expected_categories:
            assert category in [cat["category"] for cat in categories]

    def test_get_categories_for_medical_industry(self):
        """Test getting categories for medical industry."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        categories = db.get_categories("Medical")
        
        expected_categories = [
            "Services", "Specialties", "Insurance", 
            "Staff", "Facilities", "Appointments"
        ]
        
        assert isinstance(categories, list)
        assert len(categories) == 6
        for category in expected_categories:
            assert category in [cat["category"] for cat in categories]

    def test_get_categories_for_unknown_industry_returns_empty(self):
        """Test getting categories for unknown industry returns empty list."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        categories = db.get_categories("UnknownIndustry")
        
        assert categories == []

    def test_load_default_restaurant_database(self):
        """Test loading default restaurant knowledge database."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        restaurant_db = db.load_industry_database("Restaurant")
        
        assert restaurant_db is not None
        assert "categories" in restaurant_db
        assert "term_mappings" in restaurant_db
        assert "synonyms" in restaurant_db

    def test_load_default_medical_database(self):
        """Test loading default medical knowledge database."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        medical_db = db.load_industry_database("Medical")
        
        assert medical_db is not None
        assert "categories" in medical_db
        assert "term_mappings" in medical_db
        assert "synonyms" in medical_db

    def test_validate_database_schema_success(self):
        """Test database schema validation passes for valid data."""
        from src.knowledge.industry_database import IndustryDatabase
        
        valid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food and beverage offerings",
                    "customer_terms": ["food", "menu"],
                    "website_terms": ["menu", "food", "dishes"],
                    "confidence": 0.9
                }
            ]
        }
        
        db = IndustryDatabase()
        result = db.validate_schema(valid_data)
        
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_database_schema_fails_missing_fields(self):
        """Test database schema validation fails for missing required fields."""
        from src.knowledge.industry_database import IndustryDatabase
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    # Missing required fields
                }
            ]
        }
        
        db = IndustryDatabase()
        result = db.validate_schema(invalid_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert "customer_terms" in str(result["errors"])

    def test_validate_database_schema_fails_invalid_confidence(self):
        """Test database schema validation fails for invalid confidence scores."""
        from src.knowledge.industry_database import IndustryDatabase
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 1.5  # Invalid: > 1.0
                }
            ]
        }
        
        db = IndustryDatabase()
        result = db.validate_schema(invalid_data)
        
        assert result["valid"] is False
        assert "confidence" in str(result["errors"])

    def test_add_custom_term_mapping_success(self):
        """Test adding custom term mapping to database."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        
        result = db.add_custom_mapping(
            industry="Restaurant",
            customer_term="gluten-free",
            category="Menu Items",
            website_terms=["gluten-free", "celiac-friendly", "wheat-free"],
            confidence=1.0
        )
        
        assert result["success"] is True
        assert result["mapping_id"] is not None

    def test_add_custom_term_mapping_validation_error(self):
        """Test adding custom term mapping fails validation."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        
        result = db.add_custom_mapping(
            industry="Restaurant",
            customer_term="",  # Invalid: empty term
            category="Menu Items",
            website_terms=[],  # Invalid: empty list
            confidence=2.0  # Invalid: > 1.0
        )
        
        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_save_custom_mappings_to_file(self):
        """Test saving custom mappings to persistent storage."""
        from src.knowledge.industry_database import IndustryDatabase
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            config_file = f.name
        
        try:
            db = IndustryDatabase(config_file=config_file)
            
            db.add_custom_mapping(
                industry="Restaurant",
                customer_term="vegan",
                category="Menu Items",
                website_terms=["vegan", "plant-based"],
                confidence=0.95
            )
            
            result = db.save_custom_mappings()
            
            assert result["success"] is True
            assert os.path.exists(config_file)
            
            # Verify file contents
            with open(config_file, 'r') as f:
                saved_data = json.load(f)
            assert "Restaurant" in saved_data
            
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_load_custom_mappings_from_file(self):
        """Test loading custom mappings from persistent storage."""
        from src.knowledge.industry_database import IndustryDatabase
        
        custom_data = {
            "Restaurant": {
                "custom_mappings": [
                    {
                        "customer_term": "dairy-free",
                        "category": "Menu Items",
                        "website_terms": ["dairy-free", "lactose-free"],
                        "confidence": 0.9,
                        "user_defined": True
                    }
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(custom_data, f)
            config_file = f.name
        
        try:
            db = IndustryDatabase(config_file=config_file)
            
            mappings = db.get_custom_mappings("Restaurant")
            
            assert len(mappings) == 1
            assert mappings[0]["customer_term"] == "dairy-free"
            assert mappings[0]["user_defined"] is True
            
        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)

    def test_get_all_supported_industries(self):
        """Test getting list of all supported industries."""
        from src.knowledge.industry_database import IndustryDatabase
        
        db = IndustryDatabase()
        industries = db.get_supported_industries()
        
        expected_industries = [
            "Restaurant", "Real Estate", "Medical", "Dental",
            "Furniture", "Hardware/Home Improvement", "Vehicle Fuel",
            "Vehicle Sales", "Vehicle Repair/Towing", "Ride Services",
            "Shop at Home", "Fast Food"
        ]
        
        assert isinstance(industries, list)
        assert len(industries) == 12
        for industry in expected_industries:
            assert industry in industries

    def test_database_performance_with_large_dataset(self):
        """Test database performance with large number of term mappings."""
        from src.knowledge.industry_database import IndustryDatabase
        import time
        
        db = IndustryDatabase()
        
        # Add 1000 custom mappings
        start_time = time.time()
        for i in range(1000):
            db.add_custom_mapping(
                industry="Restaurant",
                customer_term=f"test_term_{i}",
                category="Menu Items",
                website_terms=[f"website_term_{i}"],
                confidence=0.8
            )
        add_time = time.time() - start_time
        
        # Test lookup performance
        start_time = time.time()
        for i in range(50):
            db.get_custom_mappings("Restaurant")
        lookup_time = time.time() - start_time
        
        # Performance requirements
        assert add_time < 5.0  # Adding 1000 mappings should take < 5 seconds
        assert lookup_time / 50 < 0.1  # Each lookup should take < 100ms

    def test_database_memory_usage_stability(self):
        """Test database memory usage remains stable with operations."""
        from src.knowledge.industry_database import IndustryDatabase
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        db = IndustryDatabase()
        
        # Perform multiple operations
        for i in range(100):
            db.get_categories("Restaurant")
            db.get_categories("Medical")
            if i % 10 == 0:
                db.add_custom_mapping(
                    industry="Restaurant",
                    customer_term=f"memory_test_{i}",
                    category="Menu Items",
                    website_terms=[f"term_{i}"],
                    confidence=0.8
                )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50 * 1024 * 1024

    def test_concurrent_database_access(self):
        """Test database handles concurrent access correctly."""
        from src.knowledge.industry_database import IndustryDatabase
        import threading
        
        db = IndustryDatabase()
        results = []
        errors = []
        
        def worker_function(worker_id):
            try:
                for i in range(10):
                    categories = db.get_categories("Restaurant")
                    results.append(len(categories))
                    
                    db.add_custom_mapping(
                        industry="Restaurant",
                        customer_term=f"concurrent_term_{worker_id}_{i}",
                        category="Menu Items",
                        website_terms=[f"term_{worker_id}_{i}"],
                        confidence=0.8
                    )
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0
        assert len(results) == 50  # 5 threads * 10 operations each

    def test_database_backup_and_restore(self):
        """Test database backup and restore functionality."""
        from src.knowledge.industry_database import IndustryDatabase
        
        # Create database with custom mappings
        db1 = IndustryDatabase()
        db1.add_custom_mapping(
            industry="Restaurant",
            customer_term="backup_test",
            category="Menu Items",
            website_terms=["backup_term"],
            confidence=0.9
        )
        
        # Create backup
        backup_data = db1.create_backup()
        
        assert backup_data is not None
        assert "Restaurant" in backup_data
        assert "timestamp" in backup_data
        
        # Restore to new database instance
        db2 = IndustryDatabase()
        result = db2.restore_from_backup(backup_data)
        
        assert result["success"] is True
        
        # Verify restored data
        restored_mappings = db2.get_custom_mappings("Restaurant")
        backup_mapping = next((m for m in restored_mappings if m["customer_term"] == "backup_test"), None)
        assert backup_mapping is not None
        assert backup_mapping["confidence"] == 0.9