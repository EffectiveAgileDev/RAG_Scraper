"""Data aggregation for multi-page restaurant data consolidation."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Union
from src.scraper.multi_strategy_scraper import RestaurantData
import re
from difflib import SequenceMatcher


@dataclass
class RestaurantEntity:
    """Enhanced entity representation for multi-page restaurant data."""

    entity_id: str
    name: str
    url: str
    entity_type: str  # restaurant, menu, contact, directory, etc.
    data: Dict[str, Any] = field(default_factory=dict)
    source_info: Optional[Dict[str, Any]] = None
    relationships: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Validate entity has required fields."""
        if not self.entity_id or not self.entity_id.strip():
            raise ValueError("Entity ID cannot be empty")
        if not self.name or not self.name.strip():
            return False
        if not self.url or not self.url.strip():
            return False
        if not self.entity_type or not self.entity_type.strip():
            return False
        return True

    def calculate_similarity(self, other: "RestaurantEntity") -> float:
        """Calculate similarity with another entity (0.0 to 1.0)."""
        if not isinstance(other, RestaurantEntity):
            return 0.0

        # Name similarity (weight: 0.4)
        name_sim = SequenceMatcher(None, self.name.lower(), other.name.lower()).ratio()

        # URL similarity (weight: 0.3)
        url_sim = SequenceMatcher(None, self.url.lower(), other.url.lower()).ratio()

        # Address similarity if available (weight: 0.3)
        addr_sim = 0.0
        self_addr = self.data.get("address", "")
        other_addr = other.data.get("address", "")
        if self_addr and other_addr:
            addr_sim = SequenceMatcher(
                None, self_addr.lower(), other_addr.lower()
            ).ratio()

        # Weighted average
        total_sim = (name_sim * 0.4) + (url_sim * 0.3) + (addr_sim * 0.3)
        return min(1.0, max(0.0, total_sim))


@dataclass
class EntityRelationship:
    """Represents relationship between two entities."""

    parent_id: str
    child_id: str
    relationship_type: str  # parent_child, has_menu, has_contact, etc.
    strength: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate relationship after initialization."""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(
                f"Relationship strength must be between 0.0 and 1.0, got {self.strength}"
            )

    def is_valid(self) -> bool:
        """Validate relationship has required fields."""
        return (
            bool(self.parent_id and self.parent_id.strip())
            and bool(self.child_id and self.child_id.strip())
            and bool(self.relationship_type and self.relationship_type.strip())
            and 0.0 <= self.strength <= 1.0
        )


@dataclass
class HierarchicalNode:
    """Node in a hierarchical data structure."""

    entity: RestaurantEntity
    parent: Optional["HierarchicalNode"] = None
    children: List["HierarchicalNode"] = field(default_factory=list)

    def get_depth(self) -> int:
        """Get depth of this node in the hierarchy."""
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1

    def add_child(self, child: "HierarchicalNode") -> None:
        """Add a child node."""
        child.parent = self
        if child not in self.children:
            self.children.append(child)

    def get_all_descendants(self) -> List["HierarchicalNode"]:
        """Get all descendant nodes."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants


@dataclass
class PageData:
    """Data extracted from a single page."""

    url: str
    page_type: str
    source: str
    restaurant_name: str = ""
    address: str = ""
    phone: str = ""
    hours: str = ""
    price_range: str = ""
    cuisine: str = ""
    website: str = ""
    menu_items: Dict[str, List[str]] = field(default_factory=dict)
    social_media: List[str] = field(default_factory=list)
    confidence: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        """Convert PageData to dictionary."""
        return {
            "url": self.url,
            "page_type": self.page_type,
            "source": self.source,
            "restaurant_name": self.restaurant_name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "website": self.website,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
        }


