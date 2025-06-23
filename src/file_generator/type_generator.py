"""Type definition generators for different languages."""

from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from pathlib import Path

from .integration_config import (
    RelationshipType, VERSION_INFO, FILE_EXTENSIONS
)


class BaseTypeGenerator(ABC):
    """Base class for type generators."""
    
    def __init__(self, version: str = "1.0.0"):
        self.version = version
        self.generated_types: List[str] = []
    
    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate type definitions."""
        pass
    
    def _format_header(self, title: str, description: str) -> str:
        """Generate header comment."""
        return f"""// {title}
// {description}
// Generated version: {self.version}

"""


class TypeScriptGenerator(BaseTypeGenerator):
    """Generator for TypeScript type definitions."""
    
    def generate(self, **kwargs) -> str:
        """Generate TypeScript type definitions."""
        output = self._format_header(
            "TypeScript type definitions for RAG_Scraper output",
            "Generated for multi-page restaurant data extraction"
        )
        
        # Generate types
        output += self._generate_enums()
        output += self._generate_interfaces()
        output += self._generate_utility_types()
        output += self._generate_type_guards()
        output += self._generate_exports()
        
        return output
    
    def _generate_enums(self) -> str:
        """Generate enum type definitions."""
        return f"""export type RelationshipType = {' | '.join(f"'{rel.value}'" for rel in RelationshipType)};

export type ChunkingMethod = 'semantic' | 'fixed' | 'sentence' | 'paragraph';

export type PreservationStrategy = 'full' | 'summary' | 'keywords' | 'hybrid';

export type AggregationMethod = 'hierarchical' | 'flat' | 'graph' | 'hybrid';

"""
    
    def _generate_interfaces(self) -> str:
        """Generate interface definitions."""
        return """export interface Location {
  address?: string;
  city: string;
  state?: string;
  zip?: string;
  country?: string;
}

export interface MenuItem {
  name: string;
  description?: string;
  price?: number;
  category?: string;
}

export interface EntityRelationship {
  type: RelationshipType;
  entity_id: string;
  entity_type: string;
  entity_name?: string;
}

export interface SemanticChunk {
  chunk_id: string;
  content: string;
  metadata: Record<string, any>;
  embedding_hints?: string[];
}

export interface CrossReference {
  ref_id: string;
  ref_type: string;
  ref_name?: string;
  ref_url?: string;
}

export interface RestaurantData {
  restaurant_id: string;
  restaurant_name: string;
  cuisine_type: string;
  location: Location;
  menu_items?: MenuItem[];
  extraction_timestamp: string;
  source_url: string;
  parent_page_url?: string;
  entity_relationships: EntityRelationship[];
  semantic_chunks: SemanticChunk[];
  cross_references: CrossReference[];
  description?: string;
  [key: string]: any; // Allow additional properties
}

export interface ExtractionMetadata {
  extraction_id: string;
  start_timestamp: string;
  end_timestamp: string;
  total_pages: number;
  successful_pages: number;
  failed_pages: number;
  extraction_config: Record<string, any>;
}

export interface BatchResult {
  restaurants: RestaurantData[];
  metadata: ExtractionMetadata;
  errors: ExtractionError[];
}

export interface ExtractionError {
  url: string;
  error: string;
  timestamp: string;
}

export interface RAGConfig {
  chunk_settings: ChunkSettings;
  embedding_hints?: EmbeddingSettings;
  context_settings?: ContextSettings;
  multi_page_settings?: MultiPageSettings;
  custom_settings?: Record<string, any>;
}

export interface ChunkSettings {
  max_chunk_size: number;
  overlap_size: number;
  chunking_method: ChunkingMethod;
  preserve_context: boolean;
}

export interface EmbeddingSettings {
  keyword_extraction: boolean;
  entity_recognition: boolean;
  max_keywords: number;
  include_metadata: boolean;
}

export interface ContextSettings {
  context_window: number;
  preservation_strategy: PreservationStrategy;
  include_parent_context: boolean;
}

export interface MultiPageSettings {
  relationship_depth: number;
  aggregation_method: AggregationMethod;
  deduplication: boolean;
  cross_reference_limit: number;
}

"""
    
    def _generate_utility_types(self) -> str:
        """Generate utility types."""
        return """// Utility types for common operations
export type RestaurantId = string;
export type EntityId = string;
export type ChunkId = string;

