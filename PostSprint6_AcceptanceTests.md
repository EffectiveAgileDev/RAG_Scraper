# Post-Sprint 6 User Acceptance Testing Script

## Overview
This document provides a comprehensive testing script for validating all RAG_Scraper features implemented through Sprint 6, including the critical integration fix that enables end-to-end file generation.

## Test Environment Setup

### Prerequisites
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Flask server
python src/web_interface/app.py
```

### Expected Server Output
```
* Running on http://localhost:8080
* Debug mode: off
```

## Test Categories

### 🔍 Category 1: URL Validation System

#### Test 1.1: Valid URL Detection
**Steps:**
1. Navigate to http://localhost:8080
2. Enter a valid restaurant URL: `https://www.example-restaurant.com`
3. Click "Validate URLs"

**Expected Results:**
- ✅ Green checkmark appears
- "1/1 URLs valid" message displayed
- No error messages

#### Test 1.2: Invalid URL Detection
**Steps:**
1. Enter invalid URL: `not-a-valid-url`
2. Click "Validate URLs"

**Expected Results:**
- ❌ Red X appears
- "0/1 URLs valid" message displayed
- Specific error message explaining the issue

#### Test 1.3: Mixed URL Validation
**Steps:**
1. Enter multiple URLs (one per line):
   ```
   https://valid-restaurant.com
   invalid-url
   https://another-valid.com
   ```
2. Click "Validate URLs"

**Expected Results:**
- "2/3 URLs valid" message
- Individual validation status for each URL
- Clear indication of which URLs failed and why

### 🌐 Category 2: Web Scraping Engine

#### Test 2.1: Single URL Scraping
**Steps:**
1. Enter valid URL: `https://example.com`
2. Leave output directory empty (uses Downloads folder)
3. Set file mode to "Single file for all restaurants"
4. Click "Start Scraping"

**Expected Results:**
- Progress bar appears and updates
- "Scraping Completed Successfully!" message
- File paths listed in results
- Actual files created in Downloads folder

#### Test 2.2: Multiple URL Batch Processing
**Steps:**
1. Enter 3-5 valid URLs (one per line)
2. Set custom output directory
3. Set file mode to "Separate file per restaurant"
4. Click "Start Scraping"

**Expected Results:**
- Progress indicator shows URL count and percentage
- Current URL being processed displayed
- Time estimates appear after first URL
- Multiple files generated (one per restaurant)

#### Test 2.3: Progress Monitoring
**Steps:**
1. Enter 2-3 URLs for scraping
2. Watch the progress container during scraping

**Expected Results:**
- Progress bar fills from 0% to 100%
- Current URL being processed shown
- Time estimate updates dynamically
- Memory usage information displayed

### 📄 Category 3: File Generation System

#### Test 3.1: Automatic Text File Generation
**Steps:**
1. Enter restaurant URL
2. Ensure no file format is explicitly selected (defaults to text)
3. Start scraping

**Expected Results:**
- Text file (.txt) automatically created
- File contains structured restaurant data
- File path returned in API response
- File accessible in specified directory

#### Test 3.2: PDF Generation Integration
**Steps:**
1. Open browser developer tools (F12)
2. Navigate to Network tab
3. Enter restaurant URL
4. Modify the scraping request to include `"file_format": "pdf"`
5. Start scraping

**Expected Results:**
- PDF file (.pdf) automatically created
- Professional formatting with headers and sections
- Restaurant data properly structured
- File viewable in PDF reader

#### Test 3.3: Dual Format Generation
**Steps:**
1. Using developer tools, modify request to include `"file_format": "both"`
2. Start scraping

**Expected Results:**
- Both .txt and .pdf files created
- Same content in both formats
- Both file paths returned in response
- Both files accessible and properly formatted

### 🔄 Category 4: End-to-End Integration

#### Test 4.1: Complete Workflow Validation
**Steps:**
1. Start with empty Downloads folder
2. Enter restaurant URL
3. Complete full scraping process
4. Check Downloads folder

**Expected Results:**
- Files appear automatically after scraping
- No need for separate file generation step
- API response includes actual file paths
- Files contain extracted restaurant data

#### Test 4.2: Error Handling and Recovery
**Steps:**
1. Enter mix of valid and invalid URLs
2. Start scraping process
3. Observe error handling

**Expected Results:**
- Process continues with valid URLs
- Failed URLs reported separately
- Partial success results returned
- Files generated for successful extractions

#### Test 4.3: Custom Directory Creation
**Steps:**
1. Enter custom output directory path
2. Create new folder if needed
3. Start scraping

**Expected Results:**
- Files created in specified location
- Directory permissions validated
- Custom paths respected
- Files accessible at specified location

### 📊 Category 5: API Integration Testing

