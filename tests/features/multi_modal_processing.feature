Feature: Multi-Modal Processing for Enhanced Data Extraction
  As a business intelligence user
  I want the scraper to extract information from images, PDFs, and other media
  So that I can get comprehensive business data including visual content

  Background:
    Given the multi-modal processing system is initialized
    And OCR capabilities are available
    And image analysis tools are configured
    And PDF processing is enabled

  Scenario: Extract menu text from restaurant menu images
    Given a restaurant webpage with menu images
    And the images contain menu items and prices
    When I run multi-modal extraction on the webpage
    Then the result should include text extracted from menu images
    And menu items should be properly categorized
    And prices should be accurately parsed
    And confidence scores should reflect OCR quality

  Scenario: Process PDF documents containing business information
    Given a business webpage with PDF documents
    And the PDFs contain service descriptions and pricing
    When I process the webpage with PDF extraction enabled
    Then the result should include text from PDF documents
    And structured data should be extracted from PDFs
    And PDF content should be integrated with web content
    And the source attribution should indicate PDF origin

  Scenario: Analyze restaurant ambiance from photos
    Given a restaurant webpage with ambiance photos
    And the photos show interior design and atmosphere
    When I run image analysis on the webpage
    Then the result should include ambiance descriptions from photos
    And visual elements should be categorized (lighting, seating, decor)
    And the analysis should complement text-based ambiance information
    And confidence scores should reflect image analysis accuracy

  Scenario: Handle multiple media types simultaneously
    Given a business webpage with images, PDFs, and videos
    And each media type contains relevant business information
    When I run comprehensive multi-modal extraction
    Then all supported media types should be processed
    And results should be merged with text extraction
    And processing should complete within reasonable time limits
    And each media source should be properly attributed

  Scenario: Gracefully handle unsupported media formats
    Given a webpage with unsupported media formats
    And some media files are corrupted or inaccessible
    When I attempt multi-modal processing
    Then unsupported formats should be skipped without errors
    And processing should continue with supported formats
    And error logs should indicate unsupported formats
    And the extraction should not fail completely

  Scenario: Extract text from complex image layouts
    Given images with complex layouts including tables and columns
    And the images contain structured business information
    When I run OCR processing on the images
    Then text should be extracted with proper structure preservation
    And tables should be recognized and parsed correctly
    And column layouts should be maintained in output
    And confidence scores should reflect layout complexity

  Scenario: Process large PDF documents efficiently
    Given large PDF documents with multiple pages
    And the PDFs contain extensive business information
    When I process the PDFs with size optimization enabled
    Then large PDFs should be processed in chunks
    And memory usage should remain within limits
    And processing time should scale reasonably with document size
    And all relevant information should be extracted

  Scenario: Handle multi-language content in images and PDFs
    Given media content in multiple languages
    And the business operates in diverse linguistic markets
    When I run multi-modal extraction with language detection
    Then content should be extracted in original languages
    And language detection should be accurate
    And text extraction quality should be maintained across languages
    And language information should be included in metadata

  Scenario: Integrate multi-modal results with AI analysis
    Given extracted content from images and PDFs
    And AI-enhanced extraction is enabled
    When I combine multi-modal and AI analysis
    Then LLM should analyze multi-modal extracted content
    And confidence scores should incorporate multi-modal reliability
    And AI should identify relationships between visual and text content
    And final results should show comprehensive business intelligence

  Scenario: Cache multi-modal processing results for performance
    Given expensive multi-modal processing operations
    And repeated requests for the same media content
    When I enable multi-modal result caching
    Then processed results should be cached efficiently
    And subsequent requests should use cached results
    And cache should handle media file changes appropriately
    And processing performance should improve for repeated content

  Scenario: Extract business hours from storefront images
    Given storefront photos showing business hour signs
    And the images contain readable hour information
    When I run OCR on storefront images
    Then business hours should be extracted accurately
    And hour formats should be normalized
    And special hours (holidays, seasonal) should be identified
    And extracted hours should integrate with other hour sources

  Scenario: Analyze product images for inventory information
    Given product or service images on business websites
    And the images show available offerings
    When I run image analysis for product identification
    Then products/services should be identified from images
    And visual characteristics should be described
    And availability indicators should be detected
    And product information should complement text descriptions

  Scenario: Process complex business documents with mixed content
    Given documents containing both text and images
    And the documents have complex formatting and layouts
    When I run comprehensive document processing
    Then both text and embedded images should be processed
    And document structure should be preserved
    And relationships between text and images should be maintained
    And extraction should handle mixed content gracefully

  Scenario: Handle media content requiring authentication
    Given protected media content behind login requirements
    And the content contains valuable business information
    When I attempt to process authenticated media
    Then authentication requirements should be detected
    And appropriate error handling should occur
    And public content should still be processed
    And security constraints should be respected

  Scenario: Extract contact information from business card images
    Given images of business cards or contact information
    And the images contain structured contact details
    When I run OCR with contact information extraction
    Then names, phones, emails should be extracted accurately
    And contact information should be properly formatted
    And multiple contact formats should be recognized
    And extracted contacts should enhance business profiles