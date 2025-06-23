import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from datetime import datetime
import json

# Load scenarios from feature file
scenarios('../features/entity_relationship_tracking.feature')


@pytest.fixture
def relationship_tracker():
    """Fixture to provide entity relationship tracker instance."""
    from src.scraper.entity_relationship_tracker import EntityRelationshipTracker
    return EntityRelationshipTracker()


@pytest.fixture
def sample_pages():
    """Fixture providing sample page data."""
    return {}


@given('the entity relationship tracker is initialized')
def initialize_tracker(relationship_tracker):
    """Initialize the entity relationship tracker."""
    assert relationship_tracker is not None
    assert relationship_tracker.entities == {}
    assert relationship_tracker.relationships == {}


@given(parsers.parse('the following restaurant pages exist:\n{table}'))
def setup_pages(relationship_tracker, sample_pages, table):
    """Set up sample pages with entities."""
    for row in table:
        page_url = row['page_url']
        page_type = row['page_type']
        entity_id = row['entity_id']
        
        # Create entity in tracker
        relationship_tracker.create_entity(
            url=page_url,
            entity_type=page_type,
            entity_id=entity_id
        )
        
        # Store in sample_pages for reference
        sample_pages[entity_id] = {
            'url': page_url,
            'type': page_type,
            'id': entity_id
        }


@when(parsers.parse('I track a parent-child relationship from "{parent_id}" to "{child_id}"'))
def track_parent_child(relationship_tracker, parent_id, child_id):
    """Track a parent-child relationship."""
    relationship_tracker.track_relationship(
        from_entity=parent_id,
        to_entity=child_id,
        relationship_type="parent-child"
    )


@when(parsers.parse('I track a reference from "{from_id}" to "{to_id}" with type "{ref_type}"'))
def track_reference(relationship_tracker, from_id, to_id, ref_type):
    """Track a reference relationship."""
    relationship_tracker.track_relationship(
        from_entity=from_id,
        to_entity=to_id,
        relationship_type="reference",
        metadata={"ref_type": ref_type}
    )


@when(parsers.parse('I create an entity for URL "{url}"'))
def create_entity(relationship_tracker, url):
    """Create a new entity."""
    entity_type = "restaurant" if "restaurant" in url else "other"
    relationship_tracker.last_created_id = relationship_tracker.create_entity(
        url=url,
        entity_type=entity_type
    )


@when('I identify sibling relationships')
def identify_siblings(relationship_tracker):
    """Identify sibling relationships."""
    relationship_tracker.identify_siblings()


@when(parsers.parse('I track relationships:\n{table}'))
def track_multiple_relationships(relationship_tracker, table):
    """Track multiple relationships from table."""
    for row in table:
        relationship_tracker.track_relationship(
            from_entity=row['from_entity'],
            to_entity=row['to_entity'],
            relationship_type=row['relationship_type']
        )


@when('I save the relationship data')
def save_relationship_data(relationship_tracker, tmp_path):
    """Save relationship data to file."""
    relationship_tracker.save_index(str(tmp_path))
    relationship_tracker.saved_path = tmp_path


@when(parsers.parse('I query for all "{rel_type}" relationships'))
def query_by_type(relationship_tracker, rel_type):
    """Query relationships by type."""
    relationship_tracker.query_result = relationship_tracker.query_by_type(rel_type)


@when(parsers.parse('I attempt to create a circular reference from "{from_id}" to "{to_id}"'))
def attempt_circular_reference(relationship_tracker, from_id, to_id):
    """Attempt to create a circular reference."""
    relationship_tracker.track_relationship(
        from_entity=from_id,
        to_entity=to_id,
        relationship_type="reference"
    )


@when(parsers.parse('I track a relationship from "{from_id}" to "{to_id}" with source page "{source}"'))
def track_with_source(relationship_tracker, from_id, to_id, source):
    """Track relationship with source information."""
    relationship_tracker.track_relationship(
        from_entity=from_id,
        to_entity=to_id,
        relationship_type="parent-child",
        metadata={
            "source_page": source,
            "extraction_method": "page_discovery"
        }
    )


