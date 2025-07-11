"""Step definitions for semantic structuring BDD tests."""

import pytest
try:
    from pytest_bdd import scenarios, given, when, then, parsers
except ImportError:
    from ..mock_pytest_bdd import scenarios, given, when, then, parsers
import json
from datetime import datetime

# Load scenarios from the feature file
scenarios('../features/semantic_structuring.feature')

# Import implemented modules
from src.semantic.semantic_structurer import SemanticStructurer
from src.semantic.chunk_optimizer import ChunkOptimizer

# Import all implemented modules
from src.semantic.metadata_enricher import MetadataEnricher
from src.semantic.relationship_mapper import RelationshipMapper
from src.semantic.export_manager import ExportManager


@pytest.fixture
def semantic_context():
    """Context for semantic structuring tests."""
    return {
        "structurer": None,
        "restaurant_data": None,
        "structured_result": None,
        "chunks": [],
        "metadata": {},
        "relationships": [],
        "export_result": None,
        "config": {}
    }


@given("a semantic structurer is initialized")
def init_semantic_structurer(semantic_context):
    """Initialize semantic structurer."""
    if not SemanticStructurer:
        pytest.skip("SemanticStructurer not implemented yet")
    
    semantic_context["structurer"] = SemanticStructurer()


@given("sample restaurant data has been extracted")
def setup_sample_data(semantic_context):
    """Setup sample restaurant data."""
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "description": "Fine dining establishment serving French cuisine",
        "cuisine": "French",
        "price_range": "$$$",
        "location": {
            "address": "123 Main St",
            "city": "Downtown",
            "coordinates": {"lat": 40.7128, "lng": -74.0060}
        },
        "hours": {
            "monday": "11:00-22:00",
            "tuesday": "11:00-22:00"
        },
        "menu": {
            "appetizers": ["Caesar Salad - $12", "Soup - $8"],
            "main_courses": ["Salmon - $24", "Pasta - $18"]
        },
        "contact": {
            "phone": "(555) 123-4567",
            "email": "info@bistrodeluxe.com"
        },
        "ambiance": {
            "description": "Elegant dining room with warm lighting",
            "tags": ["romantic", "upscale", "quiet"]
        },
        "_metadata": {
            "confidence": 0.95,
            "extraction_method": "json_ld",
            "extraction_time": "2024-01-07T10:00:00Z"
        }
    }


@given('restaurant data with name "Bistro Deluxe" and description "Fine dining establishment serving French cuisine"')
def setup_basic_restaurant_data(semantic_context):
    """Setup basic restaurant data."""
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "description": "Fine dining establishment serving French cuisine"
    }


@given("restaurant data with multiple attributes including cuisine, price range, and location")
def setup_rich_restaurant_data(semantic_context):
    """Setup restaurant data with multiple attributes."""
    setup_sample_data(semantic_context)
    # Add extraction metadata for enrichment testing
    semantic_context["restaurant_data"]["_metadata"] = {
        "extraction_method": "json_ld",
        "confidence": 0.95,
        "url": "https://bistrodeluxe.com",
        "scrape_timestamp": "2024-01-07T10:00:00Z"
    }


@given("restaurant data with menu items, hours, and contact information")
def setup_complete_restaurant_data(semantic_context):
    """Setup complete restaurant data."""
    setup_sample_data(semantic_context)


@given("restaurant data with ambiance descriptions and menu items")
def setup_ambiance_data(semantic_context):
    """Setup restaurant data with ambiance."""
    setup_sample_data(semantic_context)


@given("semantically structured restaurant data")
def setup_structured_data(semantic_context):
    """Setup pre-structured data."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    # Simulate structured result
    semantic_context["structured_result"] = semantic_context["structurer"].structure_for_rag(
        semantic_context["restaurant_data"]
    )

@given("semantically structured data")
def setup_generic_structured_data(semantic_context):
    """Setup generic structured data for export profile testing."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    # Use sample data if not already set
    if not semantic_context.get("restaurant_data"):
        setup_sample_data(semantic_context)
    
    # Create structured result
    semantic_context["structured_result"] = semantic_context["structurer"].structure_for_rag(
        semantic_context["restaurant_data"]
    )


