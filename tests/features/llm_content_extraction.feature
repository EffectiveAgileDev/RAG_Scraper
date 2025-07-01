Feature: LLM Content Extraction for AI-Powered Data Understanding
  As a user scraping business websites
  I want the LLM to extract implied information beyond exact matches
  So that I can get 10x more usable data for customer queries

  Background:
    Given the LLM extraction system is initialized
    And the Restaurant industry knowledge database is loaded

  Scenario: Extract implied information from restaurant content
    Given a restaurant webpage with content "Farm-to-table dining with seasonal ingredients from local producers"
    When I request LLM extraction for the Restaurant industry
    Then the LLM should identify implied category "Menu Items" with confidence > 0.7
    And the LLM should extract "locally sourced ingredients" as a menu characteristic
    And the LLM should extract "seasonal menu" as a menu characteristic
    And the extraction result should include source attribution

  Scenario: Understand context beyond exact matches
    Given a restaurant webpage with content "Perfect for romantic evenings with candlelit tables overlooking the harbor"
    When I request LLM extraction for the Restaurant industry
    Then the LLM should identify implied category "Dining Options" with confidence > 0.6
    And the LLM should extract "romantic atmosphere" as a dining option
    And the LLM should extract "harbor view" as an amenity
    And the LLM should extract "candlelit tables" as ambiance feature

  Scenario: Identify business differentiators from subtle content
    Given a restaurant webpage with content "Our head chef trained at Le Cordon Bleu and sources ingredients directly from Italian farms"
    When I request LLM extraction for the Restaurant industry
    Then the LLM should identify implied category "Staff" with confidence > 0.8
    And the LLM should extract "Michelin-trained chef" as a staff qualification
    And the LLM should identify implied category "Menu Items" with confidence > 0.7
    And the LLM should extract "authentic Italian ingredients" as a menu characteristic

  Scenario: Handle LLM API failures gracefully
    Given the LLM service is unavailable
    When I request LLM extraction for any content
    Then the system should return an empty extraction result
    And the system should log the API failure
    And the system should not crash or raise exceptions
    And the fallback message should indicate "LLM extraction unavailable"

  Scenario: Extract information across multiple industries
    Given a medical practice webpage with content "Board-certified specialists providing comprehensive care with same-day appointments"
    When I request LLM extraction for the Medical industry
    Then the LLM should identify implied category "Services" with confidence > 0.8
    And the LLM should extract "comprehensive medical care" as a service
    And the LLM should identify implied category "Staff" with confidence > 0.7
    And the LLM should extract "board-certified doctors" as staff qualification
    And the LLM should identify implied category "Appointments" with confidence > 0.9
    And the LLM should extract "same-day scheduling" as appointment option

  Scenario: Maintain extraction quality with confidence thresholds
    Given a webpage with vague content "We offer good service and quality products"
    When I request LLM extraction with confidence threshold 0.7
    Then the LLM should return minimal extractions due to low confidence
    And all returned extractions should have confidence >= 0.7
    And the system should log low-confidence content for review

  Scenario: Cache LLM responses for performance
    Given a restaurant webpage with specific content
    When I request LLM extraction for the first time
    Then the LLM API should be called
    When I request LLM extraction for the same content again
    Then the cached result should be returned
    And the LLM API should not be called again
    And the response time should be < 50ms for cached results

  Scenario: Track LLM usage statistics
    Given LLM usage tracking is enabled
    When I perform multiple LLM extractions
    Then the system should track total API calls
    And the system should track successful extractions
    And the system should track failed extractions
    And the system should track average confidence scores
    And the usage statistics should be accessible via get_llm_stats()