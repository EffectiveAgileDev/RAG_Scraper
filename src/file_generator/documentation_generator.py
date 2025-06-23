"""Documentation generators for RAG Integration Support."""

from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from pathlib import Path

from .integration_config import RelationshipType, VERSION_INFO


class BaseDocumentationGenerator(ABC):
    """Base class for documentation generators."""
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
    
    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate documentation."""
        pass
    
    def _format_header(self, title: str, level: int = 1) -> str:
        """Format markdown header."""
        return f"{'#' * level} {title}\n\n"
    
    def _format_code_block(self, code: str, language: str = "python") -> str:
        """Format code block."""
        return f"```{language}\n{code}\n```\n\n"
    
    def _format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Format markdown table."""
        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        for row in rows:
            table += "| " + " | ".join(row) + " |\n"
        return table + "\n"


class EntityRelationshipDocGenerator(BaseDocumentationGenerator):
    """Generator for entity relationship documentation."""
    
    def generate(self, **kwargs) -> str:
        """Generate entity relationship documentation."""
        doc = self._format_header("Entity Relationship Schema")
        
        doc += self._generate_overview()
        doc += self._generate_relationship_types()
        doc += self._generate_data_model()
        doc += self._generate_access_patterns()
        doc += self._generate_examples()
        doc += self._generate_multipage_handling()
        doc += self._generate_best_practices()
        doc += self._generate_integration_guidance()
        doc += self._generate_troubleshooting()
        
        return doc
    
    def _generate_overview(self) -> str:
        """Generate overview section."""
        return self._format_header("Overview", 2) + """
The RAG_Scraper entity relationship system enables tracking and navigation of relationships 
between scraped entities across multiple pages. This is particularly important for restaurant 
directories where data is distributed across parent directory pages and individual restaurant 
detail pages.

### Key Features

- **Multi-page relationship tracking**: Maintain connections between related entities across different pages
- **Hierarchical data organization**: Support parent-child relationships for directory structures
- **Cross-references**: Enable non-hierarchical connections between related entities
- **Bidirectional navigation**: Navigate relationships in both directions
- **Temporal tracking**: Track when relationships were discovered and last verified

"""
    
    def _generate_relationship_types(self) -> str:
        """Generate relationship types section."""
        doc = self._format_header("Relationship Types", 2)
        
        relationships = [
            ["Parent-Child", "Hierarchical", "Directory → Restaurant pages", "Bidirectional"],
            ["Sibling", "Horizontal", "Restaurants in same directory", "Via shared parent"],
            ["Reference", "Cross-reference", "Related locations, similar cuisine", "Direct links"]
        ]
        
        doc += self._format_table(
            ["Type", "Structure", "Use Case", "Navigation"],
            relationships
        )
        
        doc += self._format_header("Parent-Child Relationships", 3)
        doc += """
- **Parent**: A directory or listing page that contains links to detail pages
- **Child**: A detail page linked from a parent directory
- **Use Case**: Restaurant directory → Individual restaurant pages
- **Navigation**: Bidirectional - children know their parent, parents track their children

"""
        
        doc += self._format_header("Sibling Relationships", 3)
        doc += """
- **Definition**: Entities at the same hierarchical level sharing a common parent
- **Use Case**: Multiple restaurants listed on the same directory page
- **Navigation**: Can traverse between siblings via shared parent reference

"""
        
        doc += self._format_header("Reference Relationships", 3)
        doc += """
- **Definition**: Non-hierarchical connections between entities
- **Use Case**: "Similar restaurants", "Other locations", "Related cuisines"
- **Navigation**: Direct entity-to-entity links without hierarchy

"""
        
        return doc
    
    def _generate_data_model(self) -> str:
        """Generate data model section."""
        doc = self._format_header("Data Model", 2)
        
        doc += self._format_header("Core Relationship Structure", 3)
        doc += self._format_code_block("""
interface EntityRelationship {
  type: 'parent' | 'child' | 'sibling' | 'reference';
  entity_id: string;        // Unique identifier of related entity
  entity_type: string;      // Type of entity (e.g., 'restaurant', 'directory')
  entity_name?: string;     // Human-readable name
  relationship_metadata?: {
    discovered_at: string;  // When relationship was found
    confidence: number;     // Confidence score (0-1)
    source: string;        // How relationship was determined
  };
}
""", "typescript")
        
        doc += self._format_header("Python Implementation", 3)
        doc += self._format_code_block("""
from typing import Literal, Optional, Dict
from dataclasses import dataclass

@dataclass
class EntityRelationship:
    type: Literal['parent', 'child', 'sibling', 'reference']
    entity_id: str
    entity_type: str
    entity_name: Optional[str] = None
    relationship_metadata: Optional[Dict] = None
    
    def __post_init__(self):
        if self.relationship_metadata is None:
            self.relationship_metadata = {}
""")
        
        return doc
    
    def _generate_access_patterns(self) -> str:
        """Generate access patterns section."""
        doc = self._format_header("Access Patterns", 2)
        
        doc += self._format_header("Finding Parent from Child", 3)
        doc += self._format_code_block("""
def get_parent(restaurant_data: RestaurantData) -> Optional[EntityRelationship]:
    \"\"\"Get parent directory of a restaurant.\"\"\"
    parents = [
        rel for rel in restaurant_data.entity_relationships
        if rel.type == RelationshipType.PARENT
    ]
    return parents[0] if parents else None
""")
        
        doc += self._format_header("Finding All Children of a Parent", 3)
        doc += self._format_code_block("""
def get_children(directory_data: DirectoryData) -> List[EntityRelationship]:
    \"\"\"Get all restaurants in a directory.\"\"\"
    return [
        rel for rel in directory_data.entity_relationships
        if rel.type == RelationshipType.CHILD
    ]
""")
        
        doc += self._format_header("Finding Siblings", 3)
        doc += self._format_code_block("""
def get_siblings(
    restaurant_data: RestaurantData, 
    all_restaurants: List[RestaurantData]
) -> List[RestaurantData]:
    \"\"\"Find sibling restaurants (same parent).\"\"\"
    parent = get_parent(restaurant_data)
    if not parent:
        return []
    
    siblings = []
    for other in all_restaurants:
        if other.restaurant_id != restaurant_data.restaurant_id:
            other_parent = get_parent(other)
            if other_parent and other_parent.entity_id == parent.entity_id:
                siblings.append(other)
    return siblings
""")
        
        doc += self._format_header("Traversing References", 3)
        doc += self._format_code_block("""
def get_related_restaurants(restaurant_data: RestaurantData) -> List[EntityRelationship]:
    \"\"\"Get all referenced restaurants.\"\"\"
    return [
        rel for rel in restaurant_data.entity_relationships
        if rel.type == RelationshipType.REFERENCE
    ]
""")
        
        return doc
    
    def _generate_examples(self) -> str:
        """Generate examples section."""
        doc = self._format_header("Examples", 2)
        
        doc += self._format_header("Restaurant with Parent Directory", 3)
        doc += self._format_code_block("""
{
  "restaurant_id": "luigis_001",
  "restaurant_name": "Luigi's Italian Bistro",
  "parent_page_url": "https://example.com/restaurants/italian",
  "entity_relationships": [
    {
      "type": "parent",
      "entity_id": "dir_italian",
      "entity_type": "directory",
      "entity_name": "Italian Restaurants Directory"
    },
    {
      "type": "sibling",
      "entity_id": "marios_001",
      "entity_type": "restaurant", 
      "entity_name": "Mario's Pizza Palace"
    },
    {
      "type": "reference",
      "entity_id": "luigis_002",
      "entity_type": "restaurant",
      "entity_name": "Luigi's Downtown Location"
    }
  ]
}
""", "json")
        
        doc += self._format_header("Multi-Level Hierarchy", 3)
        doc += """
```
City Directory (parent)
  └── Cuisine Directory (child of city, parent of restaurants)
      ├── Restaurant A (child)
      ├── Restaurant B (child)
      └── Restaurant C (child)
```

"""
        return doc
    
    def _generate_multipage_handling(self) -> str:
        """Generate multi-page handling section."""
        doc = self._format_header("Multi-Page Relationship Handling", 2)
        
        doc += self._format_header("Relationship Discovery", 3)
        doc += """
1. **During Scraping**: Relationships are discovered as pages are crawled
2. **URL Analysis**: Parent-child relationships inferred from URL structure
3. **Content Analysis**: References found in page content (e.g., "See also", "Other locations")
4. **Post-Processing**: Additional relationships identified during data aggregation

"""
        
        doc += self._format_header("Relationship Integrity", 3)
        doc += """
1. **Bidirectional Validation**: Parent-child relationships verified from both directions
2. **Cycle Detection**: Prevents circular references in relationship graphs
3. **Orphan Handling**: Identifies entities without expected relationships
4. **Conflict Resolution**: Handles cases where relationships conflict

"""
        
        doc += self._format_header("Temporal Considerations", 3)
        doc += self._format_code_block("""
# Track when relationships change over time
{
  "entity_relationships": [
    {
      "type": "parent",
      "entity_id": "dir_001", 
      "entity_type": "directory",
      "relationship_metadata": {
        "discovered_at": "2024-01-20T10:30:00Z",
        "last_verified": "2024-01-20T10:30:00Z",
        "confidence": 0.95,
        "source": "url_pattern_analysis"
      }
    }
  ]
}
""", "json")
        
        return doc
    
    def _generate_best_practices(self) -> str:
        """Generate best practices section."""
        doc = self._format_header("Best Practices", 2)
        
        doc += self._format_header("Relationship Naming", 3)
        doc += """
- Use consistent entity_id format: `{type}_{identifier}`
- Include human-readable entity_name when possible
- Maintain type consistency (e.g., always "restaurant" not "eatery")

"""
        
        doc += self._format_header("Relationship Validation", 3)
        doc += self._format_code_block("""
def validate_relationship(rel: EntityRelationship) -> bool:
    \"\"\"Validate relationship data.\"\"\"
    if rel.type not in [RelationshipType.PARENT, RelationshipType.CHILD, 
                       RelationshipType.SIBLING, RelationshipType.REFERENCE]:
        return False
        
    if not rel.entity_id or not isinstance(rel.entity_id, str):
        return False
        
    if not rel.entity_type or not isinstance(rel.entity_type, str):
        return False
        
    return True
""")
        
        doc += self._format_header("Querying Relationships", 3)
        doc += self._format_code_block("""
class RelationshipQuery:
    def __init__(self, data: RestaurantData):
        self.data = data
    
    def by_type(self, rel_type: RelationshipType) -> List[EntityRelationship]:
        return [r for r in self.data.entity_relationships if r.type == rel_type]
    
    def by_entity_type(self, entity_type: str) -> List[EntityRelationship]:
        return [r for r in self.data.entity_relationships if r.entity_type == entity_type]
    
    def find(self, entity_id: str) -> Optional[EntityRelationship]:
        return next((r for r in self.data.entity_relationships if r.entity_id == entity_id), None)
""")
        
        return doc
    
    def _generate_integration_guidance(self) -> str:
        """Generate integration guidance section."""
        doc = self._format_header("Integration with RAG Systems", 2)
        
        doc += self._format_header("Contextual Retrieval", 3)
        doc += """
Use relationships to provide context in RAG queries:

"""
        doc += self._format_code_block("""
def build_context(restaurant: RestaurantData, all_data: Dict[str, RestaurantData]) -> Dict:
    \"\"\"Build context including related entities.\"\"\"
    context = {
        'main': restaurant,
        'parent': get_entity(get_parent(restaurant), all_data),
        'siblings': [get_entity(s, all_data) for s in get_siblings(restaurant, all_data.values())],
        'references': [get_entity(r, all_data) for r in get_references(restaurant)]
    }
    return context

def get_entity(relationship: EntityRelationship, all_data: Dict[str, RestaurantData]) -> Optional[RestaurantData]:
    \"\"\"Get entity data from relationship.\"\"\"
    if relationship:
        return all_data.get(relationship.entity_id)
    return None
""")
        
        doc += self._format_header("Relationship-Aware Chunking", 3)
        doc += """
Consider relationships when creating semantic chunks:

"""
        doc += self._format_code_block("""
def create_relationship_aware_chunks(restaurant: RestaurantData) -> List[SemanticChunk]:
    \"\"\"Create chunks that preserve relationship context.\"\"\"
    chunks = []
    
    # Include parent context in first chunk
    parent = get_parent(restaurant)
    if parent:
        chunks.append(SemanticChunk(
            chunk_id=f"{restaurant.restaurant_id}_context",
            content=f"Part of {parent.entity_name}. {restaurant.description}",
            metadata={'includes_parent': True, 'parent_id': parent.entity_id}
        ))
    
    # Add main content chunks
    # ... rest of chunking logic
    
    return chunks
""")
        
        return doc
    
    def _generate_troubleshooting(self) -> str:
        """Generate troubleshooting section."""
        doc = self._format_header("Troubleshooting", 2)
        
        doc += self._format_header("Common Issues", 3)
        doc += """
1. **Missing Relationships**: Check URL patterns and scraping depth
2. **Duplicate Relationships**: Implement deduplication in aggregation
3. **Broken References**: Validate entity_ids exist in dataset
4. **Performance**: Index by entity_id for fast lookups

"""
        
        doc += self._format_header("Debugging Relationships", 3)
        doc += self._format_code_block("""
def debug_relationships(entity: RestaurantData):
    \"\"\"Print relationship debugging info.\"\"\"
    print(f"Entity: {entity.restaurant_id}")
    print(f"Relationships: {len(entity.entity_relationships)}")
    
    by_type = {}
    for rel in entity.entity_relationships:
        by_type.setdefault(rel.type, []).append(rel)
    
    for rel_type, rels in by_type.items():
        print(f"  {rel_type.value}: {len(rels)} relationships")
        for rel in rels[:3]:  # Show first 3
            print(f"    - {rel.entity_name or rel.entity_id}")

def validate_relationship_integrity(all_data: List[RestaurantData]) -> List[str]:
    \"\"\"Validate relationship integrity across all data.\"\"\"
    errors = []
    entity_ids = {r.restaurant_id for r in all_data}
    
    for restaurant in all_data:
        for rel in restaurant.entity_relationships:
            # Check if referenced entity exists
            if rel.entity_id not in entity_ids:
                errors.append(f"Broken reference: {restaurant.restaurant_id} -> {rel.entity_id}")
            
            # Check for circular references
            if rel.entity_id == restaurant.restaurant_id:
                errors.append(f"Circular reference: {restaurant.restaurant_id}")
    
    return errors
""")
        
        return doc