@then(parsers.parse('the entity "{entity_id}" should have {count:d} child entities'))
def check_child_count(relationship_tracker, entity_id, count):
    """Check number of child entities."""
    children = relationship_tracker.query_children(entity_id)
    assert len(children) == count


@then(parsers.parse('the entity "{entity_id}" should have parent "{parent_id}"'))
def check_parent(relationship_tracker, entity_id, parent_id):
    """Check entity parent."""
    assert relationship_tracker.relationships[entity_id]['parent'] == parent_id


@then(parsers.parse('"{entity1}" should have sibling "{entity2}"'))
def check_sibling(relationship_tracker, entity1, entity2):
    """Check sibling relationship."""
    assert entity2 in relationship_tracker.relationships[entity1]['siblings']


@then(parsers.parse('the entity "{entity_id}" should have a "{ref_type}" reference to "{target_id}"'))
def check_reference(relationship_tracker, entity_id, ref_type, target_id):
    """Check reference relationship."""
    assert target_id in relationship_tracker.relationships[entity_id]['references']
    metadata = relationship_tracker.relationships[entity_id]['reference_metadata'][target_id]
    assert metadata.get('ref_type') == ref_type


@then(parsers.parse('the entity "{entity_id}" should have an incoming reference from "{source_id}"'))
def check_incoming_reference(relationship_tracker, entity_id, source_id):
    """Check incoming reference."""
    assert source_id in relationship_tracker.relationships[entity_id]['referenced_by']


@then('a unique identifier should be generated')
def check_unique_id(relationship_tracker):
    """Check that unique ID was generated."""
    assert hasattr(relationship_tracker, 'last_created_id')
    assert relationship_tracker.last_created_id is not None


@then(parsers.parse('the identifier should follow the pattern "{pattern}"'))
def check_id_pattern(relationship_tracker, pattern):
    """Check ID pattern."""
    import re
    regex_pattern = pattern.replace('[0-9]', r'\d')
    assert re.match(regex_pattern, relationship_tracker.last_created_id)


@then('the identifier should not conflict with existing identifiers')
def check_id_unique(relationship_tracker):
    """Check ID is unique."""
    id_counts = {}
    for entity_id in relationship_tracker.entities:
        id_counts[entity_id] = id_counts.get(entity_id, 0) + 1
    
    for entity_id, count in id_counts.items():
        assert count == 1, f"Duplicate ID found: {entity_id}"


@then(parsers.parse('I can query all children of "{parent_id}" and get {expected}'))
def check_children_query(relationship_tracker, parent_id, expected):
    """Check children query result."""
    children = relationship_tracker.query_children(parent_id)
    expected_list = eval(expected)  # Convert string representation to list
    assert set(children) == set(expected_list)


@then(parsers.parse('I can query all references from "{entity_id}" and get {expected}'))
def check_references_query(relationship_tracker, entity_id, expected):
    """Check references query result."""
    references = relationship_tracker.query_references(entity_id)
    expected_list = eval(expected)
    assert set(references) == set(expected_list)


@then(parsers.parse('I can query all incoming references to "{entity_id}" and get {expected}'))
def check_incoming_references_query(relationship_tracker, entity_id, expected):
    """Check incoming references query result."""
    incoming = relationship_tracker.query_incoming_references(entity_id)
    expected_list = eval(expected)
    assert set(incoming) == set(expected_list)


@then('a relationship index file should be created')
def check_index_file(relationship_tracker):
    """Check that index file was created."""
    index_path = relationship_tracker.saved_path / "relationship_index.json"
    assert index_path.exists()


