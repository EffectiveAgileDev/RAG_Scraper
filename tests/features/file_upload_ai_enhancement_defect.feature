Feature: File Upload AI Enhancement Integration
    As a user uploading PDF files for processing
    I want AI enhancement to work consistently with file uploads
    So that I can get AI-enhanced restaurant data from uploaded PDFs

    Background:
        Given the RAG_Scraper web interface is running
        And I have a valid OpenAI API key
        And I have uploaded a PDF file containing restaurant data

    Scenario: AI Enhancement Successfully Processes Uploaded PDF
        Given I have enabled AI enhancement in the settings
        And I have configured a valid OpenAI API key
        And I have selected AI features for analysis
        When I process the uploaded PDF file for RAG output
        Then the generated JSON file should contain an "ai_analysis" section
        And the ai_analysis should include confidence_score
        And the ai_analysis should include provider_used as "openai"
        And the ai_analysis should include analysis_timestamp
        And the ai_analysis should contain AI-enhanced restaurant data

    Scenario: AI Enhancement Fails Gracefully with Invalid API Key
        Given I have enabled AI enhancement in the settings
        And I have configured an invalid OpenAI API key
        When I process the uploaded PDF file for RAG output
        Then the processing should complete successfully
        And the generated JSON file should contain restaurant data
        And the ai_analysis section should contain error information
        And the ai_analysis should indicate fallback_used as true
        And the log should show "AI enhancement failed" with error details

    Scenario: AI Enhancement is Disabled for File Upload
        Given I have disabled AI enhancement in the settings
        When I process the uploaded PDF file for RAG output
        Then the generated JSON file should contain restaurant data
        And the ai_analysis section should not be present
        And the processing should use traditional pattern matching only

    Scenario: AI Enhancement Data Flow Consistency
        Given I have enabled AI enhancement in the settings
        And I have configured a valid OpenAI API key
        When I process the uploaded PDF file for RAG output
        Then the RestaurantData object should have ai_analysis attribute set
        And the ai_analysis should be properly converted to dictionary format
        And the JSON generator should find the ai_analysis field
        And the final JSON output should contain the ai_analysis section

    Scenario: Compare File Upload vs Multi-Page AI Enhancement
        Given I have enabled AI enhancement in the settings
        And I have configured a valid OpenAI API key
        When I process the same restaurant data via file upload
        And I process the same restaurant data via multi-page scraping
        Then both outputs should contain ai_analysis sections
        And both ai_analysis sections should have the same structure
        And both should use the same AI provider and configuration
        And both should have consistent field naming conventions