Feature: AI Results Display Enhancement
  As a user of the RAG Scraper
  I want to see AI-enhanced extraction results in the web interface
  So that I can benefit from AI-powered content analysis

  Background:
    Given the RAG Scraper web interface is loaded
    And AI enhancement is enabled
    And I have completed a scraping operation with AI analysis

  Scenario: AI-enhanced results show nutritional context
    Given the scraping results contain menu items
    When I view the extraction results
    Then I should see nutritional tags for menu items
    And I should see calorie range estimates
    And I should see dietary restriction indicators
    And nutritional context should be clearly marked as "AI Enhanced"

  Scenario: AI results display price tier analysis
    Given the scraping results contain pricing information
    When I view the price analysis section
    Then I should see price tier classification (budget/moderate/upscale)
    And I should see competitive positioning analysis
    And I should see value proposition insights
    And price analysis should show confidence score

  Scenario: AI cuisine classification is prominently displayed
    Given the scraping results contain restaurant information
    When I view the cuisine analysis section
    Then I should see primary cuisine type
    And I should see authenticity score (0-1 scale)
    And I should see cultural context explanation
    And cuisine classification should have confidence indicator

  Scenario: AI confidence scores are visible throughout results
    Given the scraping results contain AI analysis
    When I view any AI-enhanced section
    Then I should see confidence scores for each AI prediction
    And confidence scores should be color-coded (high=green, medium=yellow, low=red)
    And I should see extraction method indicators (AI vs Traditional)

  Scenario: Results can be toggled between AI and traditional views
    Given the scraping results contain both AI and traditional extraction
    When I click the "Toggle AI Enhancement" button in results
    Then the display should switch between AI-enhanced and traditional-only views
    And the current view mode should be clearly indicated
    And all data should remain accessible in both views

  Scenario: Multi-modal analysis results are displayed when available
    Given AI multi-modal analysis was performed
    And image analysis results are available
    When I view the multi-modal section
    Then I should see image-derived insights
    And I should see visual menu item descriptions
    And I should see atmosphere and ambiance analysis

  Scenario: AI error handling is gracefully displayed
    Given some AI analysis failed during processing
    When I view the results with partial AI failures
    Then I should see traditional extraction results for failed sections
    And I should see clear indicators where AI analysis was unavailable
    And I should see error explanations when appropriate
    And the overall results should still be complete and usable

  Scenario: Export functionality includes AI-enhanced data
    Given I have AI-enhanced scraping results
    When I export the results to JSON format
    Then the exported data should include AI analysis sections
    And traditional extraction data should also be included
    And the export should clearly mark AI vs traditional data sources