export type PartialRestaurantData = Partial<RestaurantData>;
export type RequiredRestaurantFields = Pick<RestaurantData, 'restaurant_id' | 'restaurant_name' | 'cuisine_type'>;

// Query types
export interface RestaurantQuery {
  cuisine_type?: string;
  location?: Partial<Location>;
  has_menu?: boolean;
  keywords?: string[];
}

export interface RelationshipQuery {
  type?: RelationshipType;
  entity_type?: string;
  depth?: number;
}

"""
    
    def _generate_type_guards(self) -> str:
        """Generate type guard functions."""
        return """// Type guards for runtime type checking
export function isRestaurantData(data: any): data is RestaurantData {
  return (
    typeof data === 'object' &&
    data !== null &&
    typeof data.restaurant_id === 'string' &&
    typeof data.restaurant_name === 'string' &&
    typeof data.cuisine_type === 'string' &&
    Array.isArray(data.entity_relationships) &&
    Array.isArray(data.semantic_chunks)
  );
}

export function isBatchResult(data: any): data is BatchResult {
  return (
    typeof data === 'object' &&
    data !== null &&
    Array.isArray(data.restaurants) &&
    typeof data.metadata === 'object' &&
    Array.isArray(data.errors)
  );
}

export function isValidRelationshipType(type: string): type is RelationshipType {
  return ['parent', 'child', 'sibling', 'reference'].includes(type);
}

export function hasValidLocation(restaurant: RestaurantData): boolean {
  return restaurant.location && typeof restaurant.location.city === 'string';
}

"""
    
    def _generate_exports(self) -> str:
        """Generate export statements."""
        return """// Export all types
export type {
  RelationshipType,
  ChunkingMethod,
  PreservationStrategy,
  AggregationMethod,
  Location,
  MenuItem,
  EntityRelationship,
  SemanticChunk,
  CrossReference,
  RestaurantData,
  ExtractionMetadata,
  BatchResult,
  ExtractionError,
  RAGConfig,
  ChunkSettings,
  EmbeddingSettings,
  ContextSettings,
  MultiPageSettings,
  RestaurantId,
  EntityId,
  ChunkId,
  PartialRestaurantData,
  RequiredRestaurantFields,
  RestaurantQuery,
  RelationshipQuery
};

// Default export
export default RestaurantData;
"""


class PythonDataclassGenerator(BaseTypeGenerator):
    """Generator for Python dataclass type definitions."""
    
    def generate(self, **kwargs) -> str:
        """Generate Python dataclass definitions."""
        output = self._format_header(
            "Python dataclass definitions for RAG_Scraper output",
            "Generated for multi-page restaurant data extraction"
        )
        
        output += self._generate_imports()
        output += self._generate_enums()
        output += self._generate_dataclasses()
        output += self._generate_utility_functions()
        output += self._generate_exports()
        
        return output
    
    def _format_header(self, title: str, description: str) -> str:
        """Generate header comment for Python."""
        return f'''"""
{title}
{description}
Generated version: {self.version}
"""

'''
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return """from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Literal, Union
from datetime import datetime
from enum import Enum

"""
    
    def _generate_enums(self) -> str:
        """Generate enum definitions."""
        return """class RelationshipType(Enum):
    \"\"\"Types of entity relationships.\"\"\"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    REFERENCE = "reference"


class ChunkingMethod(Enum):
    \"\"\"Methods for content chunking.\"\"\"
    SEMANTIC = "semantic"
    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"


class PreservationStrategy(Enum):
    \"\"\"Strategies for context preservation.\"\"\"
    FULL = "full"
    SUMMARY = "summary"
    KEYWORDS = "keywords"
    HYBRID = "hybrid"


class AggregationMethod(Enum):
    \"\"\"Methods for multi-page data aggregation.\"\"\"
    HIERARCHICAL = "hierarchical"
    FLAT = "flat"
    GRAPH = "graph"
    HYBRID = "hybrid"


"""
    
    def _generate_dataclasses(self) -> str:
        """Generate dataclass definitions."""
        return """@dataclass
class Location:
    \"\"\"Restaurant location information.\"\"\"
    city: str
    address: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None


@dataclass
class MenuItem:
    \"\"\"Restaurant menu item.\"\"\"
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


