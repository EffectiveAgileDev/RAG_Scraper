# Phase 4.3W User Testing Plan - WTEG Implementation

## Testing Overview

**Objective**: Validate Phase 4.3W WTEG-specific implementation with real-world scenarios for Where To Eat Guide client deployment.

**Scope**: Complete end-to-end testing of WTEG schema, JavaScript extraction, and RAG-ready export functionality.

**Target URLs**: mobimag.co WTEG Portland restaurant guide pages

## Critical Success Criteria

### 1. Data Extraction Completeness
- ✅ **Restaurant Names**: Extracted correctly (not generic "Portland")
- ✅ **Location Data**: Complete address information
- ✅ **Contact Info**: Phone numbers for "Click to Call"
- ✅ **Menu Items**: Detailed menu with items and prices
- ✅ **Services**: Delivery, takeout, catering options
- ✅ **Web Links**: Official websites and ordering platforms

### 2. Export Quality
- ✅ **RAG Format**: Optimized for client ChatBot consumption
- ✅ **Confidence Scoring**: Accurate quality assessment
- ✅ **Source Attribution**: Proper metadata and timestamps
- ✅ **JSON Structure**: Valid schema compliance

## Test Scenarios

### Scenario 1: Single Restaurant Extraction
**Test URL**: `https://mobimag.co/wteg/portland/21`
**Expected**: Kells Irish Pub Downtown complete data

**Test Steps**:
1. Navigate to web interface (localhost:8080)
2. Enter URL in scraping form
3. Select "Restaurant" industry
4. Execute scraping
5. Validate export contains all WTEG fields

**Success Criteria**:
- Restaurant name: "Kells Irish Pub Downtown" (not "Portland")
- Address: Complete street address in Portland
- Phone: Valid phone number extracted
- Menu: Multiple menu items with descriptions/prices
- Confidence: >0.7 score

### Scenario 2: Multi-Page Batch Processing
**Test URLs**: 
- `https://mobimag.co/wteg/portland/16`
- `https://mobimag.co/wteg/portland/21`
- `https://mobimag.co/wteg/portland/6`

**Test Steps**:
1. Enter multiple URLs (space or newline separated)
2. Execute batch scraping
3. Validate each restaurant extracted uniquely
4. Check export contains distinct data per URL

**Success Criteria**:
- 3 distinct restaurants extracted
- No duplicate "Portland" entries
- Each URL maps to correct restaurant
- All exports include complete WTEG schema

### Scenario 3: RAG System Integration Test
**Objective**: Validate export format works with RAG systems

**Test Steps**:
1. Execute scraping of 3-5 WTEG URLs
2. Export JSON data
3. Load exported data into test RAG system
4. Query for restaurant information
5. Validate responses contain extracted data

**Success Criteria**:
- JSON validates against WTEG schema
- RAG chunking preserves restaurant context
- Queries return accurate restaurant details
- Confidence scores guide response quality

## Data Quality Validation

### Required Field Coverage
| Field | Required | Test Method |
|-------|----------|-------------|
| Restaurant Name | ✅ | Verify not generic location name |
| Location Address | ✅ | Complete street address present |
| Phone Number | ✅ | Valid format for tel: links |
| Cuisine Type | ✅ | Specific cuisine classification |
| Menu Items | ✅ | Multiple items with details |
| Brief Description | ✅ | Restaurant-specific description |
| Services | ✅ | Delivery/takeout options |
| Website Links | ✅ | Official website URLs |
| Map Links | ✅ | Location mapping data |

### Data Accuracy Checks
- **Name Extraction**: Must be restaurant-specific, not city name
- **Address Parsing**: Street, city, state, zip components
- **Phone Formatting**: Consistent format for client integration
- **Menu Completeness**: Items, prices, categories present
- **Confidence Scoring**: Reflects actual data quality

## Error Handling Tests

### Scenario 4: Invalid URL Handling
**Test URLs**: 
- `https://mobimag.co/wteg/portland/999` (non-existent page)
- `https://example.com` (non-WTEG URL)

**Expected Behavior**:
- Graceful error messages
- No system crashes
- Clear user feedback
- Proper logging

### Scenario 5: Network Issues
**Test Conditions**:
- Slow network connection
- Intermittent connectivity
- Timeout scenarios

**Expected Behavior**:
- Appropriate timeout handling
- Retry mechanisms work
- User progress feedback
- Partial results handling

## Performance Testing

### Load Testing
- **Single URL**: <5 seconds extraction time
- **Batch Processing**: 5 URLs in <30 seconds
- **Memory Usage**: Stable during batch operations
- **Concurrent Users**: 3+ simultaneous sessions

### Scalability Testing
- **Large Batches**: 20+ URLs without memory issues
- **Extended Sessions**: 1+ hour continuous operation
- **Resource Cleanup**: Proper memory management

## Client-Specific Validation

### WTEG Business Requirements
- **Restaurant Discovery**: All Portland guide restaurants extractable
- **Data Completeness**: 90%+ field coverage for menu/contact data
- **Integration Ready**: Direct import to client RAG system
- **Quality Assurance**: Confidence scoring guides client usage

### ChatBot Integration
- **Query Responses**: Restaurant data answers customer questions
- **Context Preservation**: Location and menu context maintained
- **Search Optimization**: Proper embedding-friendly text format
- **Metadata Usage**: Source attribution for response validation

## Test Environment Setup

### Prerequisites
- RAG_Scraper running on localhost:8080
- Test URLs accessible and responsive
- Sample RAG system for integration testing
- Network connectivity for external URL access

### Test Data
- Known good URLs: `/21`, `/16`, `/6` from mobimag.co
- Expected restaurant names for validation
- Reference menu items for completeness checking
- Valid phone/address formats for comparison

## Acceptance Criteria

### Phase 4.3W Complete Success
- ✅ All critical WTEG fields extracted correctly
- ✅ No generic "Portland" entries in restaurant names
- ✅ Batch processing works reliably
- ✅ Export format validates with RAG systems
- ✅ Confidence scoring accurately reflects quality
- ✅ Error handling provides clear user feedback

### Client Deployment Ready
- ✅ Where To Eat Guide URLs process successfully
- ✅ Complete restaurant profiles extracted
- ✅ RAG integration works seamlessly
- ✅ Data quality meets client expectations
- ✅ Performance suitable for production use

## Test Execution Schedule

### Phase 1: Core Functionality (Day 1)
- Single URL extraction tests
- Data completeness validation
- Basic error handling

### Phase 2: Integration Testing (Day 2)
- Batch processing validation
- RAG system integration
- Performance benchmarking

### Phase 3: Client Validation (Day 3)
- WTEG-specific business scenarios
- ChatBot integration testing
- Final acceptance criteria verification

## Success Metrics

- **Data Accuracy**: 95%+ correct field extraction
- **System Reliability**: 99%+ successful extractions
- **Performance**: <5 seconds per URL average
- **Client Satisfaction**: All WTEG requirements met
- **Integration Success**: RAG system compatibility confirmed

---

**Test Lead**: Development Team  
**Client Stakeholder**: Where To Eat Guide  
**Target Completion**: End of Phase 4.3W validation cycle  
**Go/No-Go Decision**: Based on all acceptance criteria met