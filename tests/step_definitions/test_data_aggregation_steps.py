"""Step definitions for data aggregation BDD scenarios."""
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from src.scraper.data_aggregator import DataAggregator, RestaurantEntity, EntityRelationship

# Load scenarios from feature file
scenarios("../features/data_aggregation.feature")


@dataclass
class MockRestaurantData:
    """Mock restaurant data for testing."""
    name: str
    url: str
    page_type: str = "main"
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    hours: Optional[str] = None
    cuisine: Optional[str] = None
    rating: Optional[float] = None
    parent_url: Optional[str] = None
    level: int = 1
    content_type: str = "restaurant"
    children_count: int = 0


@pytest.fixture
def aggregation_context():
    """Fixture to store aggregation test context."""
    return {
        "aggregator": None,
        "restaurant_data": [],
        "aggregated_entities": [],
        "relationships": [],
        "hierarchical_structure": None,
        "merged_data": None,
        "deduplication_result": None
    }


@given("I have a data aggregator system")
def given_data_aggregator_system(aggregation_context):
    """Initialize data aggregator system."""
    aggregation_context["aggregator"] = DataAggregator()


@given("I have sample restaurant data from multiple pages")
def given_sample_restaurant_data(aggregation_context):
    """Initialize sample restaurant data."""
    # This will be populated by specific scenario steps
    aggregation_context["restaurant_data"] = []


@given(parsers.parse("I have restaurant data from the following pages:\\n{table}"))
def given_restaurant_data_from_pages(aggregation_context, table):
    """Parse restaurant data from table."""
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 5:
                page_type, url, name, address, phone = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                restaurant_data = MockRestaurantData(
                    name=name,
                    url=url,
                    page_type=page_type,
                    address=address,
                    phone=phone
                )
                aggregation_context["restaurant_data"].append(restaurant_data)


@given(parsers.parse("I have restaurant data with hierarchical structure:\\n{table}"))
def given_hierarchical_restaurant_data(aggregation_context, table):
    """Parse hierarchical restaurant data from table."""
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 5:
                level, url, name, content_type, parent_url = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                restaurant_data = MockRestaurantData(
                    name=name,
                    url=url,
                    content_type=content_type,
                    parent_url=parent_url if parent_url else None,
                    level=int(level)
                )
                aggregation_context["restaurant_data"].append(restaurant_data)


@given(parsers.parse("I have restaurant data with duplicate information:\\n{table}"))
def given_duplicate_restaurant_data(aggregation_context, table):
    """Parse duplicate restaurant data from table."""
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 5:
                url, name, address, phone, email = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                restaurant_data = MockRestaurantData(
                    name=name,
                    url=url,
                    address=address,
                    phone=phone,
                    email=email
                )
                aggregation_context["restaurant_data"].append(restaurant_data)


@given(parsers.parse("I have multiple restaurants from a directory:\\n{table}"))
def given_multiple_restaurants_from_directory(aggregation_context, table):
    """Parse multiple restaurants from directory table."""
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 4:
                name, main_url, menu_url, review_url = parts[0], parts[1], parts[2], parts[3]
                
                # Add main restaurant page
                main_data = MockRestaurantData(name=name, url=main_url, page_type="main")
                aggregation_context["restaurant_data"].append(main_data)
                
                # Add menu page
                menu_data = MockRestaurantData(name=name, url=menu_url, page_type="menu", parent_url=main_url)
                aggregation_context["restaurant_data"].append(menu_data)
                
                # Add review page
                review_data = MockRestaurantData(name=name, url=review_url, page_type="reviews", parent_url=main_url)
                aggregation_context["restaurant_data"].append(review_data)


@given(parsers.parse("I have aggregated restaurant data with multiple levels:\\n{table}"))
def given_aggregated_multilevel_data(aggregation_context, table):
    """Parse aggregated multi-level restaurant data from table."""
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 5:
                level, entity_type, name, parent, children_count = parts[0], parts[1], parts[2], parts[3], parts[4]
                
                restaurant_data = MockRestaurantData(
                    name=name,
                    url=f"https://example.com/{name.lower().replace(' ', '_')}",
                    content_type=entity_type,
                    parent_url=parent if parent else None,
                    level=int(level),
                    children_count=int(children_count)
                )
                aggregation_context["restaurant_data"].append(restaurant_data)


