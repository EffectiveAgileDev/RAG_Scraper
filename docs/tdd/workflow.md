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
