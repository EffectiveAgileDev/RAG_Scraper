"""RelationshipMapper for creating relationships between semantic chunks."""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict


class RelationshipMapper:
    """Creates and manages relationships between semantic chunks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize relationship mapper."""
        self.config = config or {}
        self.create_hierarchical = self.config.get('create_hierarchical', True)
        self.create_semantic = self.config.get('create_semantic', True)
        self.create_temporal = self.config.get('create_temporal', False)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.5)
        
        # Field hierarchy definitions
        self.field_hierarchy = {
            "name": {"level": 0, "children": ["cuisine", "description", "menu", "location", "hours", "contact"]},
            "description": {"level": 1, "children": ["cuisine", "ambiance", "price_range"]},
            "cuisine": {"level": 1, "children": ["menu"]},
            "menu": {"level": 2, "children": []},
            "location": {"level": 1, "children": ["contact", "hours"]},
            "hours": {"level": 2, "children": []},
            "contact": {"level": 2, "children": []},
            "ambiance": {"level": 2, "children": []},
            "price_range": {"level": 2, "children": []}
        }
        
        # Temporal keywords for detecting time-sensitive content
        self.temporal_keywords = {
            "hours", "schedule", "timing", "open", "closed", "weekend", "weekday",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "morning", "afternoon", "evening", "night", "lunch", "dinner", "brunch",
            "special", "promotion", "limited", "seasonal", "holiday"
        }
    
    def create_relationships(self, chunks: List[Dict[str, Any]], 
                           original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create all types of relationships between chunks."""
        if not chunks:
            return []
        
        relationships = []
        
        # Create hierarchical relationships
        if self.create_hierarchical:
            hierarchical_rels = self.create_hierarchical_relationships(chunks, original_data)
            relationships.extend(hierarchical_rels)
        
        # Create semantic relationships
        if self.create_semantic:
            semantic_rels = self.create_semantic_relationships(chunks)
            relationships.extend(semantic_rels)
        
        # Create temporal relationships
        if self.create_temporal:
            temporal_rels = self.create_temporal_relationships(chunks)
            relationships.extend(temporal_rels)
        
        # Create cross-reference relationships
        cross_ref_rels = self.create_cross_reference_relationships(chunks)
        relationships.extend(cross_ref_rels)
        
        # Create containment relationships
        containment_rels = self.detect_containment_relationships(chunks)
        relationships.extend(containment_rels)
        
        # Filter by confidence and remove duplicates
        relationships = self.filter_relationships_by_confidence(relationships)
        relationships = self.remove_duplicate_relationships(relationships)
        
        # Add metadata to relationships
        relationships = self.add_relationship_metadata(relationships)
        
        return relationships
    
    def create_hierarchical_relationships(self, chunks: List[Dict[str, Any]], 
                                        original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create hierarchical parent-child relationships."""
        relationships = []
        
        # Group chunks by field hierarchy level
        chunks_by_field = defaultdict(list)
        for chunk in chunks:
            source_field = chunk.get("source_field", "").split('.')[0]  # Remove nested paths
            chunks_by_field[source_field].append(chunk)
        
        # Create relationships based on hierarchy
        for parent_field, parent_info in self.field_hierarchy.items():
            if parent_field not in chunks_by_field:
                continue
                
            parent_chunks = chunks_by_field[parent_field]
            
            # Link to children
            for child_field in parent_info["children"]:
                if child_field not in chunks_by_field:
                    continue
                    
                child_chunks = chunks_by_field[child_field]
                
                for parent_chunk in parent_chunks:
                    for child_chunk in child_chunks:
                        relationships.append({
                            "from": parent_chunk["id"],
                            "to": child_chunk["id"],
                            "type": f"has_{child_field}",
                            "bidirectional": True,
                            "confidence": 0.9
                        })
        
        return relationships
    
    def create_semantic_relationships(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create semantic similarity relationships."""
        relationships = []
        
        # Compare each pair of chunks for semantic similarity
        for i, chunk1 in enumerate(chunks):
            for j, chunk2 in enumerate(chunks[i+1:], i+1):
                similarity = self.calculate_semantic_similarity(chunk1, chunk2)
                
                if similarity > self.confidence_threshold:
                    relationships.append({
                        "from": chunk1["id"],
                        "to": chunk2["id"],
                        "type": "semantically_related",
                        "confidence": similarity,
                        "bidirectional": True
                    })
        
        return relationships
    
    def create_temporal_relationships(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create temporal relationships for time-sensitive content."""
        relationships = []
        
        # Find chunks with temporal content
        temporal_chunks = []
        for chunk in chunks:
            content = chunk.get("content", "").lower()
            source_field = chunk.get("source_field", "")
            
            # Check for temporal keywords or fields
            has_temporal_content = (
                any(keyword in content for keyword in self.temporal_keywords) or
                source_field in ["hours", "specials", "events", "schedule"]
            )
            
            if has_temporal_content:
                temporal_chunks.append(chunk)
        
        # Create relationships between temporal chunks
        for i, chunk1 in enumerate(temporal_chunks):
            for j, chunk2 in enumerate(temporal_chunks[i+1:], i+1):
                # Hours and specials are typically related
                field1 = chunk1.get("source_field", "")
                field2 = chunk2.get("source_field", "")
                
                if (field1 == "hours" and field2 == "specials") or \
                   (field1 == "specials" and field2 == "hours"):
                    relationships.append({
                        "from": chunk1["id"],
                        "to": chunk2["id"],
                        "type": "temporally_related",
                        "confidence": 0.8,
                        "bidirectional": True
                    })
        
        return relationships
    
    def calculate_semantic_similarity(self, chunk1: Dict[str, Any], 
                                    chunk2: Dict[str, Any]) -> float:
        """Calculate semantic similarity between two chunks."""
        content1 = chunk1.get("content", "").lower()
        content2 = chunk2.get("content", "").lower()
        
        if not content1 or not content2:
            return 0.0
        
        # Simple word-based similarity (Jaccard similarity)
        words1 = set(re.findall(r'\b\w+\b', content1))
        words2 = set(re.findall(r'\b\w+\b', content2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Boost similarity for related fields
        field1 = chunk1.get("source_field", "")
        field2 = chunk2.get("source_field", "")
        
        if self._are_fields_related(field1, field2):
            jaccard_similarity *= 1.2  # 20% boost for related fields
        
        return min(jaccard_similarity, 1.0)
    
    def _are_fields_related(self, field1: str, field2: str) -> bool:
        """Check if two fields are semantically related."""
        related_field_groups = [
            {"cuisine", "menu", "description"},
            {"location", "hours", "contact"},
            {"ambiance", "description", "price_range"},
            {"menu", "price_range", "cuisine"}
        ]
        
        field1_base = field1.split('.')[0]
        field2_base = field2.split('.')[0]
        
        for group in related_field_groups:
            if field1_base in group and field2_base in group:
                return True
        
        return False
    
    def filter_relationships_by_confidence(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter relationships by confidence threshold."""
        return [
            rel for rel in relationships 
            if rel.get("confidence", 1.0) >= self.confidence_threshold
        ]
    
    def create_cross_reference_relationships(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create cross-reference relationships between related fields."""
        relationships = []
        
        # Define cross-reference patterns
        cross_refs = {
            "menu": ["price_range", "cuisine"],
            "location": ["hours", "contact"],
            "cuisine": ["ambiance", "description"],
            "hours": ["contact"]
        }
        
        chunks_by_field = defaultdict(list)
        for chunk in chunks:
            source_field = chunk.get("source_field", "").split('.')[0]
            chunks_by_field[source_field].append(chunk)
        
        for source_field, target_fields in cross_refs.items():
            if source_field not in chunks_by_field:
                continue
                
            source_chunks = chunks_by_field[source_field]
            
            for target_field in target_fields:
                if target_field not in chunks_by_field:
                    continue
                    
                target_chunks = chunks_by_field[target_field]
                
                for source_chunk in source_chunks:
                    for target_chunk in target_chunks:
                        relationships.append({
                            "from": source_chunk["id"],
                            "to": target_chunk["id"],
                            "type": "cross_references",
                            "confidence": 0.7,
                            "bidirectional": True
                        })
        
        return relationships
    
    def detect_containment_relationships(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect containment/composition relationships."""
        relationships = []
        
        # Find main entity chunks (typically name/description)
        main_chunks = [
            chunk for chunk in chunks 
            if chunk.get("source_field", "").split('.')[0] in ["name", "description"]
        ]
        
        # Find detail chunks that could be contained
        detail_chunks = [
            chunk for chunk in chunks
            if chunk.get("source_field", "").split('.')[0] not in ["name", "description"]
        ]
        
        for main_chunk in main_chunks:
            for detail_chunk in detail_chunks:
                # Check if detail field indicates containment
                detail_field = detail_chunk.get("source_field", "")
                
                if '.' in detail_field:  # Nested field suggests containment
                    relationships.append({
                        "from": main_chunk["id"],
                        "to": detail_chunk["id"],
                        "type": "contains",
                        "confidence": 0.8
                    })
        
        return relationships
    
    def create_dependency_relationships(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create dependency relationships."""
        relationships = []
        
        # Define dependency patterns
        dependencies = {
            "hours": ["location"],  # Hours depend on location context
            "contact": ["location"],  # Contact may depend on location
            "menu": ["cuisine"],  # Menu depends on cuisine type
            "price_range": ["menu"]  # Price depends on menu
        }
        
        chunks_by_field = defaultdict(list)
        for chunk in chunks:
            source_field = chunk.get("source_field", "").split('.')[0]
            chunks_by_field[source_field].append(chunk)
        
        for dependent_field, dependency_fields in dependencies.items():
            if dependent_field not in chunks_by_field:
                continue
                
            dependent_chunks = chunks_by_field[dependent_field]
            
            for dependency_field in dependency_fields:
                if dependency_field not in chunks_by_field:
                    continue
                    
                dependency_chunks = chunks_by_field[dependency_field]
                
                for dep_chunk in dependent_chunks:
                    for req_chunk in dependency_chunks:
                        relationships.append({
                            "from": dep_chunk["id"],
                            "to": req_chunk["id"],
                            "type": "depends_on",
                            "confidence": 0.6
                        })
        
        return relationships
    
    def add_relationship_metadata(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add metadata to relationships."""
        for rel in relationships:
            rel["metadata"] = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "confidence": rel.get("confidence", 0.5),
                "strength": self._calculate_relationship_strength(rel),
                "type_category": self._categorize_relationship_type(rel["type"])
            }
        
        return relationships
    
    def _calculate_relationship_strength(self, relationship: Dict[str, Any]) -> str:
        """Calculate relationship strength based on confidence and type."""
        confidence = relationship.get("confidence", 0.5)
        rel_type = relationship.get("type", "")
        
        # Hierarchical relationships are generally stronger
        if rel_type.startswith("has_") or rel_type == "contains":
            base_strength = 0.8
        elif rel_type == "semantically_related":
            base_strength = confidence
        else:
            base_strength = 0.6
        
        final_strength = base_strength * confidence
        
        if final_strength >= 0.8:
            return "strong"
        elif final_strength >= 0.6:
            return "medium"
        else:
            return "weak"
    
    def _categorize_relationship_type(self, rel_type: str) -> str:
        """Categorize relationship type."""
        if rel_type.startswith("has_") or rel_type == "contains":
            return "hierarchical"
        elif rel_type == "semantically_related":
            return "semantic"
        elif rel_type == "temporally_related":
            return "temporal"
        elif rel_type == "depends_on":
            return "dependency"
        elif rel_type == "cross_references":
            return "cross_reference"
        else:
            return "other"
    
    def remove_duplicate_relationships(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate relationships."""
        seen = set()
        deduplicated = []
        
        for rel in relationships:
            # Create a unique key for the relationship
            from_id = rel["from"]
            to_id = rel["to"]
            rel_type = rel["type"]
            
            # For bidirectional relationships, normalize the order
            if rel.get("bidirectional", False):
                key = tuple(sorted([from_id, to_id]) + [rel_type])
            else:
                key = (from_id, to_id, rel_type)
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(rel)
        
        return deduplicated