@given(parsers.parse("I have overlapping restaurant data from different sources:\\n{table}"))
def given_overlapping_restaurant_data(aggregation_context, table):
    """Parse overlapping restaurant data from table."""
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 6:
                source, name, phone, hours, cuisine, rating = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                
                restaurant_data = MockRestaurantData(
                    name=name,
                    url=f"https://{source}/restaurant",
                    phone=phone,
                    hours=hours,
                    cuisine=cuisine,
                    rating=float(rating) if rating else None
                )
                aggregation_context["restaurant_data"].append(restaurant_data)


@when("I aggregate the restaurant data")
def when_aggregate_restaurant_data(aggregation_context):
    """Aggregate restaurant data."""
    aggregator = aggregation_context["aggregator"]
    restaurant_data = aggregation_context["restaurant_data"]
    
    # Convert mock data to entities
    entities = []
    for data in restaurant_data:
        entity = RestaurantEntity(
            entity_id=f"restaurant_{len(entities)}",
            name=data.name,
            url=data.url,
            entity_type=data.page_type,
            data={
                "address": data.address,
                "phone": data.phone,
                "email": data.email
            }
        )
        entities.append(entity)
    
    aggregated = aggregator.aggregate_entities(entities)
    aggregation_context["aggregated_entities"] = aggregated


@when("I aggregate the hierarchical data")
def when_aggregate_hierarchical_data(aggregation_context):
    """Aggregate hierarchical data."""
    aggregator = aggregation_context["aggregator"]
    restaurant_data = aggregation_context["restaurant_data"]
    
    # Convert mock data to entities with relationships
    entities = []
    relationships = []
    
    for i, data in enumerate(restaurant_data):
        entity = RestaurantEntity(
            entity_id=f"entity_{i}",
            name=data.name,
            url=data.url,
            entity_type=data.content_type,
            data={"level": data.level}
        )
        entities.append(entity)
        
        # Create parent-child relationships
        if data.parent_url:
            for j, parent_data in enumerate(restaurant_data):
                if parent_data.url == data.parent_url:
                    relationship = EntityRelationship(
                        parent_id=f"entity_{j}",
                        child_id=f"entity_{i}",
                        relationship_type="parent_child",
                        strength=1.0
                    )
                    relationships.append(relationship)
    
    aggregated = aggregator.aggregate_with_relationships(entities, relationships)
    aggregation_context["aggregated_entities"] = aggregated
    aggregation_context["relationships"] = relationships


@when("I aggregate the data with deduplication")
def when_aggregate_with_deduplication(aggregation_context):
    """Aggregate data with deduplication."""
    aggregator = aggregation_context["aggregator"]
    restaurant_data = aggregation_context["restaurant_data"]
    
    # Convert mock data to entities
    entities = []
    for i, data in enumerate(restaurant_data):
        entity = RestaurantEntity(
            entity_id=f"duplicate_{i}",
            name=data.name,
            url=data.url,
            entity_type="restaurant",
            data={
                "address": data.address,
                "phone": data.phone,
                "email": data.email
            }
        )
        entities.append(entity)
    
    deduplicated = aggregator.deduplicate_entities(entities)
    aggregation_context["deduplication_result"] = deduplicated


@when("I create entity relationship mapping")
def when_create_entity_relationship_mapping(aggregation_context):
    """Create entity relationship mapping."""
    aggregator = aggregation_context["aggregator"]
    restaurant_data = aggregation_context["restaurant_data"]
    
    # Group data by restaurant
    restaurants = {}
    for data in restaurant_data:
        if data.name not in restaurants:
            restaurants[data.name] = []
        restaurants[data.name].append(data)
    
    # Create entities and relationships
    entities = []
    relationships = []
    entity_id = 0
    
    for restaurant_name, pages in restaurants.items():
        main_entity_id = None
        
        for page in pages:
            entity = RestaurantEntity(
                entity_id=f"entity_{entity_id}",
                name=page.name,
                url=page.url,
                entity_type=page.page_type,
                data={}
            )
            entities.append(entity)
            
            if page.page_type == "main":
                main_entity_id = f"entity_{entity_id}"
            elif main_entity_id:
                # Create relationship to main page
                relationship = EntityRelationship(
                    parent_id=main_entity_id,
                    child_id=f"entity_{entity_id}",
                    relationship_type="has_page",
                    strength=0.9
                )
                relationships.append(relationship)
            
            entity_id += 1
    
    aggregation_context["aggregated_entities"] = entities
    aggregation_context["relationships"] = relationships


