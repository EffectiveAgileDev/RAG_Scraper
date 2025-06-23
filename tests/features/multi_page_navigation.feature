Feature: Multi-Page Website Navigation and Data Aggregation
  As a user of RAG_Scraper
  I want to extract restaurant data from multiple pages of a website
  So that I can get complete restaurant information from sites that spread data across pages

  Background:
    Given I have access to the RAG_Scraper web interface
    And the multi-page scraping functionality is enabled
    And I have a multi-page scraper configured with max 5 pages
    And I have mock HTML content for restaurant pages

  @multi_page @orchestrator
  Scenario: Scrape restaurant directory with detail pages
    Given I have a restaurant website with multiple relevant pages
    And the website has a home page with navigation to menu, about, and contact pages
    And each page contains restaurant-specific information
    When I initiate multi-page scraping on the restaurant website
    Then I should discover all relevant pages from the navigation
    And I should successfully scrape data from each discovered page
    And I should aggregate the data from all pages into a unified result
    And the result should contain information from all successfully processed pages

  @multi_page @orchestrator @error_handling
  Scenario: Handle failed page gracefully
    Given I have a restaurant website with multiple pages
    And one of the discovered pages will fail to load
    And other pages are accessible and contain valid data
    When I initiate multi-page scraping on the restaurant website
    Then I should attempt to process all discovered pages
    And I should handle the failed page without stopping the entire process
    And I should successfully process the remaining accessible pages
    And the result should include both successful and failed page lists
    And the aggregated data should contain information from successful pages only

  @multi_page @orchestrator @progress_tracking
  Scenario: Track progress across multiple pages
    Given I have a restaurant website with 4 discoverable pages
    And I provide a progress callback function to track scraping progress
    When I initiate multi-page scraping on the restaurant website
    Then I should receive progress notifications for page discovery
    And I should receive progress updates for each page being processed
    And I should receive completion notifications with success/failure counts
    And the progress should include restaurant name and page type information
    And the final result should contain accurate processing statistics

  @multi_page @discovery
  Scenario: Discover relevant pages on a restaurant website
    Given I provide a restaurant website URL "http://example-restaurant.com"
    When I start the multi-page scraping process
    Then the system should discover navigation links
    And identify relevant pages like "Menu", "About", "Contact", "Hours"
    And limit discovery to maximum 10 pages
    And exclude irrelevant pages like "Blog", "Careers", "Privacy"

  @multi_page @progress
  Scenario: Track progress during multi-page scraping
    Given I provide a restaurant website with 4 discoverable pages
    When I start the multi-page scraping process
    Then I should see "Discovered 4 pages for Restaurant Name"
    And I should see progress updates like "Processing page 1 of 4"
    And I should see page type notifications like "Processing Menu page"
    And I should see completion message "Completed Restaurant Name (4 pages processed)"

  @multi_page @data_aggregation
  Scenario: Aggregate data from multiple pages
    Given I provide a restaurant website with data spread across pages:
      | Page Type | Content |
      | Home      | Restaurant name, basic info |
      | Menu      | Menu items, price ranges |
      | Contact   | Phone, address, hours |
      | About     | Cuisine type, description |
    When I complete the multi-page scraping
    Then the final restaurant data should combine all information
    And should contain the restaurant name from home page
    And should contain menu items from menu page
    And should contain contact details from contact page
    And should contain cuisine type from about page

  @multi_page @conflict_resolution
  Scenario: Handle conflicting data across pages
    Given I provide a restaurant website with conflicting information:
      | Page Type | Field | Value |
      | Home      | Phone | (503) 555-1234 |
      | Contact   | Phone | (503) 555-5678 |
      | About     | Hours | Mon-Fri 9-5 |
      | Contact   | Hours | Mon-Sun 10-8 |
    When I complete the multi-page scraping
    Then the system should prioritize Contact page data for contact fields
    And should use Contact page phone number
    And should use Contact page hours
    And should indicate data sources in the result

  @multi_page @error_handling
  Scenario: Handle individual page failures gracefully
    Given I provide a restaurant website with 4 discoverable pages
    And the Menu page returns a 404 error
    When I start the multi-page scraping process
    Then I should see "Failed to load Menu page - continuing with other pages"
    And the scraping should continue with remaining pages
    And the final result should contain data from successful pages
    And should indicate which pages failed to load

  @multi_page @duplicate_prevention
  Scenario: Prevent processing duplicate pages
    Given I provide a restaurant website with navigation links
    And multiple links point to the same "Menu" page URL
    When I start the multi-page scraping process
    Then the Menu page should only be processed once
    And progress should show correct page count
    And should not show duplicate processing messages

  @multi_page @navigation_limits
  Scenario: Respect navigation limits to prevent infinite loops
    Given I provide a restaurant website with extensive navigation
    And the site has more than 10 relevant pages
    When I start the multi-page scraping process
    Then only the first 10 most relevant pages should be processed
    And I should see a message about page limit reached
    And the scraping should complete successfully

  @multi_page @batch_integration
  Scenario: Multi-page processing works with batch processing
    Given I provide multiple restaurant URLs for batch processing:
      | URL | Expected Pages |
      | http://restaurant1.com | 3 |
      | http://restaurant2.com | 5 |
      | http://restaurant3.com | 2 |
    When I start the batch scraping with multi-page enabled
    Then each restaurant should have its pages discovered and processed
    And progress should show both restaurant and page-level progress
    And final results should contain aggregated data for each restaurant

  @multi_page @structured_data_priority
  Scenario: Prioritize structured data from any page
    Given I provide a restaurant website with:
      | Page Type | Data Format | Quality |
      | Home      | HTML only   | Basic |
      | Menu      | JSON-LD     | High |
      | Contact   | Microdata   | Medium |
      | About     | HTML only   | Basic |
    When I complete the multi-page scraping
    Then structured data should be prioritized regardless of page
    And JSON-LD data from Menu page should have highest priority
    And Microdata from Contact page should have medium priority
    And HTML extraction should be used as fallback

  @multi_page @performance
  Scenario: Multi-page processing completes within acceptable time
    Given I provide a restaurant website with 5 discoverable pages
    When I start the multi-page scraping process
    Then the total processing time should be reasonable
    And each page should be processed with rate limiting
    And memory usage should remain within acceptable limits
    And progress updates should be timely and accurate