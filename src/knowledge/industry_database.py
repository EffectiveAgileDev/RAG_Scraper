"""Industry knowledge database for mapping customer terms to website terms."""
import json
import os
import threading
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import psutil
import logging

from .database_query_optimizer import get_query_optimizer

logger = logging.getLogger(__name__)


class IndustryDatabase:
    """Core database for industry-specific knowledge and term mappings."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize industry database.
        
        Args:
            config_file: Optional path to custom configuration file
        """
        self.config_file = config_file
        self.industries = {}
        self.categories = {}
        self.term_mappings = {}
        self.custom_mappings = {}
        self._lock = threading.RLock()
        self._query_optimizer = get_query_optimizer()
        
        # Load default industry configurations
        self._load_default_configurations()
        
        # Load custom configurations if provided
        if config_file:
            self._load_custom_configurations()
        
        # Build indexes for optimized queries
        self._build_database_indexes()
    
    def _build_database_indexes(self):
        """Build indexes for faster database queries."""
        try:
            # Build industry index
            self._query_optimizer.build_index(
                self.industries, 
                ["categories", "term_mappings", "synonyms"]
            )
            
            # Build category indexes for each industry
            for industry, data in self.industries.items():
                if "categories" in data:
                    categories_data = {f"{industry}_{i}": cat 
                                     for i, cat in enumerate(data["categories"])}
                    self._query_optimizer.build_index(
                        categories_data,
                        ["category", "customer_terms", "website_terms"]
                    )
            
            logger.debug("Database indexes built successfully")
        except Exception as e:
            logger.warning(f"Failed to build database indexes: {e}")
    
    def _load_default_configurations(self):
        """Load default industry configurations."""
        # Restaurant industry configuration
        self.industries["Restaurant"] = {
            "categories": [
                {
                    "category": "Menu Items",
                    "description": "Food and beverage offerings",
                    "customer_terms": ["food", "menu", "dishes", "items"],
                    "website_terms": ["menu", "food", "dishes", "offerings", "items"],
                    "confidence": 0.9,
                    "synonyms": ["selections", "choices"]
                },
                {
                    "category": "Cuisine Type", 
                    "description": "Style of cooking",
                    "customer_terms": ["cuisine", "cooking", "style"],
                    "website_terms": ["cuisine", "cooking", "style", "type"],
                    "confidence": 0.85,
                    "synonyms": ["food style"]
                },
                {
                    "category": "Dining Options",
                    "description": "Service and seating types", 
                    "customer_terms": ["dining", "seating", "service"],
                    "website_terms": ["dining", "seating", "service", "options"],
                    "confidence": 0.8,
                    "synonyms": ["eating options"]
                },
                {
                    "category": "Amenities",
                    "description": "Restaurant facilities",
                    "customer_terms": ["amenities", "facilities", "features"],
                    "website_terms": ["amenities", "facilities", "features"],
                    "confidence": 0.85,
                    "synonyms": ["perks", "extras"]
                },
                {
                    "category": "Hours",
                    "description": "Operating times",
                    "customer_terms": ["hours", "time", "open"],
                    "website_terms": ["hours", "time", "open", "schedule"],
                    "confidence": 0.95,
                    "synonyms": ["schedule", "timing"]
                },
                {
                    "category": "Location",
                    "description": "Address and contact info",
                    "customer_terms": ["location", "address", "contact"],
                    "website_terms": ["location", "address", "contact", "phone"],
                    "confidence": 0.9,
                    "synonyms": ["place", "where"]
                }
            ],
            "term_mappings": {
                "vegetarian options": {
                    "website_terms": ["vegetarian", "vegan", "plant-based", "meat-free"],
                    "category": "Menu Items",
                    "confidence": 0.95
                },
                "parking": {
                    "website_terms": ["parking", "valet", "garage"],
                    "category": "Amenities", 
                    "confidence": 0.9
                }
            },
            "synonyms": {
                "parking": ["parking lot", "valet", "garage"],
                "vegetarian": ["vegan", "plant-based", "meat-free"]
            }
        }
        
        # Medical industry configuration
        self.industries["Medical"] = {
            "categories": [
                {
                    "category": "Services",
                    "description": "Medical procedures and treatments",
                    "customer_terms": ["services", "procedures", "treatments"],
                    "website_terms": ["services", "procedures", "treatments", "care"],
                    "confidence": 0.9,
                    "synonyms": ["medical care"]
                },
                {
                    "category": "Specialties",
                    "description": "Medical specialization areas",
                    "customer_terms": ["specialties", "specialization", "expertise"],
                    "website_terms": ["specialties", "specialization", "expertise"],
                    "confidence": 0.85,
                    "synonyms": ["areas of expertise"]
                },
                {
                    "category": "Insurance",
                    "description": "Accepted insurance providers",
                    "customer_terms": ["insurance", "coverage", "payment"],
                    "website_terms": ["insurance", "coverage", "payment", "billing"],
                    "confidence": 0.9,
                    "synonyms": ["health plan"]
                },
                {
                    "category": "Staff",
                    "description": "Doctor and staff information",
                    "customer_terms": ["staff", "doctors", "physicians"],
                    "website_terms": ["staff", "doctors", "physicians", "team"],
                    "confidence": 0.85,
                    "synonyms": ["medical team"]
                },
                {
                    "category": "Facilities",
                    "description": "Medical equipment and amenities",
                    "customer_terms": ["facilities", "equipment", "amenities"],
                    "website_terms": ["facilities", "equipment", "amenities"],
                    "confidence": 0.8,
                    "synonyms": ["medical equipment"]
                },
                {
                    "category": "Appointments",
                    "description": "Scheduling and availability",
                    "customer_terms": ["appointments", "scheduling", "booking"],
                    "website_terms": ["appointments", "scheduling", "booking", "visits"],
                    "confidence": 0.9,
                    "synonyms": ["visits", "consultations"]
                }
            ],
            "term_mappings": {},
            "synonyms": {}
        }
        
        # Add other industries
        for industry in ["Real Estate", "Dental", "Furniture", "Hardware/Home Improvement", 
                        "Vehicle Fuel", "Vehicle Sales", "Vehicle Repair/Towing", 
                        "Ride Services", "Shop at Home", "Fast Food"]:
            self.industries[industry] = {
                "categories": [],
                "term_mappings": {},
                "synonyms": {}
            }
    
    def _load_custom_configurations(self):
        """Load custom configurations from file."""
        try:
            with open(self.config_file, 'r') as f:
                custom_data = json.load(f)
                
            for industry, data in custom_data.items():
                # Handle custom mappings
                if "custom_mappings" in data:
                    self.custom_mappings[industry] = data["custom_mappings"]
                
                # Add or update industry data
                if industry in self.industries:
                    # Merge with existing industry
                    if "categories" in data:
                        self.industries[industry]["categories"] = data["categories"]
                    if "term_mappings" in data:
                        self.industries[industry]["term_mappings"].update(data["term_mappings"])
                else:
                    # Add new industry
                    self.industries[industry] = data
                
        except Exception as e:
            logger.error(f"Failed to load custom configurations: {e}")
    
    @property 
    def _get_categories_cached(self):
        """Cached version of get_categories method."""
        return self._query_optimizer.cached_query()(self._get_categories_impl)
    
    def _get_categories_impl(self, industry: str) -> List[Dict[str, Any]]:
        """Implementation of get_categories without caching."""
        if industry not in self.industries:
            return []
        
        return self.industries[industry].get("categories", [])
    
    def get_categories(self, industry: str) -> List[Dict[str, Any]]:
        """Get categories for a specific industry with caching.
        
        Args:
            industry: Industry name
            
        Returns:
            List of category dictionaries
        """
        return self._get_categories_cached(industry)
    
    def load_industry_database(self, industry: str) -> Optional[Dict[str, Any]]:
        """Load complete database for an industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Industry database dictionary or None
        """
        if industry not in self.industries:
            return None
        
        return self.industries[industry]
    
    def validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate database schema.
        
        Args:
            data: Data to validate
            
        Returns:
            Validation result with errors and warnings
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        if "categories" not in data:
            result["errors"].append("Missing required 'categories' field")
            result["valid"] = False
            return result
        
        for i, category in enumerate(data["categories"]):
            # Check required fields
            required_fields = ["category", "description", "customer_terms", "website_terms", "confidence"]
            for field in required_fields:
                if field not in category:
                    result["errors"].append(f"Category {i}: Missing required field '{field}'")
                    result["valid"] = False
            
            # Validate confidence range
            if "confidence" in category:
                confidence = category["confidence"]
                if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                    result["errors"].append(f"Category {i}: confidence must be between 0.0 and 1.0")
                    result["valid"] = False
            
            # Validate arrays are not empty
            for array_field in ["customer_terms", "website_terms"]:
                if array_field in category:
                    if not isinstance(category[array_field], list) or len(category[array_field]) == 0:
                        result["errors"].append(f"Category {i}: {array_field} cannot be empty")
                        result["valid"] = False
                    else:
                        # Check for duplicates
                        terms = category[array_field]
                        if len(terms) != len(set(terms)):
                            result["errors"].append(f"Category {i}: Duplicate terms in {array_field}")
                            result["valid"] = False
        
        # Check for duplicate category names
        category_names = [cat.get("category") for cat in data["categories"]]
        if len(category_names) != len(set(category_names)):
            result["errors"].append("Duplicate category names found")
            result["valid"] = False
        
        return result
    
    def add_custom_mapping(self, industry: str, customer_term: str, category: str, 
                          website_terms: List[str], confidence: float) -> Dict[str, Any]:
        """Add custom term mapping.
        
        Args:
            industry: Industry name
            customer_term: Customer search term
            category: Category for the mapping
            website_terms: List of website terms to map to
            confidence: Confidence score for the mapping
            
        Returns:
            Result dictionary with success status
        """
        with self._lock:
            # Validate input
            errors = []
            if not customer_term.strip():
                errors.append("Customer term cannot be empty")
            if not website_terms:
                errors.append("Website terms cannot be empty")
            if confidence < 0 or confidence > 1:
                errors.append("Confidence must be between 0.0 and 1.0")
            
            if errors:
                return {"success": False, "errors": errors}
            
            # Initialize custom mappings for industry if needed
            if industry not in self.custom_mappings:
                self.custom_mappings[industry] = []
            
            # Create mapping
            mapping = {
                "customer_term": customer_term,
                "category": category,
                "website_terms": website_terms,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "user_defined": True
            }
            
            self.custom_mappings[industry].append(mapping)
            
            return {
                "success": True,
                "mapping_id": f"custom_{len(self.custom_mappings[industry])}"
            }
    
    def get_custom_mappings(self, industry: str) -> List[Dict[str, Any]]:
        """Get custom mappings for an industry.
        
        Args:
            industry: Industry name
            
        Returns:
            List of custom mappings
        """
        return self.custom_mappings.get(industry, [])
    
    def save_custom_mappings(self) -> Dict[str, Any]:
        """Save custom mappings to file.
        
        Returns:
            Result dictionary with success status
        """
        if not self.config_file:
            return {"success": False, "error": "No config file specified"}
        
        try:
            # Create directory if it doesn't exist
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            # Load existing data or create new
            existing_data = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    # File exists but is empty or invalid JSON
                    existing_data = {}
            
            # Update with custom mappings
            for industry, mappings in self.custom_mappings.items():
                if industry not in existing_data:
                    existing_data[industry] = {}
                existing_data[industry]["custom_mappings"] = mappings
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_term_mapping(self, term: str, industry: str) -> Optional[Dict[str, Any]]:
        """Get term mapping for a specific customer term.
        
        Args:
            term: Customer search term
            industry: Target industry
            
        Returns:
            Term mapping result or None if not found
        """
        if industry not in self.industries:
            return None
        
        industry_data = self.industries[industry]
        
        # Check term mappings first
        if "term_mappings" in industry_data and term in industry_data["term_mappings"]:
            mapping = industry_data["term_mappings"][term].copy()
            mapping["customer_term"] = term
            return mapping
        
        # Check custom mappings
        if industry in self.custom_mappings:
            for custom_mapping in self.custom_mappings[industry]:
                if custom_mapping["customer_term"] == term:
                    return {
                        "customer_term": term,
                        "website_terms": custom_mapping["website_terms"],
                        "category": custom_mapping["category"],
                        "confidence": custom_mapping["confidence"]
                    }
        
        return None
    
    def get_term_mappings_batch(self, terms: List[str], industry: str) -> Dict[str, Any]:
        """Get multiple term mappings in batch.
        
        Args:
            terms: List of customer terms
            industry: Target industry
            
        Returns:
            Dictionary mapping terms to their results
        """
        results = {}
        for term in terms:
            mapping = self.get_term_mapping(term, industry)
            if mapping:
                results[term] = mapping
        return results
    
    def get_supported_industries(self) -> List[str]:
        """Get list of all supported industries.
        
        Returns:
            List of industry names
        """
        return list(self.industries.keys())
    
    def create_backup(self) -> Dict[str, Any]:
        """Create backup of all database data.
        
        Returns:
            Backup data dictionary
        """
        backup_data = {
            "timestamp": datetime.now().isoformat()
        }
        # Add industries as top-level keys
        backup_data.update(self.industries.copy())
        # Add custom mappings metadata
        backup_data["_metadata"] = {
            "custom_mappings": self.custom_mappings.copy()
        }
        return backup_data
    
    def restore_from_backup(self, backup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore database from backup data.
        
        Args:
            backup_data: Backup data to restore
            
        Returns:
            Result dictionary with success status
        """
        try:
            with self._lock:
                # Handle new backup format
                if "_metadata" in backup_data:
                    # Extract industries (all keys except metadata and timestamp)
                    industries = {k: v for k, v in backup_data.items() 
                                if k not in ["_metadata", "timestamp"]}
                    self.industries = industries
                    
                    # Extract custom mappings from metadata
                    if "custom_mappings" in backup_data["_metadata"]:
                        self.custom_mappings = backup_data["_metadata"]["custom_mappings"]
                else:
                    # Handle old backup format
                    if "industries" in backup_data:
                        self.industries = backup_data["industries"]
                    if "custom_mappings" in backup_data:
                        self.custom_mappings = backup_data["custom_mappings"]
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_term_mapping(self, term: str, industry: str) -> Optional[Dict[str, Any]]:
        """Get term mapping for a specific customer term.
        
        Args:
            term: Customer search term
            industry: Target industry
            
        Returns:
            Term mapping result or None if not found
        """
        if industry not in self.industries:
            return None
        
        industry_data = self.industries[industry]
        
        # Check term mappings first
        if "term_mappings" in industry_data and term in industry_data["term_mappings"]:
            mapping = industry_data["term_mappings"][term].copy()
            mapping["customer_term"] = term
            return mapping
        
        # Check custom mappings
        if industry in self.custom_mappings:
            for custom_mapping in self.custom_mappings[industry]:
                if custom_mapping["customer_term"] == term:
                    return {
                        "customer_term": term,
                        "website_terms": custom_mapping["website_terms"],
                        "category": custom_mapping["category"],
                        "confidence": custom_mapping["confidence"]
                    }
        
        return None
    
    def get_term_mappings_batch(self, terms: List[str], industry: str) -> Dict[str, Any]:
        """Get multiple term mappings in batch.
        
        Args:
            terms: List of customer terms
            industry: Target industry
            
        Returns:
            Dictionary mapping terms to their results
        """
        results = {}
        for term in terms:
            mapping = self.get_term_mapping(term, industry)
            if mapping:
                results[term] = mapping
        return results