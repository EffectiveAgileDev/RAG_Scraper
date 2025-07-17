Feature: AI API Route Integration
  As a developer integrating AI features
  I want REST API endpoints for AI functionality
  So that the web interface can access AI-powered extraction

  Background:
    Given the RAG Scraper Flask application is running
    And AI backend modules are available

  Scenario: AI providers endpoint returns available LLM options
    When I send a GET request to "/api/ai/providers"
    Then the response status should be 200
    And the response should contain "openai" provider
    And the response should contain "claude" provider
    And the response should contain "ollama" provider
    And each provider should have "enabled" and "configured" status

  Scenario: AI configuration endpoint accepts valid settings
    Given I have valid AI configuration data
    When I send a POST request to "/api/ai/configure" with the configuration
    Then the response status should be 200
    And the response should contain "success": true
    And the AI settings should be saved to the session

  Scenario: AI configuration endpoint validates required fields
    Given I have invalid AI configuration data missing required fields
    When I send a POST request to "/api/ai/configure" with the invalid data
    Then the response status should be 400
    And the response should contain validation errors
    And the AI settings should not be saved

  Scenario: AI content analysis endpoint processes restaurant content
    Given AI enhancement is enabled
    And I have valid restaurant content data
    When I send a POST request to "/api/ai/analyze-content" with the content
    Then the response status should be 200
    And the response should contain "nutritional_context"
    And the response should contain "price_analysis"
    And the response should contain "cuisine_classification"
    And the response should contain "confidence_score"

  Scenario: AI content analysis endpoint handles missing API keys gracefully
    Given AI enhancement is enabled
    But no API key is configured
    When I send a POST request to "/api/ai/analyze-content" with content
    Then the response status should be 200
    And the response should contain "fallback_used": true
    And the response should contain traditional extraction results

  Scenario: Scraping endpoint integrates AI enhancement when enabled
    Given AI enhancement is enabled in configuration
    And I have valid scraping parameters
    When I send a POST request to "/api/scrape" with AI enhancement enabled
    Then the response should include AI-enhanced results
    And the response should contain "ai_analysis" section
    And traditional extraction should also be present as fallback

  Scenario: Scraping endpoint works normally when AI is disabled
    Given AI enhancement is disabled in configuration
    When I send a POST request to "/api/scrape" with standard parameters
    Then the response should contain traditional extraction results only
    And there should be no "ai_analysis" section in the response
    And the scraping should complete successfully