Feature: AI Optional Advanced Features
  As a user of the RAG Scraper
  I want access to advanced AI features
  So that I can enhance extraction quality with multiple LLM providers, multi-modal analysis, and adaptive learning

  Background:
    Given the AI content analyzer is initialized
    And the Restaurant industry configuration is loaded

  # Claude AI Integration
  Scenario: Use Claude AI as alternative LLM provider
    Given Claude API credentials are configured
    And a restaurant webpage with complex menu descriptions
    When I run extraction using Claude as the LLM provider
    Then the extraction should use Claude's API
    And the results should include Claude-specific analysis
    And the response format should be consistent with OpenAI results
    And API usage should be tracked separately for Claude

  Scenario: Fallback from Claude to OpenAI when Claude fails
    Given Claude API is configured but unavailable
    And OpenAI API is configured as backup
    And a restaurant webpage needs processing
    When I run extraction with Claude as primary provider
    Then the system should detect Claude API failure
    And automatically fallback to OpenAI
    And the extraction should complete successfully
    And the fallback should be logged for monitoring

  # Local LLM Support
  Scenario: Use Ollama for local LLM processing
    Given Ollama is installed and running locally
    And a local model "llama2" is available
    And privacy mode is enabled in configuration
    When I run extraction using Ollama as the LLM provider
    Then the extraction should use local Ollama API
    And no external API calls should be made
    And the results should include local LLM analysis
    And processing should respect local resource constraints

  Scenario: Use llama.cpp for completely offline processing
    Given llama.cpp is configured with a local model file
    And offline mode is enabled
    And a restaurant webpage needs processing
    When I run extraction using llama.cpp
    Then the extraction should run completely offline
    And no network requests should be made
    And the results should be generated locally
    And processing time may be longer than API-based extraction

  Scenario: Dynamic LLM provider selection based on configuration
    Given multiple LLM providers are configured (OpenAI, Claude, Ollama)
    And provider preferences are set in configuration
    When I run extraction without specifying a provider
    Then the system should select the preferred provider
    And fallback to next available provider if primary fails
    And provider selection should be logged
    And the final provider used should be indicated in results

  # Multi-modal Content Analysis
  Scenario: Analyze restaurant webpage with images
    Given a restaurant webpage with menu images
    And image analysis is enabled in configuration
    And vision-capable LLM is available
    When I run multi-modal content analysis
    Then the system should extract text from images
    And identify menu items from photos
    And extract prices visible in images
    And correlate image content with text content
    And provide confidence scores for image-derived data

  Scenario: Process restaurant logo and branding images
    Given a restaurant webpage with logo and branding images
    And brand analysis is enabled
    When I run multi-modal brand analysis
    Then the system should identify restaurant logo
    And extract brand colors and design elements
    And analyze cuisine style from visual presentation
    And identify restaurant atmosphere from photos
    And generate visual brand summary

  Scenario: Handle mixed content with text and images
    Given a restaurant webpage with both text menus and image menus
    And cross-modal validation is enabled
    When I run comprehensive multi-modal analysis
    Then the system should extract data from both sources
    And cross-validate text against images
    And resolve conflicts between text and image data
    And provide unified menu structure
    And indicate data source for each extracted item

  # Site-specific Extraction Pattern Learning
  Scenario: Learn patterns from successful extractions
    Given a restaurant chain with multiple location websites
    And pattern learning is enabled
    And successful extractions from 5 similar sites
    When I process a new site from the same chain
    Then the system should identify common patterns
    And apply learned extraction rules
    And improve extraction accuracy over baseline
    And update pattern database with new learnings
    And provide pattern confidence scores

  Scenario: Adapt to custom website structures
    Given a unique restaurant website structure
    And the initial extraction has low confidence
    And adaptive learning is enabled
    When I provide feedback on extraction accuracy
    Then the system should learn from the corrections
    And generate custom extraction patterns for this site
    And improve future extractions for similar structures
    And store site-specific patterns for reuse
    And apply patterns to similar domains automatically

  Scenario: Handle franchise variations with pattern inheritance
    Given a franchise with slight variations across locations
    And base patterns exist for the franchise
    When I process a new franchise location
    Then the system should start with base franchise patterns
    And adapt patterns for location-specific variations
    And inherit successful patterns from similar locations
    And maintain franchise-level pattern library
    And provide franchise vs location-specific extraction rules

  # Dynamic Prompt Adjustment
  Scenario: Adjust prompts based on content complexity
    Given a restaurant webpage with complex poetic menu descriptions
    And dynamic prompt adjustment is enabled
    When I run extraction with complexity analysis
    Then the system should analyze content complexity
    And select appropriate prompt strategy
    And adjust extraction instructions for poetic language
    And use creative interpretation prompts
    And provide explanation of prompt selection reasoning

  Scenario: Optimize prompts based on extraction success rate
    Given historical extraction data for a cuisine type
    And prompt optimization is enabled
    And multiple prompt variations are available
    When I process a new restaurant of the same cuisine type
    Then the system should select the highest-performing prompt
    And monitor extraction quality in real-time
    And adjust prompt parameters if quality is low
    And learn from successful extraction patterns
    And update prompt effectiveness scores

  Scenario: Context-aware prompt selection for different industries
    Given the system is configured for multiple industries
    And industry-specific prompt templates exist
    And a medical practice webpage needs processing
    When I run extraction with auto-industry detection
    Then the system should detect the industry context
    And select medical industry prompt templates
    And adjust extraction focus to medical-specific fields
    And use appropriate medical terminology
    And validate results against medical industry standards

  Scenario: Real-time prompt refinement during extraction
    Given a challenging restaurant webpage with mixed languages
    And real-time prompt adjustment is enabled
    When the initial extraction produces low confidence results
    Then the system should analyze the failure points
    And generate refined prompts for problematic sections
    And re-run extraction with improved prompts
    And compare results from different prompt versions
    And select the best-performing prompt combination

  # Integration and Error Handling
  Scenario: Graceful degradation when all advanced features fail
    Given all optional AI features are enabled
    And all LLM providers become unavailable
    And a restaurant webpage needs processing
    When I run extraction with full feature set
    Then the system should detect all AI service failures
    And automatically fallback to traditional extraction methods
    And complete the extraction using heuristic patterns
    And provide clear indication of fallback mode
    And maintain extraction quality within acceptable bounds

  Scenario: Performance monitoring across all AI features
    Given multiple AI features are enabled simultaneously
    And performance monitoring is active
    When I process a batch of restaurant websites
    Then the system should track performance for each feature
    And measure processing time per feature
    And monitor API usage and costs
    And identify performance bottlenecks
    And provide feature-level performance reports
    And suggest optimization opportunities