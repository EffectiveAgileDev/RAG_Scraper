# Refactoring Test Commands Reference

## Overview

This document provides specific pytest commands for managing tests during the refactoring process. These commands help you run different categories of tests based on their brittleness and relationship to refactoring targets.

## Test Categories

### Safe Tests (Run During Refactoring)
Tests that focus on behavior and should continue to pass during refactoring:
- PDF text extraction (data transformation)
- Industry database (data contracts)  
- Synonym expansion (algorithms)
- End-to-end integration tests
- Multi-modal integration tests
- **Characterization tests** (document current behavior)

### Brittle Tests (Likely to Break)
Tests that focus on implementation details and will likely break during refactoring:
- Multi-page scraper internal methods
- AI pipeline OpenAI client mocking
- Flask app internal construction
- Format selection validation internals

## Commands for Refactoring Phases

### Phase 1: Pre-Refactoring Validation

```bash
# Run all safe tests to establish baseline
pytest -m "safe_for_refactoring or characterization" --tb=short -v

# Run characterization tests to document current behavior
pytest -m "characterization" --tb=short -v

# Run safe integration tests
pytest tests/integration/test_end_to_end_multi_modal.py tests/integration/test_multi_modal_integration.py tests/integration/test_ui_fixes_integration.py -v

# Run safe unit tests
pytest tests/unit/test_pdf_text_extractor.py tests/unit/test_industry_database.py tests/unit/test_synonym_expander.py -v
```

### Phase 2: During Refactoring

```bash
# Run only safe tests (skip brittle tests)
pytest -m "not (brittle_critical or brittle_likely)" --tb=short

# Run characterization tests to verify behavior is maintained
pytest -m "characterization" --tb=short

# Quick smoke test with safe tests
pytest -m "safe_for_refactoring" --tb=short

# Run tests for specific refactoring target
pytest -m "refactoring_target_multi_page" --tb=short
pytest -m "refactoring_target_ai_pipeline" --tb=short
pytest -m "refactoring_target_flask_app" --tb=short
pytest -m "refactoring_target_format_selection" --tb=short
```

### Phase 3: Post-Refactoring Cleanup

```bash
# Run all tests to see what needs fixing
pytest --tb=short

# Run only brittle tests to see what broke
pytest -m "brittle_critical or brittle_likely" --tb=short

# Run tests by brittleness level
pytest -m "brittle_critical" --tb=short  # Most important to fix
pytest -m "brittle_likely" --tb=short   # Likely need updates
pytest -m "brittle_possible" --tb=short # May need minor updates
```

## Target-Specific Commands

### Multi-Page Scraper Refactoring

```bash
# Run safe tests related to multi-page scraper
pytest -m "refactoring_target_multi_page and safe_for_refactoring" --tb=short

# Run characterization tests for multi-page scraper
pytest tests/characterization/test_multi_page_scraper_characterization.py -v

# See which multi-page tests are brittle
pytest -m "refactoring_target_multi_page and (brittle_critical or brittle_likely)" --tb=short
```

### AI Pipeline Refactoring

```bash
# Run safe tests for AI pipeline
pytest -m "refactoring_target_ai_pipeline and safe_for_refactoring" --tb=short

# Run characterization tests for AI pipeline
pytest tests/characterization/test_ai_pipeline_characterization.py -v

# See which AI tests are brittle
pytest -m "refactoring_target_ai_pipeline and (brittle_critical or brittle_likely)" --tb=short
```

### Flask Application Refactoring

```bash
# Run safe tests for Flask app
pytest -m "refactoring_target_flask_app and safe_for_refactoring" --tb=short

# Run characterization tests for Flask app
pytest tests/characterization/test_flask_app_characterization.py -v

# See which Flask tests are brittle
pytest -m "refactoring_target_flask_app and (brittle_critical or brittle_likely)" --tb=short
```

### Format Selection Refactoring

```bash
# Run safe tests for format selection
pytest -m "refactoring_target_format_selection and safe_for_refactoring" --tb=short

# Run characterization tests for format selection
pytest tests/characterization/test_format_selection_characterization_simple.py -v

# See which format selection tests are brittle
pytest -m "refactoring_target_format_selection and (brittle_critical or brittle_likely)" --tb=short
```

## Coverage Commands

```bash
# Run safe tests with coverage
pytest -m "safe_for_refactoring or characterization" --cov=src --cov-report=html

# Run all tests with coverage (post-refactoring)
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific target with coverage
pytest -m "refactoring_target_multi_page" --cov=src.scraper --cov-report=term-missing
```

## Debug Commands

```bash
# Run single test with verbose output
pytest tests/characterization/test_multi_page_scraper_characterization.py::TestMultiPageScraperCharacterization::test_basic_initialization_behavior -v -s

# Run tests and stop on first failure
pytest -m "safe_for_refactoring" --tb=short -x

# Run tests with pdb on failure
pytest -m "characterization" --tb=short --pdb
```

## Example Refactoring Workflow

```bash
# 1. Establish baseline with safe tests
pytest -m "safe_for_refactoring or characterization" --tb=short

# 2. Start refactoring multi-page scraper
pytest -m "refactoring_target_multi_page and safe_for_refactoring" --tb=short

# 3. Run characterization tests to verify behavior
pytest tests/characterization/test_multi_page_scraper_characterization.py -v

# 4. Continue refactoring, ignoring brittle tests
pytest -m "not (brittle_critical or brittle_likely)" --tb=short

# 5. After refactoring, see what broke
pytest -m "brittle_critical" --tb=short

# 6. Fix critical brittle tests
pytest -m "refactoring_target_multi_page and brittle_critical" --tb=short

# 7. Run full test suite
pytest --tb=short
```

## Test Marking Commands

```bash
# See all available markers
pytest --markers

# List tests by marker
pytest --collect-only -m "brittle_critical"
pytest --collect-only -m "safe_for_refactoring"
pytest --collect-only -m "characterization"

# Count tests by category
pytest --collect-only -q -m "brittle_critical" | wc -l
pytest --collect-only -q -m "safe_for_refactoring" | wc -l
```

## Performance Commands

```bash
# Run fastest tests first
pytest -m "safe_for_refactoring" --tb=short --durations=10

# Run slow tests separately
pytest -m "slow" --tb=short

# Run tests in parallel (if pytest-xdist installed)
pytest -m "safe_for_refactoring" -n auto --tb=short
```

## File-Based Commands

```bash
# Run specific safe test files
pytest tests/unit/test_pdf_text_extractor.py tests/unit/test_industry_database.py tests/unit/test_synonym_expander.py -v

# Run all characterization tests
pytest tests/characterization/ -v

# Run specific integration tests
pytest tests/integration/test_end_to_end_multi_modal.py tests/integration/test_multi_modal_integration.py -v
```

This reference ensures you can efficiently run the right tests at the right time during the refactoring process, maintaining confidence while avoiding brittle test failures.