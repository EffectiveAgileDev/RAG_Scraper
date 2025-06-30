"""Database validation functionality for ensuring data integrity and quality."""
import logging
import re
from typing import Dict, List, Optional, Any, Union
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class DatabaseValidator:
    """Validates database schema and data integrity for industry knowledge databases."""
    
    def __init__(self, supported_versions: Optional[List[str]] = None):
        """Initialize database validator.
        
        Args:
            supported_versions: List of supported schema versions
        """
        self.supported_versions = supported_versions or ["2.0.0", "2.1.0", "2.2.0"]
        
        # Define validation schema
        self.schema = {
            "categories": {
                "required": True,
                "type": "array",
                "item_schema": {
                    "category": {"required": True, "type": "string"},
                    "description": {"required": True, "type": "string"},
                    "customer_terms": {"required": True, "type": "array", "min_length": 1},
                    "website_terms": {"required": True, "type": "array", "min_length": 1},
                    "confidence": {"required": True, "type": "number", "min": 0.0, "max": 1.0},
                    "synonyms": {"required": False, "type": "array"}
                }
            },
            "term_mappings": {
                "required": False,
                "type": "object"
            },
            "synonyms": {
                "required": False,
                "type": "object"
            },
            "custom_mappings": {
                "required": False,
                "type": "array"
            }
        }
        
        # Required fields for categories
        self.required_fields = ["category", "description", "customer_terms", "website_terms", "confidence"]
        
        # Validation rules
        self.validation_rules = {
            "max_categories": 1000,
            "max_terms_per_category": 100,
            "max_category_name_length": 100,
            "min_confidence": 0.0,
            "max_confidence": 1.0
        }
        
        # Industry-specific category validation
        self.industry_categories = {
            "Restaurant": [
                "Menu Items", "Cuisine Type", "Dining Options", "Amenities", 
                "Hours", "Location", "Reviews", "Pricing"
            ],
            "Medical": [
                "Services", "Specialties", "Insurance", "Staff", "Facilities", 
                "Appointments", "Reviews", "Location"
            ]
        }
    
    def validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate database schema and data integrity.
        
        Args:
            data: Database data to validate
            
        Returns:
            Validation result with errors and warnings
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate top-level structure
        self._validate_structure(data, result)
        
        # Validate categories
        if "categories" in data:
            self._validate_categories(data["categories"], result)
        
        # Validate term mappings
        if "term_mappings" in data:
            self._validate_term_mappings(data["term_mappings"], data.get("categories", []), result)
        
        # Validate synonyms
        if "synonyms" in data:
            self._validate_synonyms(data["synonyms"], result)
        
        # Validate custom mappings
        if "custom_mappings" in data:
            self._validate_custom_mappings(data["custom_mappings"], data.get("term_mappings", {}), result)
        
        # Performance warnings
        self._check_performance_requirements(data, result)
        
        return result
    
    def _validate_structure(self, data: Dict[str, Any], result: Dict[str, Any]):
        """Validate top-level structure."""
        if "categories" not in data:
            result["errors"].append("Missing required 'categories' field")
            result["valid"] = False
    
    def _validate_categories(self, categories: List[Dict[str, Any]], result: Dict[str, Any]):
        """Validate categories structure and content."""
        if not isinstance(categories, list):
            result["errors"].append("Categories must be an array")
            result["valid"] = False
            return
        
        category_names = []
        
        for i, category in enumerate(categories):
            if not isinstance(category, dict):
                result["errors"].append(f"Category {i}: Must be an object")
                result["valid"] = False
                continue
            
            # Check required fields
            for field in self.required_fields:
                if field not in category:
                    result["errors"].append(f"Category {i}: Missing required field '{field}'")
                    result["valid"] = False
            
            # Validate field types
            self._validate_category_fields(category, i, result)
            
            # Check for duplicates within category
            self._validate_category_duplicates(category, i, result)
            
            # Track category names for uniqueness check
            if "category" in category:
                category_names.append(category["category"])
        
        # Check for duplicate category names
        name_counts = Counter(category_names)
        for name, count in name_counts.items():
            if count > 1:
                result["errors"].append(f"Duplicate category name found: '{name}'")
                result["valid"] = False
    
    def _validate_category_fields(self, category: Dict[str, Any], index: int, result: Dict[str, Any]):
        """Validate individual category fields."""
        # Check category name type
        if "category" in category:
            if not isinstance(category["category"], str):
                result["errors"].append(f"Category {index}: 'category' field has wrong type, expected string but got {type(category['category']).__name__}")
                result["valid"] = False
        
        # Check description type
        if "description" in category:
            if not isinstance(category["description"], str):
                result["errors"].append(f"Category {index}: 'description' field has wrong type, expected string but got {type(category['description']).__name__}")
                result["valid"] = False
        
        # Check customer_terms type and content
        if "customer_terms" in category:
            if not isinstance(category["customer_terms"], list):
                result["errors"].append(f"Category {index}: 'customer_terms' field has wrong type, expected array but got {type(category['customer_terms']).__name__}")
                result["valid"] = False
            elif len(category["customer_terms"]) == 0:
                result["errors"].append(f"Category {index}: 'customer_terms' cannot be empty")
                result["valid"] = False
        
        # Check website_terms type and content
        if "website_terms" in category:
            if not isinstance(category["website_terms"], list):
                result["errors"].append(f"Category {index}: 'website_terms' field has wrong type, expected array but got {type(category['website_terms']).__name__}")
                result["valid"] = False
            elif len(category["website_terms"]) == 0:
                result["errors"].append(f"Category {index}: 'website_terms' cannot be empty")
                result["valid"] = False
        
        # Check confidence type and range
        if "confidence" in category:
            confidence = category["confidence"]
            if not isinstance(confidence, (int, float)):
                result["errors"].append(f"Category {index}: 'confidence' field has wrong type, expected number but got {type(confidence).__name__}")
                result["valid"] = False
            elif confidence < 0.0 or confidence > 1.0:
                result["errors"].append(f"Category {index}: 'confidence' must be between 0.0 and 1.0, got {confidence}")
                result["valid"] = False
    
    def _validate_category_duplicates(self, category: Dict[str, Any], index: int, result: Dict[str, Any]):
        """Check for duplicate terms within category arrays."""
        # Check customer_terms duplicates
        if "customer_terms" in category and isinstance(category["customer_terms"], list):
            terms = category["customer_terms"]
            if len(terms) != len(set(terms)):
                result["errors"].append(f"Category {index}: Duplicate terms found in 'customer_terms'")
                result["valid"] = False
        
        # Check website_terms duplicates
        if "website_terms" in category and isinstance(category["website_terms"], list):
            terms = category["website_terms"]
            if len(terms) != len(set(terms)):
                result["errors"].append(f"Category {index}: Duplicate terms found in 'website_terms'")
                result["valid"] = False
    
    def _validate_term_mappings(self, term_mappings: Dict[str, Any], categories: List[Dict[str, Any]], result: Dict[str, Any]):
        """Validate term mappings structure and cross-references."""
        if not isinstance(term_mappings, dict):
            result["errors"].append("Term mappings must be an object")
            result["valid"] = False
            return
        
        # Get valid category names
        valid_categories = set()
        for category in categories:
            if "category" in category:
                valid_categories.add(category["category"])
        
        for term, mapping in term_mappings.items():
            if not isinstance(mapping, dict):
                result["errors"].append(f"Term mapping '{term}': Must be an object")
                result["valid"] = False
                continue
            
            # Check confidence
            if "confidence" in mapping:
                confidence = mapping["confidence"]
                if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                    result["errors"].append(f"Term mapping '{term}': Invalid confidence value")
                    result["valid"] = False
            
            # Check category reference
            if "category" in mapping:
                category_name = mapping["category"]
                if category_name not in valid_categories:
                    result["errors"].append(f"Term mapping '{term}': Category '{category_name}' does not exist in categories")
                    result["valid"] = False
    
    def _validate_synonyms(self, synonyms: Dict[str, Any], result: Dict[str, Any]):
        """Validate synonym relationships and bidirectionality."""
        if not isinstance(synonyms, dict):
            result["errors"].append("Synonyms must be an object")
            result["valid"] = False
            return
        
        # Check bidirectional relationships
        for primary_term, synonym_list in synonyms.items():
            if not isinstance(synonym_list, list):
                continue
            
            for synonym in synonym_list:
                if isinstance(synonym, str):
                    if synonym in synonyms:
                        # Check if the reverse relationship exists
                        reverse_list = synonyms[synonym]
                        if isinstance(reverse_list, list) and primary_term not in reverse_list:
                            result["warnings"].append(
                                f"Synonym relationship not bidirectional: '{primary_term}' -> '{synonym}' "
                                f"but '{synonym}' does not reference '{primary_term}'"
                            )
            
            # Check that all synonyms reference each other
            for i, synonym1 in enumerate(synonym_list):
                if isinstance(synonym1, str) and synonym1 in synonyms:
                    for j, synonym2 in enumerate(synonym_list):
                        if i != j and isinstance(synonym2, str):
                            if synonym2 not in synonyms.get(synonym1, []):
                                result["warnings"].append(
                                    f"Incomplete bidirectional synonym mapping: '{synonym1}' does not reference '{synonym2}' "
                                    f"though both are synonyms of '{primary_term}'"
                                )
    
    def _validate_custom_mappings(self, custom_mappings: List[Dict[str, Any]], term_mappings: Dict[str, Any], result: Dict[str, Any]):
        """Validate custom mappings for conflicts."""
        if not isinstance(custom_mappings, list):
            result["errors"].append("Custom mappings must be an array")
            result["valid"] = False
            return
        
        for mapping in custom_mappings:
            if not isinstance(mapping, dict):
                continue
            
            customer_term = mapping.get("customer_term")
            if customer_term and customer_term in term_mappings:
                result["warnings"].append(
                    f"Custom mapping for '{customer_term}' conflicts with standard term mapping"
                )
    
    def _check_performance_requirements(self, data: Dict[str, Any], result: Dict[str, Any]):
        """Check for potential performance issues."""
        categories = data.get("categories", [])
        
        # Check number of categories
        if len(categories) >= self.validation_rules["max_categories"]:
            result["warnings"].append(
                f"Large number of categories ({len(categories)}) may impact performance"
            )
        
        # Check terms per category
        for category in categories:
            if isinstance(category, dict):
                customer_terms = category.get("customer_terms", [])
                website_terms = category.get("website_terms", [])
                
                if (len(customer_terms) >= self.validation_rules["max_terms_per_category"] or
                    len(website_terms) >= self.validation_rules["max_terms_per_category"]):
                    result["warnings"].append(
                        f"Category '{category.get('category', 'Unknown')}' has many terms, "
                        "may impact performance"
                    )
    
    def validate_industry_schema(self, data: Dict[str, Any], industry: str) -> Dict[str, Any]:
        """Validate schema against industry-specific rules.
        
        Args:
            data: Database data to validate
            industry: Target industry name
            
        Returns:
            Validation result with industry-specific errors
        """
        result = self.validate_schema(data)
        
        # Apply industry-specific validation
        if industry in self.industry_categories:
            valid_categories = set(self.industry_categories[industry])
            
            categories = data.get("categories", [])
            for category in categories:
                if isinstance(category, dict) and "category" in category:
                    category_name = category["category"]
                    if category_name not in valid_categories:
                        result["errors"].append(
                            f"Category '{category_name}' is not valid for {industry} industry"
                        )
                        result["valid"] = False
        
        return result
    
    def export_validation_report(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Export detailed validation report.
        
        Args:
            validation_result: Result from validate_schema
            
        Returns:
            Detailed validation report
        """
        errors = validation_result.get("errors", [])
        warnings = validation_result.get("warnings", [])
        
        # Categorize errors
        error_categories = defaultdict(list)
        for error in errors:
            if "confidence" in error.lower():
                error_categories["confidence"].append(error)
            elif "duplicate" in error.lower():
                error_categories["duplicates"].append(error)
            elif "type" in error.lower():
                error_categories["types"].append(error)
            elif "empty" in error.lower():
                error_categories["empty_fields"].append(error)
            else:
                error_categories["other"].append(error)
        
        return {
            "validation_summary": {
                "valid": validation_result.get("valid", False),
                "total_errors": len(errors),
                "total_warnings": len(warnings)
            },
            "error_details": dict(error_categories),
            "warnings": warnings,
            "recommendations": self._generate_recommendations(validation_result)
        }
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        errors = validation_result.get("errors", [])
        
        # Analyze error patterns and suggest fixes
        if any("confidence" in error for error in errors):
            recommendations.append("Review confidence scores to ensure they are between 0.0 and 1.0")
        
        if any("duplicate" in error for error in errors):
            recommendations.append("Remove duplicate terms from category arrays")
        
        if any("empty" in error for error in errors):
            recommendations.append("Ensure all required arrays contain at least one item")
        
        if any("type" in error for error in errors):
            recommendations.append("Check data types for all fields match the expected schema")
        
        return recommendations
    
    def auto_fix_issues(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically fix common validation issues.
        
        Args:
            data: Database data to fix
            
        Returns:
            Fixed database data
        """
        fixed_data = data.copy()
        
        if "categories" in fixed_data:
            fixed_categories = []
            
            for category in fixed_data["categories"]:
                if isinstance(category, dict):
                    fixed_category = category.copy()
                    
                    # Fix category name to title case
                    if "category" in fixed_category and isinstance(fixed_category["category"], str):
                        fixed_category["category"] = fixed_category["category"].title()
                    
                    # Remove case-insensitive duplicates from arrays
                    for field in ["customer_terms", "website_terms"]:
                        if field in fixed_category and isinstance(fixed_category[field], list):
                            # Remove duplicates while preserving case of first occurrence
                            seen = set()
                            unique_terms = []
                            for term in fixed_category[field]:
                                if isinstance(term, str):
                                    term_lower = term.lower()
                                    if term_lower not in seen:
                                        seen.add(term_lower)
                                        unique_terms.append(term)
                            fixed_category[field] = unique_terms
                    
                    fixed_categories.append(fixed_category)
            
            fixed_data["categories"] = fixed_categories
        
        return fixed_data
    
    def calculate_quality_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data quality metrics.
        
        Args:
            data: Database data to analyze
            
        Returns:
            Quality metrics dictionary
        """
        categories = data.get("categories", [])
        term_mappings = data.get("term_mappings", {})
        
        if not categories:
            return {
                "completeness_score": 0.0,
                "consistency_score": 0.0,
                "coverage_score": 0.0,
                "average_confidence": 0.0
            }
        
        # Calculate completeness (all required fields present)
        complete_categories = 0
        for category in categories:
            if isinstance(category, dict):
                has_all_required = all(field in category for field in self.required_fields)
                if has_all_required:
                    complete_categories += 1
        
        completeness_score = complete_categories / len(categories) if categories else 0.0
        
        # Calculate consistency (no duplicates, valid types)
        validation_result = self.validate_schema(data)
        consistency_score = 1.0 if validation_result["valid"] else 0.5
        
        # Calculate coverage (terms per category)
        total_terms = 0
        for category in categories:
            if isinstance(category, dict):
                customer_terms = category.get("customer_terms", [])
                website_terms = category.get("website_terms", [])
                total_terms += len(customer_terms) + len(website_terms)
        
        avg_terms_per_category = total_terms / len(categories) if categories else 0.0
        coverage_score = min(1.0, avg_terms_per_category / 10.0)  # Normalize to 0-1
        
        # Calculate average confidence
        confidences = []
        for category in categories:
            if isinstance(category, dict) and "confidence" in category:
                if isinstance(category["confidence"], (int, float)):
                    confidences.append(category["confidence"])
        
        for mapping in term_mappings.values():
            if isinstance(mapping, dict) and "confidence" in mapping:
                if isinstance(mapping["confidence"], (int, float)):
                    confidences.append(mapping["confidence"])
        
        average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "completeness_score": completeness_score,
            "consistency_score": consistency_score,
            "coverage_score": coverage_score,
            "average_confidence": average_confidence
        }
    
    def validate_version_compatibility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate database version compatibility.
        
        Args:
            data: Database data with version information
            
        Returns:
            Version compatibility result
        """
        schema_version = data.get("schema_version")
        
        if not schema_version:
            return {
                "compatible": False,
                "schema_version": None,
                "message": "No schema version specified"
            }
        
        if schema_version in self.supported_versions:
            return {
                "compatible": True,
                "schema_version": schema_version,
                "message": f"Schema version {schema_version} is supported"
            }
        else:
            return {
                "compatible": False,
                "schema_version": schema_version,
                "message": f"Schema version {schema_version} is not supported. Please upgrade to one of: {', '.join(self.supported_versions)}"
            }