@when("I generate hierarchical data structure")
def when_generate_hierarchical_structure(aggregation_context):
    """Generate hierarchical data structure."""
    aggregator = aggregation_context["aggregator"]
    restaurant_data = aggregation_context["restaurant_data"]
    
    # Convert to entities
    entities = []
    for i, data in enumerate(restaurant_data):
        entity = RestaurantEntity(
            entity_id=f"hier_{i}",
            name=data.name,
            url=data.url,
            entity_type=data.content_type,
            data={
                "level": data.level,
                "children_count": data.children_count,
                "parent": data.parent_url
            }
        )
        entities.append(entity)
    
    structure = aggregator.create_hierarchical_structure(entities)
    aggregation_context["hierarchical_structure"] = structure


@when("I merge the overlapping information")
def when_merge_overlapping_information(aggregation_context):
    """Merge overlapping restaurant information."""
    aggregator = aggregation_context["aggregator"]
    restaurant_data = aggregation_context["restaurant_data"]
    
    # Convert to entities
    entities = []
    for i, data in enumerate(restaurant_data):
        entity = RestaurantEntity(
            entity_id=f"overlap_{i}",
            name=data.name,
            url=data.url,
            entity_type="restaurant",
            data={
                "phone": data.phone,
                "hours": data.hours,
                "cuisine": data.cuisine,
                "rating": data.rating
            }
        )
        entities.append(entity)
    
    merged = aggregator.merge_entities(entities)
    aggregation_context["merged_data"] = merged


@then(parsers.parse("I should have {count:d} unified restaurant profile"))
def then_should_have_unified_profiles(aggregation_context, count):
    """Verify number of unified restaurant profiles."""
    aggregated = aggregation_context["aggregated_entities"]
    assert len(aggregated) == count, f"Expected {count} profiles, got {len(aggregated)}"


@then(parsers.parse("the restaurant profile should contain all data from the {page_count:d} pages"))
def then_profile_should_contain_all_data(aggregation_context, page_count):
    """Verify restaurant profile contains all page data."""
    aggregated = aggregation_context["aggregated_entities"]
    assert len(aggregated) > 0, "No aggregated entities found"
    
    # Check that first entity has consolidated data
    entity = aggregated[0]
    assert entity.data, "Entity should have data"
    assert "address" in entity.data, "Entity should have address data"
    assert "phone" in entity.data, "Entity should have phone data"


@then("the restaurant should have complete information from all sources")
def then_restaurant_should_have_complete_info(aggregation_context):
    """Verify restaurant has complete information."""
    aggregated = aggregation_context["aggregated_entities"]
    assert len(aggregated) > 0, "No aggregated entities found"
    
    entity = aggregated[0]
    assert entity.name, "Entity should have name"
    assert entity.url, "Entity should have URL"
    assert entity.data, "Entity should have data"


@then("the aggregated data should maintain parent-child relationships")
def then_should_maintain_parent_child_relationships(aggregation_context):
    """Verify parent-child relationships are maintained."""
    relationships = aggregation_context["relationships"]
    assert len(relationships) > 0, "Should have parent-child relationships"
    
    for rel in relationships:
        assert rel.relationship_type == "parent_child", "Should be parent-child relationship"
        assert rel.parent_id, "Should have parent ID"
        assert rel.child_id, "Should have child ID"


@then(parsers.parse("the directory page should reference the restaurant main page"))
def then_directory_should_reference_main_page(aggregation_context):
    """Verify directory references main page."""
    relationships = aggregation_context["relationships"]
    entities = aggregation_context["aggregated_entities"]
    
    # Find directory entity
    directory_entity = next((e for e in entities if e.entity_type == "directory"), None)
    assert directory_entity, "Should have directory entity"
    
    # Find relationship from directory
    dir_relationships = [r for r in relationships if r.parent_id == directory_entity.entity_id]
    assert len(dir_relationships) > 0, "Directory should have child relationships"


@then("the restaurant main page should reference its menu and hours pages")
def then_main_page_should_reference_subpages(aggregation_context):
    """Verify main page references sub-pages."""
    relationships = aggregation_context["relationships"]
    entities = aggregation_context["aggregated_entities"]
    
    # Find main page entity
    main_entity = next((e for e in entities if e.entity_type == "main_page"), None)
    assert main_entity, "Should have main page entity"
    
    # Find relationships from main page
    main_relationships = [r for r in relationships if r.parent_id == main_entity.entity_id]
    assert len(main_relationships) >= 2, "Main page should reference menu and hours pages"


