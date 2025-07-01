"""Main semantic structurer for converting extracted data into RAG-ready format."""

import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum


# Constants for Clean Code
class SemanticConstants:
    """Constants for semantic structuring configuration."""
    
    DEFAULT_CHUNK_SIZE = 512
    DEFAULT_OVERLAP_SIZE = 50
    MINIMUM_CONTENT_LENGTH_FOR_PERIOD = 20
    MAXIMUM_HIERARCHY_DEPTH = 3
    SENTENCE_TERMINATORS = ('.', '!', '?')
    SCHEMA_VERSION = "1.0"
    
    # Expected restaurant data fields
    EXPECTED_RESTAURANT_FIELDS = {
        "name", "description", "cuisine", "price_range", 
        "location", "hours", "contact", "menu"
    }
    
    EXPECTED_LOCATION_FIELDS = {"address", "city", "state", "zip", "coordinates"}
    EXPECTED_CONTACT_FIELDS = {"phone", "email", "website"}


class TemporalType(Enum):
    """Types of temporal data."""
    RECURRING_SCHEDULE = "recurring_schedule"
    SPECIFIC_DATE = "specific_date"


class ChunkType(Enum):
    """Types of chunks."""
    TEXT = "text"
    STRUCTURED = "structured"
    LIST = "list"
    TEMPORAL = "temporal"
    SUMMARY = "summary"
    DETAIL = "detail"
    PARENT = "parent"
    CHILD = "child"
    CHILD_PARENT = "child_parent"
    IMAGE = "image"
    PDF = "pdf"


