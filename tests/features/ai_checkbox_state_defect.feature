Feature: AI Enhancement Checkbox State Management
    As a user of the RAG_Scraper web interface
    I want the AI Enhancement checkbox state to be properly recognized by the system
    So that when I check the AI Enhancement box, the system actually enables AI features

    Background:
        Given the RAG_Scraper web interface is loaded
        And I am in multi-page scraping mode

    Scenario: AI Enhancement checkbox checked state is properly recognized
        Given I can see the AI Enhancement checkbox in the Advanced Options
        When I check the AI Enhancement checkbox
        Then the checkbox should appear visually checked
        And the system should recognize AI enhancement as enabled
        And the AI configuration panel should become visible
        And saving AI settings should not show "AI enhancement is disabled" message

    Scenario: AI Enhancement checkbox enables AI processing
        Given I have checked the AI Enhancement checkbox
        And I have configured a valid API key
        And I have selected AI features
        When I attempt to save AI settings
        Then the system should save the AI configuration successfully
        And should not display "No AI settings to save" error message
        And the AI configuration should be retrievable

    Scenario: AI Enhancement checkbox state persists during scraping
        Given I have checked the AI Enhancement checkbox
        And I have configured AI settings properly
        When I initiate a scraping operation
        Then the AI configuration should be included in the scraping request
        And the system should not fall back to traditional extraction only
        And the processing should attempt to use AI enhancement

    Scenario: AI Enhancement checkbox unchecked state is properly recognized
        Given I have the AI Enhancement checkbox checked
        And AI enhancement is currently enabled
        When I uncheck the AI Enhancement checkbox
        Then the checkbox should appear visually unchecked
        And the system should recognize AI enhancement as disabled
        And the AI configuration panel should become hidden
        And attempting to save should show appropriate disabled message

    Scenario: AI Enhancement checkbox state matches internal configuration
        Given I am viewing the Advanced Options panel
        When I check the AI Enhancement checkbox
        Then the getAIConfiguration() function should return ai_enhancement_enabled: true
        And when I uncheck the AI Enhancement checkbox
        Then the getAIConfiguration() function should return ai_enhancement_enabled: false
        And the visual state should always match the internal state

    Scenario: AI Enhancement checkbox works in both single-page and multi-page modes
        Given I am in multi-page mode
        When I check the AI Enhancement checkbox
        Then AI enhancement should be enabled for multi-page mode
        When I switch to single-page mode
        Then the single-page AI Enhancement checkbox should reflect the same state
        And AI enhancement should work consistently in both modes