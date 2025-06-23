Feature: Entity Relationship Tracking
  As a RAG system user
  I want to track relationships between entities across multiple pages
  So that I can maintain context and connections in the scraped data

  Background:
    Given the entity relationship tracker is initialized
    And the following restaurant pages exist:
      | page_url                    | page_type | entity_id   |
      | /restaurants/directory      | directory | dir_001     |
      | /restaurants/italian-bistro | detail    | rest_001    |
      | /restaurants/french-cafe    | detail    | rest_002    |
      | /locations/downtown         | location  | loc_001     |

  Scenario: Define parent-child relationships between pages
    When I track a parent-child relationship from "dir_001" to "rest_001"
    And I track a parent-child relationship from "dir_001" to "rest_002"
    Then the entity "dir_001" should have 2 child entities
    And the entity "rest_001" should have parent "dir_001"
    And the entity "rest_002" should have parent "dir_001"

  Scenario: Track sibling relationships between entities
    Given entities "rest_001" and "rest_002" share parent "dir_001"
    When I identify sibling relationships
    Then "rest_001" should have sibling "rest_002"
    And "rest_002" should have sibling "rest_001"

  Scenario: Create reference relationships between entities
    When I track a reference from "rest_001" to "loc_001" with type "location"
    Then the entity "rest_001" should have a "location" reference to "loc_001"
    And the entity "loc_001" should have an incoming reference from "rest_001"

  Scenario: Generate unique identifiers for entities
    When I create an entity for URL "/restaurants/new-restaurant"
    Then a unique identifier should be generated
    And the identifier should follow the pattern "rest_[0-9]{3}"
    And the identifier should not conflict with existing identifiers

  Scenario: Maintain bidirectional relationship mapping
    When I track relationships:
      | from_entity | to_entity | relationship_type |
      | dir_001    | rest_001  | parent-child      |
      | rest_001   | loc_001   | reference         |
      | dir_001    | rest_002  | parent-child      |
    Then I can query all children of "dir_001" and get ["rest_001", "rest_002"]
    And I can query all references from "rest_001" and get ["loc_001"]
    And I can query all incoming references to "loc_001" and get ["rest_001"]

  Scenario: Persist relationship metadata
    Given I have tracked multiple relationships:
      | from_entity | to_entity | relationship_type | metadata                    |
      | dir_001    | rest_001  | parent-child      | {"position": 1, "strength": "strong"} |
      | dir_001    | rest_002  | parent-child      | {"position": 2, "strength": "strong"} |
      | rest_001   | loc_001   | reference         | {"ref_type": "location"}    |
    When I save the relationship data
    Then a relationship index file should be created
    And the index should contain all tracked relationships
    And relationship metadata should be preserved

  Scenario: Query relationships by type
    Given multiple relationships exist:
      | from_entity | to_entity | relationship_type |
      | dir_001    | rest_001  | parent-child      |
      | dir_001    | rest_002  | parent-child      |
      | rest_001   | rest_002  | sibling          |
      | rest_001   | loc_001   | reference        |
    When I query for all "parent-child" relationships
    Then I should get 2 relationships
    When I query for all "reference" relationships
    Then I should get 1 relationship

  Scenario: Handle circular reference prevention
    Given a relationship exists from "rest_001" to "rest_002"
    When I attempt to create a circular reference from "rest_002" to "rest_001"
    Then the circular reference should be detected
    And the relationship should be marked as "bidirectional" instead

  Scenario: Track relationship timestamps and sources
    When I track a relationship from "dir_001" to "rest_001" with source page "/restaurants/directory"
    Then the relationship should include:
      | field           | value                    |
      | timestamp      | current_time             |
      | source_page    | /restaurants/directory   |
      | extraction_method | page_discovery         |