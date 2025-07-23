Feature: Industry Status Management
  As a user of the RAG Scraper application
  I want to see which industries are available now and which are coming soon
  So that I can choose appropriate industries for my scraping tasks

  Background:
    Given the industry status configuration is loaded
    And Restaurant is marked as "coming_soon"
    And Medical is marked as "available"
    And Real Estate is marked as "coming_soon"

  Scenario: Display available industries in dropdown
    When I view the industry dropdown
    Then I should see "Medical" in the "Available Now" section
    And I should see "Medical" as selectable
    And I should not see "Medical" in the "Coming Soon" section

  Scenario: Display coming soon industries in dropdown
    When I view the industry dropdown
    Then I should see "Restaurant" in the "Coming Soon" section
    And I should see "Real Estate" in the "Coming Soon" section
    And I should see "Restaurant" as disabled
    And I should see "Real Estate" as disabled

  Scenario: Separate available and coming soon industries
    When I get industries grouped by status
    Then the "available" group should contain "Medical"
    And the "coming_soon" group should contain "Restaurant"
    And the "coming_soon" group should contain "Real Estate"
    And the "available" group should not contain "Restaurant"

  Scenario: Load industry status from configuration
    When I load the industry status configuration
    Then each industry should have a status field
    And each industry should have a description field
    And valid statuses should include "available" and "coming_soon"

  Scenario: Filter industries by availability status
    When I filter industries by status "available"
    Then I should only get industries marked as "available"
    When I filter industries by status "coming_soon"  
    Then I should only get industries marked as "coming_soon"