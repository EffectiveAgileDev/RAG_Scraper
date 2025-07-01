"""ExportManager for managing export of structured data in various formats."""

import json
import csv
import gzip
import io
import os
from typing import Dict, List, Any, Optional, Union, Iterator, Callable
from datetime import datetime, timezone


class ExportManager:
    """Manages export of structured semantic data in various formats."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize export manager."""
        self.config = config or {}
        self.default_format = self.config.get('default_format', 'json')
        self.include_metadata = self.config.get('include_metadata', True)
        self.pretty_print = self.config.get('pretty_print', False)
        self.compression = self.config.get('compression', None)
        
        # Supported formats
        self.supported_formats = ['json', 'jsonl', 'parquet', 'csv']
        
        # Profile configurations
        self.profiles = {
            'chatbot': {
                'focus': 'conversational',
                'include_relationships': True,
                'include_summaries': True,
                'chunk_priority': 'high_importance'
            },
            'search': {
                'focus': 'retrieval',
                'include_embeddings': True,
                'include_keywords': True,
                'chunk_priority': 'semantic_relevance'
            },
            'analytics': {
                'focus': 'analysis',
                'include_metrics': True,
                'include_timestamps': True,
                'chunk_priority': 'all_data'
            }
        }
    
    def export(self, structured_data: Dict[str, Any], 
               format: str = None, 
               profile: Optional[str] = None,
               serializer: Optional[Callable] = None) -> Union[str, bytes]:
        """Export structured data in specified format."""
        if not self.validate_export_data(structured_data):
            raise ValueError("Invalid export data structure")
        
        export_format = format or self.default_format
        
        if export_format not in self.supported_formats and not serializer:
            raise ValueError(f"Unsupported format: {export_format}")
        
        # Apply profile optimizations
        if profile:
            structured_data = self._apply_profile(structured_data, profile)
        
        # Add export metadata
        structured_data = self.add_export_metadata(structured_data, export_format)
        
        # Custom serializer
        if serializer:
            return serializer(structured_data)
        
        # Format-specific export
        if export_format == "json":
            return self._export_json(structured_data)
        elif export_format == "jsonl":
            return self._export_jsonl(structured_data)
        elif export_format == "parquet":
            return self._export_parquet(structured_data)
        elif export_format == "csv":
            return self._export_csv(structured_data)
        else:
            raise ValueError(f"Unsupported format: {export_format}")
    
    def _export_json(self, data: Dict[str, Any]) -> str:
        """Export data as JSON."""
        if self.pretty_print:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    def _export_jsonl(self, data: Dict[str, Any]) -> str:
        """Export data as JSONL (JSON Lines)."""
        lines = []
        
        # Export chunks as individual JSON lines
        for chunk in data.get("chunks", []):
            lines.append(json.dumps(chunk, ensure_ascii=False))
        
        # Add metadata as final line if requested
        if self.include_metadata and "metadata" in data:
            metadata_line = {
                "type": "metadata",
                "data": data["metadata"]
            }
            lines.append(json.dumps(metadata_line, ensure_ascii=False))
        
        # Add relationships as lines if present
        if "relationships" in data:
            for relationship in data["relationships"]:
                rel_line = {
                    "type": "relationship",
                    "data": relationship
                }
                lines.append(json.dumps(rel_line, ensure_ascii=False))
        
        return '\n'.join(lines)
    
    def _export_parquet(self, data: Dict[str, Any]) -> bytes:
        """Export data as Parquet format (simulated)."""
        # In a real implementation, this would use pandas/pyarrow
        # For now, we'll simulate parquet with a binary format
        json_data = json.dumps(data, ensure_ascii=False)
        parquet_header = b"PARQUET_SIMULATION_"
        return parquet_header + json_data.encode('utf-8')
    
    def _export_csv(self, data: Dict[str, Any]) -> str:
        """Export chunks as CSV format."""
        if not data.get("chunks"):
            return ""
        
        output = io.StringIO()
        
        # Determine CSV columns from first chunk
        first_chunk = data["chunks"][0]
        fieldnames = list(first_chunk.keys())
        
        # Flatten metadata if present
        if "metadata" in first_chunk and isinstance(first_chunk["metadata"], dict):
            fieldnames.remove("metadata")
            for meta_key in first_chunk["metadata"].keys():
                fieldnames.append(f"metadata_{meta_key}")
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write chunk data
        for chunk in data["chunks"]:
            row = chunk.copy()
            
            # Flatten metadata
            if "metadata" in row and isinstance(row["metadata"], dict):
                metadata = row.pop("metadata")
                for meta_key, meta_value in metadata.items():
                    row[f"metadata_{meta_key}"] = str(meta_value)
            
            # Convert complex fields to strings
            for key, value in row.items():
                if isinstance(value, (list, dict)):
                    row[key] = json.dumps(value)
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def _apply_profile(self, data: Dict[str, Any], profile: str) -> Dict[str, Any]:
        """Apply profile-specific optimizations."""
        if profile not in self.profiles:
            return data
        
        profile_config = self.profiles[profile]
        optimized_data = data.copy()
        
        # Add profile to metadata
        if "metadata" not in optimized_data:
            optimized_data["metadata"] = {}
        optimized_data["metadata"]["profile"] = profile
        optimized_data["metadata"]["profile_config"] = profile_config
        
        # Profile-specific optimizations
        if profile == "chatbot":
            # Prioritize conversational chunks
            chunks = optimized_data.get("chunks", [])
            prioritized_chunks = sorted(
                chunks,
                key=lambda x: x.get("metadata", {}).get("importance_weight", 0.5),
                reverse=True
            )
            optimized_data["chunks"] = prioritized_chunks
        
        elif profile == "search":
            # Add search-specific metadata
            for chunk in optimized_data.get("chunks", []):
                chunk.setdefault("metadata", {})["search_optimized"] = True
        
        elif profile == "analytics":
            # Include comprehensive metadata for analysis
            optimized_data["metadata"]["export_analytics"] = {
                "total_chunks": len(optimized_data.get("chunks", [])),
                "total_relationships": len(optimized_data.get("relationships", [])),
                "chunk_types": self._analyze_chunk_types(optimized_data.get("chunks", []))
            }
        
        return optimized_data
    
    def _analyze_chunk_types(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze chunk types for analytics."""
        type_counts = {}
        for chunk in chunks:
            chunk_type = chunk.get("type", "unknown")
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
        return type_counts
    
    def save_to_file(self, structured_data: Dict[str, Any], 
                     file_path: str, 
                     format: str = None,
                     profile: Optional[str] = None) -> str:
        """Save exported data to file."""
        export_format = format or self.default_format
        exported_data = self.export(structured_data, format=export_format, profile=profile)
        
        # Determine write mode
        write_mode = 'wb' if isinstance(exported_data, bytes) else 'w'
        encoding = None if isinstance(exported_data, bytes) else 'utf-8'
        
        # Create directory if it doesn't exist (only if there's a directory part)
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Apply compression if configured
        if self.compression:
            exported_data = self.compress_output(exported_data, self.compression)
            write_mode = 'wb'
            file_path += f".{self.compression}"
        
        with open(file_path, write_mode, encoding=encoding) as f:
            f.write(exported_data)
        
        return file_path
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return self.supported_formats.copy()
    
    def validate_export_data(self, data: Dict[str, Any]) -> bool:
        """Validate data structure before export."""
        if not isinstance(data, dict):
            return False
        
        # Must have chunks
        if "chunks" not in data:
            return False
        
        chunks = data["chunks"]
        if not isinstance(chunks, list):
            return False
        
        # Validate chunk structure
        for chunk in chunks:
            if not isinstance(chunk, dict):
                return False
            if "id" not in chunk or "content" not in chunk:
                return False
        
        return True
    
    def add_export_metadata(self, data: Dict[str, Any], format: str) -> Dict[str, Any]:
        """Add export-specific metadata."""
        enriched_data = data.copy()
        
        export_metadata = {
            "export_format": format,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "export_version": "1.0",
            "chunk_count": len(data.get("chunks", [])),
            "relationship_count": len(data.get("relationships", []))
        }
        
        enriched_data["export_metadata"] = export_metadata
        
        return enriched_data
    
    def compress_output(self, data: Union[str, bytes], compression: str) -> bytes:
        """Compress export output."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if compression == "gzip":
            return gzip.compress(data)
        else:
            raise ValueError(f"Unsupported compression: {compression}")
    
    def export_stream(self, structured_data: Dict[str, Any], 
                     format: str = "jsonl") -> Iterator[str]:
        """Export data as a stream for large datasets."""
        if not self.validate_export_data(structured_data):
            raise ValueError("Invalid export data structure")
        
        # Stream chunks one by one
        for chunk in structured_data.get("chunks", []):
            if format == "jsonl":
                yield json.dumps(chunk, ensure_ascii=False)
            elif format == "json":
                # For JSON streaming, we'd need to handle array structure
                yield json.dumps(chunk, ensure_ascii=False)
            else:
                raise ValueError(f"Streaming not supported for format: {format}")
        
        # Stream metadata and relationships if present
        if self.include_metadata:
            metadata = structured_data.get("metadata", {})
            if metadata:
                metadata_item = {"type": "metadata", "data": metadata}
                yield json.dumps(metadata_item, ensure_ascii=False)
            
            relationships = structured_data.get("relationships", [])
            for relationship in relationships:
                rel_item = {"type": "relationship", "data": relationship}
                yield json.dumps(rel_item, ensure_ascii=False)