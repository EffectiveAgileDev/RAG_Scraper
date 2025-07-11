Feature: RestW Schema Selection for Restaurant Data Extraction
    As a user
    I want to select RestW schema for restaurant data extraction
    So that I can get structured restaurant data in RestW format

    Background:
        Given the RAG Scraper web interface is available
        And the Restaurant industry is available in the industry dropdown

    Scenario: RestW schema option appears when Restaurant industry is selected
        Given I am on the main scraping page
        When I select "Restaurant" from the industry dropdown
        Then I should see a RestW schema selection option
        And the RestW schema option should be labeled "RestW - Enhanced Restaurant Data"
        And the RestW schema option should have helpful description text

    Scenario: RestW schema selection enables specialized extraction
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        When I select the RestW schema option
        Then the form should be configured for RestW extraction
        And I should see RestW-specific field options
        And the extraction should use WTEG processors

    Scenario: RestW schema selection shows appropriate help text
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        When I select the RestW schema option
        Then I should see help text explaining RestW features
        And the help text should mention structured location data
        And the help text should mention menu item extraction
        And the help text should mention service offerings
        And the help text should not mention "WTEG" terminology

    Scenario: RestW schema processes URLs with WTEG format
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I enter a restaurant URL "https://example-restaurant.com"
        And I click the extract button
        Then the extraction should use WTEG processors
        And the output should be in RestW format
        And the output should contain structured location data
        And the output should contain menu items with categories
        And the output should contain service offerings
        And the output should contain contact information

    Scenario: RestW schema processes uploaded files with WTEG format
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I upload a restaurant PDF file
        And I click the extract button
        Then the extraction should use WTEG PDF processors
        And the output should be in RestW format
        And the PDF should be parsed using WTEG schema
        And the output should contain structured restaurant data

    Scenario: RestW schema selection is persistent during session
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I perform an extraction
        And I return to the form
        Then the RestW schema option should still be selected
        And the form should maintain RestW configuration

    Scenario: RestW schema deselection reverts to standard extraction
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I deselect the RestW schema option
        Then the form should revert to standard restaurant extraction
        And RestW-specific options should be hidden
        And the extraction should use standard restaurant processors

    Scenario: RestW schema is only available for Restaurant industry
        Given I am on the main scraping page
        When I select "Medical" from the industry dropdown
        Then I should not see the RestW schema option
        When I select "Real Estate" from the industry dropdown
        Then I should not see the RestW schema option
        When I select "Restaurant" from the industry dropdown
        Then I should see the RestW schema option

    Scenario: RestW schema error handling
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I submit the form without entering URLs or files
        Then I should see appropriate error messages
        And the RestW schema selection should be preserved
        And the form should remain in RestW mode

    Scenario: RestW output format validation
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I extract data from a restaurant source
        Then the output should contain RestW-formatted data
        And the output should have location section with address fields
        And the output should have menu_items section with categorized items
        And the output should have services_offered section
        And the output should have contact_info section
        And the output should have web_links section
        And all field names should use RestW terminology not WTEG

    Scenario: RestW schema configuration is saved
        Given I am on the main scraping page
        And I have selected "Restaurant" from the industry dropdown
        And I have selected the RestW schema option
        When I configure RestW extraction options
        And I save the configuration
        Then the RestW configuration should be persisted
        And future sessions should remember RestW settings
        And the configuration should be available for batch processing