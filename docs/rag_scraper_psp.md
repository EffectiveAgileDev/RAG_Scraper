# RAG_Scraper Project Startup Plan (PSP)

## Document Information
- **Project Name**: RAG_Scraper
- **Version**: 1.0
- **Created**: June 9, 2025
- **Document Type**: Project Startup Plan (PSP)
- **Target Release**: 1-2 days from project start
- **Development Platform**: Linux

## Project Overview and Objectives

### App Overview
RAG_Scraper is a localhost web-based application that scrapes restaurant websites and converts the extracted data into structured text files compatible with Retrieval-Augmented Generation (RAG) systems. The application focuses on extracting comprehensive restaurant information from individual restaurant websites and chain location pages to populate directory systems.

### Primary Objectives
- **Data Extraction**: Scrape restaurant websites to extract structured information following established format standards
- **RAG Integration**: Generate text files that seamlessly integrate with RAG directory systems  
- **Batch Processing**: Handle up to 100 URLs per session with appropriate memory management and user progress indication
- **Error Resilience**: Comprehensive error handling for diverse website structures and scraping challenges
- **Quality Assurance**: 100% ATDD coverage of user features and nearly 100% TDD coverage using Red-Green-Refactor cycles

### Success Metrics
- Successful extraction from 95%+ of valid restaurant websites
- Handle 100 URL batch sessions with progress feedback
- 100% ATDD coverage of user features
- Nearly 100% TDD coverage of implementation code
- Completion within 1-2 day development timeline

## Team Size and Project Framework

### Team Structure
**Solo Developer**: You serving as Product Owner, Scrum Master, and Development Team
- **Claude Code Integration**: AI-assisted development with Red-Green-Refactor prompting
- **Role Management**: Self-directed Scrum ceremonies and decision-making

### Project Framework
**Framework**: Adapted Scrum with Goal-Based Sprints
- **Sprint Definition**: Sprints defined by functional goals rather than time-boxes
- **Sprint Duration**: Variable based on goal complexity (targeting 1-2 day total completion)
- **Daily Progress**: Self-assessment with Claude Code collaboration
- **Reviews**: Goal completion validation before moving to next sprint

### Adapted Scrum Ceremonies
- **Sprint Planning**: Define clear, testable goals for each sprint
- **Daily Check-in**: Progress assessment and impediment identification
- **Sprint Review**: Functional demonstration of completed goals
- **Sprint Retrospective**: Process improvement for remaining sprints

## Test-First Approach Implementation

### Acceptance Test Driven Development (ATDD)
**Coverage Target**: 100% of user features
**Framework**: pytest-bdd with Gherkin scenarios

**ATDD Process with Claude Code**:
1. **Red Phase**: Prompt Claude Code to write failing acceptance tests in Gherkin format
2. **Green Phase**: Prompt Claude Code to implement step definitions and minimal functionality
3. **Refactor Phase**: Prompt Claude Code to improve implementation while maintaining test coverage

**Example ATDD Workflow**:
```gherkin
Feature: Restaurant Website Scraping
  As a RAG system administrator
  I want to scrape restaurant websites in batches
  So that I can populate directory data efficiently

Scenario: Successful batch restaurant scraping with progress indication
  Given I have 5 valid restaurant website URLs
  And I have selected default data fields
  When I execute the batch scraping process
  Then I should see progress updates for each website
  And I should receive properly formatted text files
  And each file should contain restaurant name, address, and phone
```

### Unit Test Driven Development (TDD)
**Coverage Target**: Nearly 100% of implementation code
**Framework**: pytest with comprehensive mocking

**TDD Process with Claude Code**:
1. **Red Phase**: Prompt Claude Code to write failing unit tests for specific functions
2. **Green Phase**: Prompt Claude Code to implement minimal code to pass tests
3. **Refactor Phase**: Prompt Claude Code to improve code quality while maintaining coverage

### Error Testing Strategy
**Comprehensive Error Scenarios**:
- Dynamic content loading failures
- Inconsistent website structures
- Rate limiting and IP blocking responses
- Memory management during large batch processing
- Malformed HTML and missing data scenarios
- Network timeouts and connection failures