class APIDocumentationGenerator(BaseDocumentationGenerator):
    """Generator for API documentation."""
    
    def generate(self, **kwargs) -> str:
        """Generate API documentation."""
        doc = self._format_header("API Reference")
        
        doc += self._generate_overview()
        doc += self._generate_data_structures()
        doc += self._generate_file_organization() 
        doc += self._generate_access_methods()
        doc += self._generate_integration_points()
        doc += self._generate_code_examples()
        
        return doc
    
    def _generate_overview(self) -> str:
        """Generate API overview."""
        return f"""
## Overview

This API documentation describes how to programmatically access and work with data generated by RAG_Scraper version {self.version}. The system generates structured restaurant data with multi-page relationship support, optimized for RAG (Retrieval-Augmented Generation) applications.

### Key Features

- **Structured Data Output**: JSON and text formats with comprehensive metadata
- **Multi-page Relationships**: Track connections between related pages and entities
- **RAG Optimization**: Semantic chunks and embedding hints for vector databases
- **Type Safety**: Complete TypeScript and Python type definitions
- **Validation**: JSON Schema validation for data integrity

"""
    
    def _generate_data_structures(self) -> str:
        """Generate data structures documentation."""
        doc = self._format_header("Data Structures", 2)
        
        doc += self._format_header("Restaurant Data", 3)
        doc += """
The core data structure containing all information about a restaurant:

"""
        
        fields = [
            ["restaurant_id", "string", "Unique identifier", "Yes"],
            ["restaurant_name", "string", "Display name", "Yes"],
            ["cuisine_type", "string", "Type of cuisine", "Yes"],
            ["location", "Location", "Address and location details", "Yes"],
            ["menu_items", "MenuItem[]", "Array of menu items with prices", "No"],
            ["extraction_timestamp", "string", "ISO 8601 timestamp", "Yes"],
            ["source_url", "string", "Original page URL", "Yes"],
            ["parent_page_url", "string", "Parent directory URL", "No"],
            ["entity_relationships", "EntityRelationship[]", "Related entities", "No"],
            ["semantic_chunks", "SemanticChunk[]", "RAG-optimized content chunks", "No"],
            ["cross_references", "CrossReference[]", "References to related restaurants", "No"]
        ]
        
        doc += self._format_table(
            ["Field", "Type", "Description", "Required"],
            fields
        )
        
        doc += self._format_header("Entity Relationships", 3)
        doc += """
Track relationships between entities:

"""
        
        rel_fields = [
            ["type", "string", "parent, child, sibling, reference", "Yes"],
            ["entity_id", "string", "Related entity's ID", "Yes"],
            ["entity_type", "string", "Type of related entity", "Yes"],
            ["entity_name", "string", "Human-readable name", "No"]
        ]
        
        doc += self._format_table(
            ["Field", "Type", "Description", "Required"],
            rel_fields
        )
        
        return doc
    
    def _generate_file_organization(self) -> str:
        """Generate file organization documentation."""
        doc = self._format_header("File Organization", 2)
        
        doc += self._format_header("Directory Structure", 3)
        doc += self._format_code_block("""
output/
└── restaurants/
    ├── master_index.json         # Master index of all restaurants
    ├── master_index.txt          # Human-readable master index
    ├── Italian/                  # Cuisine-based directories
    │   ├── Italian_index.json    # Cuisine-specific index
    │   ├── Italian_index.txt     # Human-readable cuisine index
    │   └── *.txt                 # Individual restaurant files
    ├── Japanese/
    │   └── ...
    └── Unknown/                  # Uncategorized restaurants
""", "")
        
        doc += self._format_header("File Naming Convention", 3)
        doc += """
- Restaurant files: `{sanitized_restaurant_name}.txt`
- Index files: `{cuisine}_index.{json|txt}`
- Master index: `master_index.{json|txt}`

"""
        
        doc += self._format_header("Metadata Storage", 3)
        doc += """
Each text file contains YAML front matter with metadata:

"""
        doc += self._format_code_block("""
---
restaurant_id: rest_001
restaurant_name: Luigi's Italian Bistro
cuisine_type: Italian
extraction_timestamp: 2024-01-20T10:30:00Z
source_url: https://example.com/luigis
parent_page_url: https://example.com/restaurants
---

[Restaurant content follows...]
""", "yaml")
        
        return doc
    
    def _generate_access_methods(self) -> str:
        """Generate access methods documentation.""" 
        doc = self._format_header("Access Methods", 2)
        
        doc += self._format_header("Reading JSON Index Files", 3)
        doc += self._format_code_block("""
import json
from pathlib import Path

def load_master_index(output_dir: Path) -> dict:
    \"\"\"Load the master index file.\"\"\"
    index_path = output_dir / 'master_index.json'
    with open(index_path, 'r') as f:
        return json.load(f)

def get_restaurants_by_cuisine(output_dir: Path, cuisine: str) -> list:
    \"\"\"Get all restaurants for a specific cuisine.\"\"\"
    master_index = load_master_index(output_dir)
    cuisine_data = master_index['by_cuisine'].get(cuisine, {})
    return list(cuisine_data.get('restaurants', {}).values())

# Usage
restaurants = get_restaurants_by_cuisine(Path('output/restaurants'), 'Italian')
for restaurant in restaurants:
    print(f"{restaurant['name']} - {restaurant['location']['city']}")
""")
        
        doc += self._format_header("Reading Individual Restaurant Files", 3)
        doc += self._format_code_block("""
import yaml
from pathlib import Path

def read_restaurant_file(file_path: Path) -> tuple[dict, str]:
    \"\"\"Read restaurant file and extract metadata and content.\"\"\"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract YAML front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return metadata, body
    
    return {}, content

# Usage
metadata, content = read_restaurant_file(Path('output/restaurants/Italian/luigis_bistro.txt'))
print(f"Restaurant: {metadata['restaurant_name']}")
print(f"Content length: {len(content)} characters")
""")
        
        return doc
    
    def _generate_integration_points(self) -> str:
        """Generate integration points documentation."""
        doc = self._format_header("Integration Points", 2)
        
        doc += self._format_header("Vector Database Integration", 3)
        doc += self._format_code_block("""
from typing import List, Dict
import json

class RestaurantVectorizer:
    \"\"\"Convert restaurant data for vector database storage.\"\"\"
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.master_index = self._load_master_index()
    
    def _load_master_index(self) -> dict:
        with open(self.output_dir / 'master_index.json', 'r') as f:
            return json.load(f)
    
    def prepare_documents(self) -> List[Dict]:
        \"\"\"Prepare documents for vector database indexing.\"\"\"
        documents = []
        
        for cuisine, data in self.master_index['by_cuisine'].items():
            for rest_id, rest_data in data['restaurants'].items():
                # Load full content
                file_path = self.output_dir / cuisine / rest_data['file_path']
                metadata, content = read_restaurant_file(file_path)
                
                # Prepare document
                doc = {
                    'id': rest_id,
                    'content': content,
                    'metadata': {
                        'restaurant_name': rest_data['name'],
                        'cuisine': cuisine,
                        'location': rest_data['location'],
                        'source_url': metadata.get('source_url'),
                        'extraction_date': metadata.get('extraction_timestamp'),
                        'relationships': rest_data.get('relationships', [])
                    }
                }
                documents.append(doc)
        
        return documents
""")
        
        return doc
    
    def _generate_code_examples(self) -> str:
        """Generate code examples section."""
        doc = self._format_header("Code Examples", 2)
        
        doc += self._format_header("Python: Complete Data Access", 3)
        doc += self._format_code_block("""
from pathlib import Path
import json
from typing import List, Dict, Optional

class RestaurantDataReader:
    \"\"\"Comprehensive restaurant data access interface.\"\"\"
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.master_index = self._load_master_index()
    
    def _load_master_index(self) -> Dict:
        \"\"\"Load master index file.\"\"\"
        index_path = self.output_dir / 'master_index.json'
        if index_path.exists():
            with open(index_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_all_restaurants(self) -> List[Dict]:
        \"\"\"Get all restaurants across all cuisines.\"\"\"
        restaurants = []
        for cuisine_data in self.master_index.get('by_cuisine', {}).values():
            for rest_data in cuisine_data.get('restaurants', {}).values():
                restaurants.append(rest_data)
        return restaurants
    
    def get_by_cuisine(self, cuisine: str) -> List[Dict]:
        \"\"\"Get restaurants by cuisine type.\"\"\"
        cuisine_data = self.master_index.get('by_cuisine', {}).get(cuisine, {})
        return list(cuisine_data.get('restaurants', {}).values())
    
    def get_by_location(self, city: str, state: Optional[str] = None) -> List[Dict]:
        \"\"\"Get restaurants by location.\"\"\"
        results = []
        for restaurant in self.get_all_restaurants():
            location = restaurant.get('location', {})
            if location.get('city', '').lower() == city.lower():
                if state is None or location.get('state', '').lower() == state.lower():
                    results.append(restaurant)
        return results
    
    def get_restaurant_content(self, restaurant_id: str) -> Optional[str]:
        \"\"\"Get full content for a specific restaurant.\"\"\"
        for cuisine, data in self.master_index.get('by_cuisine', {}).items():
            if restaurant_id in data.get('restaurants', {}):
                rest_data = data['restaurants'][restaurant_id]
                file_path = self.output_dir / cuisine / rest_data['file_path']
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
        return None
    
    def search_restaurants(self, query: str) -> List[Dict]:
        \"\"\"Search restaurants by name or description.\"\"\"
        query_lower = query.lower()
        results = []
        
        for restaurant in self.get_all_restaurants():
            if (query_lower in restaurant.get('name', '').lower() or
                query_lower in restaurant.get('description', '').lower()):
                results.append(restaurant)
        
        return results

# Usage Example
reader = RestaurantDataReader(Path('output/restaurants'))

# Get all Italian restaurants
italian_restaurants = reader.get_by_cuisine('Italian')
print(f"Found {len(italian_restaurants)} Italian restaurants")

# Search for pizza places
pizza_places = reader.search_restaurants('pizza')
for place in pizza_places:
    print(f"{place['name']} - {place['location']['city']}")

# Get restaurants in New York
ny_restaurants = reader.get_by_location('New York', 'NY')
for restaurant in ny_restaurants:
    print(f"{restaurant['name']} - {restaurant['cuisine']}")
""")
        
        return doc


