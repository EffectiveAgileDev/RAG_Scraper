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
```

### Code Quality Commands
```bash
black src/ tests/        # Format code
flake8 src/ tests/       # Lint code
coverage report          # Show coverage report
```

### Application Commands
```bash
python src/app.py        # Start Flask web server (port 8080)
```

## Project Architecture

### Core Components
- **src/web_interface/** - Flask web server providing localhost interface on port 8080
- **src/scraper/** - Web scraping engine using BeautifulSoup4 and requests-html
- **src/file_generator/** - Generates text files for RAG systems and PDF documentation
- **src/config/** - Configuration management and user preferences

### Technology Stack
- **Backend**: Flask 2.3.3 web framework
- **Scraping**: BeautifulSoup4 4.12.2, requests-html 0.10.0, html5lib
- **Testing**: pytest with BDD support (pytest-bdd), comprehensive mocking
- **Code Quality**: black formatting, flake8 linting

## Test-Driven Development Approach

### Testing Strategy
This project follows strict **Test-Driven Development (TDD)** with:
- **ATDD (Acceptance Test Driven Development)**: 100% coverage target using pytest-bdd with Gherkin scenarios
- **Unit TDD**: 95%+ coverage target using pytest with extensive mocking
- **Red-Green-Refactor cycles**: Write failing tests first, implement minimal code, then refactor

### Test Structure
- **tests/features/** - Gherkin BDD scenarios for user stories
- **tests/step_definitions/** - pytest-bdd step implementations
- **tests/unit/** - Unit tests for individual components
- **tests/test_data/** - Mock HTML samples for scraper testing

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

### Development Status
- **Current**: Initial setup complete, ready for development
- **Framework**: Goal-based Scrum sprints with Claude Code assistance
- **Target**: 1-2 days total development time

## Important Notes

- Always run tests before committing changes
- Follow TDD workflow: write tests first, then implement
- Use mocking extensively for external dependencies (web requests)
- Maintain test coverage targets (100% ATDD, 95%+ unit tests)
- Implement ethical scraping practices with proper rate limiting