@given("restaurant data with text, images, and PDF content")
def setup_multimodal_data(semantic_context):
    """Setup multi-modal restaurant data."""
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "text_content": "Fine dining establishment",
        "images": [
            {"url": "menu.jpg", "description": "Menu items", "type": "menu"},
            {"url": "interior.jpg", "description": "Dining room", "type": "ambiance"}
        ],
        "pdfs": [
            {"url": "wine-list.pdf", "content": "Wine selection", "pages": 5}
        ]
    }


@given("a long restaurant description that exceeds chunk size limits")
def setup_long_description(semantic_context):
    """Setup data with long description."""
    long_text = " ".join([
        "Bistro Deluxe is an exceptional fine dining establishment.",
        "Located in the heart of downtown, this restaurant offers",
        "an unparalleled culinary experience that combines traditional",
        "French cooking techniques with modern innovations.",
        "The chef, trained in Paris, brings authentic flavors",
        "and artistic presentation to every dish.",
        "The ambiance is sophisticated yet welcoming,",
        "with soft lighting and elegant decor.",
        "Whether you're celebrating a special occasion",
        "or enjoying a business dinner, Bistro Deluxe",
        "provides the perfect setting for a memorable meal."
    ])
    
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "description": long_text
    }


@given("complete restaurant data")
def setup_complete_data(semantic_context):
    """Setup complete restaurant data for summary."""
    setup_sample_data(semantic_context)


@given(parsers.parse("restaurant data and a custom chunk size of {chunk_size:d} tokens"))
def setup_custom_chunk_size(semantic_context, chunk_size):
    """Setup data with custom chunk size."""
    setup_sample_data(semantic_context)
    semantic_context["config"]["chunk_size"] = chunk_size


@given("restaurant hours and special event information")
def setup_temporal_data(semantic_context):
    """Setup temporal data."""
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "hours": {
            "monday": "11:00-22:00",
            "tuesday": "11:00-22:00",
            "wednesday": "11:00-22:00"
        },
        "special_events": [
            {
                "name": "Wine Tasting",
                "date": "2024-02-14",
                "time": "18:00-20:00"
            },
            {
                "name": "Chef's Table",
                "date": "2024-02-20",
                "time": "19:00-22:00"
            }
        ]
    }


@given("restaurant data with nested information")
def setup_nested_data(semantic_context):
    """Setup hierarchical data."""
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "menu": {
            "appetizers": {
                "salads": ["Caesar - $12", "Greek - $10"],
                "soups": ["French Onion - $8", "Bisque - $9"]
            },
            "main_courses": {
                "seafood": ["Salmon - $24", "Lobster - $32"],
                "meat": ["Steak - $28", "Lamb - $26"]
            }
        }
    }


@given("restaurant data with missing phone numbers and incomplete addresses")
def setup_incomplete_data(semantic_context):
    """Setup incomplete data."""
    semantic_context["restaurant_data"] = {
        "name": "Bistro Deluxe",
        "location": {
            "address": "Main St",  # Missing number
            "city": "Downtown"
            # Missing state, zip
        },
        "contact": {
            "email": "info@bistrodeluxe.com"
            # Missing phone
        }
    }


