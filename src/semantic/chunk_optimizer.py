"""ChunkOptimizer for optimizing chunk boundaries and sizes for RAG systems."""

import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class ChunkBoundary:
    """Represents a potential chunk boundary."""
    
    position: int
    boundary_type: str  # "sentence", "paragraph", "word"
    confidence: float
    
    def __post_init__(self):
        """Validate chunk boundary data."""
        if self.position < 0:
            raise ValueError("position must be non-negative")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")
    
    def __lt__(self, other):
        """Enable sorting by position."""
        return self.position < other.position
    
    def __eq__(self, other):
        """Enable equality comparison."""
        if not isinstance(other, ChunkBoundary):
            return False
        return (self.position == other.position and 
                self.boundary_type == other.boundary_type)
    
    def __hash__(self):
        """Enable hashing for set operations."""
        return hash((self.position, self.boundary_type))


class ChunkOptimizer:
    """Optimizes chunk boundaries and sizes for semantic coherence."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize chunk optimizer."""
        self.config = config or {}
        self.max_chunk_size = self.config.get('max_chunk_size', 512)
        self.min_chunk_size = self.config.get('min_chunk_size', 50)
        self.overlap_size = self.config.get('overlap_size', 50)
        self.preserve_sentences = self.config.get('preserve_sentences', True)
        
        # Compile regex patterns for efficiency
        self.sentence_pattern = re.compile(r'[.!?]+\s+')
        self.paragraph_pattern = re.compile(r'\n\s*\n')
        self.word_pattern = re.compile(r'\s+')
    
    def optimize_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize existing chunks for better semantic coherence."""
        optimized = []
        
        for chunk in chunks:
            content = chunk["content"]
            word_count = len(content.split())
            
            if word_count > self.max_chunk_size:
                # Split large chunks
                split_chunks = self._split_chunk(chunk)
                optimized.extend(split_chunks)
            else:
                optimized.append(chunk.copy())
        
        # Merge small chunks if needed (but only if we actually want merging)
        # Note: Don't merge if splitting created many small chunks
        if self.min_chunk_size > 0 and len(optimized) == len(chunks):
            optimized = self.merge_small_chunks(optimized)
        
        # Add overlap information
        optimized = self.add_contextual_overlap(optimized)
        
        return optimized
    
    def _split_chunk(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a large chunk into smaller ones."""
        content = chunk["content"]
        base_id = chunk["id"]
        
        # Find optimal boundaries
        boundaries = self.find_optimal_boundaries(content, self.max_chunk_size)
        
        if not boundaries:
            # Fallback to simple word-based splitting
            return self._split_by_words(chunk)
        
        # Create chunks based on boundaries
        split_chunks = []
        last_pos = 0
        
        for i, boundary in enumerate(boundaries):
            boundary_pos = boundary.position if isinstance(boundary, ChunkBoundary) else boundary["position"]
            
            chunk_content = content[last_pos:boundary_pos].strip()
            if chunk_content:
                new_chunk = {
                    "id": f"{base_id}_split_{i+1}",
                    "content": chunk_content,
                    "type": chunk.get("type", "text"),
                    "metadata": {
                        **chunk.get("metadata", {}),
                        "split_from": base_id,
                        "split_index": i + 1,
                        "boundary_type": boundary.boundary_type if isinstance(boundary, ChunkBoundary) else boundary["boundary_type"]
                    }
                }
                split_chunks.append(new_chunk)
            
            last_pos = boundary_pos
        
        # Add final chunk if there's remaining content
        remaining_content = content[last_pos:].strip()
        if remaining_content:
            final_chunk = {
                "id": f"{base_id}_split_{len(boundaries)+1}",
                "content": remaining_content,
                "type": chunk.get("type", "text"),
                "metadata": {
                    **chunk.get("metadata", {}),
                    "split_from": base_id,
                    "split_index": len(boundaries) + 1,
                    "boundary_type": "end"
                }
            }
            split_chunks.append(final_chunk)
        
        return split_chunks
    
    def _split_by_words(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback word-based splitting."""
        content = chunk["content"]
        words = content.split()
        base_id = chunk["id"]
        
        split_chunks = []
        chunk_num = 1
        
        for i in range(0, len(words), self.max_chunk_size):
            chunk_words = words[i:i + self.max_chunk_size]
            chunk_content = ' '.join(chunk_words)
            
            new_chunk = {
                "id": f"{base_id}_word_{chunk_num}",
                "content": chunk_content,
                "type": chunk.get("type", "text"),
                "metadata": {
                    **chunk.get("metadata", {}),
                    "split_from": base_id,
                    "split_method": "word_based",
                    "word_count": len(chunk_words)
                }
            }
            split_chunks.append(new_chunk)
            chunk_num += 1
        
        return split_chunks
    
    def find_optimal_boundaries(self, text: str, max_size: int) -> List[ChunkBoundary]:
        """Find optimal boundaries for chunking."""
        boundaries = []
        words = text.split()
        
        # Always find boundaries, even for short text (for testing and flexibility)
        # Real chunking decisions happen at higher levels
        
        # Find paragraph boundaries (highest priority)
        for match in self.paragraph_pattern.finditer(text):
            pos = match.end()
            words_before = len(text[:pos].split())
            if 1 <= words_before <= max_size:  # Allow smaller chunks for natural boundaries
                boundaries.append(ChunkBoundary(
                    position=pos,
                    boundary_type="paragraph",
                    confidence=0.9
                ))
        
        # Find sentence boundaries (medium priority)
        for match in self.sentence_pattern.finditer(text):
            pos = match.end()
            words_before = len(text[:pos].split())
            if 1 <= words_before <= max_size:  # Allow smaller chunks for natural boundaries
                boundaries.append(ChunkBoundary(
                    position=pos,
                    boundary_type="sentence", 
                    confidence=0.7
                ))
        
        # If no good boundaries found, create word boundaries
        if not boundaries:
            current_pos = 0
            word_count = 0
            
            for i, word in enumerate(words):
                word_count += 1
                # Find word position more reliably
                word_start = text.find(word, current_pos)
                current_pos = word_start + len(word)
                
                if word_count >= max_size and i < len(words) - 1:  # Don't add boundary at end
                    # Find next space after the word
                    space_pos = text.find(' ', current_pos)
                    if space_pos > 0:
                        current_pos = space_pos + 1
                    
                    boundaries.append(ChunkBoundary(
                        position=current_pos,
                        boundary_type="word",
                        confidence=0.3
                    ))
                    word_count = 0
        
        # Sort boundaries by position and remove duplicates
        boundaries = sorted(list(set(boundaries)), key=lambda b: b.position)
        
        return boundaries
    
    def calculate_semantic_coherence(self, text: str) -> float:
        """Calculate semantic coherence score for text."""
        # Simple coherence calculation based on keyword repetition and sentence structure
        words = text.lower().split()
        sentences = self.sentence_pattern.split(text)
        
        if len(words) < 3:
            return 0.5  # Neutral score for very short text
        
        # Calculate keyword repetition score
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score based on repeated meaningful words (simple heuristic)
        meaningful_words = [w for w in words if len(w) > 3 and w.isalpha()]
        repetition_score = 0.0
        
        if meaningful_words:
            repeated_count = sum(1 for word, count in word_freq.items() 
                               if count > 1 and word in meaningful_words)
            repetition_score = min(repeated_count / len(meaningful_words), 1.0)
        
        # Score based on sentence structure
        sentence_score = 0.0
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Prefer moderate sentence lengths (5-20 words)
            if 5 <= avg_sentence_length <= 20:
                sentence_score = 1.0
            else:
                sentence_score = max(0.0, 1.0 - abs(avg_sentence_length - 12.5) / 12.5)
        
        # Combine scores
        coherence_score = (repetition_score * 0.6 + sentence_score * 0.4)
        return max(0.0, min(1.0, coherence_score))
    
    def merge_small_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge chunks that are too small."""
        if not chunks:
            return chunks
        
        # Keep merging until all chunks meet minimum size (or can't merge further)
        current_chunks = chunks[:]
        
        while True:
            merged = []
            i = 0
            made_changes = False
            
            while i < len(current_chunks):
                chunk = current_chunks[i]
                word_count = len(chunk["content"].split())
                
                if word_count < self.min_chunk_size:
                    # Try to merge with next chunk
                    merge_group = [chunk]
                    j = i + 1
                    
                    while j < len(current_chunks):
                        next_chunk = current_chunks[j]
                        combined_words = len(" ".join([c["content"] for c in merge_group + [next_chunk]]).split())
                        
                        if combined_words <= self.max_chunk_size:
                            merge_group.append(next_chunk)
                            j += 1
                            if combined_words >= self.min_chunk_size:
                                break  # We have enough words now
                        else:
                            break  # Would exceed max size
                    
                    if len(merge_group) > 1:
                        merged_chunk = self._merge_chunk_group(merge_group)
                        merged.append(merged_chunk)
                        i = j  # Skip all merged chunks
                        made_changes = True
                    else:
                        # Can't merge this chunk, keep as is
                        merged.append(chunk)
                        i += 1
                else:
                    # Chunk is large enough, keep as is
                    merged.append(chunk)
                    i += 1
            
            current_chunks = merged
            if not made_changes:
                break  # No more merging possible
        
        return current_chunks
    
    def _merge_chunk_group(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge a group of small chunks."""
        if len(chunks) == 1:
            return chunks[0]
        
        # Combine content
        combined_content = " ".join(chunk["content"] for chunk in chunks)
        
        # Create merged chunk
        merged_chunk = {
            "id": f"merged_{chunks[0]['id']}",
            "content": combined_content,
            "type": chunks[0].get("type", "text"),
            "metadata": {
                **chunks[0].get("metadata", {}),
                "merged_from": [chunk["id"] for chunk in chunks],
                "merge_reason": "small_chunks",
                "original_count": len(chunks)
            }
        }
        
        return merged_chunk
    
    def split_large_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split chunks that are too large."""
        result = []
        
        for chunk in chunks:
            word_count = len(chunk["content"].split())
            
            if word_count > self.max_chunk_size:
                split_chunks = self._split_chunk(chunk)
                result.extend(split_chunks)
            else:
                result.append(chunk)
        
        return result
    
    def optimize_for_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize chunks specifically for embedding generation."""
        optimized = []
        
        for chunk in chunks:
            content = chunk["content"]
            
            # Calculate keyword density
            words = content.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            keyword_density = len([w for w, count in word_freq.items() if count > 1]) / len(words) if words else 0
            
            # Add embedding metadata
            embedding_metadata = {
                "optimal_for_embedding": True,
                "keyword_density": keyword_density,
                "word_count": len(words),
                "semantic_coherence": self.calculate_semantic_coherence(content)
            }
            
            optimized_chunk = {
                **chunk,
                "embedding_metadata": embedding_metadata
            }
            
            optimized.append(optimized_chunk)
        
        return optimized
    
    def add_contextual_overlap(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add contextual overlap between adjacent chunks."""
        if len(chunks) <= 1:
            return chunks
        
        chunks_with_overlap = []
        
        for i, chunk in enumerate(chunks):
            enhanced_chunk = chunk.copy()
            metadata = enhanced_chunk.setdefault("metadata", {})
            
            # Add overlap with previous chunk
            if i > 0:
                prev_chunk = chunks[i - 1]
                prev_words = prev_chunk["content"].split()
                
                if len(prev_words) >= self.overlap_size:
                    overlap_content = " ".join(prev_words[-self.overlap_size:])
                    metadata["overlap_with_previous"] = overlap_content
                    metadata["context_from_previous"] = True
            
            # Add overlap with next chunk
            if i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                next_words = next_chunk["content"].split()
                
                if len(next_words) >= self.overlap_size:
                    overlap_content = " ".join(next_words[:self.overlap_size])
                    metadata["overlap_with_next"] = overlap_content
                    metadata["context_for_next"] = True
            
            chunks_with_overlap.append(enhanced_chunk)
        
        return chunks_with_overlap