## Development Tools and Environment

### Core Technology Stack
**Backend**: Python 3.9+ with Flask 2.3+
- **Web Scraping**: requests, BeautifulSoup4, lxml
- **Rate Limiting**: Custom implementation with respectful delays
- **Progress Tracking**: Real-time batch processing feedback
- **Memory Management**: Efficient processing for 100 URL batches

### Testing Framework
**Primary Framework**: pytest with BDD capabilities
- **pytest-bdd**: Gherkin scenario implementation
- **pytest-cov**: Real-time coverage reporting
- **responses**: HTTP request mocking for scraping tests
- **pytest-html**: Test reporting for review cycles

### AI Development Integration
**Claude Code Usage**:
- **Red Phase Prompts**: "Write failing tests for [specific functionality]"
- **Green Phase Prompts**: "Implement minimal code to make these tests pass"
- **Refactor Phase Prompts**: "Improve this code while maintaining test coverage"
- **Error Testing Prompts**: "Add comprehensive error handling tests for [scenario]"

### Frontend Technology
**Approach**: HTML5 + Vanilla JavaScript + CSS3
- Single-page application for localhost access
- Real-time progress indicators for batch processing
- User feedback for scraping status and errors

## Source Control Plan

### Version Control System
**System**: Git with GitHub remote repository

### Repository Structure
```
rag_scraper/
├── src/
│   ├── scraper/
│   ├── web_interface/
│   ├── file_generator/
│   └── config/
├── tests/
│   ├── features/          # ATDD Gherkin files
│   ├── step_definitions/   # ATDD step implementations
│   ├── unit/              # TDD unit tests
│   └── test_data/         # Mock HTML samples
├── docs/
├── requirements.txt
└── README.md
```

### Commit Strategy
**Goal-Oriented Commits**: Commit when each sprint goal is achieved
- **Sprint Goal Completion**: Single commit per completed sprint goal
- **Test-First Evidence**: Commit messages include test coverage achieved
- **Functional Milestones**: Each commit represents working, tested functionality

### Commit Message Format
```
[SPRINT-X] [GOAL] Brief description

- ATDD coverage: X scenarios passing
- TDD coverage: X% of implementation code
- Functional milestone: [specific achievement]
```

## Security and Ethical Considerations

### User Authentication and Access
**Security Model**: OS-level authentication only
- **Local Access**: Application runs on localhost for authenticated OS users
- **File Permissions**: Users can save files to any folder their system permissions allow
- **No Application Authentication**: Relies on OS user session security

### Ethical Web Scraping
**Implementation Requirements**:
- **robots.txt Compliance**: Check and respect robots.txt files before scraping
- **Rate Limiting**: Maximum 1 request per 2 seconds per domain
- **User-Agent Headers**: Identify scraper appropriately
- **Timeout Management**: 30-second timeout per page to prevent hanging
- **Respectful Behavior**: Graceful handling of 429 (Too Many Requests) responses

### Error Handling Security
- **Input Validation**: Sanitize all user inputs and URLs
- **File System Security**: Restrict file operations to user-selected directories
- **Error Message Safety**: Prevent information disclosure through error messages

## Development Structure and Sprint Goals

### Goal-Based Sprint Structure

#### Sprint 1 Goal: Foundation with ATDD/TDD Framework
**Objective**: Establish testing infrastructure and basic web interface

**ATDD Goals**:
- Create acceptance tests for single URL scraping workflow
- Define progress indication acceptance criteria
- Establish file output format validation scenarios

**TDD Goals**:
- Unit tests for URL validation and sanitization
- Basic Flask web server with localhost configuration
- File system permission handling with error cases

**Claude Code Prompting Strategy**:
1. "Write failing acceptance tests for single restaurant URL scraping"
2. "Implement minimal Flask server to make basic web interface tests pass"
3. "Add comprehensive error handling tests for invalid URLs"

