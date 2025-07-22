Feature: Custom Questions in Multi-URL AI Analysis
    As a user scraping multiple restaurant websites
    I want my custom questions to be answered for all restaurants
    So that I can get consistent information across all scraped sites

    Background:
        Given the RAG Scraper application is running
        And AI enhancement is enabled with valid OpenAI API key
        And the following custom questions are configured:
            | question                              |
            | Do you have baby highchairs?          |
            | Do you serve custom made cocktails?   |
            | Do you serve brunch on weekends?      |

    Scenario: Custom questions appear in single URL scraping
        Given I am on the multi-page scraping interface
        When I enter the URL "https://mettavern.com/"
        And I click the "Scrape Website" button
        And I wait for scraping to complete
        Then the AI analysis should include custom questions section
        And each custom question should have an answer or "No information found"
        And the JSON output file should contain the custom_questions field

    Scenario: Custom questions appear in multi-URL scraping
        Given I am on the multi-page scraping interface
        When I enter the following URLs:
            | url                           |
            | https://mettavern.com/        |
            | https://piattinopdx.com/      |
        And I click the "Scrape Websites" button
        And I wait for all scraping to complete
        Then the AI analysis for EACH restaurant should include custom questions section
        And each restaurant's JSON output should contain the custom_questions field
        And the custom questions should be identical for all restaurants

    Scenario: Custom questions persist through AI result processing pipeline
        Given I am scraping multiple URLs with custom questions
        When the AI analyzer returns results with custom_questions field
        Then the custom_questions should be preserved in:
            | processing_stage                |
            | AI analyzer response            |
            | RestaurantData object           |
            | JSON export generator           |
            | Final output file               |

    Scenario: Custom questions survive fallback processing
        Given I am scraping a URL that triggers fallback processing
        When the AI response needs to be wrapped in extraction format
        Then the custom_questions field should still be preserved
        And the final output should contain all custom questions