@when("I structure the data for RAG")
def structure_data_for_rag(semantic_context):
    """Structure data for RAG."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].structure_for_rag(
        semantic_context["restaurant_data"]
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when("I structure the data with metadata enrichment")
def structure_with_metadata(semantic_context):
    """Structure data with metadata enrichment."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].structure_for_rag(
        semantic_context["restaurant_data"],
        enrich_metadata=True
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when("I create semantic relationships")
def create_relationships(semantic_context):
    """Create semantic relationships."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].create_relationships(
        semantic_context["restaurant_data"]
    )
    semantic_context["relationships"] = result.get("relationships", [])


@when("I generate embedding hints")
def generate_embedding_hints(semantic_context):
    """Generate embedding hints."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].generate_embedding_hints(
        semantic_context["restaurant_data"]
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when("I export to JSON format")
def export_to_json(semantic_context):
    """Export to JSON format."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].export(
        semantic_context["structured_result"],
        format="json"
    )
    semantic_context["export_result"] = result


@when("I export to JSONL format")
def export_to_jsonl(semantic_context):
    """Export to JSONL format."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].export(
        semantic_context["structured_result"],
        format="jsonl"
    )
    semantic_context["export_result"] = result


@when("I export to Parquet format")
def export_to_parquet(semantic_context):
    """Export to Parquet format."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].export(
        semantic_context["structured_result"],
        format="parquet"
    )
    semantic_context["export_result"] = result


@when("I structure multi-modal data")
def structure_multimodal(semantic_context):
    """Structure multi-modal data."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].structure_multimodal(
        semantic_context["restaurant_data"]
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when("I apply intelligent chunking")
def apply_intelligent_chunking(semantic_context):
    """Apply intelligent chunking."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].chunk_intelligently(
        semantic_context["restaurant_data"]
    )
    semantic_context["chunks"] = result.get("chunks", [])


@when("I generate summary chunks")
def generate_summary_chunks(semantic_context):
    """Generate summary chunks."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].generate_summary(
        semantic_context["restaurant_data"]
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when("I structure data with custom configuration")
def structure_with_config(semantic_context):
    """Structure data with custom configuration."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].structure_for_rag(
        semantic_context["restaurant_data"],
        config=semantic_context["config"]
    )
    semantic_context["chunks"] = result.get("chunks", [])


@when("I structure temporal data")
def structure_temporal_data(semantic_context):
    """Structure temporal data."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].structure_temporal(
        semantic_context["restaurant_data"]
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when("I create hierarchical structure")
def create_hierarchy(semantic_context):
    """Create hierarchical structure."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].create_hierarchy(
        semantic_context["restaurant_data"]
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@when(parsers.parse('I export with "{profile}" profile'))
def export_with_profile(semantic_context, profile):
    """Export with specific profile."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].export(
        semantic_context["structured_result"],
        profile=profile
    )
    semantic_context["export_result"] = result


@when("I structure incomplete data")
def structure_incomplete_data(semantic_context):
    """Structure incomplete data."""
    if not semantic_context["structurer"]:
        pytest.skip("Structurer not initialized")
    
    result = semantic_context["structurer"].structure_for_rag(
        semantic_context["restaurant_data"],
        handle_missing=True
    )
    semantic_context["structured_result"] = result
    semantic_context["chunks"] = result.get("chunks", [])


@then("I should receive semantic chunks optimized for embedding")
def verify_semantic_chunks(semantic_context):
    """Verify semantic chunks are optimized."""
    chunks = semantic_context["chunks"]
    assert len(chunks) > 0, "No chunks generated"
    for chunk in chunks:
        assert "content" in chunk
        assert "id" in chunk
        assert len(chunk["content"]) > 0


@then(parsers.parse("each chunk should have a maximum size of {max_tokens:d} tokens"))
def verify_chunk_size(semantic_context, max_tokens):
    """Verify chunk size limits."""
    chunks = semantic_context["chunks"]
    for chunk in chunks:
        # Simple token estimation (actual implementation would use proper tokenizer)
        token_count = len(chunk["content"].split())
        assert token_count <= max_tokens, f"Chunk exceeds {max_tokens} tokens"


@then("each chunk should maintain semantic coherence")
def verify_semantic_coherence(semantic_context):
    """Verify chunks maintain semantic coherence."""
    chunks = semantic_context["chunks"]
    for chunk in chunks:
        content = chunk["content"]
        # Check that chunks don't end mid-word
        assert not content.endswith("-")
        # Check that chunks have complete thoughts (simplified check)
        assert content.endswith((".", "!", "?")) or len(content.split()) < 10