**Completion Criteria**:
- 100% ATDD coverage for single URL workflow
- 95%+ TDD coverage for basic infrastructure
- Functional localhost web interface
- Goal-oriented commit to GitHub

#### Sprint 2 Goal: Core Scraping Engine with Error Resilience
**Objective**: Implement robust restaurant data extraction

**ATDD Goals**:
- Acceptance tests for diverse restaurant website structures
- Error handling scenarios for malformed HTML and missing data
- Data format validation matching RAG requirements

**TDD Goals**:
- Multi-strategy extraction (JSON-LD, microdata, heuristic patterns)
- Memory-efficient HTML parsing
- Comprehensive error case handling

**Technical Challenge Testing**:
- Dynamic content loading fallback scenarios
- Inconsistent website structure adaptation
- Rate limiting response handling
- Memory management validation

**Claude Code Prompting Strategy**:
1. "Write failing tests for extracting restaurant data from various HTML structures"
2. "Implement minimal extraction logic to handle JSON-LD and microdata"
3. "Add comprehensive error handling for malformed HTML and network failures"

**Completion Criteria**:
- 100% ATDD coverage for data extraction scenarios
- 95%+ TDD coverage for scraping engine
- Successful extraction from diverse test websites
- Robust error handling with user feedback

#### Sprint 3 Goal: Batch Processing with Progress Indication
**Objective**: Handle 100 URL sessions with memory management

**ATDD Goals**:
- Acceptance tests for batch processing workflows
- Progress indication and user feedback scenarios
- Memory management validation for large batches

**TDD Goals**:
- Efficient batch processing implementation
- Real-time progress updates to web interface
- Memory cleanup and resource management

**Performance Requirements**:
- Process 100 URLs without memory overflow
- Provide progress updates for each website processed
- Continue processing when individual sites fail

**Claude Code Prompting Strategy**:
1. "Write failing tests for batch processing 100 URLs with progress tracking"
2. "Implement minimal batch processor with memory management"
3. "Add real-time progress indication to web interface"

**Completion Criteria**:
- 100% ATDD coverage for batch processing workflows
- 95%+ TDD coverage for batch implementation
- Functional 100 URL batch processing with progress feedback
- Memory usage within acceptable limits

#### Sprint 4 Goal: File Generation and RAG Integration
**Objective**: Generate properly formatted text files for RAG systems

**ATDD Goals**:
- Acceptance tests for file format compliance
- Output validation matching PDF format guide
- User file location selection scenarios

**TDD Goals**:
- Text file generation with proper formatting
- RAG system compatibility validation
- User-configurable output options

**Integration Requirements**:
- Files match existing RAG system format requirements
- Single file and multiple file output modes
- User folder selection with permission validation

**Claude Code Prompting Strategy**:
1. "Write failing tests for RAG-compatible file format generation"
2. "Implement minimal file output system matching format requirements"
3. "Add user folder selection with permission validation"

**Completion Criteria**:
- 100% ATDD coverage for file generation workflows
- 95%+ TDD coverage for output system
- RAG-compatible file format validation
- Flexible output configuration options

## Technical Challenges and Testing Strategy

### Challenge 1: Dynamic Content Loading
**Testing Approach**: Mock JavaScript-heavy sites with empty initial HTML
**Error Scenarios**: Sites requiring JavaScript execution for content display
**Claude Code Prompts**: "Add tests for detecting and handling dynamic content loading"

### Challenge 2: Inconsistent Website Structures  
**Testing Approach**: Comprehensive test data set with diverse HTML structures
**Error Scenarios**: Missing data fields, unusual markup patterns
**Claude Code Prompts**: "Create tests for various restaurant website layout patterns"

### Challenge 3: Rate Limiting and IP Blocking
**Testing Approach**: Mock HTTP 429 responses and connection timeouts
**Error Scenarios**: Rate limit violations, blocked requests
**Claude Code Prompts**: "Add tests for rate limiting compliance and error recovery"

