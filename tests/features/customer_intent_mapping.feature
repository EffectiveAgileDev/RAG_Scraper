Feature: Customer Intent Mapping for Enhanced RAG Systems
  As a RAG system user
  I want restaurant data to be mapped to common customer questions and intents
  So that the system can directly answer customer queries about restaurants

  Background:
    Given a customer intent mapper is initialized
    And sample restaurant data has been extracted and structured

  Scenario: Map restaurant content to common customer questions
    Given restaurant data with menu, hours, location, and reviews
    When I analyze customer intent patterns for restaurants
    Then I should receive intent mappings including:
      | customer_question                        | mapped_content_type | confidence_score |
      | What are the best dishes here?          | menu_highlights     | 0.9              |
      | What time do you close?                 | business_hours      | 0.95             |
      | Where are you located?                  | address_info        | 0.98             |
      | Do you take reservations?               | contact_info        | 0.85             |
      | What's the atmosphere like?             | ambiance_description| 0.8              |
    And each mapping should include supporting evidence from the content

  Scenario: Categorize customer intents by decision-making stage
    Given restaurant data with comprehensive information
    When I categorize customer intents
    Then I should have intent categories including:
      | intent_category      | description                           | example_questions                    |
      | discovery           | Finding restaurants                   | "restaurants near me"                |
      | evaluation          | Comparing options                     | "is this place good", "reviews"     |
      | practical_planning  | Logistics and details                 | "hours", "parking", "reservations"  |
      | dietary_requirements| Special needs                         | "vegetarian options", "gluten-free" |
      | experience_planning | Setting expectations                  | "atmosphere", "dress code", "music" |
    And each category should map to relevant content sections

  Scenario: Generate customer-centric content summaries
    Given restaurant data structured for RAG
    When I generate customer intent summaries
    Then I should receive summaries answering common questions like:
      | question_type        | summary_content                                          |
      | quick_decision      | "Bistro Deluxe: French cuisine, $$$, 4.5 stars, Downtown" |
      | dietary_friendly    | "Vegetarian options: 5 dishes, Gluten-free: 3 options"    |
      | visit_planning      | "Open 11-10pm daily, Reservations recommended, Parking available" |
      | experience_preview  | "Romantic atmosphere, Dress code casual, Live music weekends" |
    And summaries should be optimized for direct customer consumption

  Scenario: Map content chunks to customer query templates
    Given semantically structured restaurant chunks
    When I create customer query mappings
    Then each chunk should be mapped to potential customer queries:
      | chunk_type          | example_queries                                           |
      | menu_item          | "Do you have [dish]?", "How much is [dish]?", "What's in [dish]?" |
      | business_hours     | "Are you open now?", "What time do you close?", "Hours today?" |
      | location_info      | "Where are you?", "Address?", "How do I get there?"      |
      | contact_details    | "Phone number?", "Can I make a reservation?", "Email?"   |
    And mappings should support natural language query variations

  Scenario: Score content relevance for customer intents
    Given restaurant content and customer query patterns
    When I score content relevance for different intents
    Then each content piece should have relevance scores for:
      | intent_type         | scoring_criteria                                    |
      | immediate_decision  | Key facts, ratings, price range                    |
      | detailed_research   | Reviews, detailed descriptions, full menu          |
      | visit_logistics     | Hours, location, contact, parking, reservations    |
      | dietary_filtering   | Allergen info, dietary options, ingredient lists   |
    And scores should be between 0.0 and 1.0 with confidence intervals

  Scenario: Handle industry-specific customer intent patterns
    Given multiple restaurant types (fine dining, fast food, cafe)
    When I analyze intent patterns by restaurant category
    Then intent mappings should be customized by restaurant type:
      | restaurant_type | priority_intents                                        |
      | fine_dining     | reservations, dress_code, wine_list, occasion_suitability |
      | fast_food       | speed, price, hours, drive_through, delivery           |
      | cafe           | wifi, work_space, coffee_types, pastries, atmosphere   |
    And each type should have different intent importance weightings

  Scenario: Create bidirectional intent-content relationships
    Given restaurant content mapped to customer intents
    When I create bidirectional relationships
    Then I should have relationships including:
      | relationship_type    | from_entity           | to_entity                |
      | answers_question    | menu_content          | "what food do you serve" |
      | supports_decision   | price_range           | "can I afford this"      |
      | enables_planning    | hours_info            | "when can I visit"       |
      | addresses_concern   | dietary_options       | "can I eat here"         |
    And relationships should support both content-to-intent and intent-to-content queries

  Scenario: Generate customer FAQ from mapped content
    Given restaurant data with comprehensive intent mappings
    When I generate customer FAQs
    Then I should receive structured FAQ including:
      | question                              | answer_source          | confidence |
      | What type of food do you serve?       | cuisine_and_menu       | 0.95       |
      | How expensive is it?                  | price_range_indicators | 0.9        |
      | Do you take walk-ins?                 | reservation_policy     | 0.8        |
      | Is it kid-friendly?                   | atmosphere_analysis    | 0.7        |
    And answers should be generated from the actual scraped content

  Scenario: Support temporal intent mapping
    Given restaurant data with time-sensitive information
    When I map temporal customer intents
    Then I should handle intents like:
      | temporal_intent         | mapped_content                    | time_sensitivity |
      | "are you open now"      | current_hours_today               | real_time        |
      | "lunch specials today"  | daily_specials_current            | daily            |
      | "weekend hours"         | weekend_operating_hours           | weekly           |
      | "holiday schedule"      | special_holiday_hours             | seasonal         |
    And mappings should consider current date/time context

  Scenario: Export intent mappings in queryable format
    Given completed customer intent mappings
    When I export intent mappings for RAG system integration
    Then the output should include:
      | export_component        | format  | content                                    |
      | intent_taxonomy         | JSON    | Hierarchical customer intent categories    |
      | content_mappings        | JSONL   | Content-to-intent relationship records     |
      | query_templates         | JSON    | Natural language query variations          |
      | relevance_scores        | JSON    | Content relevance by intent type           |
    And exports should be optimized for RAG system query processing

  Scenario: Handle ambiguous or multi-intent customer queries
    Given restaurant content and complex customer scenarios
    When I process ambiguous customer intents
    Then I should handle queries like:
      | ambiguous_query                    | detected_intents                          | resolution_strategy    |
      | "good for date night"              | atmosphere, price_range, hours            | multi_intent_response  |
      | "quick lunch near office"          | location, speed, menu_type                | weighted_prioritization|
      | "family dinner with dietary needs" | kid_friendly, dietary_options, capacity   | conditional_mapping    |
    And responses should address all detected intent components

  Scenario: Learn from customer interaction patterns
    Given historical customer interaction data
    When I analyze customer behavior patterns
    Then I should identify patterns like:
      | pattern_type           | description                                      | adaptation_action           |
      | common_question_gaps   | Questions asked but not well answered           | content_prioritization      |
      | successful_responses   | Queries that led to positive outcomes           | template_reinforcement      |
      | abandonment_points     | Where customers stop engaging                   | content_improvement_flags   |
    And patterns should inform future intent mapping improvements