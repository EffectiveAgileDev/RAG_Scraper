Feature: OpenAI API Key Validation
    As a user of the RAG_Scraper web interface
    I want to validate my OpenAI API key before saving it
    So that I can ensure AI enhancement will work properly

    Background:
        Given the RAG_Scraper web interface is loaded
        And I am in multi-page scraping mode
        And I can see the AI Enhancement checkbox in the Advanced Options
        And I have checked the AI Enhancement checkbox

    Scenario: Valid API key validation shows success
        Given I have entered a valid OpenAI API key
        When I click the "Check Key" button
        Then I should see a success message indicating the key is valid
        And the available models should be displayed
        And the Save Settings button should be enabled

    Scenario: Invalid API key validation shows error
        Given I have entered an invalid OpenAI API key
        When I click the "Check Key" button
        Then I should see an error message indicating the key is invalid
        And no models should be displayed
        And I should see suggestions for fixing the issue

    Scenario: Network error during validation shows appropriate message
        Given I have entered an API key
        And there is a network connectivity issue
        When I click the "Check Key" button
        Then I should see a message indicating network connectivity problems
        And I should be able to retry the validation

    Scenario: Empty API key validation shows validation error
        Given the API key field is empty
        When I click the "Check Key" button
        Then I should see a message requiring an API key to be entered
        And no validation request should be made

    Scenario: API key validation with rate limiting
        Given I have entered a valid OpenAI API key
        And the OpenAI API is rate limiting requests
        When I click the "Check Key" button
        Then I should see a message about rate limiting
        And I should be advised to try again later

    Scenario: Check Key button is visible and accessible
        Given I am viewing the AI Enhancement configuration panel
        Then I should see a "Check Key" button next to the API key input field
        And the button should be clearly labeled and accessible
        And the button should be disabled when no API key is entered