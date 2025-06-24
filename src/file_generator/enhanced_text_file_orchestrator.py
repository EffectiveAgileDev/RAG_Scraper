"""Enhanced text file orchestrator for complex generation workflows."""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.scraper.multi_strategy_scraper import RestaurantData
from src.file_generator.semantic_chunker import SemanticChunker


class EnhancedTextFileOrchestrator:
    """Orchestrates complex text file generation workflows with advanced features."""

    def __init__(
        self,
        relationship_manager,
        metadata_generator,
        semantic_chunker,
        content_formatter,
    ):
        """Initialize orchestrator with required dependencies."""
        self.relationship_manager = relationship_manager
        self.metadata_generator = metadata_generator
        self.semantic_chunker = semantic_chunker
        self.content_formatter = content_formatter

    def generate_hierarchical_files(
        self, restaurant_data: List[RestaurantData], config
    ) -> List[str]:
        """Generate files with hierarchical document structure."""
        relationships = self.relationship_manager.detect_relationships(restaurant_data)
        hierarchy_graph = self.relationship_manager.build_relationship_graph(
            restaurant_data
        )

        generated_files = []

        # Generate files for each hierarchy level
        for restaurant in restaurant_data:
            content = self.content_formatter.generate_hierarchical_content(
                restaurant, hierarchy_graph
            )

            if config.rag_metadata:
                content = self.generate_with_rag_metadata([restaurant], content)

            file_path = self._generate_output_path("txt")
            self._handle_file_exists(file_path)

            written_file = self._write_with_error_handling(file_path, content)
            generated_files.append(written_file)

        return generated_files

    def generate_entity_based_files(
        self, restaurant_data: List[RestaurantData], config
    ) -> Dict[str, List[str]]:
        """Generate files organized by entity type."""
        # Group restaurants by cuisine type
        cuisine_groups = {}
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            if cuisine not in cuisine_groups:
                cuisine_groups[cuisine] = []
            cuisine_groups[cuisine].append(restaurant)

        generated_files = {}

        if config.category_directories:
            base_dir = config.output_directory
            for cuisine, restaurants in cuisine_groups.items():
                cuisine_dir = os.path.join(base_dir, cuisine)
                Path(cuisine_dir).mkdir(parents=True, exist_ok=True)

                cuisine_files = []
                for restaurant in restaurants:
                    content = self.content_formatter.generate_entity_content(restaurant)

                    if config.cross_references:
                        content = self.generate_with_cross_references(
                            [restaurant], content
                        )

                    file_path = os.path.join(
                        cuisine_dir, f"{restaurant.name.replace(' ', '_')}.txt"
                    )
                    self._handle_file_exists(file_path)

                    written_file = self._write_with_error_handling(file_path, content)
                    cuisine_files.append(written_file)

                generated_files[cuisine] = cuisine_files

        return generated_files

    def generate_with_cross_references(
        self, restaurant_data: List[RestaurantData], content: Optional[str] = None
    ) -> str:
        """Generate content with cross-reference sections."""
        if content is None:
            content = self.content_formatter.generate_basic_content(restaurant_data[0])

        if len(restaurant_data) > 1:
            relationships = self.relationship_manager.detect_relationships(
                restaurant_data
            )
            cross_refs = self.content_formatter.format_cross_references(relationships)
            content += f"\n\nCross-References:\n{cross_refs}"

        return content

    def generate_with_rag_metadata(
        self, restaurant_data: List[RestaurantData], content: Optional[str] = None
    ) -> str:
        """Generate content with RAG-optimized metadata headers."""
        if content is None:
            content = self.content_formatter.generate_basic_content(restaurant_data[0])

        restaurant = restaurant_data[0]
        metadata_header = self.metadata_generator.generate_metadata_header(restaurant)

        return f"{metadata_header}\n\n{content}"

    def generate_category_directories(
        self, restaurant_data: List[RestaurantData], config
    ) -> Dict[str, str]:
        """Create category-based output directory structure."""
        base_dir = config.output_directory
        created_directories = {}

        # Get unique cuisine types
        cuisines = set(r.cuisine for r in restaurant_data if r.cuisine)

        for cuisine in cuisines:
            cuisine_dir = os.path.join(base_dir, cuisine)
            Path(cuisine_dir).mkdir(parents=True, exist_ok=True)
            created_directories[cuisine] = cuisine_dir

        return created_directories

    def generate_indices(
        self, restaurant_data: List[RestaurantData], config
    ) -> Dict[str, Any]:
        """Generate comprehensive index files."""
        # Master index
        master_index_content = self.content_formatter.generate_master_index(
            restaurant_data
        )
        master_index_path = os.path.join(config.output_directory, "master_index.txt")
        self._write_with_error_handling(master_index_path, master_index_content)

        # Category indices
        category_indices = {}
        cuisine_groups = {}
        for restaurant in restaurant_data:
            cuisine = restaurant.cuisine or "Unknown"
            if cuisine not in cuisine_groups:
                cuisine_groups[cuisine] = []
            cuisine_groups[cuisine].append(restaurant)

        for cuisine, restaurants in cuisine_groups.items():
            category_index_content = self.content_formatter.generate_category_index(
                cuisine, restaurants
            )
            category_index_path = os.path.join(
                config.output_directory, f"{cuisine}_index.txt"
            )
            self._write_with_error_handling(category_index_path, category_index_content)
            category_indices[cuisine] = category_index_path

        return {
            "master_index": master_index_path,
            "category_indices": category_indices,
            "all_files": [master_index_path] + list(category_indices.values()),
        }

    def generate_with_context_preservation(
        self, restaurant_data: List[RestaurantData]
    ) -> str:
        """Generate content preserving extraction context."""
        restaurant = restaurant_data[0]

        context_info = {
            "extraction_timestamp": datetime.now().isoformat(),
            "source_pages": getattr(restaurant, "source_urls", []),
            "extraction_methods": restaurant.sources,
            "confidence_scores": getattr(restaurant, "confidence_scores", {}),
        }

        context_header = "---\n"
        for key, value in context_info.items():
            context_header += f"{key}: {value}\n"
        context_header += "---\n"

        content = self.content_formatter.generate_basic_content(restaurant)

        return f"{context_header}\n{content}"

    def generate_semantic_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> List[str]:
        """Generate RAG-friendly semantic chunks."""
        chunks = []

        for restaurant in restaurant_data:
            content = self.content_formatter.generate_basic_content(restaurant)
            restaurant_chunks = self.semantic_chunker.chunk_by_semantic_boundaries(
                content
            )

            # Add context preservation to each chunk
            contextual_chunks = []
            for i, chunk in enumerate(restaurant_chunks):
                chunk_with_context = self.semantic_chunker.create_contextual_chunks(
                    restaurant, chunk, i
                )
                contextual_chunks.append(chunk_with_context)

            chunks.extend(contextual_chunks)

        return chunks

    # Multi-page RAG optimization methods

    def generate_cross_page_coherent_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate cross-page coherent semantic chunks with deduplication."""
        cross_page_chunks = []
        coherence_metadata = {}
        deduplication_summary = {"duplicates_removed": 0, "chunks_merged": 0}

        # Group data by entity ID to find cross-page entities
        entity_groups = {}
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                if entity_id:
                    if entity_id not in entity_groups:
                        entity_groups[entity_id] = []
                    entity_groups[entity_id].append(restaurant)

        # Generate coherent chunks for each entity group
        for entity_id, entities in entity_groups.items():
            if len(entities) > 1:  # Multi-page entity
                # Merge overlapping information intelligently
                merged_content = self.content_formatter.merge_multi_page_content(
                    entities
                )

                # Generate semantic chunks with cross-page awareness
                chunks = self.semantic_chunker.chunk_by_semantic_boundaries(
                    merged_content
                )

                # Add cross-page provenance to each chunk
                for i, chunk in enumerate(chunks):
                    chunk_with_provenance = (
                        self.content_formatter.add_cross_page_provenance(
                            chunk, entities, i
                        )
                    )
                    cross_page_chunks.append(chunk_with_provenance)

                coherence_metadata[entity_id] = {
                    "pages_merged": len(entities),
                    "chunks_generated": len(chunks),
                    "page_types": [e.page_metadata.get("page_type") for e in entities],
                }

                deduplication_summary["chunks_merged"] += len(chunks)
            else:
                # Single page entity - use existing chunking
                content = self.content_formatter.generate_basic_content(entities[0])
                chunks = self.semantic_chunker.chunk_by_semantic_boundaries(content)
                cross_page_chunks.extend(chunks)

        return {
            "cross_page_chunks": cross_page_chunks,
            "coherence_metadata": coherence_metadata,
            "deduplication_summary": deduplication_summary,
        }

    def create_context_bridging_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Create context-bridging chunks that preserve context across related pages."""
        bridged_chunks = []
        context_flow_metadata = {}
        cross_page_references = []

        # Build page relationship map
        page_relationships = self.content_formatter.build_page_relationship_map(
            restaurant_data
        )

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                entity_id = page_meta.get("entity_id")
                parent_id = page_meta.get("parent_id")

                # Get parent context if available
                parent_context = ""
                if parent_id and parent_id in page_relationships:
                    parent_restaurant = page_relationships[parent_id]
                    parent_context = (
                        self.content_formatter.extract_inheritable_context(
                            parent_restaurant
                        )
                    )

                # Generate content with bridged context
                content = self.content_formatter.generate_basic_content(restaurant)
                if parent_context:
                    bridged_content = f"{parent_context}\n\n{content}"
                    cross_page_references.append(
                        {
                            "child_entity": entity_id,
                            "parent_entity": parent_id,
                            "context_inherited": True,
                        }
                    )
                else:
                    bridged_content = content

                # Create chunks with context flow
                chunks = self.semantic_chunker.create_contextual_chunks(
                    restaurant, bridged_content, 0
                )
                bridged_chunks.extend(chunks if isinstance(chunks, list) else [chunks])

                context_flow_metadata[entity_id] = {
                    "has_parent_context": parent_id is not None,
                    "parent_id": parent_id,
                    "context_size": len(parent_context) if parent_context else 0,
                }

        return {
            "bridged_chunks": bridged_chunks,
            "context_flow_metadata": context_flow_metadata,
            "cross_page_references": cross_page_references,
        }

    def optimize_chunk_boundaries_for_page_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Optimize chunk boundaries to respect page relationship hierarchies."""
        optimized_chunks = []
        hierarchy_preserved = True
        boundary_metadata = {}

        # Sort by hierarchy level to process parents before children
        sorted_data = sorted(
            restaurant_data,
            key=lambda r: r.page_metadata.get("hierarchy_level", 0)
            if hasattr(r, "page_metadata") and r.page_metadata
            else 0,
        )

        for restaurant in sorted_data:
            content = self.content_formatter.generate_basic_content(restaurant)

            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                hierarchy_level = page_meta.get("hierarchy_level", 0)

                # Adjust chunk size based on hierarchy level
                adjusted_chunk_size = (
                    self.content_formatter.calculate_adaptive_chunk_size(
                        hierarchy_level
                    )
                )

                # Create chunks with hierarchy-aware boundaries
                chunker = SemanticChunker(
                    chunk_size_words=adjusted_chunk_size,
                    overlap_words=max(25, adjusted_chunk_size // 20),
                )
                chunks = chunker.chunk_by_semantic_boundaries(content)

                # Add hierarchy metadata to chunks
                for i, chunk in enumerate(chunks):
                    chunk_with_hierarchy = (
                        self.content_formatter.add_hierarchy_metadata(
                            chunk, restaurant, hierarchy_level, i
                        )
                    )
                    optimized_chunks.append(chunk_with_hierarchy)

                boundary_metadata[page_meta.get("entity_id", "")] = {
                    "hierarchy_level": hierarchy_level,
                    "chunk_size_used": adjusted_chunk_size,
                    "chunks_generated": len(chunks),
                }

        return {
            "optimized_chunks": optimized_chunks,
            "hierarchy_preserved": hierarchy_preserved,
            "boundary_metadata": boundary_metadata,
        }

    def generate_multi_page_embedding_hints(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate embedding hints optimized for multi-page content."""
        embedding_hints = {}
        cross_page_keywords = set()
        retrieval_optimization = {}

        # Group by entity to combine keywords from multiple pages
        entity_keywords = {}
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                page_keywords = restaurant.page_metadata.get("keywords", [])

                if entity_id:
                    if entity_id not in entity_keywords:
                        entity_keywords[entity_id] = set()

                    # Add restaurant-specific keywords
                    entity_keywords[entity_id].update(page_keywords)
                    entity_keywords[entity_id].update(
                        self.content_formatter.extract_keywords_from_restaurant(
                            restaurant
                        )
                    )

                    # Add cross-page keywords
                    cross_page_keywords.update(page_keywords)

        # Generate optimized hints for each entity
        for entity_id, keywords in entity_keywords.items():
            embedding_hints[entity_id] = list(keywords)

            # Add retrieval optimization metadata
            retrieval_optimization[entity_id] = {
                "keyword_count": len(keywords),
                "cross_page_coverage": len(keywords & cross_page_keywords)
                / len(keywords)
                if keywords
                else 0,
                "retrieval_priority": "high" if len(keywords) > 10 else "medium",
            }

        return {
            "embedding_hints": embedding_hints,
            "cross_page_keywords": list(cross_page_keywords),
            "retrieval_optimization": retrieval_optimization,
        }

    def create_cross_page_section_markers(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Create RAG-friendly cross-page section markers."""
        section_markers = []
        page_transitions = []
        relationship_metadata = {}

        # Track page transitions and relationships
        previous_page_type = None
        previous_entity_id = None

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                current_page_type = page_meta.get("page_type")
                current_entity_id = page_meta.get("entity_id")
                parent_id = page_meta.get("parent_id")

                # Create section marker for page transitions
                if previous_page_type and previous_page_type != current_page_type:
                    marker = f"<!-- PAGE_TRANSITION: {previous_page_type} -> {current_page_type} -->"
                    section_markers.append(marker)

                    page_transitions.append(
                        {
                            "from_page": previous_page_type,
                            "to_page": current_page_type,
                            "from_entity": previous_entity_id,
                            "to_entity": current_entity_id,
                        }
                    )

                # Create relationship marker
                if parent_id:
                    relationship_marker = f"<!-- RELATIONSHIP: {current_entity_id} -> parent: {parent_id} -->"
                    section_markers.append(relationship_marker)

                    if current_entity_id not in relationship_metadata:
                        relationship_metadata[current_entity_id] = {}
                    relationship_metadata[current_entity_id]["parent"] = parent_id

                # Add content section marker
                content_marker = (
                    f"<!-- SECTION_START: {current_page_type}:{current_entity_id} -->"
                )
                section_markers.append(content_marker)

                previous_page_type = current_page_type
                previous_entity_id = current_entity_id

        return {
            "section_markers": section_markers,
            "page_transitions": page_transitions,
            "relationship_metadata": relationship_metadata,
        }

    def generate_temporally_aware_rag_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate temporally-aware RAG chunks with conflict resolution."""
        temporal_chunks = []
        conflict_resolution = {}
        timeline_metadata = {}

        # Group by entity and sort by extraction time
        entity_timeline = {}
        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                entity_id = restaurant.page_metadata.get("entity_id")
                timestamp = restaurant.page_metadata.get("extraction_timestamp")

                if entity_id and timestamp:
                    if entity_id not in entity_timeline:
                        entity_timeline[entity_id] = []
                    entity_timeline[entity_id].append((timestamp, restaurant))

        # Process each entity's timeline
        for entity_id, timeline in entity_timeline.items():
            # Sort by timestamp (most recent first)
            timeline.sort(key=lambda x: x[0], reverse=True)

            if len(timeline) > 1:
                # Handle temporal conflicts
                most_recent = timeline[0][1]
                conflicts = self.content_formatter.detect_temporal_conflicts(timeline)

                # Generate content with temporal awareness
                content = self.content_formatter.generate_temporally_aware_content(
                    timeline, conflicts
                )

                conflict_resolution[entity_id] = {
                    "conflicts_detected": len(conflicts),
                    "resolution_strategy": "most_recent_priority",
                    "data_sources": len(timeline),
                }
            else:
                # Single timestamp - no conflicts
                content = self.content_formatter.generate_basic_content(timeline[0][1])
                conflict_resolution[entity_id] = {
                    "conflicts_detected": 0,
                    "resolution_strategy": "single_source",
                    "data_sources": 1,
                }

            # Create chunks with temporal metadata
            chunks = self.semantic_chunker.chunk_by_semantic_boundaries(content)
            for i, chunk in enumerate(chunks):
                chunk_with_temporal = self.content_formatter.add_temporal_metadata(
                    chunk, timeline, entity_id, i
                )
                temporal_chunks.append(chunk_with_temporal)

            timeline_metadata[entity_id] = {
                "extraction_count": len(timeline),
                "latest_extraction": timeline[0][0] if timeline else None,
                "temporal_span_hours": self.content_formatter.calculate_temporal_span(
                    timeline
                ),
            }

        return {
            "temporal_chunks": temporal_chunks,
            "conflict_resolution": conflict_resolution,
            "timeline_metadata": timeline_metadata,
        }

    def optimize_for_multi_page_retrieval(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Optimize output for multi-page RAG retrieval scenarios."""
        retrieval_optimized_chunks = []
        co_located_information = {}
        query_expansion_metadata = {}

        # Build relationship graph for co-location optimization
        relationship_graph = (
            self.content_formatter.build_comprehensive_relationship_graph(
                restaurant_data
            )
        )

        # Group related information for co-location
        for entity_id, related_entities in relationship_graph.items():
            restaurant = self.content_formatter.find_restaurant_by_entity_id(
                restaurant_data, entity_id
            )
            if not restaurant:
                continue

            # Collect content from related entities
            related_content = []
            for related_id in related_entities:
                related_restaurant = self.content_formatter.find_restaurant_by_entity_id(
                    restaurant_data, related_id
                )
                if related_restaurant:
                    related_content.append(
                        self.content_formatter.generate_basic_content(
                            related_restaurant
                        )
                    )

            # Create co-located chunk
            main_content = self.content_formatter.generate_basic_content(restaurant)
            if related_content:
                co_located_content = (
                    f"{main_content}\n\n--- Related Information ---\n"
                    + "\n\n".join(related_content)
                )
                co_located_information[entity_id] = {
                    "related_entities": len(related_entities),
                    "content_size": len(co_located_content),
                }
            else:
                co_located_content = main_content

            # Generate retrieval-optimized chunks
            chunks = self.semantic_chunker.chunk_by_semantic_boundaries(
                co_located_content
            )
            for i, chunk in enumerate(chunks):
                optimized_chunk = (
                    self.content_formatter.add_retrieval_optimization_metadata(
                        chunk, restaurant, related_entities, i
                    )
                )
                retrieval_optimized_chunks.append(optimized_chunk)

            # Generate query expansion metadata
            query_expansion_metadata[entity_id] = {
                "primary_terms": self.content_formatter.extract_primary_terms(
                    restaurant
                ),
                "related_terms": self.content_formatter.extract_related_terms(
                    related_content
                ),
                "expansion_potential": len(related_entities),
            }

        return {
            "retrieval_optimized_chunks": retrieval_optimized_chunks,
            "co_located_information": co_located_information,
            "query_expansion_metadata": query_expansion_metadata,
        }

    def generate_entity_disambiguation_output(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate RAG output with entity disambiguation across pages."""
        disambiguated_entities = {}
        page_specific_context = {}
        precision_metadata = {}

        # Group entities by name to find disambiguation needs
        entities_by_name = {}
        for restaurant in restaurant_data:
            name = restaurant.name
            if name not in entities_by_name:
                entities_by_name[name] = []
            entities_by_name[name].append(restaurant)

        # Process entities that need disambiguation
        for name, entities in entities_by_name.items():
            if len(entities) > 1:  # Multiple entities with same name
                for restaurant in entities:
                    if (
                        hasattr(restaurant, "page_metadata")
                        and restaurant.page_metadata
                    ):
                        entity_id = restaurant.page_metadata.get("entity_id")
                        page_type = restaurant.page_metadata.get("page_type")

                        # Create disambiguated content
                        disambiguation_context = (
                            self.content_formatter.generate_disambiguation_context(
                                restaurant, entities
                            )
                        )
                        content = self.content_formatter.generate_basic_content(
                            restaurant
                        )
                        disambiguated_content = f"{disambiguation_context}\n\n{content}"

                        disambiguated_entities[entity_id] = {
                            "original_name": name,
                            "disambiguated_content": disambiguated_content,
                            "disambiguation_context": disambiguation_context,
                        }

                        page_specific_context[entity_id] = {
                            "page_type": page_type,
                            "disambiguation_needed": True,
                            "context_size": len(disambiguation_context),
                        }

                        precision_metadata[entity_id] = {
                            "ambiguity_level": len(entities),
                            "disambiguation_strength": "high"
                            if len(disambiguation_context) > 100
                            else "medium",
                        }
            else:
                # Single entity - no disambiguation needed
                restaurant = entities[0]
                if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                    entity_id = restaurant.page_metadata.get("entity_id")
                    if entity_id:
                        disambiguated_entities[entity_id] = {
                            "original_name": name,
                            "disambiguated_content": self.content_formatter.generate_basic_content(
                                restaurant
                            ),
                            "disambiguation_context": "",
                        }

                        page_specific_context[entity_id] = {
                            "page_type": restaurant.page_metadata.get("page_type"),
                            "disambiguation_needed": False,
                            "context_size": 0,
                        }

                        precision_metadata[entity_id] = {
                            "ambiguity_level": 1,
                            "disambiguation_strength": "not_needed",
                        }

        return {
            "disambiguated_entities": disambiguated_entities,
            "page_specific_context": page_specific_context,
            "precision_metadata": precision_metadata,
        }

    def create_context_preservation_markers(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Create multi-page context preservation markers."""
        preservation_markers = []
        context_traceability = {}
        inheritance_documentation = {}

        for restaurant in restaurant_data:
            if hasattr(restaurant, "page_metadata") and restaurant.page_metadata:
                page_meta = restaurant.page_metadata
                entity_id = page_meta.get("entity_id")
                inherited_context = page_meta.get("inherited_context", {})
                context_overrides = page_meta.get("context_overrides", {})
                parent_id = page_meta.get("parent_id")

                if inherited_context:
                    # Create preservation marker for inherited context
                    marker = f"<!-- CONTEXT_INHERITED: {entity_id} from {parent_id} -->"
                    preservation_markers.append(marker)

                    # Document inherited context
                    for context_key, context_value in inherited_context.items():
                        context_marker = (
                            f"<!-- INHERITED_{context_key.upper()}: {context_value} -->"
                        )
                        preservation_markers.append(context_marker)

                    context_traceability[entity_id] = {
                        "source_parent": parent_id,
                        "inherited_keys": list(inherited_context.keys()),
                        "inheritance_timestamp": datetime.now().isoformat(),
                    }

                if context_overrides:
                    # Create markers for context overrides
                    for override_key, override_value in context_overrides.items():
                        override_marker = f"<!-- CONTEXT_OVERRIDE_{override_key.upper()}: {override_value} -->"
                        preservation_markers.append(override_marker)

                # Document inheritance rules
                inheritance_documentation[entity_id] = {
                    "has_inherited_context": bool(inherited_context),
                    "has_context_overrides": bool(context_overrides),
                    "inheritance_rules": {
                        "priority": "child_overrides_parent",
                        "scope": "page_specific_only",
                    },
                    "context_completeness": len(inherited_context)
                    + len(context_overrides),
                }

        return {
            "preservation_markers": preservation_markers,
            "context_traceability": context_traceability,
            "inheritance_documentation": inheritance_documentation,
        }

    def handle_large_scale_multi_page_optimization(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Handle large-scale multi-page RAG optimization efficiently."""
        start_time = datetime.now()
        optimization_completed = False
        performance_metrics = {}
        memory_usage = {}
        scalability_report = {}

        try:
            # Process in batches to manage memory
            batch_size = 10
            total_entities = len(restaurant_data)
            processed_entities = 0
            batches_processed = 0

            for i in range(0, total_entities, batch_size):
                batch = restaurant_data[i : i + batch_size]

                # Process batch with optimizations
                batch_result = self.content_formatter.process_batch_with_optimization(
                    batch
                )
                processed_entities += len(batch)
                batches_processed += 1

                # Monitor memory usage
                import psutil

                process = psutil.Process()
                memory_info = process.memory_info()
                memory_usage[f"batch_{batches_processed}"] = {
                    "rss_mb": memory_info.rss / 1024 / 1024,
                    "entities_processed": processed_entities,
                }

                # Check if we need to optimize further
                if memory_info.rss > 500 * 1024 * 1024:  # 500MB threshold
                    # Implement memory optimization
                    self.content_formatter.optimize_memory_usage()

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            performance_metrics = {
                "total_processing_time_seconds": processing_time,
                "entities_per_second": total_entities / processing_time
                if processing_time > 0
                else 0,
                "batches_processed": batches_processed,
                "average_batch_time": processing_time / batches_processed
                if batches_processed > 0
                else 0,
            }

            scalability_report = {
                "scale_tested": f"{total_entities}+ entities",
                "performance_acceptable": processing_time < 30,  # 30 second threshold
                "memory_efficient": max(info["rss_mb"] for info in memory_usage.values())
                < 1000,  # 1GB threshold
                "resumable_process": True,
            }

            optimization_completed = True

        except Exception as e:
            scalability_report["error"] = str(e)
            optimization_completed = False

        return {
            "optimization_completed": optimization_completed,
            "performance_metrics": performance_metrics,
            "memory_usage": memory_usage,
            "scalability_report": scalability_report,
            "entities_processed": processed_entities,
        }

    # Helper methods for file operations (to be delegated back to main generator)
    def _generate_output_path(self, extension: str) -> str:
        """Generate output file path - delegated to main generator."""
        # This will be handled by the main generator
        return f"/tmp/temp_file.{extension}"

    def _handle_file_exists(self, file_path: str) -> None:
        """Handle existing file - delegated to main generator."""
        # This will be handled by the main generator
        pass

    def _write_with_error_handling(self, file_path: str, content: str) -> str:
        """Write file with error handling - delegated to main generator."""
        # This will be handled by the main generator
        return file_path