#### Test 5.1: REST API Validation
**Steps:**
1. Use curl or Postman to test `/api/validate`
```bash
curl -X POST http://localhost:8080/api/validate \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```

**Expected Results:**
- JSON response with validation results
- Proper HTTP status codes
- Accurate validation feedback

#### Test 5.2: Scraping API Integration
**Steps:**
1. Test `/api/scrape` endpoint directly
```bash
curl -X POST http://localhost:8080/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"], "file_format": "text"}'
```

**Expected Results:**
- Successful scraping response
- File paths in response data
- Actual files created on filesystem
- Processing statistics included

#### Test 5.3: File Generation API
**Steps:**
1. Test standalone file generation
```bash
curl -X POST http://localhost:8080/api/generate-file \
  -H "Content-Type: application/json" \
  -d '{"restaurant_data": [{"name": "Test", "sources": ["test"]}], "file_format": "pdf"}'
```

**Expected Results:**
- File creation success response
- Valid file path returned
- File accessible and properly formatted

### 🛡️ Category 6: Security and Robustness

#### Test 6.1: Input Validation
**Steps:**
1. Try various malformed inputs
2. Test with empty data
3. Submit invalid JSON

**Expected Results:**
- Graceful error handling
- Appropriate error messages
- No system crashes
- Security headers present

#### Test 6.2: File System Security
**Steps:**
1. Try path traversal attempts in output directory
2. Test with restricted directories
3. Verify file permissions

**Expected Results:**
- Path traversal blocked
- Permission errors handled gracefully
- No unauthorized file access

### 📈 Category 7: Performance Validation

#### Test 7.1: Multiple Concurrent Requests
**Steps:**
1. Open multiple browser tabs
2. Start scraping in each tab simultaneously
3. Monitor system performance

**Expected Results:**
- Requests handled appropriately
- No system overload
- Memory usage remains reasonable
- Progress tracking works per session

#### Test 7.2: Large Batch Processing
**Steps:**
1. Submit 10+ URLs for batch processing
2. Monitor progress and performance
3. Verify all files generated

**Expected Results:**
- All URLs processed successfully
- Progress tracking accurate
- Memory usage stable
- All expected files created

## Success Criteria Summary

### ✅ Sprint 1-2 Features (Core Foundation)
- [x] URL validation system working
- [x] Basic scraping functionality
- [x] Multi-strategy data extraction
- [x] Progress indication

### ✅ Sprint 3-4 Features (Enhanced Processing)
- [x] Batch processing capabilities
- [x] Error resilience and recovery
- [x] File output format options
- [x] Configuration management

### ✅ Sprint 5-6 Features (Professional Output)
- [x] PDF generation system
- [x] Professional document formatting
- [x] Dual format generation
- [x] Flask web interface integration

### ✅ Critical Integration Fix
- [x] End-to-end file generation workflow
- [x] Single API call completion
- [x] Actual file paths in responses
- [x] Automatic file creation after scraping

## Known Limitations and Notes

### Current Scope
- Restaurant website focus (not general web scraping)
- Localhost deployment only
- Basic authentication (no user accounts)
- File storage in local filesystem

### Performance Considerations
- Batch size recommended: 1-20 URLs
- Large batches may require extended processing time
- Memory usage scales with batch size
- PDF generation adds processing overhead

### Browser Compatibility
- Tested on modern browsers (Chrome, Firefox, Safari)
- JavaScript required for web interface
- API endpoints work with any HTTP client

## Troubleshooting Guide

### Common Issues
1. **Server won't start**: Check Python environment and dependencies
2. **No files generated**: Verify output directory permissions
3. **Validation fails**: Check internet connectivity and URL accessibility
4. **PDF errors**: Ensure ReportLab installation complete

### Debug Commands
```bash
# Check test coverage
pytest --cov=src

# Validate setup
python tests/test_setup.py

# Run specific test category
pytest tests/features/

# Check server logs
tail -f flask_server.log
```

## Test Completion Checklist

- [ ] All 7 test categories completed
- [ ] End-to-end workflows validated
- [ ] Error scenarios tested
- [ ] Performance acceptable
- [ ] Files generated correctly
- [ ] API responses accurate
- [ ] Security measures verified
- [ ] Documentation matches behavior

## Post-Testing Actions

### If Tests Pass
- ✅ Sprint 6 marked as complete
- ✅ Integration fix validated
- ✅ System ready for production consideration
- ✅ Ready for Sprint 7 planning

### If Tests Fail
- 🔍 Document specific failures
- 🐛 Create bug reports with reproduction steps
- 🔧 Prioritize fixes based on severity
- 🔄 Re-run tests after fixes implemented

---

**Testing completed by:** ________________  
**Date:** ________________  
**Overall Status:** ________________  
**Notes:** ________________