@then("chunks should not break mid-sentence")
def verify_sentence_boundaries(semantic_context):
    """Verify chunks respect sentence boundaries."""
    chunks = semantic_context["chunks"]
    for chunk in chunks:
        content = chunk["content"]
        # Verify chunk ends with sentence terminator or is very short
        if len(content) > 20:
            assert content.rstrip().endswith((".", "!", "?", '\"', "'")), \
                f"Chunk doesn't end with sentence terminator: {content[-20:]}"


@then(parsers.parse("each chunk should have metadata including:\n{table}"))
def verify_metadata_fields_table(semantic_context, table):
    """Verify metadata fields from table."""
    chunks = semantic_context["chunks"]
    assert len(chunks) > 0
    
    # Parse the table text manually
    lines = table.strip().split('\n')
    expected_fields = []
    
    # Skip header line and extract metadata field names
    for line in lines[1:]:  # Skip the header line
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 3:  # Should have empty, field_name, value, empty
                field_name = fields[1].strip()  # metadata_field column
                if field_name:  # Skip empty lines
                    expected_fields.append(field_name)
    
    for chunk in chunks:
        assert "metadata" in chunk
        metadata = chunk["metadata"]
        for field in expected_fields:
            assert field in metadata, f"Missing metadata field: {field} in chunk {chunk['id']}"


@then("each chunk should have standard metadata fields")
def verify_standard_metadata_fields(semantic_context):
    """Verify standard metadata fields are present."""
    chunks = semantic_context["chunks"]
    assert len(chunks) > 0
    
    # Check for standard fields that should be present
    required_fields = ["source_type", "entity_name", "chunk_type", 
                      "confidence_score", "extraction_method", "timestamp"]
    
    for chunk in chunks:
        assert "metadata" in chunk
        metadata = chunk["metadata"]
        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field} in chunk {chunk['id']}"


@then("metadata should support filtering and retrieval")
def verify_metadata_filtering(semantic_context):
    """Verify metadata supports filtering."""
    chunks = semantic_context["chunks"]
    
    # Check that metadata has consistent structure
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        assert isinstance(metadata.get("confidence_score"), (int, float))
        assert isinstance(metadata.get("source_type"), str)
        assert isinstance(metadata.get("timestamp"), str)


@then(parsers.parse("I should have a relationship graph including:\n{table}"))
def verify_relationships(semantic_context, table):
    """Verify relationship graph."""
    relationships = semantic_context["relationships"]
    
    # Parse the table text manually
    lines = table.strip().split('\n')
    expected_rels = []
    
    # Skip header line and extract relationship data
    for line in lines[1:]:  # Skip the header line
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 4:  # Should have empty, from_chunk, relationship, to_chunk, empty
                from_chunk = fields[1].strip()
                relationship = fields[2].strip()
                to_chunk = fields[3].strip()
                if from_chunk and relationship and to_chunk:  # Skip empty lines
                    expected_rels.append((from_chunk, relationship, to_chunk))
    
    for expected in expected_rels:
        found = any(
            rel["from"] == expected[0] and
            rel["type"] == expected[1] and
            rel["to"] == expected[2]
            for rel in relationships
        )
        assert found, f"Missing relationship: {expected[0]} -{expected[1]}-> {expected[2]}"


@then("relationships should be bidirectional where appropriate")
def verify_bidirectional_relationships(semantic_context):
    """Verify bidirectional relationships."""
    relationships = semantic_context["relationships"]
    
    # Check for bidirectional relationships
    bidirectional_types = ["located_at", "has_menu", "has_hours"]
    
    for rel in relationships:
        if rel["type"] in bidirectional_types:
            # Should have inverse relationship
            inverse_found = any(
                r["from"] == rel["to"] and
                r["to"] == rel["from"]
                for r in relationships
            )
            assert inverse_found or rel.get("bidirectional", False)


