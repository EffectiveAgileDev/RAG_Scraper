Feature: AI Settings Persistence
  As a user of RAG_Scraper
  I want my AI settings to be saved securely
  So that I don't have to reconfigure them every time I use the application

  Background:
    Given I am on the RAG_Scraper web interface
    And I have expanded the advanced options panel

  Scenario: Save AI settings to persistent storage
    Given I have enabled AI Enhancement
    And I have selected "OpenAI" as the LLM provider
    And I have entered an API key "sk-test123456789"
    And I have set the confidence threshold to 0.8
    And I have enabled "Nutritional Analysis" feature
    When I click the "Save AI Settings" button
    Then the AI settings should be saved to persistent storage
    And I should see a success message "AI settings saved successfully"

  Scenario: Load saved AI settings on page refresh
    Given I have previously saved AI settings with provider "Claude"
    When I refresh the page
    And I expand the advanced options panel
    Then the AI Enhancement should be enabled
    And the LLM provider should be "Claude"
    And the API key field should show masked value "••••••••••"
    And the saved features should be enabled

  Scenario: Clear saved AI settings
    Given I have previously saved AI settings
    When I click the "Clear AI Settings" button
    And I confirm the action
    Then the AI settings should be removed from persistent storage
    And the AI Enhancement should be disabled
    And all AI fields should be reset to defaults

  Scenario: API key encryption in storage
    Given I have entered an API key "sk-mysecretkey123"
    When I save the AI settings
    Then the API key should be encrypted before storage
    And the encrypted value should not contain the original key text

  Scenario: Migrate session settings to permanent storage
    Given I have configured AI settings in the current session
    But I have not saved them permanently
    When I click "Make Settings Permanent"
    Then the session settings should be migrated to persistent storage
    And the settings should persist across browser sessions

  Scenario: Handle invalid API key on load
    Given I have saved AI settings with an expired API key
    When I load the saved settings
    Then I should see a warning "Saved API key may be invalid"
    But the other settings should still be loaded correctly

  Scenario: Per-browser settings isolation
    Given I have saved AI settings in Chrome browser
    When I access the application from Firefox browser
    Then I should not see the Chrome browser's saved settings
    And I should be able to save different settings for Firefox