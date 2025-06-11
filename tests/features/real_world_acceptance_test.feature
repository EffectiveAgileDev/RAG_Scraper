Feature: Real World Restaurant Scraping Acceptance Test
  As a user of RAG_Scraper
  I want to scrape actual restaurant websites
  So that I can extract real restaurant data for my RAG systems

  Background:
    Given the RAG_Scraper web interface is running on localhost:8080
    And I am on the main interface page

  Scenario: Scrape Three Real Restaurant Websites
    Given I have entered the real restaurant URLs
    And I have set the output directory to "/home/rod/test1"
    And I have left file mode as "Single file for all restaurants"
    When I click "Start Scraping"
    Then I should see "Scraping Completed Successfully!" message
    And I should see "Successfully processed 3 restaurant(s)"
    And the Generated files section should show actual file paths
    And files should be created in "/home/rod/test1" directory
    And the files should contain extracted restaurant data

  Scenario: Debug File Generation Issue
    Given I have completed scraping of real restaurant URLs
    And the scraping reports success
    When I check the API response for file generation
    Then the response should contain actual file paths not descriptions
    And the output_files array should not be empty
    And files should physically exist at the reported paths