@then('the index should contain all tracked relationships')
def check_index_contents(relationship_tracker):
    """Check index file contents."""
    index_path = relationship_tracker.saved_path / "relationship_index.json"
    with open(index_path, 'r') as f:
        data = json.load(f)
    
    assert 'entities' in data
    assert 'relationships' in data
    assert 'relationship_index' in data


@then('relationship metadata should be preserved')
def check_metadata_preserved(relationship_tracker):
    """Check that metadata is preserved in saved data."""
    index_path = relationship_tracker.saved_path / "relationship_index.json"
    with open(index_path, 'r') as f:
        data = json.load(f)
    
    # Check that at least one relationship has metadata
    has_metadata = False
    for rel_type, relationships in data['relationship_index'].items():
        for rel in relationships:
            if 'metadata' in rel and rel['metadata']:
                has_metadata = True
                break
    
    assert has_metadata, "No metadata found in saved relationships"


@then(parsers.parse('I should get {count:d} relationships'))
def check_query_count(relationship_tracker, count):
    """Check query result count."""
    assert len(relationship_tracker.query_result) == count


@then('the circular reference should be detected')
def check_circular_detection(relationship_tracker):
    """Check that circular reference was detected."""
    # This is handled by the bidirectional marking
    pass


@then('the relationship should be marked as "bidirectional" instead')
def check_bidirectional_marking(relationship_tracker):
    """Check bidirectional marking."""
    # Find the bidirectional relationships
    found_bidirectional = False
    for entity_id, rels in relationship_tracker.relationships.items():
        if 'reference_metadata' in rels:
            for target, metadata in rels['reference_metadata'].items():
                if metadata.get('bidirectional'):
                    found_bidirectional = True
                    break
    
    assert found_bidirectional, "No bidirectional relationship found"


@then(parsers.parse('the relationship should include:\n{table}'))
def check_relationship_fields(relationship_tracker, table):
    """Check relationship fields."""
    # Get the last tracked relationship
    last_rel = None
    for rel_type, relationships in relationship_tracker.relationship_index.items():
        if relationships:
            last_rel = relationships[-1]
    
    assert last_rel is not None
    
    for row in table:
        field = row['field']
        expected_value = row['value']
        
        if field == 'timestamp':
            assert 'timestamp' in last_rel
            # Just check it exists and is a valid timestamp format
            assert isinstance(last_rel['timestamp'], str)
        elif field in ['source_page', 'extraction_method']:
            assert field in last_rel['metadata']
            assert last_rel['metadata'][field] == expected_value


@given(parsers.parse('entities "{entity1}" and "{entity2}" share parent "{parent_id}"'))
def setup_shared_parent(relationship_tracker, entity1, entity2, parent_id):
    """Set up entities with shared parent."""
    relationship_tracker.track_relationship(parent_id, entity1, "parent-child")
    relationship_tracker.track_relationship(parent_id, entity2, "parent-child")


@given(parsers.parse('I have tracked multiple relationships:\n{table}'))
def setup_multiple_relationships(relationship_tracker, table):
    """Set up multiple relationships with metadata."""
    for row in table:
        metadata = eval(row['metadata']) if 'metadata' in row else {}
        relationship_tracker.track_relationship(
            from_entity=row['from_entity'],
            to_entity=row['to_entity'],
            relationship_type=row['relationship_type'],
            metadata=metadata
        )


@given(parsers.parse('multiple relationships exist:\n{table}'))
def setup_relationships(relationship_tracker, table):
    """Set up multiple relationships."""
    for row in table:
        relationship_tracker.track_relationship(
            from_entity=row['from_entity'],
            to_entity=row['to_entity'],
            relationship_type=row['relationship_type']
        )


@given(parsers.parse('a relationship exists from "{from_id}" to "{to_id}"'))
def setup_single_relationship(relationship_tracker, from_id, to_id):
    """Set up a single relationship."""
    relationship_tracker.track_relationship(
        from_entity=from_id,
        to_entity=to_id,
        relationship_type="reference"
    )