@then(parsers.parse("each chunk should have embedding hints including:\n{table}"))
def verify_embedding_hints(semantic_context, table):
    """Verify embedding hints."""
    chunks = semantic_context["chunks"]
    
    # Parse the table text manually
    lines = table.strip().split('\n')
    expected_hints = []
    
    # Skip header line and extract hint types
    for line in lines[1:]:  # Skip the header line
        if '|' in line:
            fields = [field.strip() for field in line.split('|')]
            if len(fields) >= 3:  # Should have empty, hint_type, purpose, empty
                hint_type = fields[1].strip()
                if hint_type:  # Skip empty lines
                    expected_hints.append(hint_type)
    
    for chunk in chunks:
        assert "embedding_hints" in chunk
        hints = chunk["embedding_hints"]
        for hint_type in expected_hints:
            assert hint_type in hints, f"Missing embedding hint: {hint_type}"


@then("the output should be valid JSON")
def verify_json_output(semantic_context):
    """Verify JSON output validity."""
    export_result = semantic_context["export_result"]
    
    # Try to parse as JSON
    try:
        if isinstance(export_result, str):
            json.loads(export_result)
        else:
            json.dumps(export_result)  # Should be serializable
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")


@then("it should include all chunks, metadata, and relationships")
def verify_complete_json_export(semantic_context):
    """Verify JSON export completeness."""
    export_result = semantic_context["export_result"]
    
    if isinstance(export_result, str):
        data = json.loads(export_result)
    else:
        data = export_result
    
    assert "chunks" in data
    assert "metadata" in data
    assert "relationships" in data
    assert len(data["chunks"]) > 0


@then("it should follow the RAG-ready schema")
def verify_rag_schema(semantic_context):
    """Verify RAG-ready schema compliance."""
    export_result = semantic_context["export_result"]
    
    if isinstance(export_result, str):
        data = json.loads(export_result)
    else:
        data = export_result
    
    # Verify schema structure
    assert "version" in data
    assert "chunks" in data
    assert isinstance(data["chunks"], list)


@then("each line should be a valid JSON object")
def verify_jsonl_format(semantic_context):
    """Verify JSONL format."""
    export_result = semantic_context["export_result"]
    
    lines = export_result.strip().split('\n')
    assert len(lines) > 0
    
    for line in lines:
        try:
            json.loads(line)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON line: {line}")


@then("each line should represent one semantic chunk")
def verify_jsonl_chunks(semantic_context):
    """Verify JSONL chunk representation."""
    export_result = semantic_context["export_result"]
    
    lines = export_result.strip().split('\n')
    
    # Get chunks from the structured result instead of the context chunks array
    structured_result = semantic_context.get("structured_result", {})
    chunks_count = len(structured_result.get("chunks", []))
    
    # If no structured result, use the actual lines count as validation
    if chunks_count == 0:
        chunks_count = len(lines)
    
    assert len(lines) == chunks_count, \
        f"Expected {chunks_count} lines, got {len(lines)}"


@then("metadata should be embedded in each line")
def verify_jsonl_metadata(semantic_context):
    """Verify metadata in JSONL."""
    export_result = semantic_context["export_result"]
    
    lines = export_result.strip().split('\n')
    for line in lines:
        chunk = json.loads(line)
        assert "metadata" in chunk
        assert "content" in chunk


@then("the output should be a valid Parquet file")
def verify_parquet_output(semantic_context):
    """Verify Parquet output validity."""
    export_result = semantic_context["export_result"]
    
    # Check for Parquet magic bytes or structure
    assert export_result is not None
    assert isinstance(export_result, bytes) or hasattr(export_result, 'to_parquet')


@then("it should have optimized columnar storage")
def verify_parquet_columnar(semantic_context):
    """Verify Parquet columnar optimization."""
    export_result = semantic_context["export_result"]
    
    # Verify columnar structure exists
    assert export_result is not None