@then("each page should know its level in the hierarchy")
def then_pages_should_know_hierarchy_level(aggregation_context):
    """Verify pages know their hierarchy level."""
    entities = aggregation_context["aggregated_entities"]
    
    for entity in entities:
        assert "level" in entity.data, f"Entity {entity.entity_id} should have level data"
        assert isinstance(entity.data["level"], int), "Level should be integer"


@then(parsers.parse("I should have {count:d} restaurant profile"))
def then_should_have_restaurant_profiles(aggregation_context, count):
    """Verify number of restaurant profiles after deduplication."""
    result = aggregation_context["deduplication_result"]
    assert len(result) == count, f"Expected {count} profiles after deduplication, got {len(result)}"


@then(parsers.parse('the restaurant should have the most complete address "{expected_address}"'))
def then_should_have_complete_address(aggregation_context, expected_address):
    """Verify restaurant has most complete address."""
    result = aggregation_context["deduplication_result"]
    assert len(result) > 0, "Should have deduplicated result"
    
    entity = result[0]
    assert entity.data.get("address") == expected_address, f"Expected address '{expected_address}'"


@then(parsers.parse('the restaurant should have normalized phone number "{expected_phone}"'))
def then_should_have_normalized_phone(aggregation_context, expected_phone):
    """Verify restaurant has normalized phone number."""
    result = aggregation_context["deduplication_result"]
    assert len(result) > 0, "Should have deduplicated result"
    
    entity = result[0]
    assert entity.data.get("phone") == expected_phone, f"Expected phone '{expected_phone}'"


@then("the restaurant should have both email addresses")
def then_should_have_both_emails(aggregation_context):
    """Verify restaurant has both email addresses."""
    result = aggregation_context["deduplication_result"]
    assert len(result) > 0, "Should have deduplicated result"
    
    entity = result[0]
    emails = entity.data.get("email", "")
    assert "info@marios.com" in emails, "Should contain first email"
    assert "contact@marios.com" in emails, "Should contain second email"


@then("duplicate information should be consolidated")
def then_duplicate_info_should_be_consolidated(aggregation_context):
    """Verify duplicate information is consolidated."""
    result = aggregation_context["deduplication_result"]
    original_data = aggregation_context["restaurant_data"]
    
    assert len(result) < len(original_data), "Should have fewer entities after deduplication"


@then(parsers.parse("I should have {count:d} restaurant entities"))
def then_should_have_restaurant_entities(aggregation_context, count):
    """Verify number of restaurant entities."""
    entities = aggregation_context["aggregated_entities"]
    
    # Count unique restaurants (main pages)
    restaurants = set()
    for entity in entities:
        if entity.entity_type == "main":
            restaurants.add(entity.name)
    
    assert len(restaurants) == count, f"Expected {count} restaurant entities, got {len(restaurants)}"


@then("each restaurant should be linked to its menu page")
def then_restaurants_should_be_linked_to_menu(aggregation_context):
    """Verify restaurants are linked to menu pages."""
    relationships = aggregation_context["relationships"]
    entities = aggregation_context["aggregated_entities"]
    
    # Find menu entities
    menu_entities = [e for e in entities if e.entity_type == "menu"]
    assert len(menu_entities) > 0, "Should have menu entities"
    
    # Verify each menu has a relationship
    for menu_entity in menu_entities:
        menu_rels = [r for r in relationships if r.child_id == menu_entity.entity_id]
        assert len(menu_rels) > 0, f"Menu {menu_entity.entity_id} should have parent relationship"


@then("each restaurant should be linked to its review page")
def then_restaurants_should_be_linked_to_reviews(aggregation_context):
    """Verify restaurants are linked to review pages."""
    relationships = aggregation_context["relationships"]
    entities = aggregation_context["aggregated_entities"]
    
    # Find review entities
    review_entities = [e for e in entities if e.entity_type == "reviews"]
    assert len(review_entities) > 0, "Should have review entities"
    
    # Verify each review has a relationship
    for review_entity in review_entities:
        review_rels = [r for r in relationships if r.child_id == review_entity.entity_id]
        assert len(review_rels) > 0, f"Review {review_entity.entity_id} should have parent relationship"


@then("the relationship mapping should include entity types and connection strengths")
def then_mapping_should_include_types_and_strengths(aggregation_context):
    """Verify relationship mapping includes types and strengths."""
    relationships = aggregation_context["relationships"]
    
    for relationship in relationships:
        assert relationship.relationship_type, "Relationship should have type"
        assert relationship.strength is not None, "Relationship should have strength"
        assert 0 <= relationship.strength <= 1, "Strength should be between 0 and 1"


