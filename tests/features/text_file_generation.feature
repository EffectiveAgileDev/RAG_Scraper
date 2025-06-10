Feature: Text File Generation for RAG Systems
  As a user of the RAG scraper system
  I want to generate properly formatted text files from scraped restaurant data
  So that I can use the data in RAG (Retrieval-Augmented Generation) systems

  Background:
    Given the system is configured for text file generation
    And the output directory has write permissions

  Scenario: Generate single restaurant text file with complete data
    Given I have scraped data for "Tony's Italian Restaurant"
    And the restaurant has complete information including:
      | Field         | Value                                    |
      | name          | Tony's Italian Restaurant                |
      | address       | 1234 Commercial Street, Salem, OR 97301 |
      | phone         | (503) 555-0123                          |
      | price_range   | $18-$32                                  |
      | hours         | Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm |
      | appetizers    | Fresh bruschetta, calamari rings, antipasto platter |
      | entrees       | Homemade pasta, wood-fired pizza, fresh seafood |
      | desserts      | Tiramisu, cannoli, gelato                |
      | cuisine       | Italian                                  |
    When I generate a text file for RAG systems
    Then the output file should be named "WebScrape_yyyymmdd-hhmm.txt"
    And the file should contain the exact format:
      """
      Tony's Italian Restaurant
      1234 Commercial Street, Salem, OR 97301
      (503) 555-0123
      $18-$32
      Hours: Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm

      APPETIZERS: Fresh bruschetta, calamari rings, antipasto platter
      ENTREES: Homemade pasta, wood-fired pizza, fresh seafood
      DESSERTS: Tiramisu, cannoli, gelato

      CUISINE: Italian
      """
    And the file should be UTF-8 encoded

  Scenario: Generate text file with minimal restaurant data
    Given I have scraped data for "Simple Cafe"
    And the restaurant has minimal information:
      | Field       | Value        |
      | name        | Simple Cafe  |
      | phone       | 555-1234     |
    When I generate a text file for RAG systems
    Then the output file should contain:
      """
      Simple Cafe
      555-1234
      """
    And missing fields should be omitted from the output

  Scenario: Generate multi-restaurant text file
    Given I have scraped data for multiple restaurants:
      | Restaurant Name     | Address                    | Phone        |
      | Tony's Italian      | 1234 Commercial St         | 503-555-0123 |
      | Blue Moon Diner     | 5678 State St              | 503-555-4567 |
      | Garden Bistro       | 9012 Park Ave              | 503-555-8901 |
    When I generate a text file for RAG systems
    Then the output file should contain all restaurants separated by double carriage returns
    And the format should be:
      """
      Tony's Italian
      1234 Commercial St
      503-555-0123


      Blue Moon Diner
      5678 State St
      503-555-4567


      Garden Bistro
      9012 Park Ave
      503-555-8901
      """

  Scenario: Generate text file from multi-page scraped data
    Given I have scraped a restaurant website with multiple pages
    And the data was aggregated from:
      | Page Type | Data Found                    |
      | home      | Restaurant name, cuisine      |
      | contact   | Address, phone, hours         |
      | menu      | Menu items, price range       |
    When I generate a text file for RAG systems
    Then the output should consolidate all multi-page data into a single restaurant entry
    And the data source pages should not be mentioned in the output file

  Scenario: File naming with timestamp format
    Given the current date is "2024-03-15" and time is "14:30"
    When I generate a text file for RAG systems
    Then the output file should be named "WebScrape_20240315-1430.txt"

  Scenario: Handle special characters in restaurant data
    Given I have scraped data for "Café España"
    And the restaurant has information with special characters:
      | Field    | Value                           |
      | name     | Café España                     |
      | cuisine  | Spanish & Latin American        |
      | menu     | Paella, tapas, crème brûlée     |
    When I generate a text file for RAG systems
    Then the output file should preserve all special characters correctly
    And the file should be UTF-8 encoded to support international characters

  Scenario: User selects custom output directory
    Given I want to save files to "/home/user/restaurant_data/"
    When I configure the output directory
    Then the system should validate directory permissions
    And future text files should be saved to the selected directory

  Scenario: Persistent output directory configuration
    Given I have previously selected "/home/user/restaurant_data/" as my output directory
    When I restart the application
    Then the system should remember my output directory preference
    And use it as the default for new text file generation

  Scenario: Directory permission validation
    Given I select an output directory without write permissions
    When I try to generate a text file
    Then the system should display an error message
    And prompt me to select a different directory with proper permissions

  Scenario: File overwrite protection
    Given a file named "WebScrape_20240315-1430.txt" already exists
    When I try to generate a text file with the same timestamp
    Then the system should ask for confirmation before overwriting
    And provide an option to generate with a different filename

  Scenario: Empty or failed scraping results
    Given I have no successful restaurant data extractions
    When I try to generate a text file for RAG systems
    Then the system should inform me that no data is available for file generation
    And no empty file should be created

  Scenario: Large batch text file generation
    Given I have scraped data for 50 restaurants successfully
    When I generate a text file for RAG systems
    Then all 50 restaurants should be included in a single file
    And each restaurant should be separated by double carriage returns
    And the file should not exceed reasonable size limits for RAG processing