### Challenge 4: Memory Management for Large Batches
**Testing Approach**: Memory usage monitoring during 100 URL processing
**Error Scenarios**: Memory overflow, resource leaks
**Claude Code Prompts**: "Create tests for memory usage during large batch processing"

### Challenge 5: Data Quality and Validation
**Testing Approach**: Validation tests for extracted data format and completeness
**Error Scenarios**: Incomplete data, formatting inconsistencies
**Claude Code Prompts**: "Add comprehensive data validation tests for restaurant information"

## Performance Requirements and Testing

### Processing Performance
- **Target Speed**: 3-5 seconds per restaurant website
- **Batch Capacity**: 100 URLs per session without memory issues
- **Progress Updates**: Real-time feedback every 2 seconds during processing
- **Memory Usage**: Monitor and maintain efficient memory utilization

### User Interface Performance
- **Page Load**: Interface loads within 3 seconds on localhost
- **Responsiveness**: Form interactions respond within 500ms
- **Progress Indication**: Real-time updates during batch processing
- **Error Feedback**: Immediate validation and error reporting

## Quality Assurance and Definition of Done

### Sprint Goal Completion Criteria
- **ATDD Coverage**: 100% of user features covered by acceptance tests
- **TDD Coverage**: 95%+ of implementation code covered by unit tests
- **Functional Validation**: All acceptance criteria demonstrably working
- **Error Resilience**: Comprehensive error handling tested and validated
- **Code Quality**: Clean, maintainable code following Python best practices

### Project Completion Criteria
- **All Sprint Goals**: Successfully completed with full test coverage
- **Integration Testing**: End-to-end workflow validation
- **Performance Validation**: 100 URL batch processing capability
- **Documentation**: Clear README with installation and usage instructions
- **GitHub Repository**: Complete codebase with goal-oriented commit history

## Development Workflow with Claude Code

### Daily Development Cycle
1. **Goal Assessment**: Review current sprint goal and remaining tasks
2. **ATDD Phase**: Prompt Claude Code for acceptance test scenarios
3. **TDD Red Phase**: Prompt Claude Code for failing unit tests
4. **TDD Green Phase**: Prompt Claude Code for minimal implementation
5. **TDD Refactor Phase**: Prompt Claude Code for code quality improvements
6. **Integration Testing**: Validate component interactions
7. **Progress Evaluation**: Assess goal completion and plan next steps

### Claude Code Prompting Best Practices
- **Specific Test Requests**: "Write failing tests for extracting phone numbers from restaurant HTML"
- **Clear Implementation Goals**: "Implement minimal code to make phone extraction tests pass"
- **Focused Refactoring**: "Refactor phone extraction code for better error handling while maintaining test coverage"
- **Error Scenario Testing**: "Add comprehensive tests for network timeout scenarios during scraping"

### Sprint Transition Process
1. **Goal Validation**: Confirm all acceptance criteria met
2. **Test Coverage Review**: Verify ATDD and TDD coverage targets achieved
3. **Functional Demonstration**: Validate working features
4. **Git Commit**: Goal-oriented commit with coverage summary
5. **Next Sprint Planning**: Define next goal and acceptance criteria

## Project Setup Instructions

### Linux System Setup for RAG_Scraper Development

#### Prerequisites
- Linux system with terminal access
- Python 3.9+ installed
- Internet connection for package installation and GitHub access
- Text editor or IDE of choice

#### Step 1: Create Project Directory Structure
```bash
# Create the project directory
mkdir -p /home/AI/Projects/RAG_Scraper
cd /home/AI/Projects/RAG_Scraper

# Create initial directory structure
mkdir -p src/{scraper,web_interface,file_generator,config}
mkdir -p tests/{features,step_definitions,unit,test_data}
mkdir -p docs
```

#### Step 2: Python Environment Setup
```bash
# Check Python version (should be 3.9+)
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### Step 3: Create Requirements File
```bash
# Create requirements.txt with initial dependencies
cat > requirements.txt << 'EOF'
# Web Framework
Flask==2.3.3
requests==2.31.0