@dataclass
class ChunkingConfig:
    """Configuration for chunking operations."""
    chunk_size: int = SemanticConstants.DEFAULT_CHUNK_SIZE
    overlap_size: int = SemanticConstants.DEFAULT_OVERLAP_SIZE
    enable_summaries: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class SemanticResult:
    """Result of semantic structuring process."""
    
    chunks: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    relationships: List[Dict[str, Any]]
    processing_time: float
    
    def __post_init__(self):
        """Validate the semantic result."""
        self._validate_chunks()
        self._validate_relationships()
        self._validate_processing_time()
    
    def _validate_chunks(self):
        """Validate chunks are a list."""
        if not isinstance(self.chunks, list):
            raise TypeError("chunks must be a list")
    
    def _validate_relationships(self):
        """Validate relationships are a list."""
        if not isinstance(self.relationships, list):
            raise TypeError("relationships must be a list")
    
    def _validate_processing_time(self):
        """Validate processing time is non-negative."""
        if self.processing_time < 0:
            raise ValueError("processing_time must be non-negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ChunkFactory:
    """Factory for creating different types of chunks."""
    
    @staticmethod
    def create_text_chunk(chunk_id: str, content: str, source_field: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a text chunk."""
        return {
            "id": chunk_id,
            "content": content,
            "type": ChunkType.TEXT.value,
            "source_field": source_field,
            "metadata": metadata or {}
        }
    
    @staticmethod
    def create_structured_chunk(chunk_id: str, content: str, source_field: str,
                               parent_field: str, nested_key: str) -> Dict[str, Any]:
        """Create a structured chunk."""
        return {
            "id": chunk_id,
            "content": content,
            "type": ChunkType.STRUCTURED.value,
            "source_field": source_field,
            "metadata": {
                "parent_field": parent_field,
                "nested_key": nested_key,
                "chunk_type": parent_field
            }
        }
    
    @staticmethod
    def create_list_chunk(chunk_id: str, content: str, source_field: str,
                         item_count: int, chunk_index: Optional[int] = None) -> Dict[str, Any]:
        """Create a list chunk."""
        metadata = {
            "item_count": item_count,
            "chunk_type": source_field
        }
        if chunk_index is not None:
            metadata["chunk_index"] = chunk_index
            
        return {
            "id": chunk_id,
            "content": content,
            "type": ChunkType.LIST.value,
            "source_field": source_field,
            "metadata": metadata
        }


class ContentProcessor:
    """Processes different types of content into chunks."""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
    
    def ensure_sentence_termination(self, content: str) -> str:
        """Ensure content ends with proper sentence termination."""
        content = content.strip()
        
        if (len(content) > SemanticConstants.MINIMUM_CONTENT_LENGTH_FOR_PERIOD and 
            not content.endswith(SemanticConstants.SENTENCE_TERMINATORS)):
            content += '.'
            
        return content
    
    def split_into_words(self, text: str) -> List[str]:
        """Split text into words."""
        return text.split()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using simple regex."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def find_sentence_boundary(self, words: List[str], start_index: int) -> int:
        """Find the best sentence boundary within the overlap window."""
        overlap_limit = min(self.config.overlap_size, len(words) - start_index - 1)
        
        for j in range(overlap_limit, 0, -1):
            word_index = start_index + len(words) - j
            if word_index < len(words) and words[word_index].endswith(SemanticConstants.SENTENCE_TERMINATORS):
                return word_index + 1
        
        return len(words)  # No sentence boundary found


class SemanticStructurer:
    """Main semantic structurer for RAG systems."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize semantic structurer."""
        self.config = self._create_config(config)
        self.content_processor = ContentProcessor(self.config)
        self.chunk_factory = ChunkFactory()
        
        # Backward compatibility attributes
        self.chunk_size = self.config.chunk_size
        self.overlap_size = self.config.overlap_size
        self.enable_summaries = self.config.enable_summaries
    
    def _create_config(self, config_dict: Optional[Dict[str, Any]]) -> ChunkingConfig:
        """Create chunking configuration from dictionary."""
        if not config_dict:
            return ChunkingConfig()
        
        return ChunkingConfig(
            chunk_size=config_dict.get('chunk_size', SemanticConstants.DEFAULT_CHUNK_SIZE),
            overlap_size=config_dict.get('overlap_size', SemanticConstants.DEFAULT_OVERLAP_SIZE),
            enable_summaries=config_dict.get('enable_summaries', True)
        )
    
    def structure_for_rag(self, data: Dict[str, Any], 
                         enrich_metadata: bool = False,
                         config: Optional[Dict[str, Any]] = None,
                         handle_missing: bool = False) -> Dict[str, Any]:
        """Structure data for RAG consumption."""
        start_time = time.time()
        
        processing_config = self._resolve_processing_config(config)
        chunks = self._create_all_chunks(data, processing_config)
        
        self._apply_post_processing(chunks, data, enrich_metadata, handle_missing, config)
        
        relationships = self._create_basic_relationships(chunks, data)
        metadata = self._create_result_metadata(data, len(chunks))
        
        processing_time = time.time() - start_time
        
        return {
            "chunks": chunks,
            "metadata": metadata,
            "relationships": relationships,
            "processing_time": processing_time
        }
    
    def _resolve_processing_config(self, config: Optional[Dict[str, Any]]) -> ChunkingConfig:
        """Resolve the configuration to use for processing."""
        if config:
            return self._create_config(config)
        return self.config
    
    def _create_all_chunks(self, data: Dict[str, Any], config: ChunkingConfig) -> List[Dict[str, Any]]:
        """Create chunks for all data types."""
        chunks = []
        chunk_id_counter = 1
        
        for key, value in data.items():
            if self._should_skip_field(key):
                continue
                
            new_chunks, chunk_id_counter = self._process_field(
                key, value, config.chunk_size, chunk_id_counter
            )
            chunks.extend(new_chunks)
        
        return chunks
    
    def _should_skip_field(self, key: str) -> bool:
        """Check if field should be skipped during processing."""
        return key.startswith('_')
    
    def _process_field(self, key: str, value: Any, chunk_size: int, 
                      chunk_id_counter: int) -> Tuple[List[Dict[str, Any]], int]:
        """Process a single field based on its value type."""
        if isinstance(value, str):
            chunks = self._create_text_chunks(value, key, chunk_size, chunk_id_counter)
        elif isinstance(value, dict):
            chunks = self._create_nested_chunks(value, key, chunk_size, chunk_id_counter)
        elif isinstance(value, list):
            chunks = self._create_list_chunks(value, key, chunk_size, chunk_id_counter)
        else:
            chunks = []
        
        return chunks, chunk_id_counter + len(chunks)
    
    def _apply_post_processing(self, chunks: List[Dict[str, Any]], data: Dict[str, Any],
                              enrich_metadata: bool, handle_missing: bool, 
                              config: Optional[Dict[str, Any]]):
        """Apply post-processing steps to chunks."""
        if handle_missing:
            self._handle_missing_data(chunks, data)
        
        if enrich_metadata:
            self._enrich_all_chunks(chunks, data)
        
        if config:
            self._store_config_in_chunks(chunks, config)
    
    def _enrich_all_chunks(self, chunks: List[Dict[str, Any]], data: Dict[str, Any]):
        """Enrich metadata for all chunks."""
        for chunk in chunks:
            self._enrich_chunk_metadata(chunk, data)
    
    def _store_config_in_chunks(self, chunks: List[Dict[str, Any]], config: Dict[str, Any]):
        """Store configuration in chunk metadata."""
        for chunk in chunks:
            chunk.setdefault("metadata", {})["chunk_config"] = config
    
    def _create_result_metadata(self, data: Dict[str, Any], chunk_count: int) -> Dict[str, Any]:
        """Create metadata for the result."""
        return {
            "version": SemanticConstants.SCHEMA_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_count": chunk_count,
            "source_type": "restaurant",
            "entity_name": data.get("name", "Unknown")
        }
    
    def _create_text_chunks(self, text: str, field_name: str, 
                           chunk_size: int, start_id: int) -> List[Dict[str, Any]]:
        """Create chunks from text content."""
        words = self.content_processor.split_into_words(text)
        
        if self._is_single_chunk(words, chunk_size):
            return self._create_single_text_chunk(text, field_name, words, start_id)
        else:
            return self._create_multiple_text_chunks(words, field_name, chunk_size, start_id)
    
    def _is_single_chunk(self, words: List[str], chunk_size: int) -> bool:
        """Check if content fits in a single chunk."""
        return len(words) <= chunk_size
    
    def _create_single_text_chunk(self, text: str, field_name: str, 
                                 words: List[str], start_id: int) -> List[Dict[str, Any]]:
        """Create a single text chunk."""
        content = self.content_processor.ensure_sentence_termination(text)
        
        chunk = self.chunk_factory.create_text_chunk(
            chunk_id=f"chunk_{start_id}",
            content=content,
            source_field=field_name,
            metadata={
                "word_count": len(words),
                "chunk_type": field_name
            }
        )
        
        return [chunk]
    
    def _create_multiple_text_chunks(self, words: List[str], field_name: str,
                                    chunk_size: int, start_id: int) -> List[Dict[str, Any]]:
        """Create multiple text chunks from long content."""
        chunks = []
        chunk_num = 0
        
        for i in range(0, len(words), chunk_size):
            chunk_words = self._get_chunk_words(words, i, chunk_size)
            content = ' '.join(chunk_words)
            
            chunk = self.chunk_factory.create_text_chunk(
                chunk_id=f"chunk_{start_id + chunk_num}",
                content=content,
                source_field=field_name,
                metadata={
                    "word_count": len(chunk_words),
                    "chunk_type": field_name,
                    "chunk_index": chunk_num
                }
            )
            
            chunks.append(chunk)
            chunk_num += 1
        
        return chunks
    
    def _get_chunk_words(self, words: List[str], start_index: int, chunk_size: int) -> List[str]:
        """Get words for a chunk, respecting sentence boundaries."""
        chunk_words = words[start_index:start_index + chunk_size]
        
        # Don't break mid-sentence if not at end
        if (start_index + chunk_size < len(words) and 
            not chunk_words[-1].endswith(SemanticConstants.SENTENCE_TERMINATORS)):
            
            boundary = self.content_processor.find_sentence_boundary(chunk_words, 0)
            if boundary < len(chunk_words):
                chunk_words = chunk_words[:boundary]
        
        return chunk_words
    
    def _create_nested_chunks(self, nested_data: Dict[str, Any], 
                             parent_field: str, chunk_size: int, 
                             start_id: int) -> List[Dict[str, Any]]:
        """Create chunks from nested dictionary data."""
        chunks = []
        chunk_id = start_id
        
        for key, value in nested_data.items():
            content = self._format_nested_content(key, value)
            
            chunk = self.chunk_factory.create_structured_chunk(
                chunk_id=f"chunk_{chunk_id}",
                content=content,
                source_field=f"{parent_field}.{key}",
                parent_field=parent_field,
                nested_key=key
            )
            
            chunks.append(chunk)
            chunk_id += 1
        
        return chunks
    
    def _format_nested_content(self, key: str, value: Any) -> str:
        """Format nested content into readable string."""
        if isinstance(value, str):
            return f"{key}: {value}"
        elif isinstance(value, list):
            return f"{key}: {', '.join(str(v) for v in value)}"
        else:
            return f"{key}: {str(value)}"
    
    def _create_list_chunks(self, list_data: List[Any], field_name: str,
                           chunk_size: int, start_id: int) -> List[Dict[str, Any]]:
        """Create chunks from list data."""
        if self._is_small_list(list_data, chunk_size):
            return self._create_single_list_chunk(list_data, field_name, start_id)
        else:
            return self._create_multiple_list_chunks(list_data, field_name, chunk_size, start_id)
    
    def _is_small_list(self, list_data: List[Any], chunk_size: int) -> bool:
        """Check if list is small enough for single chunk."""
        return len(list_data) <= chunk_size
    
    def _create_single_list_chunk(self, list_data: List[Any], field_name: str, 
                                 start_id: int) -> List[Dict[str, Any]]:
        """Create a single chunk for small lists."""
        content = f"{field_name}: {', '.join(str(item) for item in list_data)}"
        
        chunk = self.chunk_factory.create_list_chunk(
            chunk_id=f"chunk_{start_id}",
            content=content,
            source_field=field_name,
            item_count=len(list_data)
        )
        
        return [chunk]
    
    def _create_multiple_list_chunks(self, list_data: List[Any], field_name: str,
                                    chunk_size: int, start_id: int) -> List[Dict[str, Any]]:
        """Create multiple chunks for large lists."""
        chunks = []
        chunk_num = 0
        
        for i in range(0, len(list_data), chunk_size):
            chunk_items = list_data[i:i + chunk_size]
            content = f"{field_name}: {', '.join(str(item) for item in chunk_items)}"
            
            chunk = self.chunk_factory.create_list_chunk(
                chunk_id=f"chunk_{start_id + chunk_num}",
                content=content,
                source_field=field_name,
                item_count=len(chunk_items),
                chunk_index=chunk_num
            )
            
            chunks.append(chunk)
            chunk_num += 1
        
        return chunks
    
    def _enrich_chunk_metadata(self, chunk: Dict[str, Any], original_data: Dict[str, Any]):
        """Enrich chunk with additional metadata."""
        metadata = chunk.setdefault("metadata", {})
        extraction_metadata = original_data.get("_metadata", {})
        
        metadata.update({
            "source_type": "restaurant",
            "entity_name": original_data.get("name", "Unknown"),
            "confidence_score": extraction_metadata.get("confidence", 0.9),
            "extraction_method": extraction_metadata.get("extraction_method", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def _create_basic_relationships(self, chunks: List[Dict[str, Any]], 
                                   original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create basic relationships between chunks."""
        field_chunks = self._group_chunks_by_field(chunks)
        return self._create_field_relationships(field_chunks, original_data)
    
    def _group_chunks_by_field(self, chunks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Group chunks by their source field."""
        field_chunks = {}
        
        for chunk in chunks:
            field = chunk.get("source_field", "unknown")
            base_field = field.split('.')[0]  # Remove nested keys
            field_chunks.setdefault(base_field, []).append(chunk["id"])
        
        return field_chunks
    
    def _create_field_relationships(self, field_chunks: Dict[str, List[str]], 
                                   original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create relationships for different field types."""
        relationships = []
        field_targets = {
            "menu": "menu_items",
            "hours": "business_hours", 
            "contact": "contact_info",
            "location": "address_chunk"
        }
        
        for field, chunk_ids in field_chunks.items():
            if field in field_targets:
                target_name = field_targets[field]
                relationships.append({
                    "from": "restaurant_info",
                    "to": target_name,
                    "type": f"has_{field}",
                    "bidirectional": True
                })
        
        # Add menu-price relationship if both exist
        if "menu" in field_chunks and "price_range" in original_data:
            relationships.append({
                "from": "menu_items",
                "to": "price_range", 
                "type": "priced_in",
                "bidirectional": False
            })
        
        return relationships
    
    def create_relationships(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create semantic relationships between data elements."""
        relationship_builder = RelationshipBuilder()
        return relationship_builder.build_relationships(data)
    
    def generate_embedding_hints(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embedding hints for optimal vectorization."""
        hint_generator = EmbeddingHintGenerator()
        return hint_generator.generate_hints(data)
    
    def export(self, structured_data: Dict[str, Any], 
               format: str = "json", profile: Optional[str] = None) -> Any:
        """Export structured data in specified format."""
        exporter = DataExporter()
        return exporter.export(structured_data, format, profile)
    
    def structure_multimodal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure multi-modal content (text, images, PDFs)."""
        multimodal_processor = MultiModalProcessor()
        return multimodal_processor.process(data)
    
    def chunk_intelligently(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent chunking that respects natural boundaries."""
        intelligent_chunker = IntelligentChunker(self.config)
        return intelligent_chunker.process(data)
    
    def generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary chunks for quick retrieval."""
        summary_generator = SummaryGenerator()
        return summary_generator.generate(data)
    
    def structure_temporal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure temporal data with time-sensitive metadata."""
        temporal_processor = TemporalProcessor()
        return temporal_processor.process(data)
    
    def create_hierarchy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create hierarchical chunk organization."""
        hierarchy_builder = HierarchyBuilder()
        return hierarchy_builder.build(data)
    
    def _handle_missing_data(self, chunks: List[Dict[str, Any]], original_data: Dict[str, Any]):
        """Handle missing or incomplete data by marking in metadata."""
        missing_data_handler = MissingDataHandler()
        missing_data_handler.mark_missing_fields(chunks, original_data)
    
    def _create_child_chunks(self, nested_data: Dict[str, Any], parent_key: str, 
                            parent_id: str, chunks: List[Dict[str, Any]], 
                            start_id: int, level: int):
        """Create child chunks recursively - backward compatibility method."""
        hierarchy_builder = HierarchyBuilder()
        hierarchy_builder._create_child_chunks(nested_data, parent_key, parent_id, chunks, start_id, level)


class RelationshipBuilder:
    """Builds semantic relationships between data elements."""
    
    def build_relationships(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build relationships based on data structure."""
        relationships = []
        
        relationship_mappings = {
            "menu": ("restaurant_info", "menu_items", "has_menu"),
            "hours": ("restaurant_info", "business_hours", "has_hours"),
            "contact": ("restaurant_info", "contact_info", "has_contact"),
            "location": ("restaurant_info", "address_chunk", "located_at")
        }
        
        for field, (from_entity, to_entity, relation_type) in relationship_mappings.items():
            if field in data:
                relationships.append({
                    "from": from_entity,
                    "to": to_entity,
                    "type": relation_type,
                    "bidirectional": True
                })
        
        # Menu-price relationships
        if "menu" in data and "price_range" in data:
            relationships.append({
                "from": "menu_items",
                "to": "price_range",
                "type": "priced_in",
                "bidirectional": False
            })
        
        return {"relationships": relationships}


class EmbeddingHintGenerator:
    """Generates embedding hints for optimal vectorization."""
    
    def generate_hints(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embedding hints for data fields."""
        chunks = []
        
        for key, value in data.items():
            if key.startswith('_'):
                continue
                
            content = self._format_content(value)
            domain_keywords = self._get_domain_keywords(key)
            importance_weight = self._get_importance_weight(key)
            
            chunk = {
                "id": f"chunk_{key}",
                "content": content,
                "type": ChunkType.TEXT.value,
                "embedding_hints": {
                    "semantic_context": f"Restaurant {key} information",
                    "domain_keywords": domain_keywords,
                    "importance_weight": importance_weight,
                    "query_templates": self._get_query_templates(key)
                }
            }
            chunks.append(chunk)
        
        return {"chunks": chunks}
    
    def _format_content(self, value: Any) -> str:
        """Format value as content string."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)
    
    def _get_domain_keywords(self, key: str) -> List[str]:
        """Get domain-specific keywords for a field."""
        keyword_mapping = {
            "cuisine": ["food", "dining", "restaurant", "culinary"],
            "ambiance": ["atmosphere", "setting", "environment", "mood"],
            "menu": ["food", "dishes", "meals", "cuisine"]
        }
        return keyword_mapping.get(key, [])
    
    def _get_importance_weight(self, key: str) -> float:
        """Get importance weight for a field."""
        weights = {
            "name": 1.0,
            "description": 0.9,
            "cuisine": 0.8,
            "menu": 0.8,
            "ambiance": 0.7,
            "hours": 0.6,
            "contact": 0.6
        }
        return weights.get(key, 0.5)
    
    def _get_query_templates(self, key: str) -> List[str]:
        """Get query templates for a field."""
        return [
            f"What is the {key}?",
            f"Tell me about the {key}",
            f"Find restaurants with {key}"
        ]


class DataExporter:
    """Exports structured data in various formats."""
    
    def export(self, structured_data: Dict[str, Any], 
               format: str, profile: Optional[str] = None) -> Any:
        """Export data in specified format."""
        if format == "json":
            return self._export_json(structured_data, profile)
        elif format == "jsonl":
            return self._export_jsonl(structured_data)
        elif format == "parquet":
            return self._export_parquet(structured_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, data: Dict[str, Any], profile: Optional[str] = None) -> str:
        """Export as JSON with RAG-ready schema."""
        result = data.copy()
        
        if profile:
            result.setdefault("metadata", {})["profile"] = profile
        
        # Ensure RAG-ready schema compliance
        if "version" not in result:
            result["version"] = result.get("metadata", {}).get("version", SemanticConstants.SCHEMA_VERSION)
        
        return json.dumps(result, indent=2)
    
    def _export_jsonl(self, data: Dict[str, Any]) -> str:
        """Export as JSONL format."""
        lines = []
        for chunk in data.get("chunks", []):
            lines.append(json.dumps(chunk))
        return '\n'.join(lines)
    
    def _export_parquet(self, data: Dict[str, Any]) -> bytes:
        """Export as Parquet format (simulated)."""
        # Simulate parquet export (would use pandas/pyarrow in real implementation)
        return b"PARQUET_DATA_" + json.dumps(data).encode()


class MultiModalProcessor:
    """Processes multi-modal content (text, images, PDFs)."""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process multi-modal data into chunks."""
        chunks = []
        chunk_id = 1
        
        # Process text content
        if "text_content" in data:
            text_chunks = self._process_text_content(data["text_content"], chunk_id)
            chunks.extend(text_chunks)
            chunk_id += len(text_chunks)
        
        # Process images
        if "images" in data:
            image_chunks = self._process_images(data["images"], chunk_id)
            chunks.extend(image_chunks)
            chunk_id += len(image_chunks)
        
        # Process PDFs
        if "pdfs" in data:
            pdf_chunks = self._process_pdfs(data["pdfs"], chunk_id)
            chunks.extend(pdf_chunks)
            chunk_id += len(pdf_chunks)
        
        relationships = self._create_multimodal_relationships(chunks)
        
        return {
            "chunks": chunks,
            "relationships": relationships
        }
    
    def _process_text_content(self, text_content: str, start_id: int) -> List[Dict[str, Any]]:
        """Process text content into chunks."""
        # This would use the main text chunking logic
        # Simplified for this refactor
        return [{
            "id": f"chunk_{start_id}",
            "content": text_content,
            "type": ChunkType.TEXT.value
        }]
    
    def _process_images(self, images: List[Dict[str, Any]], start_id: int) -> List[Dict[str, Any]]:
        """Process images into chunks."""
        chunks = []
        for i, img in enumerate(images):
            chunk = {
                "id": f"chunk_{start_id + i}",
                "content": img.get("description", "Image content"),
                "type": ChunkType.IMAGE.value,
                "image_metadata": {
                    "url": img.get("url"),
                    "image_type": img.get("type", "general")
                }
            }
            chunks.append(chunk)
        return chunks
    
    def _process_pdfs(self, pdfs: List[Dict[str, Any]], start_id: int) -> List[Dict[str, Any]]:
        """Process PDFs into chunks."""
        chunks = []
        for i, pdf in enumerate(pdfs):
            chunk = {
                "id": f"chunk_{start_id + i}",
                "content": pdf.get("content", "PDF document"),
                "type": ChunkType.PDF.value,
                "document_metadata": {
                    "url": pdf.get("url"),
                    "pages": pdf.get("pages", 1)
                }
            }
            chunks.append(chunk)
        return chunks
    
    def _create_multimodal_relationships(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create relationships between different modalities."""
        relationships = []
        
        text_chunks = [c for c in chunks if c["type"] == ChunkType.TEXT.value]
        image_chunks = [c for c in chunks if c["type"] == ChunkType.IMAGE.value]
        pdf_chunks = [c for c in chunks if c["type"] == ChunkType.PDF.value]
        
        # Link text to images and PDFs
        for text_chunk in text_chunks:
            for img_chunk in image_chunks:
                relationships.append({
                    "from": text_chunk["id"],
                    "to": img_chunk["id"],
                    "type": "has_visual"
                })
            
            for pdf_chunk in pdf_chunks:
                relationships.append({
                    "from": text_chunk["id"],
                    "to": pdf_chunk["id"],
                    "type": "has_document"
                })
        
        return relationships


class IntelligentChunker:
    """Applies intelligent chunking respecting natural boundaries."""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.content_processor = ContentProcessor(config)
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent chunking to data."""
        chunks = []
        
        for key, value in data.items():
            if isinstance(value, str):
                chunks.extend(self._chunk_text_intelligently(value, key))
        
        self._add_overlap_metadata(chunks)
        return {"chunks": chunks}
    
    def _chunk_text_intelligently(self, text: str, key: str) -> List[Dict[str, Any]]:
        """Chunk text respecting paragraph and sentence boundaries."""
        paragraphs = text.split('\n\n')
        chunks = []
        chunk_id = len(chunks) + 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            chunks.extend(self._process_paragraph(para, key, chunk_id))
            chunk_id = len(chunks) + 1
        
        return chunks
    
    def _process_paragraph(self, paragraph: str, key: str, chunk_id: int) -> List[Dict[str, Any]]:
        """Process a single paragraph into chunks."""
        words = self.content_processor.split_into_words(paragraph)
        
        if len(words) <= self.config.chunk_size:
            return self._create_paragraph_chunk(paragraph, key, chunk_id)
        else:
            return self._split_large_paragraph(paragraph, key, chunk_id)
    
    def _create_paragraph_chunk(self, paragraph: str, key: str, chunk_id: int) -> List[Dict[str, Any]]:
        """Create a single chunk for a paragraph."""
        chunk = {
            "id": f"chunk_{chunk_id}",
            "content": paragraph,
            "type": ChunkType.TEXT.value,
            "metadata": {
                "chunk_type": key,
                "boundary_type": "paragraph"
            }
        }
        return [chunk]
    
    def _split_large_paragraph(self, paragraph: str, key: str, chunk_id: int) -> List[Dict[str, Any]]:
        """Split large paragraph at sentence boundaries."""
        sentences = self.content_processor.split_into_sentences(paragraph)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_words = self.content_processor.split_into_words(sentence)
            
            if current_size + len(sentence_words) <= self.config.chunk_size:
                current_chunk.append(sentence)
                current_size += len(sentence_words)
            else:
                if current_chunk:
                    chunks.append(self._create_sentence_chunk(current_chunk, key, chunk_id))
                    chunk_id += 1
                
                current_chunk = [sentence]
                current_size = len(sentence_words)
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_sentence_chunk(current_chunk, key, chunk_id))
        
        return chunks
    
    def _create_sentence_chunk(self, sentences: List[str], key: str, chunk_id: int) -> Dict[str, Any]:
        """Create a chunk from sentences."""
        content = ' '.join(sentences)
        return {
            "id": f"chunk_{chunk_id}",
            "content": content,
            "type": ChunkType.TEXT.value,
            "metadata": {
                "chunk_type": key,
                "boundary_type": "sentence"
            }
        }
    
    def _add_overlap_metadata(self, chunks: List[Dict[str, Any]]):
        """Add overlap metadata for context continuity."""
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                chunks[i].setdefault("metadata", {})["overlap_with_next"] = True
                chunks[i + 1].setdefault("metadata", {})["overlap_with_previous"] = True


class SummaryGenerator:
    """Generates summary chunks for quick retrieval."""
    
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary chunks."""
        summary_chunk = self._create_primary_summary(data)
        detail_chunks = self._create_detail_chunks(data)
        all_chunks = [summary_chunk] + detail_chunks
        
        relationships = self._create_summary_relationships(summary_chunk, detail_chunks)
        
        return {
            "chunks": all_chunks,
            "relationships": relationships
        }
    
    def _create_primary_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create the main summary chunk."""
        name = data.get("name", "Unknown Restaurant")
        cuisine = data.get("cuisine", "")
        price_range = data.get("price_range", "")
        location = data.get("location", {})
        address = self._extract_address(location)
        
        summary_content = self._build_summary_content(name, cuisine, price_range, address)
        
        return {
            "id": "summary_1",
            "content": summary_content,
            "type": ChunkType.SUMMARY.value,
            "metadata": {
                "chunk_type": "summary",
                "importance": 1.0
            }
        }
    
    def _extract_address(self, location: Any) -> str:
        """Extract address from location data."""
        if isinstance(location, dict):
            return location.get("address", "")
        return str(location) if location else ""
    
    def _build_summary_content(self, name: str, cuisine: str, price_range: str, address: str) -> str:
        """Build summary content from components."""
        parts = [name]
        
        if cuisine:
            parts.append(f"serving {cuisine} cuisine")
        if price_range:
            parts.append(f"in the {price_range} price range")
        if address:
            parts.append(f"located at {address}")
        
        return ", ".join(parts) + "."
    
    def _create_detail_chunks(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create detail chunks for non-summary fields."""
        detail_chunks = []
        chunk_id = 2
        summary_fields = {"name", "cuisine", "price_range", "location"}
        
        for key, value in data.items():
            if key in summary_fields or not isinstance(value, str) or not value:
                continue
            
            chunk = {
                "id": f"detail_{chunk_id}",
                "content": f"{key}: {value}",
                "type": ChunkType.DETAIL.value,
                "metadata": {
                    "chunk_type": key,
                    "linked_to_summary": True
                }
            }
            detail_chunks.append(chunk)
            chunk_id += 1
        
        return detail_chunks
    
    def _create_summary_relationships(self, summary_chunk: Dict[str, Any], 
                                     detail_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create relationships from summary to details."""
        relationships = []
        
        for detail_chunk in detail_chunks:
            relationships.append({
                "from": summary_chunk["id"],
                "to": detail_chunk["id"],
                "type": "summarizes"
            })
        
        return relationships


class TemporalProcessor:
    """Processes temporal data with time-sensitive metadata."""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process temporal data into chunks."""
        chunks = []
        chunk_id = 1
        
        for key, value in data.items():
            if key.startswith('_'):
                continue
            
            if key == "hours" and isinstance(value, dict):
                chunks.extend(self._process_business_hours(value, chunk_id))
                chunk_id += len(chunks)
            elif key == "special_events" and isinstance(value, list):
                event_chunks = self._process_special_events(value, chunk_id)
                chunks.extend(event_chunks)
                chunk_id += len(event_chunks)
            else:
                chunks.extend(self._process_regular_field(key, value, chunk_id))
                chunk_id = len(chunks) + 1
        
        return {
            "chunks": chunks,
            "structured_result": {"chunks": chunks}
        }
    
    def _process_business_hours(self, hours_data: Dict[str, str], chunk_id: int) -> List[Dict[str, Any]]:
        """Process business hours into temporal chunks."""
        hours_list = [f"{day}: {hours}" for day, hours in hours_data.items()]
        content = f"Business hours: {', '.join(hours_list)}"
        
        chunk = {
            "id": f"chunk_{chunk_id}",
            "content": content,
            "type": ChunkType.TEMPORAL.value,
            "metadata": {
                "temporal_type": TemporalType.RECURRING_SCHEDULE.value,
                "chunk_type": "hours",
                "time_reference": "recurring",
                "schedule": "business_hours"
            }
        }
        
        return [chunk]
    
    def _process_special_events(self, events: List[Dict[str, Any]], start_id: int) -> List[Dict[str, Any]]:
        """Process special events into temporal chunks."""
        chunks = []
        
        for i, event in enumerate(events):
            content = self._format_event_content(event)
            
            chunk = {
                "id": f"chunk_{start_id + i}",
                "content": content,
                "type": ChunkType.TEMPORAL.value,
                "metadata": {
                    "temporal_type": TemporalType.SPECIFIC_DATE.value,
                    "chunk_type": "event",
                    "time_reference": event.get('date'),
                    "schedule": event.get('time')
                }
            }
            chunks.append(chunk)
        
        return chunks
    
    def _format_event_content(self, event: Dict[str, Any]) -> str:
        """Format event content string."""
        content = f"Special event: {event.get('name', 'Event')}"
        
        if event.get('date'):
            content += f" on {event['date']}"
        if event.get('time'):
            content += f" at {event['time']}"
        
        return content
    
    def _process_regular_field(self, key: str, value: Any, chunk_id: int) -> List[Dict[str, Any]]:
        """Process regular fields into chunks."""
        if isinstance(value, str):
            content = f"{key}: {value}"
        else:
            content = f"{key}: {str(value)}"
        
        chunk = {
            "id": f"chunk_{chunk_id}",
            "content": content,
            "type": ChunkType.TEXT.value,
            "metadata": {
                "chunk_type": key
            }
        }
        
        return [chunk]


class HierarchyBuilder:
    """Builds hierarchical chunk organization."""
    
    def build(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build hierarchical structure from data."""
        chunks = []
        relationships = []
        chunk_id = 1
        
        for key, value in data.items():
            if key.startswith('_'):
                continue
            
            if self._is_complex_nested_data(value):
                parent_chunk, child_chunks, chunk_id = self._create_hierarchical_chunks(
                    key, value, chunk_id
                )
                chunks.append(parent_chunk)
                chunks.extend(child_chunks)
                
                relationships.extend(self._create_hierarchy_relationships(parent_chunk, child_chunks))
            else:
                simple_chunk = self._create_simple_chunk(key, value, chunk_id)
                chunks.append(simple_chunk)
                chunk_id += 1
        
        return {
            "chunks": chunks,
            "relationships": relationships,
            "structured_result": {"chunks": chunks, "relationships": relationships}
        }
    
    def _is_complex_nested_data(self, value: Any) -> bool:
        """Check if value is complex nested data needing hierarchy."""
        return isinstance(value, dict) and len(value) > 1
    
    def _create_hierarchical_chunks(self, key: str, value: Dict[str, Any], 
                                   chunk_id: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]], int]:
        """Create parent and child chunks for hierarchical data."""
        parent_chunk = {
            "id": f"parent_{chunk_id}",
            "content": f"{key.title()} Information",
            "type": ChunkType.PARENT.value,
            "hierarchy_level": 0,
            "is_parent": True,
            "metadata": {
                "chunk_type": key,
                "category": key
            }
        }
        
        child_chunks = []
        chunk_id += 1
        
        self._create_child_chunks(value, key, parent_chunk["id"], child_chunks, chunk_id, 1)
        
        return parent_chunk, child_chunks, len(child_chunks) + chunk_id
    
    def _create_simple_chunk(self, key: str, value: Any, chunk_id: int) -> Dict[str, Any]:
        """Create a simple chunk for non-hierarchical data."""
        if isinstance(value, str):
            content = f"{key}: {value}"
        else:
            content = f"{key}: {str(value)}"
        
        return {
            "id": f"chunk_{chunk_id}",
            "content": content,
            "type": ChunkType.DETAIL.value,
            "hierarchy_level": 0,
            "metadata": {
                "chunk_type": key
            }
        }
    
    def _create_child_chunks(self, nested_data: Dict[str, Any], parent_key: str, 
                            parent_id: str, chunks: List[Dict[str, Any]], 
                            start_id: int, level: int):
        """Create child chunks recursively."""
        if level > SemanticConstants.MAXIMUM_HIERARCHY_DEPTH:
            return
        
        for key, value in nested_data.items():
            if isinstance(value, dict):
                child_chunks = self._create_nested_child_chunks(
                    key, value, parent_key, parent_id, start_id, level
                )
                chunks.extend(child_chunks)
            elif isinstance(value, list):
                child_chunk = self._create_list_child_chunk(
                    key, value, parent_key, parent_id, start_id, level
                )
                chunks.append(child_chunk)
            else:
                child_chunk = self._create_simple_child_chunk(
                    key, value, parent_key, parent_id, start_id, level
                )
                chunks.append(child_chunk)
            
            start_id += 1
    
    def _create_nested_child_chunks(self, key: str, value: Dict[str, Any], 
                                   parent_key: str, parent_id: str, 
                                   start_id: int, level: int) -> List[Dict[str, Any]]:
        """Create chunks for nested dictionary data."""
        child_parent = {
            "id": f"child_parent_{start_id}",
            "content": f"{key.title()} Category",
            "type": ChunkType.CHILD_PARENT.value,
            "hierarchy_level": level,
            "parent_id": parent_id,
            "metadata": {
                "chunk_type": f"{parent_key}_{key}",
                "category": key
            }
        }
        
        nested_chunks = [child_parent]
        self._create_child_chunks(value, f"{parent_key}_{key}", 
                                 child_parent["id"], nested_chunks, start_id + 1, level + 1)
        
        return nested_chunks
    
    def _create_list_child_chunk(self, key: str, value: List[Any], 
                                parent_key: str, parent_id: str, 
                                start_id: int, level: int) -> Dict[str, Any]:
        """Create chunk for list content."""
        content = f"{key}: {', '.join(str(item) for item in value)}"
        
        return {
            "id": f"child_{start_id}",
            "content": content,
            "type": ChunkType.CHILD.value,
            "hierarchy_level": level,
            "parent_id": parent_id,
            "metadata": {
                "chunk_type": f"{parent_key}_{key}",
                "list_items": len(value)
            }
        }
    
    def _create_simple_child_chunk(self, key: str, value: Any, 
                                  parent_key: str, parent_id: str, 
                                  start_id: int, level: int) -> Dict[str, Any]:
        """Create chunk for simple content."""
        content = f"{key}: {str(value)}"
        
        return {
            "id": f"child_{start_id}",
            "content": content,
            "type": ChunkType.CHILD.value,
            "hierarchy_level": level,
            "parent_id": parent_id,
            "metadata": {
                "chunk_type": f"{parent_key}_{key}"
            }
        }
    
    def _create_hierarchy_relationships(self, parent_chunk: Dict[str, Any], 
                                       child_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create relationships for hierarchy navigation."""
        relationships = []
        
        for chunk in child_chunks:
            if chunk.get("parent_id"):
                relationships.extend([
                    {
                        "from": chunk["parent_id"],
                        "to": chunk["id"],
                        "type": "has_child"
                    },
                    {
                        "from": chunk["id"],
                        "to": chunk["parent_id"],
                        "type": "has_parent"
                    }
                ])
        
        return relationships


class MissingDataHandler:
    """Handles missing or incomplete data by marking in metadata."""
    
    def mark_missing_fields(self, chunks: List[Dict[str, Any]], original_data: Dict[str, Any]):
        """Mark missing fields in chunk metadata."""
        missing_fields = self._identify_missing_fields(original_data)
        
        if missing_fields:
            self._update_chunk_metadata(chunks, missing_fields)
    
    def _identify_missing_fields(self, data: Dict[str, Any]) -> List[str]:
        """Identify missing fields in the data."""
        present_fields = set(data.keys())
        missing_fields = SemanticConstants.EXPECTED_RESTAURANT_FIELDS - present_fields
        
        # Check nested field completeness
        missing_fields.update(self._check_location_completeness(data))
        missing_fields.update(self._check_contact_completeness(data))
        
        return sorted(list(missing_fields))
    
    def _check_location_completeness(self, data: Dict[str, Any]) -> Set[str]:
        """Check for missing location sub-fields."""
        location_data = data.get("location", {})
        if not isinstance(location_data, dict):
            return set()
        
        missing_location = SemanticConstants.EXPECTED_LOCATION_FIELDS - set(location_data.keys())
        return {f"location.{field}" for field in missing_location}
    
    def _check_contact_completeness(self, data: Dict[str, Any]) -> Set[str]:
        """Check for missing contact sub-fields."""
        contact_data = data.get("contact", {})
        if not isinstance(contact_data, dict):
            return set()
        
        missing_contact = SemanticConstants.EXPECTED_CONTACT_FIELDS - set(contact_data.keys())
        return {f"contact.{field}" for field in missing_contact}
    
    def _update_chunk_metadata(self, chunks: List[Dict[str, Any]], missing_fields: List[str]):
        """Update chunk metadata with missing field information."""
        completeness_ratio = self._calculate_completeness_ratio(missing_fields)
        confidence_score = min(0.8, completeness_ratio)
        
        for chunk in chunks:
            metadata = chunk.setdefault("metadata", {})
            metadata["missing_fields"] = missing_fields
            metadata["confidence_score"] = confidence_score
    
    def _calculate_completeness_ratio(self, missing_fields: List[str]) -> float:
        """Calculate data completeness ratio."""
        total_expected = len(SemanticConstants.EXPECTED_RESTAURANT_FIELDS)
        missing_count = len([f for f in missing_fields if '.' not in f])  # Only top-level fields
        present_count = total_expected - missing_count
        return present_count / total_expected if total_expected > 0 else 0.0