@dataclass
class EntityRelationship:
    \"\"\"Relationship to another entity.\"\"\"
    type: RelationshipType
    entity_id: str
    entity_type: str
    entity_name: Optional[str] = None
    
    def __post_init__(self):
        \"\"\"Validate relationship after initialization.\"\"\"
        if isinstance(self.type, str):
            self.type = RelationshipType(self.type)


@dataclass
class SemanticChunk:
    \"\"\"RAG-optimized content chunk.\"\"\"
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding_hints: List[str] = field(default_factory=list)


@dataclass
class CrossReference:
    \"\"\"Cross-reference to related entity.\"\"\"
    ref_id: str
    ref_type: str
    ref_name: Optional[str] = None
    ref_url: Optional[str] = None


@dataclass
class RestaurantData:
    \"\"\"Complete restaurant data with multi-page support.\"\"\"
    restaurant_id: str
    restaurant_name: str
    cuisine_type: str
    location: Location
    extraction_timestamp: str
    source_url: str
    entity_relationships: List[EntityRelationship] = field(default_factory=list)
    semantic_chunks: List[SemanticChunk] = field(default_factory=list)
    cross_references: List[CrossReference] = field(default_factory=list)
    menu_items: List[MenuItem] = field(default_factory=list)
    parent_page_url: Optional[str] = None
    description: Optional[str] = None
    additional_fields: Dict[str, Any] = field(default_factory=dict)
    
    def get_parent_relationships(self) -> List[EntityRelationship]:
        \"\"\"Get all parent relationships.\"\"\"
        return [rel for rel in self.entity_relationships if rel.type == RelationshipType.PARENT]
    
    def get_child_relationships(self) -> List[EntityRelationship]:
        \"\"\"Get all child relationships.\"\"\"
        return [rel for rel in self.entity_relationships if rel.type == RelationshipType.CHILD]
    
    def get_sibling_relationships(self) -> List[EntityRelationship]:
        \"\"\"Get all sibling relationships.\"\"\"
        return [rel for rel in self.entity_relationships if rel.type == RelationshipType.SIBLING]
    
    def has_menu_items(self) -> bool:
        \"\"\"Check if restaurant has menu items.\"\"\"
        return len(self.menu_items) > 0


