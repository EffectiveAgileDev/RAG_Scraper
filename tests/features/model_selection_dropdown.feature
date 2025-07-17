Feature: Model Selection Dropdown
    As a user of the RAG_Scraper web interface
    I want to select which AI model to use with my chosen LLM provider
    So that I can use the most appropriate model for my needs

    Background:
        Given the RAG_Scraper web interface is loaded
        And I am in multi-page scraping mode
        And I can see the AI Enhancement checkbox in the Advanced Options
        And I have checked the AI Enhancement checkbox

    Scenario: Model dropdown appears when OpenAI provider is selected
        Given I have selected "OpenAI" as the LLM provider
        When I enter a valid API key
        Then I should see a model selection dropdown
        And the dropdown should be enabled and populated with models

    Scenario: Model dropdown shows available models for valid API key
        Given I have selected "OpenAI" as the LLM provider
        And I have entered a valid OpenAI API key
        When the model dropdown is populated
        Then I should see "gpt-3.5-turbo" in the model options
        And I should see "gpt-4" in the model options if available
        And I should not see non-text models like "dall-e-3"

    Scenario: Model dropdown shows "Not Implemented" for Claude provider
        Given I have selected "Claude" as the LLM provider
        When the model dropdown is populated
        Then I should see "Not Implemented" as the only option
        And the dropdown should be disabled

    Scenario: Model dropdown shows "Not Implemented" for Ollama provider
        Given I have selected "Ollama" as the LLM provider
        When the model dropdown is populated
        Then I should see "Not Implemented" as the only option
        And the dropdown should be disabled

    Scenario: Model dropdown shows error for invalid API key
        Given I have selected "OpenAI" as the LLM provider
        And I have entered an invalid API key
        When the model dropdown tries to populate
        Then I should see an error message about invalid API key
        And the dropdown should show no available models

    Scenario: Selected model is saved in AI configuration
        Given I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        And the model dropdown is populated with models
        When I select "gpt-4" from the model dropdown
        And I save the AI settings
        Then the AI configuration should include "gpt-4" as the selected model

    Scenario: Model dropdown defaults to gpt-3.5-turbo for OpenAI
        Given I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        When the model dropdown is populated
        Then "gpt-3.5-turbo" should be selected by default

    Scenario: Model dropdown refreshes when API key changes
        Given I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        And the model dropdown is populated
        When I change the API key to a different valid key
        Then the model dropdown should refresh with new available models