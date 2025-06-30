"""Unit tests for database validation functionality."""
import pytest
from unittest.mock import Mock, patch
import json


class TestDatabaseValidator:
    """Test cases for the DatabaseValidator class."""

    def test_validator_initialization(self):
        """Test DatabaseValidator initializes with correct schema."""
        from src.knowledge.database_validator import DatabaseValidator
        
        validator = DatabaseValidator()
        
        assert hasattr(validator, 'schema')
        assert hasattr(validator, 'required_fields')
        assert hasattr(validator, 'validation_rules')

    def test_validate_schema_success_valid_data(self):
        """Test schema validation passes for valid database structure."""
        from src.knowledge.database_validator import DatabaseValidator
        
        valid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food and beverage offerings",
                    "customer_terms": ["food", "menu", "dishes"],
                    "website_terms": ["menu", "food", "dishes", "offerings"],
                    "confidence": 0.9,
                    "synonyms": ["items", "selections"]
                }
            ],
            "term_mappings": {
                "vegetarian": {
                    "website_terms": ["vegetarian", "vegan", "plant-based"],
                    "category": "Menu Items",
                    "confidence": 0.95
                }
            }
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(valid_data)
        
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["warnings"] == []

    def test_validate_schema_fails_missing_required_fields(self):
        """Test schema validation fails when required fields are missing."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    # Missing required fields: description, customer_terms, website_terms, confidence
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("customer_terms" in error for error in result["errors"])
        assert any("website_terms" in error for error in result["errors"])
        assert any("confidence" in error for error in result["errors"])

    def test_validate_confidence_scores_range(self):
        """Test validation of confidence score ranges (0.0 to 1.0)."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 1.5  # Invalid: > 1.0
                }
            ],
            "term_mappings": {
                "test": {
                    "website_terms": ["test"],
                    "category": "Menu Items",
                    "confidence": -0.1  # Invalid: < 0.0
                }
            }
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        confidence_errors = [e for e in result["errors"] if "confidence" in e.lower()]
        assert len(confidence_errors) >= 2

    def test_validate_array_fields_not_empty(self):
        """Test validation ensures array fields contain at least one item."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": [],  # Invalid: empty array
                    "website_terms": [],  # Invalid: empty array
                    "confidence": 0.9
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        empty_array_errors = [e for e in result["errors"] if "empty" in e.lower()]
        assert len(empty_array_errors) >= 2

    def test_validate_no_duplicate_entries_within_category(self):
        """Test validation detects duplicate entries within categories."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food", "menu", "food"],  # Duplicate "food"
                    "website_terms": ["menu", "dishes", "menu"],  # Duplicate "menu"
                    "confidence": 0.9
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        duplicate_errors = [e for e in result["errors"] if "duplicate" in e.lower()]
        assert len(duplicate_errors) >= 2

    def test_validate_field_types_correct(self):
        """Test validation checks correct field types."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": 123,  # Invalid: should be string
                    "description": ["not", "a", "string"],  # Invalid: should be string
                    "customer_terms": "not_an_array",  # Invalid: should be array
                    "website_terms": {"not": "array"},  # Invalid: should be array
                    "confidence": "not_a_number"  # Invalid: should be float
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        type_errors = [e for e in result["errors"] if "type" in e.lower()]
        assert len(type_errors) >= 5

    def test_validate_category_names_unique(self):
        """Test validation ensures category names are unique."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 0.9
                },
                {
                    "category": "Menu Items",  # Duplicate category name
                    "description": "Another description",
                    "customer_terms": ["dishes"],
                    "website_terms": ["dishes"],
                    "confidence": 0.8
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        duplicate_category_errors = [e for e in result["errors"] 
                                   if "duplicate category" in e.lower()]
        assert len(duplicate_category_errors) >= 1

    def test_validate_cross_references_integrity(self):
        """Test validation checks cross-reference integrity between sections."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 0.9
                }
            ],
            "term_mappings": {
                "test_term": {
                    "website_terms": ["test"],
                    "category": "NonExistent Category",  # Invalid: category doesn't exist
                    "confidence": 0.8
                }
            }
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        assert result["valid"] is False
        reference_errors = [e for e in result["errors"] 
                          if "category" in e.lower() and "exist" in e.lower()]
        assert len(reference_errors) >= 1

    def test_validate_database_performance_requirements(self):
        """Test validation checks performance-related requirements."""
        from src.knowledge.database_validator import DatabaseValidator
        
        # Create data that might have performance issues
        large_data = {
            "categories": [],
            "term_mappings": {}
        }
        
        # Add many categories and terms
        for i in range(1000):
            large_data["categories"].append({
                "category": f"Category_{i}",
                "description": f"Description {i}",
                "customer_terms": [f"term_{i}_{j}" for j in range(100)],  # Many terms
                "website_terms": [f"web_term_{i}_{j}" for j in range(100)],
                "confidence": 0.8
            })
        
        validator = DatabaseValidator()
        result = validator.validate_schema(large_data)
        
        # Should have warnings about performance
        performance_warnings = [w for w in result["warnings"] 
                              if "performance" in w.lower()]
        assert len(performance_warnings) > 0

    def test_validate_industry_specific_rules(self):
        """Test validation applies industry-specific validation rules."""
        from src.knowledge.database_validator import DatabaseValidator
        
        restaurant_data = {
            "industry": "Restaurant",
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 0.9
                },
                {
                    "category": "Invalid Restaurant Category",  # Invalid for restaurant
                    "description": "Not restaurant related",
                    "customer_terms": ["medical"],
                    "website_terms": ["surgery"],
                    "confidence": 0.9
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_industry_schema(restaurant_data, "Restaurant")
        
        assert result["valid"] is False
        industry_errors = [e for e in result["errors"] 
                         if "restaurant" in e.lower() or "industry" in e.lower()]
        assert len(industry_errors) >= 1

    def test_validate_synonym_relationship_integrity(self):
        """Test validation checks synonym relationship integrity."""
        from src.knowledge.database_validator import DatabaseValidator
        
        invalid_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 0.9,
                    "synonyms": ["dishes", "items"]
                }
            ],
            "synonyms": {
                "parking": ["parking lot", "valet"],
                "parking lot": ["parking", "garage"],  # Missing valet bidirectionality
                "valet": ["parking"]  # Missing parking lot bidirectionality
            }
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(invalid_data)
        
        # Should have warnings about incomplete bidirectional relationships
        bidirectional_warnings = [w for w in result["warnings"] 
                                if "bidirectional" in w.lower() or "synonym" in w.lower()]
        assert len(bidirectional_warnings) > 0

    def test_validate_custom_mapping_conflicts(self):
        """Test validation detects conflicts in custom mappings."""
        from src.knowledge.database_validator import DatabaseValidator
        
        conflicted_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food"],
                    "website_terms": ["menu"],
                    "confidence": 0.9
                }
            ],
            "term_mappings": {
                "vegetarian": {
                    "website_terms": ["vegetarian", "vegan"],
                    "category": "Menu Items",
                    "confidence": 0.9
                }
            },
            "custom_mappings": [
                {
                    "customer_term": "vegetarian",  # Conflicts with term_mappings
                    "website_terms": ["plant-based"],
                    "category": "Menu Items",
                    "confidence": 0.8,
                    "user_defined": True
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(conflicted_data)
        
        # Should detect conflicts between standard and custom mappings
        conflict_warnings = [w for w in result["warnings"] 
                           if "conflict" in w.lower() or "override" in w.lower()]
        assert len(conflict_warnings) > 0

    def test_export_validation_report(self):
        """Test exporting detailed validation report."""
        from src.knowledge.database_validator import DatabaseValidator
        
        test_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food items",
                    "customer_terms": ["food", "food"],  # Duplicate
                    "website_terms": ["menu"],
                    "confidence": 1.5  # Invalid range
                }
            ]
        }
        
        validator = DatabaseValidator()
        result = validator.validate_schema(test_data)
        report = validator.export_validation_report(result)
        
        assert "validation_summary" in report
        assert "error_details" in report
        assert "warnings" in report
        assert "recommendations" in report
        assert report["validation_summary"]["total_errors"] > 0

    def test_fix_common_validation_issues(self):
        """Test automatic fixing of common validation issues."""
        from src.knowledge.database_validator import DatabaseValidator
        
        fixable_data = {
            "categories": [
                {
                    "category": "menu items",  # Should be title case
                    "description": "Food items",
                    "customer_terms": ["food", "Food", "FOOD"],  # Duplicates with different cases
                    "website_terms": ["menu", "Menu"],  # Case duplicates
                    "confidence": 0.9
                }
            ]
        }
        
        validator = DatabaseValidator()
        fixed_data = validator.auto_fix_issues(fixable_data)
        
        assert fixed_data["categories"][0]["category"] == "Menu Items"
        assert len(fixed_data["categories"][0]["customer_terms"]) == 1  # Duplicates removed
        assert len(fixed_data["categories"][0]["website_terms"]) == 1  # Case duplicates removed

    def test_validate_data_quality_metrics(self):
        """Test validation calculates data quality metrics."""
        from src.knowledge.database_validator import DatabaseValidator
        
        test_data = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food and beverage offerings",
                    "customer_terms": ["food", "menu", "dishes"],
                    "website_terms": ["menu", "food", "dishes", "offerings"],
                    "confidence": 0.9
                },
                {
                    "category": "Amenities",
                    "description": "Restaurant facilities",
                    "customer_terms": ["wifi"],
                    "website_terms": ["wifi"],
                    "confidence": 0.7
                }
            ],
            "term_mappings": {
                "vegetarian": {
                    "website_terms": ["vegetarian", "vegan"],
                    "category": "Menu Items",
                    "confidence": 0.95
                }
            }
        }
        
        validator = DatabaseValidator()
        metrics = validator.calculate_quality_metrics(test_data)
        
        assert "completeness_score" in metrics
        assert "consistency_score" in metrics
        assert "coverage_score" in metrics
        assert "average_confidence" in metrics
        assert 0.0 <= metrics["completeness_score"] <= 1.0
        assert 0.0 <= metrics["consistency_score"] <= 1.0
        assert metrics["average_confidence"] > 0.0

    def test_validate_version_compatibility(self):
        """Test validation checks database version compatibility."""
        from src.knowledge.database_validator import DatabaseValidator
        
        versioned_data = {
            "version": "1.0.0",
            "schema_version": "2.1.0",
            "categories": [],
            "term_mappings": {}
        }
        
        validator = DatabaseValidator(supported_versions=["2.0.0", "2.1.0"])
        result = validator.validate_version_compatibility(versioned_data)
        
        assert result["compatible"] is True
        assert result["schema_version"] == "2.1.0"
        
        # Test incompatible version
        incompatible_data = {
            "version": "1.0.0",
            "schema_version": "3.0.0",  # Unsupported
            "categories": []
        }
        
        result = validator.validate_version_compatibility(incompatible_data)
        
        assert result["compatible"] is False
        assert "upgrade" in result["message"].lower()