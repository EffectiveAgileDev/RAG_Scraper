"""MetadataEnricher for adding rich metadata to semantic chunks."""

import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


class MetadataEnricher:
    """Enriches semantic chunks with additional metadata for RAG systems."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize metadata enricher."""
        self.config = config or {}
        self.add_timestamps = self.config.get('add_timestamps', True)
        self.add_confidence_scores = self.config.get('add_confidence_scores', True)
        self.add_extraction_metadata = self.config.get('add_extraction_metadata', True)
        self.add_domain_keywords = self.config.get('add_domain_keywords', True)
        self.add_content_metrics = self.config.get('add_content_metrics', False)
        self.add_relationship_hints = self.config.get('add_relationship_hints', False)
        self.add_embedding_hints = self.config.get('add_embedding_hints', False)
        self.add_temporal_metadata = self.config.get('add_temporal_metadata', False)
        
        # Compile regex patterns for efficiency
        self.sentence_pattern = re.compile(r'[.!?]+')
        self.temporal_pattern = re.compile(r'\b(january|february|march|april|may|june|july|august|september|october|november|december|\d{4}|today|tomorrow|yesterday|weekend|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', re.IGNORECASE)
    
    def enrich_chunk(self, chunk: Dict[str, Any], original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single chunk with metadata."""
        enriched_chunk = chunk.copy()
        metadata = enriched_chunk.setdefault("metadata", {})
        
        # Add basic enrichment
        self._add_basic_metadata(metadata, original_data)
        
        # Add optional enrichments based on config
        if self.add_timestamps:
            self._add_timestamps(metadata)
        
        if self.add_extraction_metadata:
            self._add_extraction_metadata(metadata, original_data)
        
        if self.add_domain_keywords:
            self._add_domain_keywords(metadata, chunk, original_data)
        
        if self.add_content_metrics:
            self._add_content_metrics(metadata, chunk)
        
        if self.add_relationship_hints:
            self._add_relationship_hints(metadata, chunk, original_data)
        
        if self.add_embedding_hints:
            self._add_embedding_hints(metadata, chunk, original_data)
        
        if self.add_temporal_metadata:
            self._add_temporal_metadata(metadata, chunk)
        
        return enriched_chunk
    
    def enrich_chunks(self, chunks: List[Dict[str, Any]], 
                     original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich multiple chunks in batch."""
        return [self.enrich_chunk(chunk, original_data) for chunk in chunks]
    
    def _add_basic_metadata(self, metadata: Dict[str, Any], original_data: Dict[str, Any]):
        """Add basic metadata fields."""
        metadata.update({
            "entity_name": original_data.get("name", "Unknown"),
            "source_type": "restaurant",
            "confidence_score": original_data.get("_metadata", {}).get("confidence", 0.9)
        })
    
    def _add_timestamps(self, metadata: Dict[str, Any]):
        """Add timestamp metadata."""
        now = datetime.now(timezone.utc)
        metadata.update({
            "timestamp": now.isoformat(),
            "processing_date": now.strftime("%Y-%m-%d")
        })
    
    def _add_extraction_metadata(self, metadata: Dict[str, Any], original_data: Dict[str, Any]):
        """Add extraction-specific metadata."""
        source_metadata = original_data.get("_metadata", {})
        
        metadata.update({
            "extraction_method": source_metadata.get("extraction_method", "unknown"),
            "confidence_score": source_metadata.get("confidence", 0.9),
            "source_url": source_metadata.get("url", ""),
            "scrape_timestamp": source_metadata.get("scrape_timestamp", "")
        })
    
    def _add_domain_keywords(self, metadata: Dict[str, Any], chunk: Dict[str, Any], 
                           original_data: Dict[str, Any]):
        """Add domain-specific keywords."""
        source_field = chunk.get("source_field", "")
        content = chunk.get("content", "")
        
        # Generate keywords based on field type
        keywords = ["restaurant", "food", "dining"]  # Base keywords
        
        if source_field == "cuisine":
            keywords.extend(["cuisine", "culinary", "cooking", "flavors"])
        elif source_field == "menu":
            keywords.extend(["menu", "dishes", "meals", "ingredients"])
        elif source_field == "ambiance":
            keywords.extend(["atmosphere", "environment", "setting", "mood"])
        elif source_field == "location":
            keywords.extend(["address", "location", "neighborhood", "area"])
        elif source_field == "hours":
            keywords.extend(["hours", "schedule", "timing", "open"])
        
        # Add cuisine-specific keywords
        cuisine = original_data.get("cuisine", "")
        if cuisine:
            keywords.append(cuisine.lower())
        
        metadata["domain_keywords"] = list(set(keywords))
    
    def _add_content_metrics(self, metadata: Dict[str, Any], chunk: Dict[str, Any]):
        """Add content analysis metrics."""
        content = chunk.get("content", "")
        
        # Basic metrics
        words = content.split()
        sentences = self.sentence_pattern.split(content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple readability score (average words per sentence)
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        readability_score = min(max(0.0, 1.0 - (avg_words_per_sentence - 15) / 10), 1.0)
        
        metadata.update({
            "word_count": len(words),
            "sentence_count": len(sentences),
            "readability_score": round(readability_score, 2)
        })
    
    def _add_relationship_hints(self, metadata: Dict[str, Any], chunk: Dict[str, Any], 
                              original_data: Dict[str, Any]):
        """Add hints for relationship creation."""
        source_field = chunk.get("source_field", "")
        
        # Suggest related fields based on current field
        related_fields = []
        
        if source_field == "menu":
            related_fields = ["cuisine", "price_range", "ambiance", "location"]
        elif source_field == "location":
            related_fields = ["hours", "contact", "parking", "menu"]
        elif source_field == "ambiance":
            related_fields = ["cuisine", "price_range", "menu"]
        elif source_field == "hours":
            related_fields = ["location", "contact"]
        
        # Filter to only include fields that exist in original data
        existing_related = [field for field in related_fields if field in original_data]
        
        metadata["relationship_hints"] = {
            "related_fields": existing_related,
            "relationship_strength": "high" if len(existing_related) > 2 else "medium"
        }
    
    def _add_embedding_hints(self, metadata: Dict[str, Any], chunk: Dict[str, Any], 
                           original_data: Dict[str, Any]):
        """Add hints for embedding optimization."""
        source_field = chunk.get("source_field", "")
        
        # Calculate importance weight
        importance_weights = {
            "name": 1.0,
            "description": 0.9,
            "cuisine": 0.8,
            "menu": 0.8,
            "ambiance": 0.7,
            "location": 0.7,
            "hours": 0.6,
            "contact": 0.6,
            "price_range": 0.5
        }
        
        importance_weight = importance_weights.get(source_field, 0.5)
        
        # Generate query templates
        templates = [
            f"What is the {source_field}?",
            f"Tell me about the {source_field}",
            f"Find restaurants with {source_field}"
        ]
        
        metadata["embedding_hints"] = {
            "semantic_context": f"Restaurant {source_field} information",
            "importance_weight": importance_weight,
            "query_templates": templates
        }
    
    def _add_temporal_metadata(self, metadata: Dict[str, Any], chunk: Dict[str, Any]):
        """Add temporal metadata for time-sensitive information."""
        content = chunk.get("content", "").lower()
        
        # Check for temporal indicators
        temporal_matches = self.temporal_pattern.findall(content)
        
        if temporal_matches:
            metadata["temporal_relevance"] = "high"
            metadata["expiry_hint"] = "may_expire"
            metadata["temporal_keywords"] = temporal_matches
        else:
            metadata["temporal_relevance"] = "low"
            metadata["expiry_hint"] = "stable"
    
    def calculate_chunk_importance(self, chunk: Dict[str, Any], 
                                 original_data: Dict[str, Any]) -> float:
        """Calculate importance score for a chunk."""
        source_field = chunk.get("source_field", "")
        content = chunk.get("content", "")
        
        # Base importance scores by field type
        field_importance = {
            "name": 1.0,
            "description": 0.9,
            "cuisine": 0.8,
            "menu": 0.8,
            "ambiance": 0.7,
            "location": 0.7,
            "hours": 0.6,
            "contact": 0.6,
            "price_range": 0.5
        }
        
        base_score = field_importance.get(source_field, 0.5)
        
        # Adjust based on content length (longer content may be more important)
        word_count = len(content.split())
        length_multiplier = min(1.0 + (word_count / 100), 1.5)  # Cap at 1.5x
        
        # Adjust based on confidence if available
        confidence = original_data.get("_metadata", {}).get("confidence", 0.9)
        
        final_score = base_score * length_multiplier * confidence
        return min(final_score, 1.0)  # Cap at 1.0