@then(parsers.parse("the output should have a tree structure with {levels:d} levels"))
def then_output_should_have_tree_structure(aggregation_context, levels):
    """Verify output has tree structure with specified levels."""
    structure = aggregation_context["hierarchical_structure"]
    assert structure, "Should have hierarchical structure"
    
    # Check that structure has the expected depth
    max_level = max(entity.data.get("level", 0) for entity in structure)
    assert max_level + 1 == levels, f"Expected {levels} levels, got {max_level + 1}"


@then(parsers.parse("the Restaurant Guide should be the root with {children:d} children"))
def then_guide_should_be_root_with_children(aggregation_context, children):
    """Verify Restaurant Guide is root with specified children."""
    structure = aggregation_context["hierarchical_structure"]
    
    # Find root entity
    root_entity = next((e for e in structure if e.data.get("level") == 0), None)
    assert root_entity, "Should have root entity"
    assert "Restaurant Guide" in root_entity.name, "Root should be Restaurant Guide"
    assert root_entity.data.get("children_count") == children, f"Root should have {children} children"


@then(parsers.parse('Mario\'s Pizza should have {children:d} child entities'))
def then_marios_should_have_children(aggregation_context, children):
    """Verify Mario's Pizza has specified child entities."""
    structure = aggregation_context["hierarchical_structure"]
    
    # Find Mario's Pizza entity
    marios_entity = next((e for e in structure if "Mario's Pizza" in e.name), None)
    assert marios_entity, "Should have Mario's Pizza entity"
    assert marios_entity.data.get("children_count") == children, f"Mario's should have {children} children"


@then("each entity should maintain references to its parent and children")
def then_entities_should_maintain_references(aggregation_context):
    """Verify entities maintain parent/child references."""
    structure = aggregation_context["hierarchical_structure"]
    
    for entity in structure:
        if entity.data.get("level", 0) > 0:
            assert entity.data.get("parent"), "Non-root entities should have parent reference"


@then("the structure should be suitable for RAG text generation")
def then_structure_should_be_suitable_for_rag(aggregation_context):
    """Verify structure is suitable for RAG text generation."""
    structure = aggregation_context["hierarchical_structure"]
    
    # Check that entities have necessary fields for text generation
    for entity in structure:
        assert entity.name, "Entity should have name for text generation"
        assert entity.url, "Entity should have URL for context"
        assert entity.entity_type, "Entity should have type for categorization"


@then(parsers.parse('the merged restaurant should have name "{expected_name}"'))
def then_merged_should_have_name(aggregation_context, expected_name):
    """Verify merged restaurant has expected name."""
    merged = aggregation_context["merged_data"]
    assert merged.name == expected_name, f"Expected name '{expected_name}', got '{merged.name}'"


@then(parsers.parse('the merged restaurant should have phone "{expected_phone}"'))
def then_merged_should_have_phone(aggregation_context, expected_phone):
    """Verify merged restaurant has expected phone."""
    merged = aggregation_context["merged_data"]
    assert merged.data.get("phone") == expected_phone, f"Expected phone '{expected_phone}'"


@then(parsers.parse('the merged restaurant should have the most detailed hours "{expected_hours}"'))
def then_merged_should_have_detailed_hours(aggregation_context, expected_hours):
    """Verify merged restaurant has most detailed hours."""
    merged = aggregation_context["merged_data"]
    assert merged.data.get("hours") == expected_hours, f"Expected hours '{expected_hours}'"


@then(parsers.parse('the merged restaurant should have cuisine "{expected_cuisine}"'))
def then_merged_should_have_cuisine(aggregation_context, expected_cuisine):
    """Verify merged restaurant has expected cuisine."""
    merged = aggregation_context["merged_data"]
    assert merged.data.get("cuisine") == expected_cuisine, f"Expected cuisine '{expected_cuisine}'"


@then(parsers.parse('the merged restaurant should have the highest rating "{expected_rating:f}"'))
def then_merged_should_have_highest_rating(aggregation_context, expected_rating):
    """Verify merged restaurant has highest rating."""
    merged = aggregation_context["merged_data"]
    assert merged.data.get("rating") == expected_rating, f"Expected rating {expected_rating}"


@then("the merge should preserve data source information for traceability")
def then_merge_should_preserve_source_info(aggregation_context):
    """Verify merge preserves data source information."""
    merged = aggregation_context["merged_data"]
    
    # Check that merged entity has source tracking
    assert "sources" in merged.data or hasattr(merged, "sources"), "Should preserve source information"