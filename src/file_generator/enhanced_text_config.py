"""Enhanced text file generator configuration."""
from typing import Dict, Any
from dataclasses import dataclass

from src.common.generator_base import BaseGeneratorConfig
from src.common.validation_utils import ValidationUtils


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
        """Convert config to dictionary."""
        return {
            "output_directory": self.output_directory,
            "allow_overwrite": self.allow_overwrite,
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedTextFileConfig":
        """Create config from dictionary."""
        return cls(
            output_directory=data.get("output_directory", ""),
            allow_overwrite=data.get("allow_overwrite", False),
            hierarchical_structure=data.get("hierarchical_structure", True),
            entity_organization=data.get("entity_organization", True),
            cross_references=data.get("cross_references", True),
            rag_metadata=data.get("rag_metadata", True),
            category_directories=data.get("category_directories", True),
            comprehensive_indices=data.get("comprehensive_indices", True),
            semantic_chunking=data.get("semantic_chunking", True),
            context_preservation=data.get("context_preservation", True),
            chunk_size_words=data.get("chunk_size_words", 500),
            chunk_overlap_words=data.get("chunk_overlap_words", 50),
            max_cross_references=data.get("max_cross_references", 10),
        )