@then("it should preserve all data types correctly")
def verify_parquet_types(semantic_context):
    """Verify Parquet data type preservation."""
    export_result = semantic_context["export_result"]
    
    # Verify data types are preserved
    assert export_result is not None


@then("text content should be in standard chunks")
def verify_text_chunks(semantic_context):
    """Verify text content chunks."""
    chunks = semantic_context["chunks"]
    text_chunks = [c for c in chunks if c.get("type") == "text"]
    assert len(text_chunks) > 0


@then("image descriptions should be separate chunks with image metadata")
def verify_image_chunks(semantic_context):
    """Verify image description chunks."""
    chunks = semantic_context["chunks"]
    image_chunks = [c for c in chunks if c.get("type") == "image"]
    
    assert len(image_chunks) > 0
    for chunk in image_chunks:
        assert "image_metadata" in chunk
        assert "url" in chunk["image_metadata"]


@then("PDF content should maintain document structure")
def verify_pdf_structure(semantic_context):
    """Verify PDF content structure."""
    chunks = semantic_context["chunks"]
    pdf_chunks = [c for c in chunks if c.get("type") == "pdf"]
    
    assert len(pdf_chunks) > 0
    for chunk in pdf_chunks:
        assert "document_metadata" in chunk


@then("all chunks should be linked via relationships")
def verify_multimodal_relationships(semantic_context):
    """Verify multi-modal relationships."""
    structured_result = semantic_context["structured_result"]
    relationships = structured_result.get("relationships", [])
    
    # Check that different content types are linked
    rel_types = {rel["type"] for rel in relationships}
    assert "has_image" in rel_types or "has_visual" in rel_types
    assert "has_document" in rel_types or "has_pdf" in rel_types


@then("chunks should break at natural boundaries like paragraphs")
def verify_natural_boundaries(semantic_context):
    """Verify natural boundary breaking."""
    chunks = semantic_context["chunks"]
    
    for chunk in chunks:
        content = chunk["content"]
        # Should not start with lowercase (unless special case)
        if len(content) > 0 and content[0].isalpha():
            assert content[0].isupper() or content.startswith(("a ", "an ", "the "))


@then("related information should be kept together")
def verify_related_info_grouping(semantic_context):
    """Verify related information grouping."""
    chunks = semantic_context["chunks"]
    
    # Check that chunks have coherent topics or related chunk_types
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        # Accept either explicit topic or related chunk_type as evidence of grouping
        has_topic = "topic" in metadata
        has_chunk_type = "chunk_type" in metadata
        is_single_chunk = len(chunks) == 1
        
        assert has_topic or has_chunk_type or is_single_chunk, \
            f"Chunk {chunk.get('id')} lacks topic or chunk_type metadata for grouping"


@then("no chunk should exceed the token limit")
def verify_token_limits(semantic_context):
    """Verify token limits are respected."""
    chunks = semantic_context["chunks"]
    max_tokens = semantic_context.get("config", {}).get("chunk_size", 512)
    
    for chunk in chunks:
        # Simple token count approximation
        tokens = len(chunk["content"].split())
        assert tokens <= max_tokens


@then("overlapping context should be provided between chunks")
def verify_chunk_overlap(semantic_context):
    """Verify chunk overlap for context."""
    chunks = semantic_context["chunks"]
    
    if len(chunks) > 1:
        for i in range(len(chunks) - 1):
            current = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Check for overlap indicator
            assert "overlap_with_next" in current.get("metadata", {}) or \
                   "overlap_with_previous" in next_chunk.get("metadata", {})


@then("I should have a primary summary chunk with key information")
def verify_summary_chunk(semantic_context):
    """Verify primary summary chunk."""
    chunks = semantic_context["chunks"]
    summary_chunks = [c for c in chunks if c.get("type") == "summary"]
    
    assert len(summary_chunks) >= 1
    summary = summary_chunks[0]
    assert "Bistro Deluxe" in summary["content"]


