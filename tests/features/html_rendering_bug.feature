Feature: HTML Rendering Bug Fix in API Key Sections
    As a user of the RAG Scraper application
    I want the API key input sections to render correctly
    So that I don't see raw HTML code in the interface

    Background:
        Given the RAG Scraper web interface is loaded

    Scenario: Single-page API key section renders without HTML artifacts
        When I expand the single-page configuration section
        And I enable AI Enhancement in single-page mode
        And I look at the API key input section in single-page mode
        Then I should not see raw HTML text "autocomplete=" in the single-page section
        And I should not see raw HTML text "off" in the single-page section
        And I should not see raw HTML text "/>" in the single-page section
        And the single-page API key input should have autocomplete disabled

    Scenario: Multi-page API key section renders without HTML artifacts
        When I expand the AI Enhancement Options section in multi-page mode
        And I look at the API key input section in multi-page mode
        Then I should not see raw HTML text "autocomplete=" in the multi-page section
        And I should not see raw HTML text "off" in the multi-page section
        And I should not see raw HTML text "/>" in the multi-page section
        And the multi-page API key input should have autocomplete disabled

    Scenario: Both API key inputs function correctly
        When I expand the single-page configuration section
        And I enable AI Enhancement in single-page mode
        And I enter "test-key-123" in the single-page API key input
        Then the single-page API key input should contain "test-key-123"
        When I expand the AI Enhancement Options section in multi-page mode
        And I enter "test-key-456" in the multi-page API key input
        Then the multi-page API key input should contain "test-key-456"