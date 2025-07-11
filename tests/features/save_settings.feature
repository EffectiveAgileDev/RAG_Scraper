Feature: Save Settings Toggle
    As a user of RAG_Scraper
    I want to save my preferred settings
    So that I don't have to reconfigure them every time I use the application

    Background:
        Given I am on the RAG_Scraper home page

    Scenario: Save Settings toggle is visible
        Then I should see a "Save Settings" toggle
        And the toggle should be positioned between the target analysis and scraping mode sections
        And the toggle should be OFF by default

    Scenario: Settings persist when Save Settings is ON
        Given I turn ON the Save Settings toggle
        When I set the following settings:
            | Setting           | Value                    |
            | SCRAPING_MODE     | Multi-page               |
            | AGGREGATION_MODE  | SEGMENTED                |
            | OUTPUT_FORMAT     | PDF                      |
            | MAX_PAGES         | 100                      |
            | CRAWL_DEPTH       | 3                        |
        And I click "EXECUTE_EXTRACTION"
        And I refresh the page
        Then the Save Settings toggle should be ON
        And I should see the following settings:
            | Setting           | Value                    |
            | SCRAPING_MODE     | Multi-page               |
            | AGGREGATION_MODE  | SEGMENTED                |
            | OUTPUT_FORMAT     | PDF                      |
            | MAX_PAGES         | 100                      |
            | CRAWL_DEPTH       | 3                        |

    Scenario: Settings reset to defaults when Save Settings is OFF
        Given I have previously saved settings
        When I turn OFF the Save Settings toggle
        And I refresh the page
        Then I should see the following default settings:
            | Setting           | Value                    |
            | SCRAPING_MODE     | Single-page              |
            | AGGREGATION_MODE  | UNIFIED                  |
            | OUTPUT_FORMAT     | TEXT                     |
            | MAX_PAGES         | 50                       |
            | CRAWL_DEPTH       | 2                        |

    Scenario: Settings persist across browser sessions when ON
        Given I turn ON the Save Settings toggle
        And I configure custom settings
        When I close the browser
        And I open a new browser session
        And I navigate to the RAG_Scraper home page
        Then the Save Settings toggle should be ON
        And my custom settings should be restored

    Scenario: Toggle state itself persists
        Given I turn ON the Save Settings toggle
        When I refresh the page
        Then the Save Settings toggle should remain ON
        
    Scenario: Settings are saved immediately when toggle is turned ON
        Given the Save Settings toggle is OFF
        And I have configured custom settings
        When I turn ON the Save Settings toggle
        Then my current settings should be saved immediately
        And refreshing the page should restore these settings

    Scenario: Industry and Schema type are not affected by Save Settings
        Given I turn ON the Save Settings toggle
        And I select "Restaurant" as the industry
        And I select "RestW" as the schema type
        When I refresh the page
        Then the industry selection should be empty
        And the schema type should be at default
        # These are intentionally not saved as they are job-specific