# Web Scraping
beautifulsoup4==4.12.2
lxml==4.9.3
html5lib==1.1

# Testing Framework
pytest==7.4.2
pytest-bdd==6.1.1
pytest-cov==4.1.0
pytest-html==3.2.0
pytest-mock==3.11.1
responses==0.23.3

# Development Tools
black==23.7.0
flake8==6.0.0
coverage==7.3.0
EOF

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Git Repository Setup
```bash
# Initialize Git repository
git init

# Create .gitignore file
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
output/
scraped_data/
EOF

# Create initial README
cat > README.md << 'EOF'
# RAG_Scraper

A web-based application that scrapes restaurant websites and converts extracted data into structured text files compatible with Retrieval-Augmented Generation (RAG) systems.

## Development Status
- Project initialized
- TDD/ATDD framework ready
- Goal-based Sprint development in progress

## Setup
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest`
4. Start application: `python src/app.py`

## Development Approach
- Full ATDD with TDD using Red-Green-Refactor cycles
- Claude Code assisted development
- Goal-based Scrum sprints
- 100% ATDD coverage target
- Nearly 100% TDD coverage target
EOF

# Create initial commit
git add .
git commit -m "[SETUP] Initial project structure with TDD framework

- ATDD framework: pytest-bdd ready for Gherkin scenarios
- TDD framework: pytest with coverage reporting
- Development environment: Python virtual environment configured
- Project milestone: Ready for Sprint 1 development"
```

#### Step 5: GitHub Repository Setup
```bash
# Create GitHub repository (requires GitHub CLI or manual creation)
# Option 1: Using GitHub CLI (if installed)
gh repo create RAG_Scraper --public --source=. --remote=origin --push

# Option 2: Manual GitHub setup
# 1. Go to GitHub.com and create new repository named 'RAG_Scraper'
# 2. Copy the repository URL
# 3. Add remote origin:
# git remote add origin https://github.com/[your-username]/RAG_Scraper.git
# git branch -M main
# git push -u origin main
```

#### Step 6: Claude Code Setup and Configuration

##### Install Claude Code
```bash
# Install Claude Code CLI (requires npm/node.js)
# If npm not installed:
sudo apt update
sudo apt install nodejs npm

# Install Claude Code globally
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

##### Configure Claude Code for TDD Workflow
```bash
# Create project documentation directory for TDD references
mkdir -p docs/tdd

# Create TDD workflow documentation for reference
cat > docs/tdd/workflow.md << 'EOF'
# RAG_Scraper TDD Workflow with Claude Code

## Red-Green-Refactor Process

### Red Phase Commands
- "Write failing tests for [specific functionality]"
- "Create acceptance tests for [user story]"
- "Add unit tests for [component/function]"

### Green Phase Commands  
- "Implement minimal code to make these tests pass"
- "Write the simplest solution for [failing test]"
- "Add basic implementation for [feature]"

### Refactor Phase Commands
- "Refactor this code while maintaining test coverage"
- "Improve code quality and structure"
- "Optimize performance while keeping tests green"

## Project Goals
- 100% ATDD coverage of user features
- 95%+ TDD coverage of implementation code
- Goal-based sprint completion

## Test Commands
- Run tests: pytest
- Coverage: pytest --cov=src
- Specific tests: pytest tests/[specific_test].py
EOF

# Note: Claude Code will create its own CLAUDE.md file during /init
# This will contain project-specific context and commands
echo "Claude Code configuration ready for TDD workflow"
```

#### Step 7: Initial Project Structure Validation
```bash
# Create basic test to validate setup
cat > tests/test_setup.py << 'EOF'
"""Setup validation tests for RAG_Scraper project."""
import sys
import os

def test_python_version():
    """Verify Python version is 3.9+"""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version_info}"

def test_project_structure():
    """Verify project directory structure exists"""
    required_dirs = [
        'src',
        'src/scraper',
        'src/web_interface', 
        'src/file_generator',
        'src/config',
        'tests',
        'tests/features',
        'tests/step_definitions',
        'tests/unit',
        'tests/test_data'
    ]
    
    for directory in required_dirs:
        assert os.path.exists(directory), f"Required directory missing: {directory}"

def test_dependencies_importable():
    """Verify key dependencies can be imported"""
    try:
        import flask
        import pytest
        import requests
        import bs4
        import pytest_bdd
        assert True
    except ImportError as e:
        assert False, f"Failed to import required dependency: {e}"
EOF

# Run setup validation
pytest tests/test_setup.py -v

# Check test coverage setup
pytest --cov=src tests/test_setup.py --cov-report=html
```

