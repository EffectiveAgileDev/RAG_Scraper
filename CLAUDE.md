# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt  # Install dependencies
```

### Testing Commands
```bash
pytest                    # Run all tests
pytest --cov=src         # Run tests with coverage report
pytest tests/unit/       # Run unit tests only
pytest tests/features/   # Run BDD/ATDD tests only
pytest tests/test_setup.py # Validate project setup
pytest -xvs tests/path/to/test.py::test_name  # Run single test with verbose output
```

### Code Quality Commands
```bash
black src/ tests/        # Format code
flake8 src/ tests/       # Lint code
coverage report          # Show coverage report
coverage html            # Generate HTML coverage report
```

### Application Commands
```bash
python run_app_venv.py   # Start Flask web server with virtual environment (port 8085) - RECOMMENDED
python run_app.py        # Manual startup (requires virtual environment to be pre-activated)
python start_server.py   # Alternative startup method (port 8085)
./start_server.sh        # Shell script startup
# Note: Do NOT use "python src/web_interface/app.py" - has import path issues

# IMPORTANT: Always use run_app_venv.py to prevent OpenAI package import errors
# This script automatically activates the virtual environment if needed
```

## Project Architecture

### Core Components
- **src/web_interface/** - Flask web server providing localhost interface on port 8085
- **src/scraper/** - Web scraping engine using BeautifulSoup4, requests-html, and Playwright
- **src/file_generator/** - Generates text files for RAG systems and PDF documentation
- **src/config/** - Configuration management and user preferences
- **src/ai/** - AI/LLM integration for content enhancement
- **src/wteg/** - Where To Eat Guide specialized module
- **src/processors/** - Multi-modal content processors (images, PDFs)
- **src/semantic/** - Semantic structuring for enhanced RAG output
- **src/knowledge/** - Industry-specific knowledge database

### Technology Stack
- **Backend**: Flask 2.3.3 web framework
- **Scraping**: BeautifulSoup4 4.12.2, requests-html 0.10.0, Playwright (JS rendering)
- **Testing**: pytest 7.4.4 with pytest-bdd, pytest-cov (95%+ coverage requirement)
- **Code Quality**: black formatting, flake8 linting
- **PDF Generation**: reportlab for documentation output
- **File Processing**: PyPDF2 for PDF import functionality
- **AI Integration**: OpenAI package (already installed in venv) - ignore "OpenAI package not installed" warning in logs

## Test-Driven Development Approach

### Testing Strategy
This project follows strict **Test-Driven Development (TDD)** with:
- **ATDD (Acceptance Test Driven Development)**: 100% coverage target using pytest-bdd with Gherkin scenarios
- **Unit TDD**: 95%+ coverage target using pytest with extensive mocking
- **Red-Green-Refactor cycles**: Write failing tests first, implement minimal code, then refactor

### TDD Process Requirements
When asked to implement any feature:
1. **STOP** - Do not write implementation code first
2. Ask for clarification on acceptance criteria if unclear
3. Write acceptance test at user function level that FAILS
4. Run the acceptance tests to confirm they FAIL
5. Write unit tests for supporting components that FAIL
6. Run tests to confirm they fail (RED phase)
7. Write minimal implementation to make tests pass (GREEN phase)
8. Refactor code while keeping tests green
9. Commit only when all tests pass

### Test Structure
- **tests/features/** - Gherkin BDD scenarios for user stories
- **tests/step_definitions/** - pytest-bdd step implementations
- **tests/unit/** - Unit tests for individual components
- **tests/test_data/** - Mock HTML samples and test fixtures
- **tests/features/pdf_import.feature** - PDF import acceptance tests
- **tests/features/manual_test_defects.feature** - Defect resolution tests

### Development Workflow
1. **Red Phase**: Write failing tests first (ATDD then unit tests)
2. **Green Phase**: Implement minimal code to pass tests
3. **Refactor Phase**: Improve code quality while maintaining coverage

## Key Project Characteristics

### Purpose
RAG_Scraper is a localhost web application that scrapes restaurant websites and converts data into structured text files for RAG (Retrieval-Augmented Generation) systems.

### Features
- Multi-page website navigation and data aggregation
- Batch processing up to 100 URLs with real-time progress indicators
- JSON-LD, microdata, and heuristic pattern extraction
- Dual output: text files for RAG systems, PDF for documentation
- Rate limiting and ethical scraping compliance
- **Phase 4.1A**: JavaScript rendering and restaurant popup handling
- **Phase 4.3W**: WTEG (Where To Eat Guide) implementation with specialized extraction
- **Phase 4.3W.1**: Local file upload and PDF import capabilities
- Multi-modal processing for images and visual content
- Semantic structuring for enhanced RAG compatibility

### Development Status
- **Current Phase**: 4.3W.1 - Local file upload implementation complete
- **Framework**: Goal-based Scrum sprints with Claude Code assistance
- **Coverage**: Maintaining 95%+ test coverage across all modules
- **Recent Achievements**: WTEG implementation, PDF processing, file upload UI

## Important Notes

- Always run tests before committing changes
- Follow TDD workflow: write tests first, then implement
- Use mocking extensively for external dependencies (web requests, file I/O)
- Maintain test coverage targets (100% ATDD, 95%+ unit tests)
- Implement ethical scraping practices with proper rate limiting
- When working with new features, check existing sprint documentation in docs/sprints/
- Configuration files are in both src/config/ and root (file_generator_config.json)
- The project uses comprehensive error handling with custom exception classes
- All UI components must integrate with the existing Flask templates in src/web_interface/templates/