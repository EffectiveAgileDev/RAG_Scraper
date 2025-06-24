"""Semantic chunking functionality for restaurant content."""
from typing import List, Optional

from src.scraper.multi_strategy_scraper import RestaurantData


class SemanticChunker:
    """Handles semantic chunking of restaurant content."""

    def __init__(self, chunk_size_words: int = 500, overlap_words: int = 50):
        """Initialize semantic chunker."""
        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words

    def chunk_by_semantic_boundaries(self, content: str) -> List[str]:
        """Chunk content by semantic boundaries."""
        # Split content into sections based on double newlines
        sections = content.split("\n\n")

        chunks = []
        current_chunk = []
        current_word_count = 0

        for section in sections:
            section_words = len(section.split())

            # If adding this section would exceed chunk size, finalize current chunk
            if (
                current_word_count + section_words > self.chunk_size_words
                and current_chunk
            ):
                chunk_content = "\n\n".join(current_chunk)
                chunks.append(f"CHUNK_START\n{chunk_content}\nCHUNK_END")

                # Start new chunk with overlap from previous chunk
                if self.overlap_words > 0 and current_chunk:
                    overlap_text = current_chunk[-1]
                    overlap_word_count = len(overlap_text.split())
                    if overlap_word_count <= self.overlap_words:
                        current_chunk = [overlap_text]
                        current_word_count = overlap_word_count
                    else:
                        current_chunk = []
                        current_word_count = 0
                else:
                    current_chunk = []
                    current_word_count = 0

            current_chunk.append(section)
            current_word_count += section_words

        # Add final chunk if there's remaining content
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunks.append(f"CHUNK_START\n{chunk_content}\nCHUNK_END")

        return chunks

    def create_contextual_chunks(
        self,
        restaurant: RestaurantData,
        chunk_content: Optional[str] = None,
        chunk_index: int = 0,
    ) -> str:
        """Create chunks with preserved context."""
        if chunk_content is None:
            # Generate chunk from restaurant data
            content_parts = []

            content_parts.append(f"Restaurant: {restaurant.name}")

            if restaurant.address:
                content_parts.append(f"Address: {restaurant.address}")

            if restaurant.cuisine:
                content_parts.append(f"Cuisine: {restaurant.cuisine}")

            chunk_content = "\n".join(content_parts)

        # Add context header to chunk
        context_header = f"[CHUNK {chunk_index + 1} - {restaurant.name}]"

        return f"{context_header}\n{chunk_content}"

    def handle_overlapping_information(self, content: str) -> List[str]:
        """Handle overlapping information in chunks."""
        # Simple deduplication approach
        lines = content.split("\n")
        unique_lines = []
        seen_lines = set()

        for line in lines:
            line_normalized = line.strip().lower()
            if line_normalized and line_normalized not in seen_lines:
                unique_lines.append(line)
                seen_lines.add(line_normalized)
            elif not line.strip():  # Keep empty lines for formatting
                unique_lines.append(line)

        return ["\n".join(unique_lines)]