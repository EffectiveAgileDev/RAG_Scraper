Feature: AI Enhancement Section Reorganization
  As a user configuring AI enhancement settings
  I want the AI enhancement options to be in a separate section next to Advanced Options
  So that I can easily find and configure AI features without cluttering the main advanced options

  Background:
    Given the RAG Scraper web interface is running
    And I am on the main scraping page

  Scenario: AI Enhancement section is positioned as a separate section
    When I expand the Advanced Options panel
    Then I should see a separate "AI Enhancement Options" section
    And the "AI Enhancement Options" section should be positioned to the right of "Advanced Options"
    And both sections should be at the same vertical level
    And the sections should be visually distinct from each other

  Scenario: AI Enhancement controls are moved to the new section
    When I expand the Advanced Options panel
    And I view the AI Enhancement Options section
    Then all AI enhancement controls should be in the AI Enhancement Options section
    And the AI provider selection should be in the AI Enhancement Options section
    And the AI feature toggles should be in the AI Enhancement Options section
    And the AI configuration options should be in the AI Enhancement Options section
    And no AI enhancement controls should remain in the Advanced Options section

  Scenario: AI Enhancement section has proper layout structure
    When I expand the Advanced Options panel
    And I expand the AI Enhancement Options section
    Then the AI Enhancement Options section should have its own header
    And the AI Enhancement Options section should have its own collapsible panel
    And the AI Enhancement Options section should function independently of Advanced Options
    And the AI Enhancement Options section should maintain proper spacing and alignment

  Scenario: Layout remains functional with both sections
    When I expand the Advanced Options panel
    And I expand the AI Enhancement Options section
    Then both sections should be fully functional
    And both sections should maintain their expanded state independently
    And the layout should adapt properly to different screen sizes
    And the sections should not overlap or interfere with each other