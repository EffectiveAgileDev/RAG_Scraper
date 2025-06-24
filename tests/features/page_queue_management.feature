Feature: Page Queue Management and Traversal
  As a developer using the RAG_Scraper system  
  I want to have a dedicated PageQueueManager class
  So that queue management and traversal strategies are properly separated from scraping logic

  Background:
    Given I have a PageQueueManager with max 5 pages
    And I have sample restaurant website URLs for testing

  @queue_manager @initialization
  Scenario: Initialize page queue manager
    Given I create a new PageQueueManager instance
    When I initialize the page queue
    Then the queue should be empty
    And the visited pages set should be empty  
    And the priority queue should be empty
    And the default traversal strategy should be "BFS"

  @queue_manager @basic_operations
  Scenario: Add pages to queue with different strategies
    Given I have initialized the page queue
    When I add pages ["http://example.com/", "http://example.com/menu"] with "BFS" strategy
    Then the queue should contain 2 pages
    And getting the next page should return "http://example.com/"
    And getting the next page should return "http://example.com/menu"
    And the queue should be empty after both pages are retrieved

  @queue_manager @depth_first_strategy  
  Scenario: Add pages with depth-first strategy
    Given I have initialized the page queue
    When I add pages ["http://example.com/", "http://example.com/menu", "http://example.com/contact"] with "DFS" strategy
    Then getting the next page should return "http://example.com/contact"
    And getting the next page should return "http://example.com/menu"
    And getting the next page should return "http://example.com/"

  @queue_manager @priority_queue
  Scenario: Handle priority-based page ordering
    Given I have initialized the page queue
    When I add pages with priorities:
      | URL                        | Priority |
      | http://example.com/about   | 1        |
      | http://example.com/menu    | 10       |
      | http://example.com/contact | 5        |
    Then getting the next page should return "http://example.com/menu"
    And getting the next page should return "http://example.com/contact"  
    And getting the next page should return "http://example.com/about"

  @queue_manager @duplicate_prevention
  Scenario: Prevent duplicate pages in queue
    Given I have initialized the page queue
    When I add pages ["http://example.com/menu", "http://example.com/menu", "http://example.com/contact"]
    Then the queue should contain 2 unique pages
    And all pages retrieved should be unique

  @queue_manager @max_pages_limit
  Scenario: Respect maximum pages limit
    Given I have a PageQueueManager with max 3 pages
    And I have initialized the page queue
    When I add 5 pages to the queue
    Then the queue should contain at most 3 pages
    And no more than 3 pages total should be processed

  @queue_manager @traversal_strategies
  Scenario: Switch between traversal strategies
    Given I have initialized the page queue
    When I set the traversal strategy to "DFS"
    Then the traversal strategy should be "DFS"
    When I set the traversal strategy to "BFS"  
    Then the traversal strategy should be "BFS"

  @queue_manager @breadth_first_traversal
  Scenario: Perform breadth-first traversal
    Given I have a website with hierarchical structure:
      | Level | URL                           | Links To                      |
      | 0     | http://example.com/           | /level1-a, /level1-b         |
      | 1     | http://example.com/level1-a   | /level2-a                     |
      | 1     | http://example.com/level1-b   | /level2-b                     |
    When I perform breadth-first traversal from "http://example.com/"
    Then pages should be visited in breadth-first order
    And level 1 pages should be visited before level 2 pages

  @queue_manager @depth_first_traversal
  Scenario: Perform depth-first traversal
    Given I have a website with hierarchical structure:
      | Level | URL                           | Links To                      |
      | 0     | http://example.com/           | /branch1, /branch2            |
      | 1     | http://example.com/branch1    | /branch1/deep                 |
      | 1     | http://example.com/branch2    | /branch2/deep                 |
    When I perform depth-first traversal from "http://example.com/"
    Then pages should be visited in depth-first order
    And one branch should be explored completely before the other

  @queue_manager @priority_traversal
  Scenario: Perform priority-based traversal
    Given I have a restaurant website with different page types
    When I perform priority traversal from "http://example.com/"
    Then high-priority pages like "menu" should be visited first
    And low-priority pages like "blog" should be visited last
    And the traversal should respect the priority ordering

  @queue_manager @queue_statistics
  Scenario: Get accurate queue statistics
    Given I have initialized the page queue
    And I add 3 pages to the queue
    And I retrieve 1 page from the queue
    When I get queue statistics
    Then the statistics should show 2 pending pages
    And should show 1 visited page
    And should show the current traversal strategy

  @queue_manager @thread_safety
  Scenario: Queue operations are thread-safe
    Given I have initialized the page queue
    When I perform concurrent queue operations
    Then all operations should complete without errors
    And the queue state should remain consistent
    And no pages should be lost or duplicated due to race conditions

  @queue_manager @error_handling
  Scenario: Handle queue errors gracefully
    Given I have a PageQueueManager instance
    When I attempt invalid operations like setting invalid strategy
    Then appropriate errors should be raised
    And the queue state should remain valid
    And I should be able to continue with valid operations