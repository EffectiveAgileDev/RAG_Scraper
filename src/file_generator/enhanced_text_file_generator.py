"""Enhanced text file generator for RAG systems with advanced features."""
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from src.scraper.multi_strategy_scraper import RestaurantData
from src.common.generator_base import BaseFileGenerator, BaseGeneratorConfig
from src.common.validation_utils import ValidationUtils
from src.file_generator.entity_relationship_manager import EntityRelationshipManager
from src.file_generator.rag_metadata_generator import RAGMetadataGenerator
from src.file_generator.semantic_chunker import SemanticChunker
from src.file_generator.enhanced_text_content_formatter import EnhancedTextContentFormatter
from src.file_generator.enhanced_text_file_orchestrator import EnhancedTextFileOrchestrator


@dataclass
class EnhancedTextFileConfig(BaseGeneratorConfig):
    """Enhanced configuration for text file generation."""

    hierarchical_structure: bool = True
    entity_organization: bool = True
    cross_references: bool = True
    rag_metadata: bool = True
    category_directories: bool = True
    comprehensive_indices: bool = True
    semantic_chunking: bool = True
    context_preservation: bool = True
    chunk_size_words: int = 500
    chunk_overlap_words: int = 50
    max_cross_references: int = 10

    def validate(self) -> None:
        """Validate configuration values."""
        validation_error = ValidationUtils.validate_not_empty(
            self.output_directory, "output_directory"
        )
        if validation_error:
            raise ValueError(validation_error)

        validation_error = ValidationUtils.validate_positive_number(
            self.chunk_size_words, "chunk_size_words"
        )
        if validation_error:
            raise ValueError(validation_error)

        validation_error = ValidationUtils.validate_positive_number(
            self.chunk_overlap_words, "chunk_overlap_words"
        )
        if validation_error:
            raise ValueError(validation_error)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "output_directory": self.output_directory,
            "allow_overwrite": self.allow_overwrite,
            "filename_pattern": self.filename_pattern,
            "hierarchical_structure": self.hierarchical_structure,
            "entity_organization": self.entity_organization,
            "cross_references": self.cross_references,
            "rag_metadata": self.rag_metadata,
            "category_directories": self.category_directories,
            "comprehensive_indices": self.comprehensive_indices,
            "semantic_chunking": self.semantic_chunking,
            "context_preservation": self.context_preservation,
            "chunk_size_words": self.chunk_size_words,
            "chunk_overlap_words": self.chunk_overlap_words,
            "max_cross_references": self.max_cross_references,
        }


