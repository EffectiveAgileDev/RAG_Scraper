Feature: Memory-Efficient Batch Processing
  As a RAG system user
  I want to process up to 100 URLs efficiently
  So that I can scrape large batches without system strain

  Background:
    Given I have initialized the batch processing engine
    And I have configured memory management settings
    And I have progress tracking capabilities enabled

  Scenario: Single URL processing baseline
    Given I have 1 restaurant URL to process
    When I process the single URL
    Then memory usage should be minimal and stable
    And processing should complete within 10 seconds
    And memory should be freed after completion
    And baseline metrics should be established for scaling

  Scenario: Small batch processing (10 URLs)
    Given I have 10 restaurant URLs to process
    When I process the batch sequentially
    Then memory usage should scale linearly with batch size
    And processing should complete within 2 minutes
    And progress should be reported for each URL
    And memory should be freed after each URL completion

  Scenario: Medium batch processing (50 URLs)
    Given I have 50 restaurant URLs to process
    When I process the batch with memory optimization
    Then memory usage should remain within acceptable limits
    And processing should complete within 10 minutes
    And progress should show percentage completion
    And memory peaks should not exceed 2x baseline usage

  Scenario: Large batch processing (100 URLs)
    Given I have 100 restaurant URLs to process
    When I process the maximum batch size
    Then memory usage should remain stable throughout processing
    And processing should complete within 20 minutes
    And progress should provide time estimates
    And system should not become unresponsive

  Scenario: Memory-efficient HTML parsing
    Given I have URLs pointing to very large HTML pages (>5MB each)
    When I process these memory-intensive pages
    Then HTML should be parsed in streaming fashion where possible
    And large DOM trees should be processed in sections
    And unnecessary HTML elements should be discarded early
    And memory should be freed immediately after data extraction

  Scenario: Concurrent processing with memory limits
    Given I have 20 restaurant URLs to process
    And I enable concurrent processing with 5 threads
    When I process URLs with concurrent extraction
    Then memory usage should be managed across all threads
    And no single thread should consume excessive memory
    And thread pools should be properly managed
    And concurrent memory peaks should not exceed safe limits

  Scenario: Progressive data flushing during batch processing
    Given I have 75 restaurant URLs to process
    And I enable progressive data saving every 10 URLs
    When I process the batch with periodic flushes
    Then extracted data should be saved in chunks
    And memory should be freed after each chunk save
    And partial results should be preserved if processing stops
    And memory usage should reset after each flush

  Scenario: Large content filtering and preprocessing
    Given I have URLs with pages containing lots of irrelevant content
    And pages have large amounts of advertising and navigation
    When I process these content-heavy pages
    Then irrelevant sections should be filtered out early
    And only restaurant-relevant content should be kept in memory
    And content filtering should reduce memory footprint
    And extraction should focus on cleaned content

  Scenario: Memory monitoring and alerts
    Given I have 60 restaurant URLs to process
    And I enable memory monitoring during processing
    When memory usage approaches dangerous levels
    Then the system should detect high memory usage
    And processing should be paused to allow memory recovery
    And users should be alerted about memory constraints
    And processing should resume when memory is available

  Scenario: Garbage collection optimization
    Given I have 40 restaurant URLs to process
    When I process the batch with optimized cleanup
    Then Python garbage collection should be triggered appropriately
    And large objects should be explicitly deleted when done
    And circular references should be avoided in data structures
    And memory should be consistently released throughout processing

  Scenario: Batch size dynamic adjustment
    Given I start processing with a batch of 100 URLs
    And the system detects insufficient memory for full batch
    When memory constraints are encountered
    Then the batch should be automatically split into smaller chunks
    And processing should continue with reduced batch sizes
    And users should be informed about the batch size adjustment
    And final results should be equivalent to full batch processing

  Scenario: Progress tracking with minimal overhead
    Given I have 80 restaurant URLs to process
    When I enable detailed progress tracking
    Then progress updates should not significantly impact memory
    And progress data should be kept minimal and efficient
    And real-time updates should not create memory leaks
    And progress information should be accurate and timely

  Scenario: Error recovery without memory leaks
    Given I have 30 restaurant URLs to process
    And some URLs will fail during processing
    When errors occur during batch processing
    Then failed URL processing should not leave memory allocated
    And error handling should properly clean up resources
    And memory should be freed even when processing fails
    And subsequent URLs should start with clean memory state

  Scenario: Resource pooling for network connections
    Given I have 50 restaurant URLs to process
    When I process URLs with connection pooling
    Then network connections should be reused efficiently
    And connection pools should be properly sized
    And connections should be closed when no longer needed
    And network resource usage should be optimized

  Scenario: Data structure optimization for large batches
    Given I have 90 restaurant URLs to process
    When I store extracted data during processing
    Then data structures should be optimized for memory efficiency
    And repeated data should be deduplicated to save memory
    And data should be stored in compressed format when possible
    And large text fields should be handled efficiently

  Scenario: Batch processing interruption and resumption
    Given I have 70 restaurant URLs to process
    And processing is interrupted after 40 URLs
    When I resume batch processing from the interruption point
    Then processing should continue from where it left off
    And memory state should be cleanly restored
    And already processed URLs should not be reprocessed
    And final results should be complete and consistent

  Scenario: Memory profiling and optimization feedback
    Given I have completed processing a batch of 50 URLs
    When processing completes successfully
    Then memory usage statistics should be collected
    And peak memory usage should be reported
    And memory efficiency metrics should be calculated
    And recommendations for optimization should be provided