Feature: Configuration Updates for Multi-Page Scraping
  As a developer
  I want to configure multi-page scraping parameters
  So that I can control how the scraper discovers and processes multiple pages

  Background:
    Given I have a configuration system for the scraper

  Scenario: Configure multi-page scraping parameters
    When I create a configuration with the following multi-page settings:
      | Parameter                | Value   |
      | max_pages_per_site      | 20      |
      | page_discovery_enabled  | true    |
      | follow_pagination       | true    |
      | max_crawl_depth        | 3       |
    Then the configuration should have max_pages_per_site set to 20
    And the configuration should have page_discovery_enabled set to true
    And the configuration should have follow_pagination set to true
    And the configuration should have max_crawl_depth set to 3

  Scenario: Validate link pattern configuration
    When I configure link patterns with the following rules:
      | Pattern Type    | Pattern                          | Action  |
      | include        | /restaurants/.*                   | follow  |
      | include        | /menu/.*                         | follow  |
      | exclude        | .*(login OR signup).*            | skip    |
      | exclude        | .*\.(jpg OR png OR gif OR pdf)$  | skip    |
    Then the configuration should include pattern "/restaurants/.*" for following
    And the configuration should include pattern "/menu/.*" for following
    And the configuration should exclude pattern ".*(login OR signup).*"
    And the configuration should exclude pattern ".*\.(jpg OR png OR gif OR pdf)$"

  Scenario: Set crawl depth and page limits
    When I set the following crawl limits:
      | Limit Type           | Value |
      | max_crawl_depth     | 2     |
      | max_pages_per_site  | 15    |
      | max_total_pages     | 100   |
      | page_timeout        | 45    |
    Then the crawler should not exceed depth 2
    And the crawler should process at most 15 pages per site
    And the crawler should stop after 100 total pages
    And each page should timeout after 45 seconds

  Scenario: Load configuration from file
    Given I have a configuration file "test_config.json" with:
      """
      {
        "urls": ["https://example.com"],
        "max_pages_per_site": 25,
        "page_discovery_enabled": true,
        "link_patterns": {
          "include": ["/restaurants/.*", "/reviews/.*"],
          "exclude": [".*\\.(jpg|png|gif)$"]
        },
        "crawl_settings": {
          "max_crawl_depth": 3,
          "follow_pagination": true,
          "respect_robots_txt": true
        }
      }
      """
    When I load the configuration from "test_config.json"
    Then the configuration should have max_pages_per_site set to 25
    And the configuration should have 2 include patterns
    And the configuration should have 1 exclude pattern
    And the crawl_settings should have max_crawl_depth set to 3

  Scenario: Save configuration to file
    Given I have a configuration with:
      | Parameter               | Value                    |
      | max_pages_per_site     | 30                       |
      | page_discovery_enabled | true                     |
      | output_directory       | /tmp/scraper_output      |
    When I save the configuration to "output_config.json"
    Then the file "output_config.json" should exist
    And the file should contain valid JSON
    And the JSON should have "max_pages_per_site" set to 30

  Scenario: Handle invalid configuration values
    When I try to create a configuration with invalid values:
      | Parameter          | Invalid Value | Expected Error              |
      | max_pages_per_site | -5           | must be positive            |
      | max_crawl_depth    | 0            | must be at least 1          |
      | page_timeout       | -30          | must be positive            |
      | rate_limit_delay   | -2.5         | cannot be negative          |
    Then each invalid value should raise an appropriate ValueError

  Scenario: Apply default configuration values
    When I create a configuration without specifying optional parameters
    Then the configuration should have these default values:
      | Parameter                | Default Value |
      | max_pages_per_site      | 10           |
      | page_discovery_enabled  | true         |
      | max_crawl_depth        | 2            |
      | follow_pagination      | false        |
      | respect_robots_txt     | true         |
      | concurrent_requests    | 3            |

  Scenario: Configure per-domain settings
    When I configure per-domain settings:
      | Domain           | Rate Limit | Max Pages | User Agent              |
      | restaurant1.com  | 1.0       | 50        | RAG_Scraper/1.0 Polite |
      | restaurant2.com  | 3.0       | 20        | RAG_Scraper/1.0 Fast   |
      | default         | 2.0       | 10        | RAG_Scraper/1.0        |
    Then domain "restaurant1.com" should have rate_limit of 1.0 seconds
    And domain "restaurant1.com" should have max_pages of 50
    And domain "restaurant2.com" should have rate_limit of 3.0 seconds
    And unknown domains should use default settings