Feature: Model Selection Dropdown UI Integration
    As a user of the RAG_Scraper web interface
    I want to see and use model selection dropdowns in both single-page and multi-page modes
    So that I can choose specific AI models for my chosen provider

    Background:
        Given the RAG_Scraper web interface is loaded
        And I can see both single-page and multi-page AI Enhancement sections

    Scenario: Model dropdown appears when OpenAI is selected in single-page mode
        Given I am in single-page scraping mode
        And I have enabled AI Enhancement
        When I select "OpenAI" as the LLM provider
        Then I should see a model selection dropdown with id "singleModelSelect"
        And the model dropdown should be visible
        And it should have a refresh button with id "refreshSingleModelsButton"

    Scenario: Model dropdown appears when OpenAI is selected in multi-page mode
        Given I am in multi-page scraping mode
        And I have enabled AI Enhancement
        When I select "OpenAI" as the LLM provider
        Then I should see a model selection dropdown with id "modelSelect"
        And the model dropdown should be visible
        And it should have a refresh button with id "refreshModelsButton"

    Scenario: Model dropdown is hidden for non-OpenAI providers in single-page mode
        Given I am in single-page scraping mode
        And I have enabled AI Enhancement
        When I select "Claude" as the LLM provider
        Then the model selection dropdown "singleModelSelect" should be hidden
        When I select "Ollama" as the LLM provider
        Then the model selection dropdown "singleModelSelect" should be hidden

    Scenario: Model dropdown is hidden for non-OpenAI providers in multi-page mode
        Given I am in multi-page scraping mode
        And I have enabled AI Enhancement
        When I select "Claude" as the LLM provider
        Then the model selection dropdown "modelSelect" should be hidden
        When I select "Ollama" as the LLM provider
        Then the model selection dropdown "modelSelect" should be hidden

    Scenario: Model dropdown refreshes available models when API key is entered in single-page mode
        Given I am in single-page scraping mode
        And I have enabled AI Enhancement
        And I have selected "OpenAI" as the LLM provider
        And the model dropdown is visible
        When I enter a valid API key
        Then the model dropdown should automatically populate with available models
        And I should see "gpt-3.5-turbo" as the default selected option

    Scenario: Model dropdown refreshes available models when API key is entered in multi-page mode
        Given I am in multi-page scraping mode
        And I have enabled AI Enhancement
        And I have selected "OpenAI" as the LLM provider
        And the model dropdown is visible
        When I enter a valid API key
        Then the model dropdown should automatically populate with available models
        And I should see "gpt-3.5-turbo" as the default selected option

    Scenario: Model selection is included in AI configuration in single-page mode
        Given I am in single-page scraping mode
        And I have enabled AI Enhancement
        And I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        And the model dropdown is populated
        When I select "gpt-4" from the model dropdown
        And I save the AI configuration
        Then the saved configuration should include "gpt-4" as the selected model

    Scenario: Model selection is included in AI configuration in multi-page mode
        Given I am in multi-page scraping mode
        And I have enabled AI Enhancement
        And I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        And the model dropdown is populated
        When I select "gpt-4" from the model dropdown
        And I save the AI configuration
        Then the saved configuration should include "gpt-4" as the selected model

    Scenario: Manual model refresh works in single-page mode
        Given I am in single-page scraping mode
        And I have enabled AI Enhancement
        And I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        When I click the refresh models button "refreshSingleModelsButton"
        Then the model dropdown should refresh and show available models
        And no error messages should be displayed

    Scenario: Manual model refresh works in multi-page mode
        Given I am in multi-page scraping mode
        And I have enabled AI Enhancement
        And I have selected "OpenAI" as the LLM provider
        And I have entered a valid API key
        When I click the refresh models button "refreshModelsButton"
        Then the model dropdown should refresh and show available models
        And no error messages should be displayed