class EnhancedTextFileGenerator(BaseFileGenerator):
    """Enhanced text file generator with hierarchical structure and RAG optimization."""

    def __init__(self, config: Optional[EnhancedTextFileConfig] = None):
        """Initialize enhanced text file generator."""
        if config is None:
            config = EnhancedTextFileConfig()

        super().__init__(config)
        self.config = config

        # Initialize helper components
        self.relationship_manager = EntityRelationshipManager()
        self.metadata_generator = RAGMetadataGenerator()
        self.semantic_chunker = SemanticChunker(
            chunk_size_words=config.chunk_size_words,
            overlap_words=config.chunk_overlap_words,
        )
        self.content_formatter = EnhancedTextContentFormatter(
            chunk_size_words=config.chunk_size_words,
            chunk_overlap_words=config.chunk_overlap_words,
            max_cross_references=config.max_cross_references,
        )
        
        # Initialize orchestrator with dependencies
        self.orchestrator = EnhancedTextFileOrchestrator(
            relationship_manager=self.relationship_manager,
            metadata_generator=self.metadata_generator,
            semantic_chunker=self.semantic_chunker,
            content_formatter=self.content_formatter,
        )
        
        # Ensure orchestrator has access to proper file handling methods
        self._setup_orchestrator_file_handling()

    def _setup_orchestrator_file_handling(self):
        """Set up orchestrator with proper file handling methods from base class."""
        self.orchestrator._generate_output_path = self._generate_output_path
        self.orchestrator._handle_file_exists = self._handle_file_exists
        self.orchestrator._write_with_error_handling = self._write_with_error_handling

    def generate_file(self, restaurant_data: List[RestaurantData], **kwargs) -> str:
        """Generate enhanced text files from restaurant data."""
        return self.generate_files(restaurant_data, **kwargs)

    def generate_files(
        self, restaurant_data: List[RestaurantData], **kwargs
    ) -> List[str]:
        """Generate enhanced text files with all enabled features."""
        self._validate_input_data(restaurant_data)
        self._validate_write_permissions()

        generated_files = []

        if self.config.entity_organization:
            generated_files.extend(self.generate_entity_based_files(restaurant_data))

        if self.config.hierarchical_structure:
            generated_files.extend(self.generate_hierarchical_files(restaurant_data))

        if self.config.comprehensive_indices:
            index_files = self.generate_indices(restaurant_data)
            generated_files.extend(index_files.get("all_files", []))

        return generated_files

    def generate_hierarchical_files(
        self, restaurant_data: List[RestaurantData]
    ) -> List[str]:
        """Generate files with hierarchical document structure."""
        # Orchestrator already has file handling methods from constructor
        return self.orchestrator.generate_hierarchical_files(restaurant_data, self.config)

    def generate_entity_based_files(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, List[str]]:
        """Generate files organized by entity type."""
        # Orchestrator already has file handling methods from constructor
        return self.orchestrator.generate_entity_based_files(restaurant_data, self.config)

    def generate_with_cross_references(
        self, restaurant_data: List[RestaurantData], content: Optional[str] = None
    ) -> str:
        """Generate content with cross-reference sections."""
        return self.orchestrator.generate_with_cross_references(restaurant_data, content)

    def generate_with_rag_metadata(
        self, restaurant_data: List[RestaurantData], content: Optional[str] = None
    ) -> str:
        """Generate content with RAG-optimized metadata headers."""
        return self.orchestrator.generate_with_rag_metadata(restaurant_data, content)

    def generate_category_directories(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, str]:
        """Create category-based output directory structure."""
        return self.orchestrator.generate_category_directories(restaurant_data, self.config)

    def generate_indices(self, restaurant_data: List[RestaurantData]) -> Dict[str, Any]:
        """Generate comprehensive index files."""
        # Delegate to orchestrator with file handling setup
        self.orchestrator._write_with_error_handling = self._write_with_error_handling
        
        return self.orchestrator.generate_indices(restaurant_data, self.config)

    def generate_with_context_preservation(
        self, restaurant_data: List[RestaurantData]
    ) -> str:
        """Generate content preserving extraction context."""
        return self.orchestrator.generate_with_context_preservation(restaurant_data)

    def generate_semantic_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> List[str]:
        """Generate RAG-friendly semantic chunks."""
        return self.orchestrator.generate_semantic_chunks(restaurant_data)

    def validate_output_integrity(self, generated_files: List[str]) -> Dict[str, Any]:
        """Validate output file integrity."""
        validation_result = {
            "valid": True,
            "required_files_present": True,
            "cross_references_valid": True,
            "metadata_complete": True,
            "issues": [],
        }

        # Check that all files exist
        for file_path in generated_files:
            if not os.path.exists(file_path):
                validation_result["required_files_present"] = False
                validation_result["issues"].append(f"Missing file: {file_path}")

        # Validate file contents
        for file_path in generated_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if not content.strip():
                        validation_result["issues"].append(f"Empty file: {file_path}")

                except Exception as e:
                    validation_result["issues"].append(
                        f"Error reading file {file_path}: {str(e)}"
                    )

        validation_result["valid"] = len(validation_result["issues"]) == 0

        return validation_result


    # Multi-page RAG optimization methods (delegated to orchestrator)

    def generate_cross_page_coherent_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate cross-page coherent semantic chunks with deduplication."""
        return self.orchestrator.generate_cross_page_coherent_chunks(restaurant_data)

    def create_context_bridging_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Create context-bridging chunks that preserve context across related pages."""
        return self.orchestrator.create_context_bridging_chunks(restaurant_data)

    def optimize_chunk_boundaries_for_page_relationships(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Optimize chunk boundaries to respect page relationship hierarchies."""
        return self.orchestrator.optimize_chunk_boundaries_for_page_relationships(restaurant_data)

    def generate_multi_page_embedding_hints(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate embedding hints optimized for multi-page content."""
        return self.orchestrator.generate_multi_page_embedding_hints(restaurant_data)

    def create_cross_page_section_markers(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Create RAG-friendly cross-page section markers."""
        return self.orchestrator.create_cross_page_section_markers(restaurant_data)

    def generate_temporally_aware_rag_chunks(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate temporally-aware RAG chunks with conflict resolution."""
        return self.orchestrator.generate_temporally_aware_rag_chunks(restaurant_data)

    def optimize_for_multi_page_retrieval(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Optimize output for multi-page RAG retrieval scenarios."""
        return self.orchestrator.optimize_for_multi_page_retrieval(restaurant_data)

    def generate_entity_disambiguation_output(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Generate RAG output with entity disambiguation across pages."""
        return self.orchestrator.generate_entity_disambiguation_output(restaurant_data)

    def create_context_preservation_markers(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Create multi-page context preservation markers."""
        return self.orchestrator.create_context_preservation_markers(restaurant_data)

    def handle_large_scale_multi_page_optimization(
        self, restaurant_data: List[RestaurantData]
    ) -> Dict[str, Any]:
        """Handle large-scale multi-page RAG optimization efficiently."""
        return self.orchestrator.handle_large_scale_multi_page_optimization(restaurant_data)



