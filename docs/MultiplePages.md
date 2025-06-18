# Multi-Page Scraping Enhancement for RAG Scraper

## Overview

This document outlines the architectural changes and implementation details required to enhance the RAG Scraper application with multi-page scraping capabilities. The enhancement will enable the scraper to follow links from a primary page and extract data from linked pages, which is essential for scraping restaurant directory sites where detailed information is spread across multiple pages.

## Current Architecture vs. Enhanced Architecture

### Current State
- Single URL scraping with data extraction from one page
- Batch processing supports multiple independent URLs
- No link traversal or relationship tracking between pages

### Enhanced State
- Primary page acts as entry point (e.g., restaurant directory listing)
- Automatic discovery and traversal of linked pages
- Parent-child relationship tracking for hierarchical data organization
- Aggregated data storage suitable for RAG system consumption

## Key Components to Modify

### 1. Page Discovery System (`src/scraper/page_discovery.py`)
**New Component**
- Implement link extraction from primary pages
- Filter and validate discovered links based on patterns
- Maintain crawl depth limits to prevent infinite traversal
- Support configurable link selection criteria (CSS selectors, URL patterns)

### 2. Multi-Page Scraper (`src/scraper/multi_page_scraper.py`)
**New Component**
- Orchestrate scraping across multiple related pages
- Manage page queue and visited page tracking
- Implement breadth-first or depth-first traversal strategies
- Handle circular references and duplicate pages

### 3. Data Aggregator (`src/scraper/data_aggregator.py`)
**New Component**
- Combine data from multiple pages into coherent records
- Maintain data relationships (e.g., restaurant → menu items, reviews)
- Support nested data structures for hierarchical information
- Generate unique identifiers for cross-page data correlation

### 4. Enhanced Scraping Configuration (`src/config/scraping_config.py`)
**Modifications Required**
```python
class ScrapingConfig:
    # Existing configuration...
    
    # New multi-page settings
    max_crawl_depth: int = 2
    max_pages_per_site: int = 50
    link_patterns: List[str] = []  # Regex patterns for valid links
    exclude_patterns: List[str] = []  # Patterns to exclude
    follow_external_links: bool = False
    page_relationship_rules: Dict[str, Any] = {}
```

### 5. Modified File Generator (`src/file_generator/text_file_generator.py`)
**Enhancements Required**
- Support hierarchical document structure
- Generate separate files for each entity with cross-references
- Include metadata about source pages and relationships
- Format output optimized for RAG chunking strategies

## Implementation Strategy

### Phase 1: Core Infrastructure
1. Implement page discovery mechanism
2. Create multi-page scraper orchestrator
3. Add page relationship tracking
4. Update rate limiter for multi-page scenarios

### Phase 2: Data Management
1. Develop data aggregation logic
2. Implement entity relationship mapping
3. Create hierarchical data structures
4. Add deduplication mechanisms

### Phase 3: Output Generation
1. Enhance text file generator for structured output
2. Add metadata embedding for RAG optimization
3. Create index files for entity relationships
4. Implement cross-reference generation

## Data Storage Format for RAG

### Proposed Structure
```
output/
├── index.json                    # Master index of all scraped entities
├── restaurants/
│   ├── restaurant_001.txt       # Main restaurant data
│   ├── restaurant_001_menu.txt  # Menu items
│   ├── restaurant_001_reviews.txt # Customer reviews
│   └── metadata/
│       └── restaurant_001.json  # Relationship metadata
└── categories/
    └── category_index.json      # Category mappings
```

### Text File Format Example
```text
[ENTITY: Restaurant]
[ID: restaurant_001]
[SOURCE: https://directory.example.com/restaurants/italian-bistro]
[SCRAPED: 2024-01-15T10:30:00Z]

Name: Italian Bistro
Category: Italian Restaurant
Address: 123 Main St, City, State
Phone: (555) 123-4567
Rating: 4.5/5

[RELATED_ENTITIES]
- Menu: restaurant_001_menu.txt
- Reviews: restaurant_001_reviews.txt

[CONTENT]
Award-winning Italian restaurant serving authentic cuisine...
```

## Configuration Examples

### Link Discovery Rules
```json
{
  "link_patterns": [
    {
      "name": "restaurant_detail",
      "pattern": "/restaurants/[^/]+$",
      "max_pages": 100,
      "data_type": "restaurant"
    },
    {
      "name": "menu_page",
      "pattern": "/menu/[^/]+$",
      "parent_type": "restaurant",
      "data_type": "menu"
    }
  ]
}
```

### Data Aggregation Rules
```json
{
  "aggregation_rules": [
    {
      "parent_type": "directory_listing",
      "child_type": "restaurant",
      "relationship": "contains",
      "merge_strategy": "separate_files"
    },
    {
      "parent_type": "restaurant",
      "child_type": "menu_item",
      "relationship": "has_menu",
      "merge_strategy": "append_to_parent"
    }
  ]
}
```

## Testing Strategy

### New Test Scenarios
1. **Multi-page navigation**: Verify correct link discovery and traversal
2. **Data relationship integrity**: Ensure parent-child relationships are maintained
3. **Circular reference handling**: Test prevention of infinite loops
4. **Rate limiting compliance**: Verify ethical scraping across multiple pages
5. **Data aggregation accuracy**: Test combining data from multiple sources

### Performance Considerations
- Implement concurrent page fetching with proper throttling
- Use connection pooling for efficient HTTP requests
- Cache intermediate results to handle failures gracefully
- Monitor memory usage for large-scale scraping operations

## API Changes

### New Endpoints
```python
@app.route('/api/scrape/multi-page', methods=['POST'])
def scrape_multi_page():
    """
    Request body:
    {
        "start_url": "https://directory.example.com",
        "crawl_config": {
            "max_depth": 2,
            "max_pages": 50,
            "link_patterns": ["..."]
        }
    }
    """
```

### Enhanced Progress Reporting
```python
{
    "status": "in_progress",
    "primary_url": "https://directory.example.com",
    "pages_discovered": 45,
    "pages_scraped": 23,
    "pages_remaining": 22,
    "current_page": "https://directory.example.com/restaurants/page-2",
    "entities_extracted": 18
}
```

## Backwards Compatibility

- Existing single-page scraping functionality remains unchanged
- New multi-page features are opt-in via configuration
- Default behavior maintains current single-page operation
- API versioning ensures existing integrations continue working

## Security and Ethical Considerations

### Rate Limiting Enhancements
- Per-domain request throttling
- Respect robots.txt for all discovered pages
- Implement exponential backoff for errors
- Honor retry-after headers

### Access Control
- Validate all discovered URLs before fetching
- Implement domain whitelist/blacklist
- Prevent access to private/authenticated pages
- Log all page access for audit trails

## Conclusion

This multi-page scraping enhancement will transform the RAG Scraper into a comprehensive data extraction tool suitable for complex directory sites. The hierarchical data organization and relationship tracking will provide the RAG system with rich, contextual information that improves chat bot responses about restaurants and their associated data.