Feature: AI Analysis Integration into JSON Output
  As a user of the RAG Scraper system
  I want AI analysis results to be included in the generated JSON files
  So that I can use AI-enhanced data in my RAG system

  Background:
    Given I have a configured AI analyzer with OpenAI provider
    And I have valid restaurant data with AI analysis results

  Scenario: AI analysis results are included in JSON export
    Given I have restaurant data with AI nutritional analysis
    When I generate a JSON export file
    Then the JSON output should contain an "ai_analysis" section
    And the "ai_analysis" section should include "nutritional_context"
    And the "ai_analysis" section should include "confidence_score"
    And the "ai_analysis" section should include "provider_used"

  Scenario: AI price analysis is included in JSON export
    Given I have restaurant data with AI price analysis
    When I generate a JSON export file
    Then the JSON output should contain "price_analysis" in the ai_analysis section
    And the price analysis should include "price_range_analysis"
    And the price analysis should include "competitive_positioning"

  Scenario: AI cuisine classification is included in JSON export
    Given I have restaurant data with AI cuisine classification
    When I generate a JSON export file
    Then the JSON output should contain "cuisine_classification" in the ai_analysis section
    And the cuisine classification should include "primary_cuisine"
    And the cuisine classification should include "authenticity_score"

  Scenario: AI dietary accommodations are included in JSON export
    Given I have restaurant data with AI dietary analysis
    When I generate a JSON export file
    Then the JSON output should contain "dietary_accommodations" in the ai_analysis section
    And the dietary accommodations should include allergen information
    And the dietary accommodations should include dietary restriction compatibility

  Scenario: JSON export works without AI analysis
    Given I have restaurant data without AI analysis
    When I generate a JSON export file
    Then the JSON output should not contain an "ai_analysis" section
    And the traditional restaurant data should be exported normally

  Scenario: AI analysis with low confidence is marked appropriately
    Given I have restaurant data with AI analysis below confidence threshold
    When I generate a JSON export file
    Then the JSON output should contain "meets_threshold" as false
    And the confidence score should be included
    And the low confidence should be clearly indicated

  Scenario: AI analysis errors are handled gracefully in JSON export
    Given I have restaurant data with AI analysis errors
    When I generate a JSON export file
    Then the JSON output should contain "ai_analysis" section with error information
    And the error should be clearly documented
    And the traditional extraction data should still be present