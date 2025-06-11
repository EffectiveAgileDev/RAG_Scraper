Feature: API Integration
  As a developer or advanced user
  I want comprehensive REST API functionality
  So that I can integrate RAG_Scraper with other systems and tools

  Background:
    Given the RAG_Scraper Flask server is running on localhost:8080
    And all API endpoints are properly configured

  Scenario: URL Validation API Endpoint
    Given I have a list of restaurant URLs to validate
    When I make a POST request to "/api/validate" with:
      """
      {
        "urls": ["https://example-restaurant.com", "invalid-url"]
      }
      """
    Then I should receive a JSON response with validation results
    And the response should have proper HTTP status code 200
    And the response should contain accurate validation feedback for each URL
    And invalid URLs should be clearly identified with error messages

  Scenario: Single URL Validation API
    Given I have one restaurant URL to validate
    When I make a POST request to "/api/validate" with:
      """
      {
        "url": "https://restaurant.example.com"
      }
      """
    Then I should receive a JSON response with single URL validation
    And the response should indicate if the URL is valid or invalid
    And any validation errors should be included in the response

  Scenario: Scraping API Integration with File Generation
    Given I have valid restaurant URLs
    When I make a POST request to "/api/scrape" with:
      """
      {
        "urls": ["https://example.com"],
        "file_format": "text",
        "output_dir": "/tmp/test_output"
      }
      """
    Then I should receive a successful scraping response
    And the response should include actual file paths (not descriptions)
    And actual files should be created on the filesystem
    And processing statistics should be included in the response

  Scenario: Scraping API with PDF Format
    Given I have restaurant data to process
    When I make a POST request to "/api/scrape" with PDF format:
      """
      {
        "urls": ["https://example.com"],
        "file_format": "pdf",
        "output_dir": "/tmp/test_output"
      }
      """
    Then PDF files should be generated automatically
    And the response should contain PDF file paths
    And the files should be accessible and properly formatted

  Scenario: Scraping API with Dual Format
    Given I want both text and PDF output
    When I make a POST request to "/api/scrape" with:
      """
      {
        "urls": ["https://example.com"],
        "file_format": "both",
        "output_dir": "/tmp/test_output"
      }
      """
    Then both text and PDF files should be created
    And the response should contain paths for both file types
    And both files should contain the same restaurant data

  Scenario: Standalone File Generation API
    Given I have restaurant data in JSON format
    When I make a POST request to "/api/generate-file" with:
      """
      {
        "restaurant_data": [
          {
            "name": "Test Restaurant",
            "address": "123 Test St",
            "phone": "(555) 123-4567",
            "sources": ["api_test"]
          }
        ],
        "file_format": "pdf",
        "output_directory": "/tmp/test_output",
        "allow_overwrite": true
      }
      """
    Then a file should be created successfully
    And the response should include the actual file path
    And the file should be accessible and contain the provided data

  Scenario: Progress Monitoring API
    Given a scraping operation is in progress
    When I make a GET request to "/api/progress"
    Then I should receive current progress information
    And the response should include progress percentage
    And current operation status should be provided
    And time estimates should be included when available

  Scenario: File Configuration API - Get Configuration
    Given the file generation system is initialized
    When I make a GET request to "/api/file-config"
    Then I should receive current configuration settings
    And supported file formats should be listed
    And available directory options should be provided

  Scenario: File Configuration API - Update Configuration
    Given I want to update file generation settings
    When I make a POST request to "/api/file-config" with:
      """
      {
        "default_format": "pdf",
        "output_directory": "/custom/path",
        "allow_overwrite": false
      }
      """
    Then the configuration should be updated successfully
    And subsequent operations should use the new settings

  Scenario: Directory Validation API
    Given I want to validate a custom output directory
    When I make a POST request to "/api/validate-directory" with:
      """
      {
        "directory_path": "/tmp/test_directory"
      }
      """
    Then I should receive directory validation results
    And permission status should be included
    And recommendations should be provided if issues exist

  Scenario: Directory Creation API
    Given I need to create a custom output directory
    When I make a POST request to "/api/create-directory" with:
      """
      {
        "parent_directory": "/tmp",
        "directory_name": "rag_scraper_output"
      }
      """
    Then the directory should be created if possible
    And the response should confirm creation success or failure
    And appropriate permissions should be set

  Scenario: Error Handling in API Endpoints
    Given I make requests with invalid data
    When I send malformed JSON or missing required fields
    Then I should receive appropriate HTTP error codes
    And error messages should be clear and helpful
    And the system should not crash or hang

  Scenario: API Security Headers
    Given I make any request to the API
    When I examine the response headers
    Then appropriate security headers should be present
    And content type should be properly set
    And CORS policies should be enforced

  Scenario: API Response Consistency
    Given I make multiple API calls
    When I examine the response formats
    Then all responses should follow consistent JSON structure
    And error responses should follow the same pattern
    And status codes should be used appropriately

  Scenario: API Integration with Web Interface
    Given the web interface is making API calls
    When I monitor network traffic during web interface usage
    Then API calls should match the documented endpoints
    And request/response formats should be consistent
    And the web interface should handle API errors gracefully