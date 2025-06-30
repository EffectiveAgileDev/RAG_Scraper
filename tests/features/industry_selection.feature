Feature: Industry Selection Interface
  As a user of the RAG Scraper
  I need to select an industry before scraping
  So that the system can apply industry-specific extraction logic

  Background:
    Given I am on the RAG Scraper homepage

  Scenario: User must select industry before scraping
    When I enter "https://example-restaurant.com" in the URL input field
    And I click the "Scrape Website" button without selecting an industry
    Then I should see an error message "Please select an industry before scraping"
    And the scraping process should not start

  Scenario: Display all 12 industry options
    When I click on the industry dropdown
    Then I should see the following industry options:
      | Industry                    |
      | Restaurant                  |
      | Real Estate                 |
      | Medical                     |
      | Dental                      |
      | Furniture                   |
      | Hardware / Home Improvement |
      | Vehicle Fuel                |
      | Vehicle Sales               |
      | Vehicle Repair / Towing     |
      | Ride Services               |
      | Shop at Home                |
      | Fast Food                   |

  Scenario: Validate industry selection is mandatory
    When I enter "https://example-business.com" in the URL input field
    And I have not selected any industry
    And I click the "Scrape Website" button
    Then the industry dropdown should be highlighted with an error state
    And I should see a validation message "Industry selection is required"
    And the URL input should retain the entered value

  Scenario: Store selected industry in session
    When I select "Restaurant" from the industry dropdown
    And I enter "https://restaurant1.com" in the URL input field
    And I click the "Scrape Website" button
    And the scraping completes successfully
    And I navigate back to the homepage
    Then the industry dropdown should still show "Restaurant" selected
    And I should be able to scrape another URL without reselecting the industry

  Scenario: Show industry-specific help text
    When I select "Restaurant" from the industry dropdown
    Then I should see help text "Extracts menu items, hours, location, ambiance, and dining options"
    When I select "Real Estate" from the industry dropdown
    Then I should see help text "Extracts property listings, agent info, prices, and features"
    When I select "Medical" from the industry dropdown
    Then I should see help text "Extracts services, insurance info, doctor profiles, and hours"

  Scenario Outline: Industry selection enables appropriate extraction
    When I select "<industry>" from the industry dropdown
    And I enter "<test_url>" in the URL input field
    And I click the "Scrape Website" button
    Then the system should use the "<industry>" specific extractor
    And the extracted data should include industry-specific categories

    Examples:
      | industry    | test_url                        |
      | Restaurant  | https://example-restaurant.com  |
      | Real Estate | https://example-realty.com      |
      | Medical     | https://example-clinic.com      |

  Scenario: Clear industry selection option
    When I select "Restaurant" from the industry dropdown
    And I click the "Clear Selection" button next to the dropdown
    Then the industry dropdown should show "Select an industry..."
    And any industry-specific help text should be hidden

  Scenario: Industry selection persists during batch processing
    When I select "Restaurant" from the industry dropdown
    And I enter multiple URLs in the batch input:
      """
      https://restaurant1.com
      https://restaurant2.com
      https://restaurant3.com
      """
    And I click the "Scrape All" button
    Then all URLs should be processed using the "Restaurant" extractor
    And the progress indicator should show "Processing as Restaurant websites"