"""Entity Relationship Tracker for Multi-Page Scraping.

This module tracks relationships between entities across multiple scraped pages,
maintaining parent-child, sibling, and reference relationships for proper
data aggregation and context preservation.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import random
import string


class EntityRelationshipTracker:
    """Tracks relationships between entities across multiple pages."""

    def __init__(self):
        """Initialize the entity relationship tracker."""
        self.entities: Dict[str, Dict] = {}
        self.relationships: Dict[str, Dict] = {}
        self.relationship_index: Dict[str, List[Dict]] = {
            'parent-child': [],
            'sibling': [],
            'reference': []
        }
        self._id_counter = {}

    def create_entity(self, url: str, entity_type: str, entity_id: Optional[str] = None) -> str:
        """Create a new entity with optional custom ID.
        
        Args:
            url: The URL of the entity
            entity_type: Type of entity (restaurant, directory, location, menu)
            entity_id: Optional custom entity ID
            
        Returns:
            The entity ID (generated or provided)
        """
        if entity_id is None:
            entity_id = self._generate_unique_id(entity_type)
        
        self.entities[entity_id] = {
            'url': url,
            'type': entity_type,
            'created_at': datetime.now().isoformat()
        }
        
        # Initialize relationship structure for the entity
        self.relationships[entity_id] = {
            'parent': None,
            'children': [],
            'siblings': [],
            'references': [],
            'referenced_by': [],
            'reference_metadata': {}
        }
        
        return entity_id

    def _generate_unique_id(self, entity_type: str) -> str:
        """Generate a unique ID for an entity based on its type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Unique entity ID with appropriate prefix
        """
        # Determine prefix based on entity type
        prefix_map = {
            'restaurant': 'rest',
            'directory': 'dir',
            'location': 'loc',
            'menu': 'menu'
        }
        prefix = prefix_map.get(entity_type, 'ent')
        
        # Get next counter for this prefix
        if prefix not in self._id_counter:
            self._id_counter[prefix] = 0
        
        # Generate unique ID
        while True:
            self._id_counter[prefix] += 1
            entity_id = f"{prefix}_{self._id_counter[prefix]:03d}"
            
            if entity_id not in self.entities:
                return entity_id

    def track_relationship(self, from_entity: str, to_entity: str, 
                         relationship_type: str, metadata: Optional[Dict] = None) -> bool:
        """Track a relationship between two entities.
        
        Args:
            from_entity: Source entity ID
            to_entity: Target entity ID
            relationship_type: Type of relationship (parent-child, sibling, reference)
            metadata: Optional metadata for the relationship
            
        Returns:
            True if relationship was tracked, False if circular reference detected
        """
        # Ensure both entities exist
        if from_entity not in self.entities or to_entity not in self.entities:
            raise ValueError(f"Entity not found: {from_entity if from_entity not in self.entities else to_entity}")
        
        # Handle different relationship types
        if relationship_type == "parent-child":
            self._track_parent_child(from_entity, to_entity, metadata)
        elif relationship_type == "sibling":
            self._track_sibling(from_entity, to_entity, metadata)
        elif relationship_type == "reference":
            result = self._track_reference(from_entity, to_entity, metadata)
            if result:  # Only add to index if not circular reference
                # Add to relationship index
                index_entry = {
                    'from': from_entity,
                    'to': to_entity,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': metadata or {}
                }
                self.relationship_index[relationship_type].append(index_entry)
            return result
        else:
            raise ValueError(f"Unknown relationship type: {relationship_type}")
        
        # Add to relationship index for non-reference types
        if relationship_type != "reference":
            index_entry = {
                'from': from_entity,
                'to': to_entity,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            self.relationship_index[relationship_type].append(index_entry)
        
        return True

    def _track_parent_child(self, parent: str, child: str, metadata: Optional[Dict] = None):
        """Track parent-child relationship."""
        self.relationships[parent]['children'].append(child)
        self.relationships[child]['parent'] = parent

    def _track_sibling(self, entity1: str, entity2: str, metadata: Optional[Dict] = None):
        """Track sibling relationship (bidirectional)."""
        if entity2 not in self.relationships[entity1]['siblings']:
            self.relationships[entity1]['siblings'].append(entity2)
        if entity1 not in self.relationships[entity2]['siblings']:
            self.relationships[entity2]['siblings'].append(entity1)

    def _track_reference(self, from_entity: str, to_entity: str, metadata: Optional[Dict] = None) -> bool:
        """Track reference relationship with circular reference detection."""
        # Check for circular reference
        if (to_entity in self.relationships and 
            from_entity in self.relationships[to_entity]['references']):
            # Mark as bidirectional instead of creating circular reference
            self.relationships[from_entity]['reference_metadata'][to_entity] = metadata or {}
            self.relationships[from_entity]['reference_metadata'][to_entity]['bidirectional'] = True
            self.relationships[to_entity]['reference_metadata'][from_entity]['bidirectional'] = True
            
            # Still add to index but mark as bidirectional
            index_entry = {
                'from': from_entity,
                'to': to_entity,
                'timestamp': datetime.now().isoformat(),
                'metadata': {**(metadata or {}), 'bidirectional': True}
            }
            self.relationship_index['reference'].append(index_entry)
            return False
        
        # Add reference
        if to_entity not in self.relationships[from_entity]['references']:
            self.relationships[from_entity]['references'].append(to_entity)
        self.relationships[from_entity]['reference_metadata'][to_entity] = metadata or {}
        
        # Add reverse reference
        if from_entity not in self.relationships[to_entity]['referenced_by']:
            self.relationships[to_entity]['referenced_by'].append(from_entity)
        
        return True

    def identify_siblings(self):
        """Automatically identify siblings based on shared parents."""
        for entity_id, rels in self.relationships.items():
            if rels['parent']:
                parent_id = rels['parent']
                # Get all children of the parent
                siblings = self.relationships[parent_id]['children']
                
                # Add all other children as siblings
                for sibling in siblings:
                    if sibling != entity_id:
                        self._track_sibling(entity_id, sibling)

    def query_children(self, parent_id: str) -> List[str]:
        """Query all children of an entity."""
        if parent_id not in self.relationships:
            return []
        return self.relationships[parent_id]['children']

    def query_references(self, entity_id: str) -> List[str]:
        """Query all references from an entity."""
        if entity_id not in self.relationships:
            return []
        return self.relationships[entity_id]['references']

    def query_incoming_references(self, entity_id: str) -> List[str]:
        """Query all incoming references to an entity."""
        if entity_id not in self.relationships:
            return []
        return self.relationships[entity_id]['referenced_by']

    def query_by_type(self, relationship_type: str) -> List[Dict]:
        """Query all relationships of a specific type."""
        return self.relationship_index.get(relationship_type, [])

    def save_index(self, output_dir: str):
        """Save the relationship index to a JSON file.
        
        Args:
            output_dir: Directory to save the index file
        """
        os.makedirs(output_dir, exist_ok=True)
        index_path = os.path.join(output_dir, "relationship_index.json")
        
        data = {
            'entities': self.entities,
            'relationships': self.relationships,
            'relationship_index': self.relationship_index
        }
        
        with open(index_path, 'w') as f:
            f.write(json.dumps(data, indent=2))

    def load_index(self, output_dir: str):
        """Load the relationship index from a JSON file.
        
        Args:
            output_dir: Directory containing the index file
        """
        index_path = os.path.join(output_dir, "relationship_index.json")
        
        with open(index_path, 'r') as f:
            data = json.load(f)
        
        self.entities = data['entities']
        self.relationships = data['relationships']
        self.relationship_index = data['relationship_index']