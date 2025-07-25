# RAG_Scraper - Current State Documentation

## Project Overview

RAG_Scraper is a localhost web application that scrapes restaurant websites and converts extracted data into structured text files optimized for Retrieval-Augmented Generation (RAG) systems. The application has evolved through multiple development phases using Test-Driven Development (TDD) methodology with comprehensive ATDD coverage.

**Current Phase**: 4.3W.1 - WTEG implementation with local file upload capabilities (partial)
**Development Status**: Production-ready for web scraping with extensive test coverage
**Target Users**: AI/ML Engineers, Data Engineers, Content Managers building RAG systems

## Architecture Overview

### Core Components

#### 1. Web Interface (`src/web_interface/`)
- **Flask 2.3.3** web framework with localhost deployment (port 8085)
- Terminal-themed single-page interface with real-time progress visualization
- Dual scraping modes: Single-page and Multi-page with intelligent mode selection
- Advanced configuration panels with collapsible options
- Real-time progress monitoring with page queue status
- Complete API endpoints for programmatic access

#### 2. Scraping Engine (`src/scraper/`)
- **Multi-strategy extraction**: JSON-LD → microdata → heuristic patterns
- **JavaScript rendering support** with Playwright browser automation
- **Restaurant popup detection** (age verification, location selectors, reservations)
- **Multi-page navigation** with intelligent page discovery and relationship tracking
- **Ethical scraping** with configurable rate limiting and robots.txt compliance
- **Error recovery** with retry mechanisms and graceful degradation

#### 3. File Generation System (`src/file_generator/`)
- **Multiple output formats**: Text, PDF, JSON with dual-format capability
- **RAG-optimized text generation** with semantic chunking and metadata
- **Professional PDF generation** using ReportLab with customizable formatting
- **Index file generation** with relationship mapping and search metadata
- **Entity relationship management** for multi-page data aggregation

#### 4. Multi-Modal Processing (`src/processors/`)
- **HTML content extraction** with pattern recognition
- **PDF processing capabilities** (limited - download only, no text extraction)
- **Image analysis integration** (OCR processor framework)
- **Service extraction** for business hours, contact info, menu items

#### 5. AI Integration (`src/ai/`)
- **LLM-powered content extraction** with Claude, OpenAI, and Ollama support
- **Multi-modal analysis** for complex content understanding
- **Confidence scoring** and quality assessment
- **Traditional fallback extractors** for reliability

## Current Capabilities

### ✅ Fully Implemented Features

#### Web Scraping Core
- **Single URL scraping** with comprehensive data extraction
- **Batch processing** up to 100 URLs with real-time progress
- **Multi-page website navigation** with automatic page discovery
- **JavaScript-rendered content support** using Playwright
- **Restaurant popup handling** (age verification, location selection, etc.)
- **Data validation and normalization** with confidence scoring

#### Output Generation
- **Text file generation** in RAG-optimized format with semantic chunking
- **PDF generation** with professional formatting and customizable options
- **JSON export** with structured schema and metadata
- **Index file generation** with relationship mapping and search optimization
- **Dual format output** (simultaneous text and PDF generation)

#### User Interface
- **Terminal-themed web interface** with smooth animations and real-time feedback
- **Scraping mode selector** (Single-page vs Multi-page) with smart configuration
- **Advanced options panel** with timeout, concurrency, and ethical scraping controls
- **Real-time progress visualization** with current page tracking and queue status
- **Enhanced results display** with page relationships and processing metrics
- **File download functionality** with automatic cleanup

#### Industry Support
- **Restaurant industry** fully implemented with comprehensive schema
- **WTEG (Where To Eat Guide)** specialized implementation for mobimag.co sites
- **Industry selection system** with configurable schemas (Restaurant/RestW)
- **Dynamic industry configuration** (foundation for expansion)

#### Testing & Quality
- **95%+ test coverage** with comprehensive TDD/ATDD methodology
- **80+ BDD scenarios** covering all major functionality
- **57 JavaScript rendering tests** (100% passing for core functionality)
- **68+ UI enhancement tests** with comprehensive coverage
- **Performance and security validation** included

### ⚠️ Partially Implemented Features

#### File Upload System (Phase 4.3W.1)
- **✅ Complete UI**: Drag-drop file upload interface with validation (26/26 tests passing)
- **✅ Backend API**: Secure file handling with virus scanning simulation (21/21 tests passing)
- **❌ PDF Text Extraction**: Mock implementation only - returns hardcoded data
- **❌ Integration**: File upload UI not integrated into main interface
- **Status**: UI and API complete, but PDF processing is non-functional

#### Cloud Deployment
- **✅ Documentation**: Comprehensive deployment guide with Docker, Heroku, DigitalOcean
- **✅ Health checks**: Production monitoring endpoints implemented
- **✅ Environment configuration**: Ready for cloud deployment
- **❌ Implementation**: Not deployed to cloud platforms

### ❌ Not Implemented Features

#### Advanced Content Processing
- **Semantic content structuring** (marked complete but no implementation found)
- **Customer intent mapping** (marked complete but no implementation found)
- **Real PDF text extraction** (PyMuPDF, pdfplumber return mock data only)

#### Enterprise Features
- **Multi-user support** and access control
- **Database storage** for scraped data persistence
- **API rate limiting** per customer
- **Audit logging** for compliance

## Technology Stack

### Backend Framework
- **Python 3.13** with Flask 2.3.3 web framework
- **BeautifulSoup4 4.12.2** for HTML parsing
- **requests-html 0.10.0** for dynamic content
- **Playwright 1.40.0** for JavaScript rendering and browser automation

