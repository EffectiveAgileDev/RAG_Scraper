Feature: AI Custom Questions Enhancement
  As a user scraping restaurant websites
  I want to add custom questions to AI analysis
  So that I can extract specific information I care about beyond standard restaurant data

  Background:
    Given the AI enhancement system is available
    And I have a valid OpenAI API key configured

  Scenario: Add custom question to AI settings
    Given I am on the scraping interface
    And I have enabled AI enhancement
    When I open the AI settings panel
    And I enter "Are takeout containers eco-friendly?" in the custom questions field
    And I save the AI configuration
    Then the custom question should be stored in my AI settings
    And the question should have a 200 character limit

  Scenario: Custom question included in AI analysis
    Given I have configured AI enhancement with a custom question "What's the wifi password policy?"
    And I have restaurant content to analyze
    When I perform AI analysis on the content
    Then the AI prompt should include my custom question
    And the AI should attempt to answer the custom question
    And the analysis results should include custom question responses

  Scenario: Multiple custom questions support
    Given I am configuring AI enhancement
    When I add multiple custom questions:
      | question                                    |
      | Pet-friendly seating available?            |
      | Do they offer gluten-free options?        |
      | What are the parking restrictions?        |
    And I save the configuration
    Then all custom questions should be stored
    And each question should be included in AI analysis

  Scenario: Custom question character limit enforcement
    Given I am adding a custom question
    When I enter a question longer than 200 characters
    Then the input should be limited to 200 characters
    And I should see a character count indicator
    And the system should show "200/200" when at the limit

  Scenario: Custom questions persist across sessions
    Given I have saved custom questions in my AI settings
    When I close and reopen the application
    And I load my saved AI settings
    Then my custom questions should be restored
    And they should be available for new scraping operations

  Scenario: Custom questions work with different AI providers
    Given I have custom questions configured
    When I switch between different AI providers:
      | provider |
      | openai   |
      | claude   |
      | custom   |
    Then the custom questions should work with each provider
    And the questions should be included in provider-specific prompts

  Scenario: Empty custom questions handling
    Given I am configuring AI enhancement
    When I leave the custom questions field empty
    And I save the configuration
    Then the AI analysis should work normally without custom questions
    And no additional prompting should occur for custom questions

  Scenario: Custom question results display
    Given I have performed AI analysis with custom questions
    When I view the analysis results
    Then I should see a dedicated section for custom question answers
    And each answer should be clearly labeled with its corresponding question
    And unanswered questions should be marked as "No information found"

  Scenario: Custom questions in JSON export
    Given I have scraped restaurant data with custom questions enabled
    And the AI analysis includes custom question responses
    When I export the results to JSON format
    Then the JSON should include a "custom_questions" section
    And each question-answer pair should be properly formatted
    And the export should maintain the original question text

  Scenario: Custom questions API integration
    Given I am using the AI API endpoints
    When I configure custom questions via "/api/ai/configure"
    Then the questions should be stored in the session configuration
    And subsequent "/api/ai/analyze-content" calls should include the questions
    And the API should return custom question responses in the analysis results