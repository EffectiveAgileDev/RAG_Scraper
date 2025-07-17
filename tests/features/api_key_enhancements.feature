Feature: API Key and Provider Enhancements
  As a user of the RAG Scraper system
  I want improved API key handling and provider configuration
  So that I can easily configure and use various AI providers

  Background:
    Given I am on the web interface
    And I have expanded the advanced options panel
    And I have enabled AI Enhancement

  Scenario: API key entry is not obfuscated during typing
    Given I am in the AI configuration section
    When I click on the API key input field
    And I start typing an API key
    Then I should be able to see the characters I am typing
    And the input field should not use password masking
    And the API key should be visible in plain text during entry

  Scenario: API key visibility can be toggled
    Given I am in the AI configuration section
    And I have entered an API key
    When I click the visibility toggle button
    Then the API key should switch between visible and hidden states
    And I should be able to toggle visibility multiple times
    And the toggle button should show the appropriate icon

  Scenario: API key length validation is flexible
    Given I am in the API key input field
    When I enter a short API key like "sk-123"
    Then the system should accept it without length validation errors
    And the API key should be stored correctly
    And no length restriction warnings should appear

  Scenario: API key length validation accepts very long keys
    Given I am in the API key input field
    When I enter a very long API key with 200 characters
    Then the system should accept it without length validation errors
    And the API key should be stored completely
    And no truncation should occur

  Scenario: API key validation is based on content not length
    Given I am in the API key input field
    When I enter an API key that doesn't match traditional patterns
    Then the system should still accept it if it's not empty
    And the validation should focus on functionality not format
    And the API key should be passed to the provider for validation

  Scenario: Custom OpenAI-compatible provider configuration
    Given I am in the AI provider selection dropdown
    When I select "Custom OpenAI-Compatible" option
    Then I should see additional configuration fields
    And I should see a "Base URL" input field
    And I should see a "Model Name" input field
    And I should see a "Provider Name" input field

  Scenario: Custom provider base URL configuration
    Given I have selected "Custom OpenAI-Compatible" provider
    When I enter "https://my-local-llm.com/v1" as the base URL
    And I enter "gpt-3.5-turbo" as the model name
    And I enter "My Local LLM" as the provider name
    Then the custom provider should be configured correctly
    And the settings should be saved with the custom endpoint
    And the provider should appear as "My Local LLM" in the interface

  Scenario: Custom provider validation and testing
    Given I have configured a custom OpenAI-compatible provider
    When I click the "Test Connection" button
    Then the system should attempt to connect to the custom endpoint
    And I should receive feedback about the connection status
    And the test should use the custom base URL and model

  Scenario: Multiple custom providers can be configured
    Given I have configured one custom provider
    When I add another custom OpenAI-compatible provider
    Then both providers should be available in the dropdown
    And each provider should maintain its own configuration
    And I should be able to switch between them

  Scenario: Custom provider settings persistence
    Given I have configured a custom OpenAI-compatible provider
    When I save the AI settings
    And I reload the page
    Then the custom provider should still be available
    And the custom configuration should be restored
    And the base URL and model should be preserved

  Scenario: API key works with custom providers
    Given I have configured a custom OpenAI-compatible provider
    When I enter an API key for the custom provider
    And I test the connection
    Then the API key should be sent to the custom endpoint
    And the authentication should work with the custom provider
    And the key should be validated against the custom service

  Scenario: Error handling for custom provider configuration
    Given I am configuring a custom OpenAI-compatible provider
    When I enter an invalid base URL
    Then I should see a clear error message
    And the system should provide guidance on correct URL format
    And the error should not break the configuration interface

  Scenario: Custom provider fallback behavior
    Given I have configured a custom provider that becomes unavailable
    When I run an AI-enhanced extraction
    Then the system should handle the failure gracefully
    And I should see an informative error message
    And the traditional extraction should still work