@dataclass
class ExtractionMetadata:
    \"\"\"Metadata about the extraction process.\"\"\"
    extraction_id: str
    start_timestamp: str
    end_timestamp: str
    total_pages: int
    successful_pages: int
    failed_pages: int
    extraction_config: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        \"\"\"Calculate success rate.\"\"\"
        if self.total_pages == 0:
            return 0.0
        return self.successful_pages / self.total_pages
    
    @property
    def duration_seconds(self) -> Optional[float]:
        \"\"\"Calculate extraction duration in seconds.\"\"\"
        try:
            start = datetime.fromisoformat(self.start_timestamp.replace('Z', '+00:00'))
            end = datetime.fromisoformat(self.end_timestamp.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except ValueError:
            return None


@dataclass
class ExtractionError:
    \"\"\"Error during extraction.\"\"\"
    url: str
    error: str
    timestamp: str


@dataclass
class BatchResult:
    \"\"\"Result of batch processing multiple restaurants.\"\"\"
    restaurants: List[RestaurantData]
    metadata: ExtractionMetadata
    errors: List[ExtractionError] = field(default_factory=list)
    
    def get_by_cuisine(self, cuisine: str) -> List[RestaurantData]:
        \"\"\"Get restaurants by cuisine type.\"\"\"
        return [r for r in self.restaurants if r.cuisine_type.lower() == cuisine.lower()]
    
    def get_by_location(self, city: str, state: Optional[str] = None) -> List[RestaurantData]:
        \"\"\"Get restaurants by location.\"\"\"
        results = [r for r in self.restaurants if r.location.city.lower() == city.lower()]
        if state:
            results = [r for r in results if r.location.state and r.location.state.lower() == state.lower()]
        return results


@dataclass
class ChunkSettings:
    \"\"\"Settings for semantic chunking.\"\"\"
    max_chunk_size: int = 1000
    overlap_size: int = 100
    chunking_method: ChunkingMethod = ChunkingMethod.SEMANTIC
    preserve_context: bool = True
    
    def __post_init__(self):
        \"\"\"Validate settings after initialization.\"\"\"
        if isinstance(self.chunking_method, str):
            self.chunking_method = ChunkingMethod(self.chunking_method)


@dataclass
class EmbeddingSettings:
    \"\"\"Settings for embedding optimization.\"\"\"
    keyword_extraction: bool = True
    entity_recognition: bool = True
    max_keywords: int = 10
    include_metadata: bool = True


@dataclass
class ContextSettings:
    \"\"\"Settings for context preservation.\"\"\"
    context_window: int = 2000
    preservation_strategy: PreservationStrategy = PreservationStrategy.HYBRID
    include_parent_context: bool = True
    
    def __post_init__(self):
        \"\"\"Validate settings after initialization.\"\"\"
        if isinstance(self.preservation_strategy, str):
            self.preservation_strategy = PreservationStrategy(self.preservation_strategy)


@dataclass
class MultiPageSettings:
    \"\"\"Settings for multi-page processing.\"\"\"
    relationship_depth: int = 2
    aggregation_method: AggregationMethod = AggregationMethod.HIERARCHICAL
    deduplication: bool = True
    cross_reference_limit: int = 10
    
    def __post_init__(self):
        \"\"\"Validate settings after initialization.\"\"\"
        if isinstance(self.aggregation_method, str):
            self.aggregation_method = AggregationMethod(self.aggregation_method)


@dataclass
class RAGConfig:
    \"\"\"Complete RAG configuration.\"\"\"
    chunk_settings: ChunkSettings
    embedding_hints: Optional[EmbeddingSettings] = None
    context_settings: Optional[ContextSettings] = None
    multi_page_settings: Optional[MultiPageSettings] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        \"\"\"Set defaults if not provided.\"\"\"
        if self.embedding_hints is None:
            self.embedding_hints = EmbeddingSettings()
        if self.context_settings is None:
            self.context_settings = ContextSettings()
        if self.multi_page_settings is None:
            self.multi_page_settings = MultiPageSettings()


"""
    
    def _generate_utility_functions(self) -> str:
        """Generate utility functions."""
        return """# Type aliases for convenience
RestaurantId = str
EntityId = str
ChunkId = str
RestaurantDict = Dict[str, Any]
RestaurantList = List[RestaurantData]


# Utility functions
def validate_restaurant_data(data: Dict[str, Any]) -> bool:
    \"\"\"Validate restaurant data dictionary.\"\"\"
    required_fields = ['restaurant_id', 'restaurant_name', 'cuisine_type', 'extraction_timestamp', 'source_url']
    return all(field in data for field in required_fields)


def create_restaurant_from_dict(data: Dict[str, Any]) -> RestaurantData:
    \"\"\"Create RestaurantData from dictionary.\"\"\"
    # Convert location
    location_data = data.get('location', {})
    location = Location(**location_data) if location_data else Location(city="Unknown")
    
    # Convert relationships
    relationships = []
    for rel_data in data.get('entity_relationships', []):
        relationships.append(EntityRelationship(**rel_data))
    
    # Convert chunks
    chunks = []
    for chunk_data in data.get('semantic_chunks', []):
        chunks.append(SemanticChunk(**chunk_data))
    
    # Convert cross references
    cross_refs = []
    for ref_data in data.get('cross_references', []):
        cross_refs.append(CrossReference(**ref_data))
    
    # Convert menu items
    menu_items = []
    for item_data in data.get('menu_items', []):
        menu_items.append(MenuItem(**item_data))
    
    return RestaurantData(
        restaurant_id=data['restaurant_id'],
        restaurant_name=data['restaurant_name'],
        cuisine_type=data['cuisine_type'],
        location=location,
        extraction_timestamp=data['extraction_timestamp'],
        source_url=data['source_url'],
        entity_relationships=relationships,
        semantic_chunks=chunks,
        cross_references=cross_refs,
        menu_items=menu_items,
        parent_page_url=data.get('parent_page_url'),
        description=data.get('description'),
        additional_fields=data.get('additional_fields', {})
    )


def restaurant_to_dict(restaurant: RestaurantData) -> Dict[str, Any]:
    \"\"\"Convert RestaurantData to dictionary.\"\"\"
    return {
        'restaurant_id': restaurant.restaurant_id,
        'restaurant_name': restaurant.restaurant_name,
        'cuisine_type': restaurant.cuisine_type,
        'location': {
            'city': restaurant.location.city,
            'address': restaurant.location.address,
            'state': restaurant.location.state,
            'zip': restaurant.location.zip,
            'country': restaurant.location.country
        },
        'extraction_timestamp': restaurant.extraction_timestamp,
        'source_url': restaurant.source_url,
        'parent_page_url': restaurant.parent_page_url,
        'description': restaurant.description,
        'entity_relationships': [
            {
                'type': rel.type.value,
                'entity_id': rel.entity_id,
                'entity_type': rel.entity_type,
                'entity_name': rel.entity_name
            } for rel in restaurant.entity_relationships
        ],
        'semantic_chunks': [
            {
                'chunk_id': chunk.chunk_id,
                'content': chunk.content,
                'metadata': chunk.metadata,
                'embedding_hints': chunk.embedding_hints
            } for chunk in restaurant.semantic_chunks
        ],
        'cross_references': [
            {
                'ref_id': ref.ref_id,
                'ref_type': ref.ref_type,
                'ref_name': ref.ref_name,
                'ref_url': ref.ref_url
            } for ref in restaurant.cross_references
        ],
        'menu_items': [
            {
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category': item.category
            } for item in restaurant.menu_items
        ],
        **restaurant.additional_fields
    }


"""
    
    def _generate_exports(self) -> str:
        """Generate export statements."""
        return """# Export all classes and functions
__all__ = [
    # Enums
    "RelationshipType",
    "ChunkingMethod", 
    "PreservationStrategy",
    "AggregationMethod",
    
    # Main data classes
    "Location",
    "MenuItem",
    "EntityRelationship",
    "SemanticChunk",
    "CrossReference",
    "RestaurantData",
    "ExtractionMetadata",
    "ExtractionError",
    "BatchResult",
    
    # Configuration classes
    "ChunkSettings",
    "EmbeddingSettings",
    "ContextSettings",
    "MultiPageSettings",
    "RAGConfig",
    
    # Type aliases
    "RestaurantId",
    "EntityId",
    "ChunkId",
    "RestaurantDict",
    "RestaurantList",
    
    # Utility functions
    "validate_restaurant_data",
    "create_restaurant_from_dict",
    "restaurant_to_dict"
]
"""


class PydanticGenerator(PythonDataclassGenerator):
    """Generator for Pydantic model type definitions."""
    
    def _generate_imports(self) -> str:
        """Generate import statements for Pydantic."""
        return """from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, Dict, Optional, Any, Literal, Union
from datetime import datetime
from enum import Enum

"""
    
    def _generate_dataclasses(self) -> str:
        """Generate Pydantic model definitions."""
        return """class Location(BaseModel):
    \"\"\"Restaurant location information.\"\"\"
    model_config = ConfigDict(extra="allow")
    
    city: str
    address: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = Field(None, pattern=r"^\\d{5}(-\\d{4})?$")
    country: Optional[str] = None


class MenuItem(BaseModel):
    \"\"\"Restaurant menu item.\"\"\"
    name: str
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None


class EntityRelationship(BaseModel):
    \"\"\"Relationship to another entity.\"\"\"
    type: RelationshipType
    entity_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")
    entity_type: str
    entity_name: Optional[str] = None
    
    @field_validator('type', mode='before')
    def validate_type(cls, v):
        if isinstance(v, str):
            return RelationshipType(v)
        return v


class SemanticChunk(BaseModel):
    \"\"\"RAG-optimized content chunk.\"\"\"
    chunk_id: str
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding_hints: List[str] = Field(default_factory=list)


class CrossReference(BaseModel):
    \"\"\"Cross-reference to related entity.\"\"\"
    ref_id: str
    ref_type: str
    ref_name: Optional[str] = None
    ref_url: Optional[str] = Field(None, pattern=r"^https?://")


class RestaurantData(BaseModel):
    \"\"\"Complete restaurant data with multi-page support.\"\"\"
    model_config = ConfigDict(extra="allow")
    
    restaurant_id: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")
    restaurant_name: str = Field(..., min_length=1)
    cuisine_type: str
    location: Location
    extraction_timestamp: str = Field(..., pattern=r"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}")
    source_url: str = Field(..., pattern=r"^https?://")
    entity_relationships: List[EntityRelationship] = Field(default_factory=list)
    semantic_chunks: List[SemanticChunk] = Field(default_factory=list)
    cross_references: List[CrossReference] = Field(default_factory=list)
    menu_items: List[MenuItem] = Field(default_factory=list)
    parent_page_url: Optional[str] = Field(None, pattern=r"^https?://")
    description: Optional[str] = None
    
    def get_parent_relationships(self) -> List[EntityRelationship]:
        \"\"\"Get all parent relationships.\"\"\"
        return [rel for rel in self.entity_relationships if rel.type == RelationshipType.PARENT]
    
    def get_child_relationships(self) -> List[EntityRelationship]:
        \"\"\"Get all child relationships.\"\"\"
        return [rel for rel in self.entity_relationships if rel.type == RelationshipType.CHILD]
    
    @field_validator('entity_relationships', mode='before')
    def validate_relationships(cls, v):
        if isinstance(v, list):
            return [EntityRelationship(**item) if isinstance(item, dict) else item for item in v]
        return v


class ExtractionMetadata(BaseModel):
    \"\"\"Metadata about the extraction process.\"\"\"
    extraction_id: str
    start_timestamp: str
    end_timestamp: str
    total_pages: int = Field(..., ge=0)
    successful_pages: int = Field(..., ge=0)
    failed_pages: int = Field(..., ge=0)
    extraction_config: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_page_counts(self):
        if self.successful_pages + self.failed_pages != self.total_pages:
            raise ValueError("successful_pages + failed_pages must equal total_pages")
        return self
    
    @property
    def success_rate(self) -> float:
        \"\"\"Calculate success rate.\"\"\"
        if self.total_pages == 0:
            return 0.0
        return self.successful_pages / self.total_pages


class ExtractionError(BaseModel):
    \"\"\"Error during extraction.\"\"\"
    url: str = Field(..., pattern=r"^https?://")
    error: str
    timestamp: str


class BatchResult(BaseModel):
    \"\"\"Result of batch processing multiple restaurants.\"\"\"
    restaurants: List[RestaurantData]
    metadata: ExtractionMetadata
    errors: List[ExtractionError] = Field(default_factory=list)
    
    def get_by_cuisine(self, cuisine: str) -> List[RestaurantData]:
        \"\"\"Get restaurants by cuisine type.\"\"\"
        return [r for r in self.restaurants if r.cuisine_type.lower() == cuisine.lower()]


class ChunkSettings(BaseModel):
    \"\"\"Settings for semantic chunking.\"\"\"
    max_chunk_size: int = Field(1000, ge=100, le=5000)
    overlap_size: int = Field(100, ge=0, le=500)
    chunking_method: ChunkingMethod = ChunkingMethod.SEMANTIC
    preserve_context: bool = True
    
    @field_validator('chunking_method', mode='before')
    def validate_chunking_method(cls, v):
        if isinstance(v, str):
            return ChunkingMethod(v)
        return v


class EmbeddingSettings(BaseModel):
    \"\"\"Settings for embedding optimization.\"\"\"
    keyword_extraction: bool = True
    entity_recognition: bool = True
    max_keywords: int = Field(10, ge=1, le=50)
    include_metadata: bool = True


class ContextSettings(BaseModel):
    \"\"\"Settings for context preservation.\"\"\"
    context_window: int = Field(2000, ge=500, le=10000)
    preservation_strategy: PreservationStrategy = PreservationStrategy.HYBRID
    include_parent_context: bool = True
    
    @field_validator('preservation_strategy', mode='before')
    def validate_preservation_strategy(cls, v):
        if isinstance(v, str):
            return PreservationStrategy(v)
        return v


class MultiPageSettings(BaseModel):
    \"\"\"Settings for multi-page processing.\"\"\"
    relationship_depth: int = Field(2, ge=1, le=5)
    aggregation_method: AggregationMethod = AggregationMethod.HIERARCHICAL
    deduplication: bool = True
    cross_reference_limit: int = Field(10, ge=0, le=100)
    
    @field_validator('aggregation_method', mode='before')
    def validate_aggregation_method(cls, v):
        if isinstance(v, str):
            return AggregationMethod(v)
        return v


class RAGConfig(BaseModel):
    \"\"\"Complete RAG configuration.\"\"\"
    chunk_settings: ChunkSettings
    embedding_hints: Optional[EmbeddingSettings] = Field(default_factory=EmbeddingSettings)
    context_settings: Optional[ContextSettings] = Field(default_factory=ContextSettings)
    multi_page_settings: Optional[MultiPageSettings] = Field(default_factory=MultiPageSettings)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


"""