#### Step 8: Claude Code Project Initialization
```bash
# Start Claude Code in the project directory
claude

# Initialize the project with Claude Code (this analyzes the codebase and creates CLAUDE.md)
/init

# This will:
# - Analyze your project structure and dependencies
# - Create a CLAUDE.md file with project-specific information
# - Document build/test/lint commands for the project
# - Establish code style guidelines
# - Set up project context for future Claude Code sessions

# Verify the CLAUDE.md file was created
ls -la CLAUDE.md

# Review the generated project documentation
cat CLAUDE.md
```

#### Step 9: Claude Code TDD Workflow Verification
```bash
# Test basic Claude Code functionality within the session
# (After running /init above, you should still be in the Claude Code session)

# Test project understanding
> summarize this project

# Test TDD workflow capability
> help me set up pytest for this project

# Test file analysis capability  
> analyze the project structure

# Exit Claude Code session (type 'exit' or Ctrl+C)
exit
```

#### Step 10: Development Environment Validation
```bash
# Create validation script
cat > validate_setup.sh << 'EOF'
#!/bin/bash
echo "=== RAG_Scraper Development Environment Validation ==="

echo "1. Checking Python version..."
python3 --version

echo "2. Checking virtual environment..."
which python
which pip

echo "3. Checking Git status..."
git status

echo "4. Checking installed packages..."
pip list | grep -E "(flask|pytest|requests|beautifulsoup4)"

echo "5. Running setup tests..."
pytest tests/test_setup.py -v

echo "6. Checking test coverage capability..."
pytest --cov=src tests/test_setup.py --cov-report=term-missing

echo "8. Checking Claude Code installation..."
claude --version

echo "9. Checking project initialization readiness..."
if [ -f "CLAUDE.md" ]; then
    echo "✓ CLAUDE.md project file exists"
    echo "✓ Claude Code project initialization previously completed"
else
    echo "ℹ CLAUDE.md not found - run 'claude' then '/init' after validation"
    echo "ℹ This is normal for first-time setup"
fi

echo "=== Setup validation complete ==="
echo "Ready for Sprint 1 development with Claude Code TDD workflow"
EOF

chmod +x validate_setup.sh
./validate_setup.sh
```

#### Step 11: Ready for Development
```bash
# Final commit with complete setup
git add .
git commit -m "[SETUP] Complete development environment ready for TDD

- Claude Code configured with TDD workflow templates
- Test framework validated with setup tests
- Coverage reporting functional
- Project structure validated
- Ready for Sprint 1: ATDD/TDD Foundation development"

git push origin main

echo "=== RAG_Scraper Development Setup Complete ==="
echo "Project location: /home/AI/Projects/RAG_Scraper"
echo "Virtual environment: source venv/bin/activate"
echo "Test command: pytest"
echo "Coverage command: pytest --cov=src"
echo "Claude Code: claude (then /init to initialize project)"
echo ""
echo "Next step: Begin Sprint 1 with Claude Code assistance"
echo "Remember to run '/init' in Claude Code session to create CLAUDE.md"
```

---

**Next Steps**:
1. Complete the setup instructions above
2. Validate development environment using validation script
3. Begin Sprint 1 with Claude Code-assisted ATDD framework establishment
4. Use Claude Code prompt templates for Red-Green-Refactor cycles
5. Commit to GitHub when each sprint goal is achieved

**Document Status**: Ready for Development Start  
**Estimated Completion**: 1-2 days with goal-based sprint execution