Feature: Data Aggregation for Multi-Page Restaurant Scraping
  As a developer
  I want to aggregate restaurant data from multiple pages
  So that I can maintain relationships between pages and create unified restaurant profiles

  Background:
    Given I have a data aggregator system
    And I have sample restaurant data from multiple pages

  Scenario: Aggregate restaurant data from multiple pages
    Given I have restaurant data from the following pages:
      | Page Type    | URL                                    | Restaurant Name | Address           | Phone         |
      | main         | https://restaurant1.com                | Mario's Pizza   | 123 Main St      | 555-0001     |
      | menu         | https://restaurant1.com/menu          | Mario's Pizza   | 123 Main St      | 555-0001     |
      | contact      | https://restaurant1.com/contact       | Mario's Pizza   | 123 Main St      | 555-0001     |
    When I aggregate the restaurant data
    Then I should have 1 unified restaurant profile
    And the restaurant profile should contain all data from the 3 pages
    And the restaurant should have complete information from all sources

  Scenario: Maintain parent-child relationships between pages
    Given I have restaurant data with hierarchical structure:
      | Page Level | URL                                    | Restaurant Name | Content Type     | Parent URL                    |
      | 1         | https://directory.com/restaurants      | Multiple        | directory        |                               |
      | 2         | https://restaurant1.com                | Mario's Pizza   | main_page        | https://directory.com/restaurants |
      | 3         | https://restaurant1.com/menu          | Mario's Pizza   | menu_page        | https://restaurant1.com       |
      | 3         | https://restaurant1.com/hours         | Mario's Pizza   | hours_page       | https://restaurant1.com       |
    When I aggregate the hierarchical data
    Then the aggregated data should maintain parent-child relationships
    And the directory page should reference the restaurant main page
    And the restaurant main page should reference its menu and hours pages
    And each page should know its level in the hierarchy

  Scenario: Handle duplicate data across pages
    Given I have restaurant data with duplicate information:
      | Source Page                           | Restaurant Name | Address           | Phone         | Email                |
      | https://restaurant1.com               | Mario's Pizza   | 123 Main St      | 555-0001     | info@marios.com     |
      | https://restaurant1.com/contact       | Mario's Pizza   | 123 Main Street  | (555) 000-1  | contact@marios.com  |
      | https://restaurant1.com/about         | Mario's Pizza   | 123 Main St      | 555-0001     | info@marios.com     |
    When I aggregate the data with deduplication
    Then I should have 1 restaurant profile
    And the restaurant should have the most complete address "123 Main Street"
    And the restaurant should have normalized phone number "555-0001"
    And the restaurant should have both email addresses
    And duplicate information should be consolidated

  Scenario: Create entity relationship mapping
    Given I have multiple restaurants from a directory:
      | Restaurant Name    | Main URL                          | Menu URL                              | Review URL                               |
      | Mario's Pizza     | https://restaurant1.com          | https://restaurant1.com/menu         | https://reviews.com/restaurant1         |
      | Luigi's Pasta     | https://restaurant2.com          | https://restaurant2.com/menu         | https://reviews.com/restaurant2         |
      | Tony's Grill      | https://restaurant3.com          | https://restaurant3.com/specials     | https://reviews.com/restaurant3         |
    When I create entity relationship mapping
    Then I should have 3 restaurant entities
    And each restaurant should be linked to its menu page
    And each restaurant should be linked to its review page
    And the relationship mapping should include entity types and connection strengths

  Scenario: Generate hierarchical data structure for output
    Given I have aggregated restaurant data with multiple levels:
      | Level | Entity Type     | Name             | Parent           | Children Count |
      | 0     | directory       | Restaurant Guide |                  | 2             |
      | 1     | restaurant      | Mario's Pizza    | Restaurant Guide | 3             |
      | 2     | menu_section    | Appetizers       | Mario's Pizza    | 5             |
      | 2     | menu_section    | Main Courses     | Mario's Pizza    | 8             |
      | 2     | info_page       | Contact Info     | Mario's Pizza    | 0             |
    When I generate hierarchical data structure
    Then the output should have a tree structure with 3 levels
    And the Restaurant Guide should be the root with 2 children
    And Mario's Pizza should have 3 child entities
    And each entity should maintain references to its parent and children
    And the structure should be suitable for RAG text generation

  Scenario: Merge overlapping restaurant information
    Given I have overlapping restaurant data from different sources:
      | Source           | Name            | Phone     | Hours                    | Cuisine      | Rating |
      | main_site        | Mario's Pizza   | 555-0001  | Mon-Sun 11am-10pm       | Italian      |        |
      | review_site      | Mario's Pizzeria| 555-0001  | Daily 11:00-22:00       | Italian, Pizza| 4.5   |
      | directory_site   | Mario's         | 555-0001  | 11am-10pm every day     | Pizza        | 4.3   |
    When I merge the overlapping information
    Then the merged restaurant should have name "Mario's Pizza"
    And the merged restaurant should have phone "555-0001"
    And the merged restaurant should have the most detailed hours "Mon-Sun 11am-10pm"
    And the merged restaurant should have cuisine "Italian, Pizza"
    And the merged restaurant should have the highest rating "4.5"
    And the merge should preserve data source information for traceability