class DataAggregator:
    """Aggregates restaurant data from multiple pages with conflict resolution."""

    # Source priority (higher = more trustworthy)
    SOURCE_PRIORITY = {"json-ld": 10, "microdata": 7, "heuristic": 1}

    # Page type priority for specific fields
    PAGE_TYPE_PRIORITY = {
        "contact": {"phone": 15, "address": 15, "hours": 15},
        "hours": {"hours": 9},
        "about": {"cuisine": 8, "restaurant_name": 7},
        "menu": {"price_range": 8, "menu_items": 10, "restaurant_name": 3},
        "home": {"restaurant_name": 8, "cuisine": 6},
    }

    def __init__(self):
        """Initialize data aggregator."""
        self.page_data: List[PageData] = []
        self.conflict_resolution_rules = {
            "restaurant_name": self._resolve_restaurant_name,
            "phone": self._resolve_contact_field,
            "address": self._resolve_contact_field,
            "hours": self._resolve_contact_field,
            "price_range": self._resolve_field_by_source,
            "cuisine": self._resolve_field_by_source,
            "menu_items": self._merge_menu_items,
            "social_media": self._merge_social_media,
        }

    def add_page_data(self, page_data: PageData) -> None:
        """Add data from a single page.

        Args:
            page_data: PageData object containing extracted information
        """
        self.page_data.append(page_data)

    def aggregate(self) -> Optional[RestaurantData]:
        """Aggregate all page data into a single RestaurantData object.

        Returns:
            Aggregated RestaurantData or None if no data available
        """
        if not self.page_data:
            return None

        # Initialize aggregated data
        aggregated = RestaurantData()

        # Collect all sources
        sources = list(set(page.source for page in self.page_data))
        aggregated.sources = sources

        # Resolve each field using appropriate strategy
        aggregated.name = self._resolve_restaurant_name()
        aggregated.phone = self._resolve_contact_field("phone")
        aggregated.address = self._clean_address(self._resolve_contact_field("address"))
        aggregated.hours = self._clean_hours(self._resolve_contact_field("hours"))
        aggregated.price_range = self._resolve_field_by_source("price_range")
        aggregated.cuisine = self._resolve_field_by_source("cuisine")
        aggregated.website = self._resolve_website()
        aggregated.menu_items = self._merge_menu_items()
        aggregated.social_media = self._merge_social_media()

        # Calculate overall confidence
        original_confidence = getattr(aggregated, 'confidence', 'unknown')
        new_confidence = self._calculate_overall_confidence()
        print(f"DEBUG: DataAggregator overriding confidence: {original_confidence} -> {new_confidence}")
        print(f"DEBUG: DataAggregator context: {len(self.page_data)} pages, sources: {[p.source for p in self.page_data]}")
        
        # Don't override confidence if this is just single-page data from multiple URLs
        if len(self.page_data) == 1 and original_confidence in ['medium', 'high']:
            print(f"DEBUG: Skipping confidence override for single-page data with good confidence")
            # Keep original confidence for single-page extractions
        else:
            aggregated.confidence = new_confidence

        return aggregated

    def _resolve_restaurant_name(self) -> str:
        """Resolve restaurant name conflicts.

        Returns:
            Best restaurant name from all pages
        """
        candidates = []

        for page in self.page_data:
            if page.restaurant_name and page.restaurant_name.strip():
                source_priority = self.SOURCE_PRIORITY.get(page.source, 0)
                page_priority = self.PAGE_TYPE_PRIORITY.get(page.page_type, {}).get(
                    "restaurant_name", 5
                )

                candidates.append(
                    {
                        "name": page.restaurant_name.strip(),
                        "priority": source_priority + page_priority,
                        "source": page.source,
                        "page_type": page.page_type,
                    }
                )

        if not candidates:
            return ""

        # Sort by priority and return best match
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["name"]

    def _resolve_contact_field(self, field_name: str) -> str:
        """Resolve contact field conflicts (phone, address, hours).

        Args:
            field_name: Name of the field to resolve

        Returns:
            Best value for the contact field
        """
        candidates = []

        for page in self.page_data:
            field_value = getattr(page, field_name, "")
            if field_value and field_value.strip():
                source_priority = self.SOURCE_PRIORITY.get(page.source, 0)
                page_priority = self.PAGE_TYPE_PRIORITY.get(page.page_type, {}).get(
                    field_name, 5
                )

                candidates.append(
                    {
                        "value": field_value.strip(),
                        "priority": source_priority + page_priority,
                        "source": page.source,
                        "page_type": page.page_type,
                    }
                )

        if not candidates:
            return ""

        # Sort by priority and return best match
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["value"]

    def _resolve_field_by_source(self, field_name: str) -> str:
        """Resolve field conflicts primarily by source quality.

        Args:
            field_name: Name of the field to resolve

        Returns:
            Best value based on source priority
        """
        candidates = []

        for page in self.page_data:
            field_value = getattr(page, field_name, "")
            if field_value and field_value.strip():
                source_priority = self.SOURCE_PRIORITY.get(page.source, 0)

                candidates.append(
                    {
                        "value": field_value.strip(),
                        "priority": source_priority,
                        "source": page.source,
                    }
                )

        if not candidates:
            return ""

        # Sort by source priority and return best match
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates[0]["value"]

    def _merge_menu_items(self) -> Dict[str, List[str]]:
        """Merge menu items from all pages.

        Returns:
            Consolidated menu items dictionary
        """
        merged_menu = {}

        for page in self.page_data:
            if not page.menu_items:
                continue

            for section, items in page.menu_items.items():
                if section not in merged_menu:
                    merged_menu[section] = []

                # Add unique items only
                for item in items:
                    if item and item not in merged_menu[section]:
                        merged_menu[section].append(item)

        return merged_menu

    def _merge_social_media(self) -> List[str]:
        """Merge social media links from all pages.

        Returns:
            List of unique social media links
        """
        all_links = set()

        for page in self.page_data:
            if page.social_media:
                for link in page.social_media:
                    if link and link.strip():
                        all_links.add(link.strip())

        return list(all_links)

    def _calculate_overall_confidence(self) -> str:
        """Calculate overall confidence based on sources and data quality.

        Returns:
            Confidence level ('high', 'medium', 'low')
        """
        if not self.page_data:
            return "low"

        # First, check the predominant confidence level from individual pages
        confidence_counts = {'high': 0, 'medium': 0, 'low': 0}
        for page in self.page_data:
            page_confidence = getattr(page, 'confidence', 'low')
            if page_confidence in confidence_counts:
                confidence_counts[page_confidence] += 1
        
        print(f"DEBUG: DataAggregator confidence distribution: {confidence_counts}")
        
        # If majority of pages have medium or high confidence, preserve that
        total_pages = len(self.page_data)
        if confidence_counts['high'] >= total_pages / 2:
            print(f"DEBUG: Majority high confidence ({confidence_counts['high']}/{total_pages}), returning 'high'")
            return 'high'
        elif (confidence_counts['high'] + confidence_counts['medium']) >= total_pages / 2:
            print(f"DEBUG: Majority medium+ confidence ({confidence_counts['high'] + confidence_counts['medium']}/{total_pages}), returning 'medium'")
            return 'medium'
        
        # Otherwise fall back to the original calculation
        # Count high-quality sources (include high-confidence heuristic)
        high_quality_sources = sum(
            1 for page in self.page_data 
            if (page.source in ["json-ld", "microdata"] or 
                (page.source == "heuristic" and getattr(page, 'confidence', 'low') == 'high'))
        )

        # Count number of unique sources
        unique_sources = len(set(page.source for page in self.page_data))

        # Count number of pages with data
        pages_with_data = sum(
            1
            for page in self.page_data
            if any(
                [
                    page.restaurant_name,
                    page.phone,
                    page.address,
                    page.hours,
                    page.cuisine,
                    page.menu_items,
                ]
            )
        )

        # Calculate confidence score
        confidence_score = 0

        # Bonus for structured data sources
        if high_quality_sources >= 2:
            confidence_score += 3
        elif high_quality_sources >= 1:
            confidence_score += 2

        # Bonus for multiple sources
        if unique_sources >= 3:
            confidence_score += 2
        elif unique_sources >= 2:
            confidence_score += 1

        # Bonus for multiple pages with data
        if pages_with_data >= 3:
            confidence_score += 2
        elif pages_with_data >= 2:
            confidence_score += 1

        # Determine confidence level
        if confidence_score >= 5:
            return "high"
        elif confidence_score >= 3:
            return "medium"
        else:
            return "low"

    def get_data_sources_summary(self) -> Dict[str, Any]:
        """Get summary of data sources and their contributions.

        Returns:
            Dictionary summarizing data sources
        """
        summary = {
            "total_pages": len(self.page_data),
            "sources": {},
            "page_types": {},
            "fields_found": set(),
        }

        for page in self.page_data:
            # Count sources
            if page.source not in summary["sources"]:
                summary["sources"][page.source] = 0
            summary["sources"][page.source] += 1

            # Count page types
            if page.page_type not in summary["page_types"]:
                summary["page_types"][page.page_type] = 0
            summary["page_types"][page.page_type] += 1

            # Track fields found
            if page.restaurant_name:
                summary["fields_found"].add("restaurant_name")
            if page.phone:
                summary["fields_found"].add("phone")
            if page.address:
                summary["fields_found"].add("address")
            if page.hours:
                summary["fields_found"].add("hours")
            if page.cuisine:
                summary["fields_found"].add("cuisine")
            if page.price_range:
                summary["fields_found"].add("price_range")
            if page.menu_items:
                summary["fields_found"].add("menu_items")
            if page.social_media:
                summary["fields_found"].add("social_media")

        # Convert set to list for JSON serialization
        summary["fields_found"] = list(summary["fields_found"])

        return summary
    
    def _clean_address(self, address: str) -> str:
        """Clean and format address string."""
        if not address:
            return address
            
        # Fix common spacing issues
        # Add space before city name (e.g., "AvenuePortland" -> "Avenue Portland")
        address = re.sub(r'([a-z])([A-Z])', r'\1 \2', address)
        
        # Add space before state abbreviation (e.g., "Portland, OR97232" -> "Portland, OR 97232")
        address = re.sub(r',\s*([A-Z]{2})(\d{5})', r', \1 \2', address)
        
        # Ensure proper spacing after commas
        address = re.sub(r',\s*', ', ', address)
        
        # Clean up multiple spaces
        address = re.sub(r'\s+', ' ', address)
        
        return address.strip()
    
    def _clean_hours(self, hours: str) -> str:
        """Clean and format hours string."""
        if not hours:
            return hours
            
        # Fix common truncation issues where first letter is missing
        # If hours starts with lowercase letter that should be uppercase
        if hours and hours[0].islower() and hours.startswith(('erved', 'pen', 'losed')):
            # Common fixes
            if hours.startswith('erved'):
                hours = 'S' + hours
            elif hours.startswith('pen'):
                hours = 'O' + hours
            elif hours.startswith('losed'):
                hours = 'C' + hours
                
        return hours.strip()
    
    def _resolve_website(self) -> str:
        """Resolve website URL from page data."""
        # First check if any page has explicit website field
        for page in self.page_data:
            if hasattr(page, 'website') and page.website:
                return page.website
                
        # Otherwise, use the first page URL as website
        if self.page_data and hasattr(self.page_data[0], 'url') and self.page_data[0].url:
            # Extract base URL (domain) from page URL
            url = self.page_data[0].url
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Return the base domain URL
            return f"{parsed.scheme}://{parsed.netloc}/"
            
        return ""

    # Enhanced methods for entity-based aggregation

    def aggregate_entities(
        self, entities: List[RestaurantEntity]
    ) -> List[RestaurantEntity]:
        """Aggregate entities by consolidating similar ones.

        Args:
            entities: List of RestaurantEntity objects to aggregate

        Returns:
            List of aggregated entities
        """
        if not entities:
            return []

        # Group entities by name similarity
        groups = self._group_entities_by_similarity(entities)

        # Aggregate each group
        aggregated = []
        for group in groups:
            if len(group) == 1:
                aggregated.append(group[0])
            else:
                merged_entity = self._merge_entity_group(group)
                aggregated.append(merged_entity)

        return aggregated

    def aggregate_with_relationships(
        self, entities: List[RestaurantEntity], relationships: List[EntityRelationship]
    ) -> List[RestaurantEntity]:
        """Aggregate entities while preserving relationships.

        Args:
            entities: List of entities to aggregate
            relationships: List of relationships between entities

        Returns:
            List of aggregated entities with relationship metadata
        """
        # First aggregate entities
        aggregated_entities = self.aggregate_entities(entities)

        # Add relationship information to entities
        relationship_map = self._build_relationship_map(relationships)

        for entity in aggregated_entities:
            if entity.entity_id in relationship_map:
                entity.relationships = relationship_map[entity.entity_id]
                entity.data["relationships"] = relationship_map[entity.entity_id]

        return aggregated_entities

    def deduplicate_entities(
        self, entities: List[RestaurantEntity]
    ) -> List[RestaurantEntity]:
        """Remove duplicate entities based on URL and name similarity.

        Args:
            entities: List of entities to deduplicate

        Returns:
            List of unique entities with merged data
        """
        if not entities:
            return []

        # Group by exact URL first
        url_groups = {}
        for entity in entities:
            url = entity.url.lower().strip()
            if url not in url_groups:
                url_groups[url] = []
            url_groups[url].append(entity)

        # Merge entities with same URL
        url_merged = []
        for url, group in url_groups.items():
            if len(group) == 1:
                url_merged.append(group[0])
            else:
                merged = self._merge_entity_group(group)
                url_merged.append(merged)

        # Now check for name similarity across different URLs
        return self._deduplicate_by_name_similarity(url_merged)

    def merge_entities(
        self, entities: List[RestaurantEntity], strategy: str = "priority"
    ) -> RestaurantEntity:
        """Merge multiple entities into one using specified strategy.

        Args:
            entities: List of entities to merge
            strategy: Merging strategy ('priority', 'max_value', 'latest')

        Returns:
            Merged entity
        """
        if not entities:
            raise ValueError("Cannot merge empty entity list")

        if len(entities) == 1:
            return entities[0]

        # Use first entity as base
        merged = RestaurantEntity(
            entity_id=entities[0].entity_id,
            name=entities[0].name,
            url=entities[0].url,
            entity_type=entities[0].entity_type,
            data={},
            source_info=entities[0].source_info,
        )

        # Apply merging strategy
        if strategy == "max_value":
            merged.data = self._merge_data_max_value(entities)
        elif strategy == "latest":
            merged.data = self._merge_data_latest(entities)
        else:  # priority strategy
            merged.data = self._merge_data_priority(entities)

        # Preserve source information
        sources = []
        for entity in entities:
            if entity.source_info:
                sources.append(entity.source_info)
        if sources:
            merged.data["sources"] = sources

        return merged

    def create_hierarchical_structure(
        self, entities: List[RestaurantEntity]
    ) -> List[RestaurantEntity]:
        """Create hierarchical structure from flat entity list.

        Args:
            entities: List of entities to organize hierarchically

        Returns:
            List of entities organized in hierarchical order
        """
        # Sort by level if available
        sorted_entities = sorted(entities, key=lambda e: e.data.get("level", 0))

        # Create nodes and maintain hierarchy
        nodes = {}
        root_nodes = []

        for entity in sorted_entities:
            node = HierarchicalNode(entity=entity)
            nodes[entity.entity_id] = node

            # Check if this entity has a parent
            parent_id = entity.data.get("parent")
            if parent_id and parent_id in nodes:
                parent_node = nodes[parent_id]
                parent_node.add_child(node)
            else:
                root_nodes.append(node)

        # Convert back to entity list maintaining hierarchy
        result = []
        for root in root_nodes:
            result.append(root.entity)
            result.extend([desc.entity for desc in root.get_all_descendants()])

        return result

    def create_cross_reference_mapping(
        self, entities: List[RestaurantEntity], relationships: List[EntityRelationship]
    ) -> Dict[str, List[str]]:
        """Create cross-reference mapping between entities.

        Args:
            entities: List of entities
            relationships: List of relationships

        Returns:
            Dictionary mapping entity IDs to related entity IDs
        """
        cross_refs = {}

        # Initialize all entity IDs
        for entity in entities:
            cross_refs[entity.entity_id] = []

        # Add relationships
        for rel in relationships:
            if rel.parent_id in cross_refs:
                cross_refs[rel.parent_id].append(rel.child_id)
            if rel.child_id in cross_refs:
                cross_refs[rel.child_id].append(rel.parent_id)

        return cross_refs

    def _group_entities_by_similarity(
        self, entities: List[RestaurantEntity], threshold: float = 0.8
    ) -> List[List[RestaurantEntity]]:
        """Group entities by name similarity.

        Args:
            entities: List of entities to group
            threshold: Similarity threshold for grouping

        Returns:
            List of entity groups
        """
        groups = []
        used = set()

        for i, entity in enumerate(entities):
            if i in used:
                continue

            group = [entity]
            used.add(i)

            for j, other in enumerate(entities[i + 1 :], i + 1):
                if j in used:
                    continue

                # Check for exact name match first (higher priority)
                if entity.name.strip().lower() == other.name.strip().lower():
                    group.append(other)
                    used.add(j)
                else:
                    # Fall back to similarity calculation
                    similarity = entity.calculate_similarity(other)
                    if similarity >= threshold:
                        group.append(other)
                        used.add(j)

            groups.append(group)

        return groups

    def _merge_entity_group(self, entities: List[RestaurantEntity]) -> RestaurantEntity:
        """Merge a group of similar entities.

        Args:
            entities: List of entities to merge

        Returns:
            Merged entity
        """
        if not entities:
            raise ValueError("Cannot merge empty entity group")

        if len(entities) == 1:
            return entities[0]

        # Use entity with most complete data as base
        base_entity = max(entities, key=lambda e: len(e.data))

        merged = RestaurantEntity(
            entity_id=base_entity.entity_id,
            name=base_entity.name,
            url=base_entity.url,
            entity_type=base_entity.entity_type,
            data={},
            source_info=base_entity.source_info,
        )

        # Merge all data
        merged.data = self._merge_data_priority(entities)

        return merged

    def _build_relationship_map(
        self, relationships: List[EntityRelationship]
    ) -> Dict[str, List[str]]:
        """Build mapping of entity IDs to their relationships.

        Args:
            relationships: List of relationships

        Returns:
            Dictionary mapping entity IDs to relationship info
        """
        rel_map = {}

        for rel in relationships:
            # Add to parent
            if rel.parent_id not in rel_map:
                rel_map[rel.parent_id] = []
            rel_map[rel.parent_id].append(
                {
                    "type": rel.relationship_type,
                    "target": rel.child_id,
                    "strength": rel.strength,
                    "role": "parent",
                }
            )

            # Add to child
            if rel.child_id not in rel_map:
                rel_map[rel.child_id] = []
            rel_map[rel.child_id].append(
                {
                    "type": rel.relationship_type,
                    "target": rel.parent_id,
                    "strength": rel.strength,
                    "role": "child",
                }
            )

        return rel_map

    def _deduplicate_by_name_similarity(
        self, entities: List[RestaurantEntity], threshold: float = 0.9
    ) -> List[RestaurantEntity]:
        """Deduplicate entities by name similarity.

        Args:
            entities: List of entities to deduplicate
            threshold: Similarity threshold for deduplication

        Returns:
            List of deduplicated entities
        """
        if len(entities) <= 1:
            return entities

        result = []
        used = set()

        for i, entity in enumerate(entities):
            if i in used:
                continue

            similar_entities = [entity]
            used.add(i)

            for j, other in enumerate(entities[i + 1 :], i + 1):
                if j in used:
                    continue

                # Calculate name similarity only
                name_sim = SequenceMatcher(
                    None, entity.name.lower(), other.name.lower()
                ).ratio()
                if name_sim >= threshold:
                    similar_entities.append(other)
                    used.add(j)

            # Merge similar entities or keep single entity
            if len(similar_entities) == 1:
                result.append(similar_entities[0])
            else:
                merged = self._merge_entity_group(similar_entities)
                result.append(merged)

        return result

    def _merge_data_priority(self, entities: List[RestaurantEntity]) -> Dict[str, Any]:
        """Merge entity data using priority rules.

        Args:
            entities: List of entities to merge data from

        Returns:
            Merged data dictionary
        """
        merged_data = {}

        # Collect all unique keys
        all_keys = set()
        for entity in entities:
            all_keys.update(entity.data.keys())

        # Merge each field
        for key in all_keys:
            values = []
            for entity in entities:
                if key in entity.data and entity.data[key] is not None:
                    values.append(
                        {
                            "value": entity.data[key],
                            "entity_type": entity.entity_type,
                            "source": entity.source_info,
                        }
                    )

            if values:
                # For numeric fields, use max value; for strings, use most detailed
                if all(isinstance(v["value"], (int, float)) for v in values):
                    best_value = max(values, key=lambda v: v["value"])
                else:
                    # Use most detailed value (longest string)
                    best_value = max(
                        values, key=lambda v: len(str(v["value"])) if v["value"] else 0
                    )
                merged_data[key] = best_value["value"]

        return merged_data

    def _merge_data_max_value(self, entities: List[RestaurantEntity]) -> Dict[str, Any]:
        """Merge entity data by taking maximum values.

        Args:
            entities: List of entities to merge data from

        Returns:
            Merged data dictionary
        """
        merged_data = {}

        # Collect all unique keys
        all_keys = set()
        for entity in entities:
            all_keys.update(entity.data.keys())

        # For each key, take the maximum value
        for key in all_keys:
            values = []
            for entity in entities:
                if key in entity.data and entity.data[key] is not None:
                    values.append(entity.data[key])

            if values:
                try:
                    # Try numeric comparison first
                    numeric_values = [
                        float(v) for v in values if isinstance(v, (int, float))
                    ]
                    if numeric_values:
                        merged_data[key] = max(numeric_values)
                    else:
                        # Fall back to string comparison by length
                        merged_data[key] = max(
                            values, key=lambda v: len(str(v)) if v else 0
                        )
                except (ValueError, TypeError):
                    # Fall back to first value if comparison fails
                    merged_data[key] = values[0]

        return merged_data

    def _merge_data_latest(self, entities: List[RestaurantEntity]) -> Dict[str, Any]:
        """Merge entity data by taking latest values.

        Args:
            entities: List of entities to merge data from

        Returns:
            Merged data dictionary
        """
        merged_data = {}

        # Use last entity's data as base, then override with earlier entities' unique fields
        for entity in reversed(entities):
            for key, value in entity.data.items():
                if value is not None and (
                    key not in merged_data or not merged_data[key]
                ):
                    merged_data[key] = value

        return merged_data
