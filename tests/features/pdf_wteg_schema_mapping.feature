Feature: PDF WTEG Schema Mapping
  As a RAG Scraper user
  I want to extract restaurant data from PDF files into WTEG schema format
  So that I can use PDF menus and guides for restaurant information

  Background:
    Given the RAG Scraper is running
    And the PDF import processing system is enabled
    And the WTEG schema mapping is configured

  Scenario: Extract restaurant data from PDF menu into WTEG schema
    Given I have a restaurant PDF menu file "sample_menu.pdf"
    And the PDF contains structured restaurant information
    When I process the PDF with WTEG schema mapping
    Then the extracted data should be mapped to WTEG schema format
    And the restaurant name should be identified correctly
    And the location information should be extracted
    And the menu items should be organized by category
    And the contact information should be formatted properly

  Scenario: Parse menu sections from PDF structure
    Given I have a restaurant PDF menu file "complex_menu.pdf"
    And the PDF contains multiple menu sections
    When I process the PDF with menu section identification
    Then the appetizers section should be identified
    And the main courses section should be identified
    And the desserts section should be identified
    And the beverages section should be identified
    And each section should contain appropriate menu items

  Scenario: Extract restaurant hours from PDF text
    Given I have a restaurant PDF file "restaurant_info.pdf"
    And the PDF contains operating hours information
    When I process the PDF with hours parsing
    Then the hours should be extracted in structured format
    And the weekday hours should be identified
    And the weekend hours should be identified
    And special hours should be noted if present

  Scenario: Identify service offerings from PDF content
    Given I have a restaurant PDF file "service_menu.pdf"
    And the PDF contains service information
    When I process the PDF with service extraction
    Then delivery availability should be identified
    And takeout options should be detected
    And catering services should be noted
    And reservation information should be extracted

  Scenario: Pattern recognition for restaurant data
    Given I have a restaurant PDF file "varied_format.pdf"
    And the PDF uses non-standard formatting
    When I process the PDF with pattern recognition
    Then the system should identify restaurant name patterns
    And address patterns should be recognized
    And phone number patterns should be extracted
    And price patterns should be identified for menu items

  Scenario: Handle PDF with missing required information
    Given I have a restaurant PDF file "incomplete_menu.pdf"
    And the PDF is missing some required WTEG fields
    When I process the PDF with WTEG schema mapping
    Then the system should extract available information
    And missing fields should be marked as unavailable
    And the confidence score should reflect completeness
    And the extraction should still succeed with partial data

  Scenario: Process PDF with multiple restaurants
    Given I have a restaurant PDF file "restaurant_guide.pdf"
    And the PDF contains multiple restaurant entries
    When I process the PDF with WTEG schema mapping
    Then each restaurant should be extracted separately
    And each restaurant should have its own WTEG schema entry
    And the restaurants should be properly separated
    And all restaurant data should be preserved

  Scenario: Extract contact information with various formats
    Given I have a restaurant PDF file "contact_formats.pdf"
    And the PDF contains phone numbers in different formats
    When I process the PDF with contact extraction
    Then phone numbers should be normalized to standard format
    And international numbers should be handled correctly
    And extension numbers should be preserved
    And toll-free numbers should be identified

  Scenario: Handle PDF with embedded images and logos
    Given I have a restaurant PDF file "image_menu.pdf"
    And the PDF contains images and logos
    When I process the PDF with WTEG schema mapping
    Then text should be extracted around images
    And image-based text should be processed with OCR
    And the restaurant logo should not interfere with text extraction
    And menu item images should be noted but not processed

  Scenario: Validate extracted data against WTEG schema
    Given I have a restaurant PDF file "full_restaurant_data.pdf"
    And the PDF contains comprehensive restaurant information
    When I process the PDF with WTEG schema mapping
    Then the extracted data should conform to WTEG schema structure
    And all required WTEG fields should be validated
    And data types should match WTEG schema requirements
    And the schema validation should pass completely