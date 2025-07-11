Feature: Restaurant Schema Type Selection for Data Extraction
    As a user
    I want to select from multiple schema types for restaurant data extraction
    So that I can choose the most appropriate schema for my specific use case

    Background:
        Given the RAG Scraper web interface is available
        And the Restaurant industry is available in the industry dropdown

    Scenario: Restaurant schema type appears as default option
        Given I am on the main scraping page
        When I select "Restaurant" from the industry dropdown
        Then I should see a schema type selection section
        And I should see "Restaurant" as the default schema type option
        And the "Restaurant" schema type should be selected by default
        And I should see helpful description text for the Restaurant schema type

    Scenario: Multiple schema types are available for Restaurant industry
        Given I am on the main scraping page
        When I select "Restaurant" from the industry dropdown
        Then I should see a schema type selection section
        And I should see "Restaurant" as a schema type option
        And I should see "RestW" as a schema type option
        And exactly 2 schema type options should be available
        And the "Restaurant" schema type should be selected by default

    Scenario: Restaurant schema type selection configures standard extraction
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        When I select the "Restaurant" schema type
        Then the form should be configured for standard restaurant extraction
        And I should see standard restaurant field options
        And the extraction should use standard restaurant processors
        And I should not see RestW-specific field options

    Scenario: Restaurant schema type shows appropriate help text
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        When I select the "Restaurant" schema type
        Then I should see help text explaining Restaurant schema features
        And the help text should mention standard restaurant data extraction
        And the help text should mention menu information
        And the help text should mention location and contact details
        And the help text should not mention "RestW" or "WTEG" terminology

    Scenario: Restaurant schema type processes URLs with standard format
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I enter a restaurant URL "https://example-restaurant.com"
        And I click the extract button
        Then the extraction should use standard restaurant processors
        And the output should be in standard restaurant format
        And the output should contain basic restaurant information
        And the output should contain menu items
        And the output should contain contact information

    Scenario: Restaurant schema type processes uploaded files with standard format
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I upload a restaurant PDF file
        And I click the extract button
        Then the extraction should use standard restaurant PDF processors
        And the output should be in standard restaurant format
        And the PDF should be parsed using standard restaurant schema
        And the output should contain restaurant data

    Scenario: Restaurant schema type selection is persistent during session
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I perform an extraction
        And I return to the form
        Then the "Restaurant" schema type should still be selected
        And the form should maintain standard restaurant configuration

    Scenario: Schema type switching between Restaurant and RestW
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I switch to the "RestW" schema type
        Then the form should be configured for RestW extraction
        And I should see RestW-specific field options
        When I switch back to the "Restaurant" schema type
        Then the form should be configured for standard restaurant extraction
        And I should see standard restaurant field options

    Scenario: Schema type selection is only available for Restaurant industry
        Given I am on the main scraping page
        When I select "Medical" from the industry dropdown
        Then I should not see the schema type selection section
        When I select "Real Estate" from the industry dropdown
        Then I should not see the schema type selection section
        When I select "Restaurant" from the industry dropdown
        Then I should see the schema type selection section

    Scenario: Restaurant schema type error handling
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I submit the form without entering URLs or files
        Then I should see appropriate error messages
        And the "Restaurant" schema type selection should be preserved
        And the form should remain in standard restaurant mode

    Scenario: Restaurant schema type output format validation
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I extract data from a restaurant source
        Then the output should contain standard restaurant-formatted data
        And the output should have restaurant name and description
        And the output should have menu information
        And the output should have location and contact details
        And the output should have business hours
        And all field names should use standard restaurant terminology

    Scenario: Restaurant schema type configuration is saved
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the "Restaurant" schema type
        When I configure restaurant extraction options
        And I save the configuration
        Then the restaurant schema configuration should be persisted
        And future sessions should remember restaurant schema settings
        And the configuration should be available for batch processing