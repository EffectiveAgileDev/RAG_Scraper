Feature: File Output Format Validation
  As a RAG system administrator
  I want scraped data to be formatted correctly
  So that it integrates seamlessly with my RAG directory system

  Background:
    Given the RAG_Scraper web interface is running
    And I have access to the localhost application

  Scenario: Standard RAG format text file generation
    Given I have scraped restaurant data for "Tony's Italian Restaurant"
    When I generate a text file output
    Then the file should be UTF-8 encoded
    And the file should follow the RAG format structure:
      """
      Tony's Italian Restaurant
      1234 Commercial Street, Salem, OR 97301
      (503) 555-0123
      www.tonysitalian.com
      $18-$32
      Hours: Tuesday-Saturday 5pm-10pm, Sunday 4pm-9pm
      
      APPETIZERS: Fresh bruschetta, calamari rings, antipasto platter
      ENTREES: Homemade pasta, wood-fired pizza, fresh seafood
      DESSERTS: Tiramisu, cannoli, gelato
      """
    And each line should end with proper line breaks
    And the file should contain no HTML markup
    And the file should contain no escape characters

  Scenario: Multiple restaurant separator format
    Given I have scraped data for multiple restaurants:
      | Tony's Italian Restaurant |
      | Maria's Cantina          |
      | Joe's Coffee Shop        |
    When I generate a single text file output
    Then restaurants should be separated by double line breaks
    And the format should be:
      """
      [Restaurant 1 content]
      
      
      [Restaurant 2 content]
      
      
      [Restaurant 3 content]
      """
    And each restaurant section should follow RAG format
    And the file should be readable as a continuous text

  Scenario: Missing data field handling in format
    Given I have scraped incomplete restaurant data with missing phone
    When I generate a text file output
    Then missing phone should be indicated as "Phone: Not Available"
    And missing hours should be indicated as "Hours: Not Available"
    And missing menu should be indicated as "Menu: Not Available"
    And the overall format structure should remain consistent
    And all available data should be properly formatted

  Scenario: Special character handling in format
    Given I have restaurant data with special characters:
      | Name with "quotes" and & symbols |
      | Address with àccénts             |
      | Menu with émojis 🍕🍝           |
    When I generate a text file output
    Then special characters should be preserved correctly
    And UTF-8 encoding should handle all characters
    And quotes should not break the format
    And accented characters should display properly
    And emojis should be preserved if present

  Scenario: Price range format standardization
    Given I have restaurant data with various price formats:
      | Raw Price Data    | Expected Format |
      | $15.00 - $25.00  | $15-$25        |
      | 15-25 dollars     | $15-$25        |
      | $$$               | $$$ (Expensive) |
      | Moderate pricing  | Moderate       |
    When I generate text file outputs
    Then price ranges should follow standard format "$XX-$YY"
    And text prices should be preserved if no range available
    And price symbols should be normalized consistently

  Scenario: Hours format standardization
    Given I have restaurant data with various hour formats:
      | Raw Hours Data                    | Expected Format                           |
      | Mon-Fri: 11am-9pm, Sat: 10am-10pm | Monday-Friday 11am-9pm, Saturday 10am-10pm |
      | 11:00 AM - 9:00 PM daily         | Daily 11am-9pm                           |
      | Closed Mondays                    | Tuesday-Sunday [hours], Closed Mondays   |
    When I generate text file outputs
    Then hours should follow consistent format
    And day names should be fully spelled out
    And time format should use am/pm notation
    And closed days should be clearly indicated

  Scenario: Menu section organization format
    Given I have restaurant data with unorganized menu items
    When I generate a text file output
    Then menu items should be organized in sections
    And sections should use uppercase headers "APPETIZERS:", "ENTREES:", "DESSERTS:"
    And items within sections should be comma-separated
    And unknown items should go in "OTHER:" section
    And each section should be on its own line

  Scenario: File naming format validation
    Given I am generating output files
    When I create files at "2025-06-09 14:30"
    Then text file should be named "WebScrape_20250609-1430.txt"
    And the timestamp should reflect generation time
    And the format should be "WebScrape_yyyymmdd-hhmm.txt"
    And files should not overwrite existing files with same timestamp

  Scenario: Large content format handling
    Given I have restaurant data with very long descriptions
    And menu items exceeding 1000 characters per section
    When I generate a text file output
    Then the format should remain consistent
    And long content should not break line structure
    And the file should remain readable
    And memory usage should stay reasonable

  Scenario: Empty or minimal data format handling
    Given I have restaurant data with only name and address
    When I generate a text file output
    Then the file should still follow RAG format structure
    And missing fields should show "Not Available"
    And the format should be:
      """
      Restaurant Name
      123 Address Street, City, State Zip
      Phone: Not Available
      Website: Not Available
      Price Range: Not Available
      Hours: Not Available
      
      Menu: Not Available
      """
    And the structure should remain consistent

  Scenario: File size and performance validation
    Given I have scraped data for 100 restaurants
    When I generate a single text file output
    Then the file should be generated within 5 seconds
    And the file size should be reasonable (under 10MB)
    And the file should remain properly formatted throughout
    And memory usage should not exceed 100MB during generation
    And the file should be immediately readable after generation

  Scenario: Cross-platform file format compatibility
    Given I generate text files on Linux system
    When the files are transferred to Windows or Mac systems
    Then line endings should be compatible
    And UTF-8 encoding should be preserved
    And special characters should display correctly
    And the files should open in standard text editors
    And the RAG format should remain intact