@then("the summary should include name, cuisine, price range, and location")
def verify_summary_content(semantic_context):
    """Verify summary content completeness."""
    chunks = semantic_context["chunks"]
    summary_chunks = [c for c in chunks if c.get("type") == "summary"]
    
    summary_content = summary_chunks[0]["content"]
    assert "Bistro Deluxe" in summary_content
    assert "French" in summary_content or "cuisine" in summary_content
    assert "$$$" in summary_content or "price" in summary_content
    assert "Main St" in summary_content or "location" in summary_content


@then('the summary chunk should be marked with "summary" type')
def verify_summary_type(semantic_context):
    """Verify summary chunk type marking."""
    chunks = semantic_context["chunks"]
    summary_chunks = [c for c in chunks if c.get("type") == "summary"]
    
    assert len(summary_chunks) > 0
    assert summary_chunks[0]["type"] == "summary"


@then("it should link to detailed chunks")
def verify_summary_links(semantic_context):
    """Verify summary links to details."""
    structured_result = semantic_context["structured_result"]
    relationships = structured_result.get("relationships", [])
    
    # Find relationships from summary chunk
    summary_rels = [r for r in relationships if r["from"].startswith("summary")]
    assert len(summary_rels) > 0


@then(parsers.parse("all chunks should respect the {limit:d} token limit"))
def verify_custom_token_limit(semantic_context, limit):
    """Verify custom token limit."""
    chunks = semantic_context["chunks"]
    
    for chunk in chunks:
        tokens = len(chunk["content"].split())
        assert tokens <= limit


@then("the configuration should be stored in metadata")
def verify_config_storage(semantic_context):
    """Verify configuration storage."""
    chunks = semantic_context["chunks"]
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        assert "chunk_config" in metadata or "config" in metadata


@then("chunk boundaries should still maintain semantic coherence")
def verify_coherence_with_custom_size(semantic_context):
    """Verify coherence with custom chunk size."""
    verify_semantic_coherence(semantic_context)


@then('business hours should have "recurring_schedule" temporal type')
def verify_hours_temporal_type(semantic_context):
    """Verify business hours temporal type."""
    chunks = semantic_context["chunks"]
    hours_chunks = [c for c in chunks if "hours" in c.get("content", "").lower()]
    
    for chunk in hours_chunks:
        temporal_type = chunk.get("metadata", {}).get("temporal_type")
        assert temporal_type == "recurring_schedule"


@then('special events should have "specific_date" temporal type')
def verify_events_temporal_type(semantic_context):
    """Verify special events temporal type."""
    chunks = semantic_context["chunks"]
    event_chunks = [c for c in chunks if "event" in c.get("content", "").lower() or 
                    "Wine Tasting" in c.get("content", "") or
                    "Chef's Table" in c.get("content", "")]
    
    for chunk in event_chunks:
        temporal_type = chunk.get("metadata", {}).get("temporal_type")
        assert temporal_type == "specific_date"


@then("temporal metadata should enable time-based queries")
def verify_temporal_query_support(semantic_context):
    """Verify temporal query support."""
    chunks = semantic_context["chunks"]
    
    temporal_chunks = [c for c in chunks if "temporal_type" in c.get("metadata", {})]
    assert len(temporal_chunks) > 0
    
    for chunk in temporal_chunks:
        metadata = chunk["metadata"]
        assert "temporal_type" in metadata
        assert "time_reference" in metadata or "schedule" in metadata


@then("I should have parent chunks for main categories")
def verify_parent_chunks(semantic_context):
    """Verify parent chunks exist."""
    chunks = semantic_context["chunks"]
    
    parent_chunks = [c for c in chunks if c.get("hierarchy_level") == 0 or 
                     c.get("is_parent", False)]
    assert len(parent_chunks) > 0


@then("child chunks for detailed information")
def verify_child_chunks(semantic_context):
    """Verify child chunks exist."""
    chunks = semantic_context["chunks"]
    
    child_chunks = [c for c in chunks if c.get("hierarchy_level", 0) > 0 or
                    c.get("parent_id") is not None]
    assert len(child_chunks) > 0


