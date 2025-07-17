Feature: AI Settings Panel UI Integration
  As a user of the RAG Scraper web interface
  I want to configure AI enhancement options through the UI
  So that I can enable AI-powered extraction features when desired

  Background:
    Given the RAG Scraper web interface is loaded
    And I am on the main scraping page
    And the advanced options panel is available

  Scenario: AI Settings Panel is hidden by default
    Given I view the advanced options panel
    When I look for AI enhancement options
    Then the AI settings panel should be collapsed by default
    And the AI enhancement toggle should be OFF
    And no AI features should be visible initially

  Scenario: Enable AI Enhancement reveals configuration options
    Given I expand the advanced options panel
    When I toggle the "Enable AI Enhancement" switch to ON
    Then the AI configuration options should become visible
    And I should see LLM provider selection dropdown
    And I should see API key input field
    And I should see individual AI feature toggles
    And I should see confidence threshold slider

  Scenario: LLM Provider selection shows appropriate options
    Given AI Enhancement is enabled
    When I click on the LLM Provider dropdown
    Then I should see "OpenAI" as an option
    And I should see "Claude" as an option  
    And I should see "Ollama (Local)" as an option
    And "OpenAI" should be selected by default

  Scenario: API Key input field appears for external providers
    Given AI Enhancement is enabled
    When I select "OpenAI" as the LLM provider
    Then I should see an API key input field
    And the input field should be of type password for security
    And I should see placeholder text "Enter OpenAI API Key (optional)"
    
  Scenario: Individual AI feature toggles are present
    Given AI Enhancement is enabled
    When I view the AI feature options
    Then I should see "Nutritional Analysis" toggle (ON by default)
    And I should see "Price Analysis" toggle (ON by default)
    And I should see "Cuisine Classification" toggle (ON by default)
    And I should see "Multi-modal Analysis" toggle (OFF by default)

  Scenario: Confidence threshold slider is configurable
    Given AI Enhancement is enabled
    When I view the confidence threshold setting
    Then I should see a slider with range 0.1 to 1.0
    And the default value should be 0.7
    And I should see the current value displayed

  Scenario: Disable AI Enhancement hides all AI options
    Given AI Enhancement is enabled
    And AI configuration options are visible
    When I toggle the "Enable AI Enhancement" switch to OFF
    Then all AI configuration options should be hidden
    And AI features should be disabled for scraping