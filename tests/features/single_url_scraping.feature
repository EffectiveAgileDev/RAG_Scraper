Feature: Single Restaurant URL Scraping
  As a RAG system administrator
  I want to scrape a single restaurant website
  So that I can extract structured data for my directory system

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the localhost application

  Scenario: Successful single restaurant scraping with default fields
    Given I have a valid restaurant website URL "http://tonysitalian.com"
    And I have selected default data fields
    When I submit the URL for scraping
    Then I should see a progress indicator
    And the scraping should complete successfully
    And I should receive a properly formatted text file
    And the file should contain restaurant name
    And the file should contain restaurant address
    And the file should contain restaurant phone number
    And the file should contain restaurant website
    And the file should contain restaurant hours
    And the file should contain menu items with sections
    And the file should follow RAG format standards

  Scenario: Invalid URL handling
    Given I have an invalid URL "not-a-real-url"
    When I submit the URL for scraping
    Then I should see an error message
    And no file should be generated
    And the error should specify the URL validation failure

  Scenario: Unreachable website handling
    Given I have a valid but unreachable URL "http://nonexistent-restaurant.com"
    When I submit the URL for scraping
    Then I should see a network error message
    And no file should be generated
    And the error should specify the connection failure

  Scenario: Website with missing restaurant data
    Given I have a valid URL "http://incomplete-restaurant.com" with minimal data
    When I submit the URL for scraping
    Then the scraping should complete with warnings
    And I should receive a text file with available data
    And missing fields should be indicated as "Not Available"
    And the file should still follow RAG format standards

  Scenario: Default output file location
    Given I have a valid restaurant website URL "http://tonysitalian.com"
    And I have not specified an output directory
    When I submit the URL for scraping
    Then the file should be saved to the default downloads location
    And the filename should include timestamp
    And the filename should follow format "WebScrape_yyyymmdd-hhmm.txt"