### Testing & Quality
- **pytest 7.4.2** with pytest-bdd 6.1.1 for ATDD
- **pytest-cov 4.1.0** for coverage analysis (95%+ target)
- **black 23.7.0** for code formatting
- **flake8 6.0.0** for linting

### File Processing
- **ReportLab 4.0.4** for PDF generation
- **PyMuPDF 1.26.3** for PDF processing (mock implementation)
- **pdfplumber 0.11.7** for text extraction (mock implementation)

### AI Integration
- **OpenAI 1.3.0** for GPT-based content analysis
- **Anthropic 0.8.1** for Claude-based extraction
- **Custom LLM extractors** with confidence scoring

### System Monitoring
- **psutil 5.9.5** for resource monitoring
- **Health check endpoints** for production deployment

## Performance Characteristics

### Current Performance Metrics
- **Processing Speed**: 1 restaurant per 3-5 seconds (single page), 10-30 seconds (multi-page)
- **Batch Processing**: Up to 100 URLs per session
- **Memory Usage**: <500MB during active scraping
- **Test Execution**: Unit tests <30 seconds, integration tests <2 minutes
- **File Generation**: 1000+ entries/second (text), 100+ entries/second (PDF)

### Scalability Features
- **Concurrent processing** with configurable limits (1-10 requests)
- **Rate limiting** with per-domain throttling
- **Resource monitoring** with automatic throttling
- **Error isolation** preventing cascade failures

## Data Quality & Validation

### Extraction Quality
- **Multi-strategy approach** ensures 90%+ extraction success rate
- **Confidence scoring** for all extracted fields
- **Data validation** with format normalization
- **Relationship tracking** for multi-page content aggregation

### Output Quality
- **Schema validation** for all export formats
- **Content integrity** verification with checksums
- **RAG optimization** with semantic chunking and metadata
- **Professional formatting** for PDF outputs with customizable styling

## API Endpoints

### Core Functionality
- `GET /` - Main web interface
- `POST /api/scrape` - Main scraping endpoint (single/multi-page modes)
- `GET /api/progress` - Real-time progress monitoring
- `POST /api/validate` - URL validation

### File Management
- `POST /api/generate-file` - Generate files from scraped data
- `GET /api/download/<filename>` - Secure file download
- `POST /api/upload` - File upload (UI complete, processing mock)

### Configuration
- `GET/POST /api/file-config` - File generation configuration
- `POST /api/validate-directory` - Directory validation
- `POST /api/create-directory` - Directory creation

### Monitoring
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /metrics` - System metrics

## Security Features

### Input Validation
- **URL sanitization** with format validation
- **File upload security** with type validation and virus scanning simulation
- **Path traversal prevention** for file operations
- **XSS protection** in web interface

### Ethical Scraping
- **Rate limiting** (configurable 100-5000ms delays)
- **Robots.txt compliance** checking
- **User-agent rotation** and request throttling
- **Resource usage monitoring** and fair use policies

## Development Workflow

### TDD Methodology
- **Red-Green-Refactor cycles** for all feature development
- **ATDD with Gherkin** scenarios for user acceptance
- **95%+ unit test coverage** for custom code
- **Mock-driven testing** for external dependencies

### Code Quality
- **Black formatting** with consistent style
- **Flake8 linting** for code quality
- **Coverage analysis** with automated reporting
- **Comprehensive documentation** in markdown format

## Deployment Options

### Local Development
- **Virtual environment** with `run_app_venv.py` (recommended)
- **Manual startup** with `run_app.py`
- **Alternative methods** with shell scripts

### Production Ready
- **Docker containerization** with multi-stage builds
- **Gunicorn WSGI server** for production deployment
- **Health checks** and monitoring endpoints
- **Environment configuration** with .env support

### Cloud Platforms
- **Heroku** deployment ready with Procfile
- **DigitalOcean App Platform** configuration included
- **Generic cloud** deployment with Docker support

## Critical Limitations

### PDF Processing
- **No real PDF text extraction** - all PDF processors return hardcoded mock data
- **File upload UI exists but not integrated** into main interface
- **19 PDF extractor tests SKIPPED** (not implemented)

### Missing Features
- **Local file import** capability (critical client need)
- **Real semantic structuring** (marked complete but not implemented)
- **Customer intent mapping** (marked complete but not implemented)

### Test Coverage Gaps
- **PDF extraction tests skipped** due to mock implementations
- **File upload integration** not tested in main workflow
- **Real PDF processing pipeline** not validated

## File Structure

```
RAG_Scraper/
├── src/
│   ├── web_interface/          # Flask web application
│   ├── scraper/               # Web scraping engine
│   ├── file_generator/        # Output file generation
│   ├── processors/            # Multi-modal content processing
│   ├── ai/                    # AI/LLM integration
│   ├── config/                # Configuration management
│   ├── wteg/                  # WTEG-specific implementation
│   └── common/                # Shared utilities
├── tests/
│   ├── features/              # BDD scenarios (80+ files)
│   ├── step_definitions/      # pytest-bdd implementations
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                      # Project documentation
└── requirements.txt           # Python dependencies
```

## Current Status Summary

**✅ Production Ready For**: Web scraping of restaurant websites with comprehensive data extraction and multiple export formats

**⚠️ Partial Implementation**: File upload system (UI complete, PDF processing mock only)

**❌ Not Implemented**: Real PDF text extraction, semantic structuring, customer intent mapping

**🧪 Test Coverage**: 95%+ for implemented features with comprehensive ATDD/TDD methodology

**🚀 Deployment**: Ready for cloud deployment with comprehensive documentation and health monitoring

The RAG_Scraper represents a sophisticated, well-tested web scraping solution with strong architectural foundations and comprehensive feature set for restaurant data extraction and RAG system integration.