Feature: HTML WTEG Schema Mapping for Restaurant Data
  As a RAG system developer
  I want to extract restaurant data from HTML sources and map it to WTEG schema
  So that I can process restaurant information from web pages consistently

  Background:
    Given the RAG Scraper is running
    And the HTML import processing system is enabled
    And the WTEG schema mapping is configured

  Scenario: Extract restaurant data from HTML content into WTEG schema
    Given I have a restaurant HTML content "restaurant.html"
    And the HTML contains structured restaurant information
    When I process the HTML with WTEG schema mapping
    Then the extracted data should be mapped to WTEG schema format
    And the restaurant name should be identified correctly
    And the location information should be extracted
    And the menu items should be organized by category
    And the contact information should be formatted properly

  Scenario: Extract restaurant data from URL into WTEG schema
    Given I have a restaurant URL "https://example.com/restaurant"
    And the URL contains accessible restaurant information
    When I process the URL with WTEG schema mapping
    Then the extracted data should be mapped to WTEG schema format
    And the restaurant name should be identified correctly
    And the location information should be extracted
    And the menu items should be organized by category
    And the contact information should be formatted properly

  Scenario: Parse menu sections from HTML structure
    Given I have a restaurant HTML content "complex_menu.html"
    And the HTML contains multiple menu sections
    When I process the HTML with menu section identification
    Then the appetizers section should be identified
    And the main courses section should be identified
    And the desserts section should be identified
    And the beverages section should be identified
    And each section should contain appropriate menu items

  Scenario: Extract restaurant hours from HTML content
    Given I have a restaurant HTML content "restaurant_hours.html"
    And the HTML contains operating hours information
    When I process the HTML with hours parsing
    Then the hours should be extracted in structured format
    And the weekday hours should be identified
    And the weekend hours should be identified
    And special hours should be noted if present

  Scenario: Identify service offerings from HTML content
    Given I have a restaurant HTML content "restaurant_services.html"
    And the HTML contains service information
    When I process the HTML with service extraction
    Then delivery availability should be identified
    And takeout options should be detected
    And catering services should be noted
    And reservation information should be extracted
    And online ordering should be detected if present

  Scenario: Pattern recognition for restaurant data in HTML
    Given I have a restaurant HTML content "varied_format.html"
    And the HTML uses varied formatting patterns
    When I process the HTML with pattern recognition
    Then the system should identify restaurant name patterns
    And address patterns should be recognized
    And phone number patterns should be extracted
    And email patterns should be identified
    And website patterns should be extracted
    And price patterns should be identified for menu items

  Scenario: Handle HTML with missing required information
    Given I have a restaurant HTML content "incomplete_info.html"
    And the HTML is missing some required WTEG fields
    When I process the HTML with WTEG schema mapping
    Then the system should extract available information
    And missing fields should be marked as unavailable
    And the confidence score should reflect completeness
    And the extraction should still succeed with partial data

  Scenario: Extract structured data from HTML with JSON-LD
    Given I have a restaurant HTML content "structured_data.html"
    And the HTML contains JSON-LD structured data
    When I process the HTML with structured data extraction
    Then the JSON-LD data should be extracted
    And the structured data should enhance pattern recognition
    And the restaurant information should be more accurate
    And the confidence score should be higher

  Scenario: Extract structured data from HTML with microdata
    Given I have a restaurant HTML content "microdata.html"
    And the HTML contains microdata markup
    When I process the HTML with structured data extraction
    Then the microdata should be extracted
    And the microdata should enhance pattern recognition
    And the restaurant information should be more accurate
    And the confidence score should be higher

  Scenario: Handle HTML with social media links
    Given I have a restaurant HTML content "social_media.html"
    And the HTML contains social media links
    When I process the HTML with pattern recognition
    Then Facebook links should be identified
    And Instagram links should be identified
    And Twitter links should be identified
    And other social media platforms should be detected
    And the social media links should be included in WTEG schema