class ReadmeGenerator(BaseDocumentationGenerator):
    """Generator for README documentation."""
    
    def generate(self, package_info: Dict[str, Any], **kwargs) -> str:
        """Generate README for integration package."""
        doc = self._format_header("RAG_Scraper Integration Package")
        
        doc += self._generate_overview()
        doc += self._generate_quick_start()
        doc += self._generate_installation()
        doc += self._generate_usage_examples()
        doc += self._generate_integration_examples()
        doc += self._generate_documentation_links()
        doc += self._generate_testing()
        doc += self._generate_version_info(package_info)
        doc += self._generate_support()
        
        return doc
    
    def _generate_overview(self) -> str:
        """Generate overview section."""
        return """
## Overview

This integration package provides comprehensive support for consuming RAG_Scraper output in your applications. It includes type definitions, schemas, documentation, and working examples for popular RAG frameworks.

### What's Included

- **JSON Schemas**: Complete validation schemas for all data structures
- **Type Definitions**: TypeScript and Python type definitions with full type safety
- **Documentation**: Comprehensive guides for entity relationships and API usage
- **Integration Examples**: Working code for LangChain, LlamaIndex, and custom implementations
- **Validation Tools**: Scripts to validate and verify your data

"""
    
    def _generate_quick_start(self) -> str:
        """Generate quick start section."""
        doc = self._format_header("Quick Start", 2)
        
        doc += self._format_header("Python", 3)
        doc += self._format_code_block("""
# Import the models
from models import RestaurantData, RestaurantDataReader

# Create a data reader
reader = RestaurantDataReader('path/to/output/restaurants')

# Get all restaurants
restaurants = reader.get_all_restaurants()

# Work with individual restaurants
for restaurant_dict in restaurants:
    # Convert to typed object
    restaurant = RestaurantData.from_dict(restaurant_dict)
    print(f"{restaurant.restaurant_name} - {restaurant.cuisine_type}")
    
    # Access relationships
    parent_rels = restaurant.get_parent_relationships()
    if parent_rels:
        print(f"  Parent: {parent_rels[0].entity_name}")
""")
        
        doc += self._format_header("TypeScript", 3)
        doc += self._format_code_block("""
// Import types
import { RestaurantData, BatchResult } from './types';

// Load and validate data
const restaurantJson = await fetch('/api/restaurant/rest_001');
const restaurant: RestaurantData = await restaurantJson.json();

// Type-safe access
console.log(`${restaurant.restaurant_name} - ${restaurant.cuisine_type}`);

// Work with relationships
const parentRels = restaurant.entity_relationships
  .filter(rel => rel.type === 'parent');
  
if (parentRels.length > 0) {
  console.log(`Parent: ${parentRels[0].entity_name}`);
}
""", "typescript")
        
        return doc
    
    def _generate_installation(self) -> str:
        """Generate installation section."""
        doc = self._format_header("Installation", 2)
        
        doc += self._format_header("Copy Type Definitions", 3)
        doc += """
1. **TypeScript**: Copy `types/typescript/index.d.ts` to your project
2. **Python**: Copy `types/python/models.py` or `models_pydantic.py` to your project

"""
        
        doc += self._format_header("Schema Validation", 3)
        doc += """
Use the JSON schemas for validation:

"""
        doc += self._format_code_block("""
# Python validation with jsonschema
import json
from jsonschema import validate

# Load schema
with open('schemas/restaurant_data.schema.json', 'r') as f:
    schema = json.load(f)

# Validate data
with open('your_data.json', 'r') as f:
    data = json.load(f)

validate(instance=data, schema=schema)
print("Data is valid!")
""")
        
        return doc
    
    def _generate_usage_examples(self) -> str:
        """Generate usage examples section."""
        doc = self._format_header("Usage Examples", 2)
        
        doc += self._format_header("Basic Data Access", 3)
        doc += self._format_code_block("""
from models import RestaurantDataReader
from pathlib import Path

# Initialize reader
reader = RestaurantDataReader(Path('output/restaurants'))

# Get restaurants by cuisine
italian_restaurants = reader.get_by_cuisine('Italian')
print(f"Found {len(italian_restaurants)} Italian restaurants")

# Search functionality
pizza_places = reader.search_restaurants('pizza')
for place in pizza_places:
    location = place['location']
    print(f"{place['name']} in {location['city']}, {location['state']}")

# Get full content
content = reader.get_restaurant_content('rest_001')
if content:
    print(f"Content length: {len(content)} characters")
""")
        
        doc += self._format_header("Working with Relationships", 3)
        doc += self._format_code_block("""
from models import RestaurantData, create_restaurant_from_dict

# Load restaurant data
restaurant_dict = reader.get_by_cuisine('Italian')[0]
restaurant = create_restaurant_from_dict(restaurant_dict)

# Access relationships
print(f"Restaurant: {restaurant.restaurant_name}")

# Get parent relationships
parents = restaurant.get_parent_relationships()
for parent in parents:
    print(f"  Parent: {parent.entity_name} ({parent.entity_type})")

# Get siblings (restaurants in same directory)
siblings = restaurant.get_sibling_relationships()
for sibling in siblings:
    print(f"  Sibling: {sibling.entity_name}")

# Check for menu items
if restaurant.has_menu_items():
    print(f"  Has {len(restaurant.menu_items)} menu items")
""")
        
        return doc
    
    def _generate_integration_examples(self) -> str:
        """Generate integration examples section."""
        doc = self._format_header("Integration Examples", 2)
        
        doc += """
Complete working examples are provided in the `examples/` directory:

"""
        
        examples = [
            ["LangChain", "`examples/langchain/integration.py`", "Complete RAG implementation with relationship-aware retrieval"],
            ["LlamaIndex", "`examples/llamaindex/integration.py`", "Index creation and querying with multi-page support"],
            ["Custom RAG", "`examples/custom/`", "Build your own RAG system with the provided types"]
        ]
        
        doc += self._format_table(
            ["Framework", "File", "Description"],
            examples
        )
        
        return doc
    
    def _generate_documentation_links(self) -> str:
        """Generate documentation links section."""
        doc = self._format_header("Documentation", 2)
        
        doc += """
- **Entity Relationships**: `docs/entity_relationships.md` - Understanding multi-page relationships
- **API Reference**: `docs/api_reference.md` - Complete API documentation  
- **Type Definitions**: `types/` - TypeScript and Python type definitions
- **Schemas**: `schemas/` - JSON schemas for validation

"""
        
        return doc
    
    def _generate_testing(self) -> str:
        """Generate testing section."""
        doc = self._format_header("Testing", 2)
        
        doc += """
Validate your data against the schemas:

"""
        doc += self._format_code_block("""
# Using the provided validation script
python tests/validate_schema.py path/to/your/data.json

# Using test data
python tests/validate_schema.py tests/test_data.json
""", "bash")
        
        return doc
    
    def _generate_version_info(self, package_info: Dict[str, Any]) -> str:
        """Generate version information section."""
        doc = self._format_header("Version Information", 2)
        
        doc += f"""
- **Package Version**: {package_info.get('version', '1.0.0')}
- **Schema Version**: {package_info.get('schema_version', '1.0.0')}
- **Compatible RAG_Scraper**: {package_info.get('scraper_version', '1.0.0')}+
- **Minimum Python**: {VERSION_INFO['min_python_version']}
- **Supported Frameworks**: {', '.join(VERSION_INFO['supported_frameworks'])}

"""
        
        return doc
    
    def _generate_support(self) -> str:
        """Generate support section."""
        return self._format_header("Support", 2) + """
For issues, questions, or contributions:

1. Check the documentation in the `docs/` directory
2. Review the examples in `examples/`
3. Validate your data with `tests/validate_schema.py`
4. Refer to the RAG_Scraper main documentation

## License

This integration package is provided as-is with the RAG_Scraper project.
"""