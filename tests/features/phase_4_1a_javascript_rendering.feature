Feature: JavaScript Rendering and Popup Handling for Restaurant Websites
  As a user scraping restaurant websites
  I want the system to handle JavaScript-rendered content and common popups
  So that I can extract data from modern restaurant websites

  Background:
    Given the web scraping system is initialized
    And JavaScript rendering is enabled

  Scenario: Handle age verification popup
    Given a restaurant website "https://example-restaurant.com" with an age verification popup
    When I scrape the website in single-page mode
    Then the system should detect the age verification popup
    And the system should handle the popup automatically
    And the restaurant data should be successfully extracted
    And the extraction should include menu items and restaurant details

  Scenario: Handle newsletter signup modal
    Given a restaurant website with a newsletter signup modal
    When I scrape the website
    Then the system should detect the newsletter modal
    And the system should bypass the modal
    And continue with data extraction

  Scenario: Handle cookie consent banner
    Given a restaurant website with a cookie consent banner
    When I scrape the website
    Then the system should detect the cookie banner
    And the system should handle the banner appropriately
    And extract data without interruption

  Scenario: Extract data from JavaScript-rendered menu
    Given a restaurant website with JavaScript-rendered menu content
    When I scrape the website
    Then the system should wait for JavaScript execution
    And the system should extract dynamically loaded menu items
    And all menu sections should be captured

  Scenario: Handle location selection popup
    Given a restaurant website with multiple locations
    And a location selection popup appears on load
    When I scrape the website
    Then the system should detect the location selector
    And the system should handle location selection
    And extract data for the selected location

  Scenario: Fallback to static scraping when JavaScript not needed
    Given a restaurant website with static HTML content
    When I scrape the website
    Then the system should detect that JavaScript rendering is not required
    And use static scraping for better performance
    And successfully extract restaurant data

  Scenario: Handle timeout for slow JavaScript rendering
    Given a restaurant website with slow-loading JavaScript content
    When I scrape the website with a 30-second timeout
    Then the system should wait up to the timeout period
    And if content loads within timeout, extract the data
    And if timeout is exceeded, fall back to available content

  Scenario: Multi-page scraping with JavaScript content
    Given a restaurant website with JavaScript-rendered pages
    When I scrape the website in multi-page mode
    Then the system should handle JavaScript on each page
    And maintain session state between pages
    And aggregate data from all JavaScript-rendered pages