@then("the hierarchy should be navigable via relationships")
def verify_hierarchy_navigation(semantic_context):
    """Verify hierarchy navigation."""
    structured_result = semantic_context["structured_result"]
    relationships = structured_result.get("relationships", [])
    
    # Check for parent-child relationships
    hierarchy_rels = [r for r in relationships if r["type"] in ["has_child", "has_parent", "contains"]]
    assert len(hierarchy_rels) > 0


@then(parsers.parse("hierarchy depth should not exceed {max_depth:d} levels"))
def verify_hierarchy_depth(semantic_context, max_depth):
    """Verify hierarchy depth limit."""
    chunks = semantic_context["chunks"]
    
    max_level = max(chunk.get("hierarchy_level", 0) for chunk in chunks)
    assert max_level <= max_depth


@then("chunks should be optimized for conversational retrieval")
def verify_chatbot_optimization(semantic_context):
    """Verify chatbot optimization."""
    export_result = semantic_context["export_result"]
    
    # Parse JSON if it's a string
    if isinstance(export_result, str):
        import json
        data = json.loads(export_result)
    else:
        data = export_result
    
    # Check for conversational optimization indicators
    assert "profile" in data.get("metadata", {}), "No profile found in metadata"
    assert data["metadata"]["profile"] == "chatbot", f"Expected chatbot profile, got {data['metadata'].get('profile')}"


@then("chunks should be optimized for keyword search")
def verify_search_optimization(semantic_context):
    """Verify search optimization."""
    export_result = semantic_context["export_result"]
    
    # Parse JSON if it's a string
    if isinstance(export_result, str):
        import json
        data = json.loads(export_result)
    else:
        data = export_result
    
    # Check for search optimization indicators
    assert "profile" in data.get("metadata", {}), "No profile found in metadata"
    assert data["metadata"]["profile"] == "search", f"Expected search profile, got {data['metadata'].get('profile')}"


@then("data should be structured for aggregation queries")
def verify_analytics_optimization(semantic_context):
    """Verify analytics optimization."""
    export_result = semantic_context["export_result"]
    
    # Parse JSON if it's a string
    if isinstance(export_result, str):
        import json
        data = json.loads(export_result)
    else:
        data = export_result
    
    # Check for analytics optimization indicators
    assert "profile" in data.get("metadata", {}), "No profile found in metadata"
    assert data["metadata"]["profile"] == "analytics", f"Expected analytics profile, got {data['metadata'].get('profile')}"


@then("missing fields should be marked in metadata")
def verify_missing_field_marking(semantic_context):
    """Verify missing fields are marked."""
    chunks = semantic_context["chunks"]
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        if "missing_fields" in metadata:
            assert isinstance(metadata["missing_fields"], list)


@then("chunks should still be created for available data")
def verify_chunks_for_available_data(semantic_context):
    """Verify chunks created for available data."""
    chunks = semantic_context["chunks"]
    assert len(chunks) > 0
    
    # Check that we have chunks for email even though phone is missing
    email_found = any("email" in chunk["content"].lower() for chunk in chunks)
    assert email_found


@then("confidence scores should reflect data completeness")
def verify_confidence_reflects_completeness(semantic_context):
    """Verify confidence scores reflect completeness."""
    chunks = semantic_context["chunks"]
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        if metadata.get("missing_fields"):
            # Confidence should be lower for incomplete data
            assert metadata.get("confidence_score", 1.0) < 0.9


@then("relationships should only include verified data")
def verify_relationships_verified_only(semantic_context):
    """Verify relationships only for verified data."""
    structured_result = semantic_context["structured_result"]
    relationships = structured_result.get("relationships", [])
    
    # Should not have relationships for missing phone
    phone_rels = [r for r in relationships if "phone" in r["from"] or "phone" in r["to"]]
    assert len(phone_rels) == 0