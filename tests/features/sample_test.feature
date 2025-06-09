Feature: Sample BDD Test
  As a developer
  I want to verify pytest-bdd is working
  So that I can write acceptance tests

  Scenario: Basic BDD test passes
    Given I have a working pytest-bdd setup
    When I run a simple test
    Then the test should pass