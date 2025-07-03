# WTEG Module Clean Code Refactoring Plan

## Clean Code Principles to Apply

### 1. Single Responsibility Principle (SRP)
- **Issue**: `WTEGRestaurantData` has too many responsibilities (data storage, formatting, RAG conversion)
- **Solution**: Extract formatting and conversion logic to separate classes

### 2. DRY (Don't Repeat Yourself)
- **Issue**: Similar `to_dict()` methods repeated across all dataclasses
- **Solution**: Create base class with common serialization logic

### 3. Meaningful Names
- **Issue**: Some method names are too long (_create_location_summary, _extract_name_from_description)
- **Solution**: Shorter, more descriptive names

### 4. Small Functions
- **Issue**: Some methods in `wteg_extractor.py` are too long (>20 lines)
- **Solution**: Break down into smaller, focused functions

### 5. Code Organization
- **Issue**: Mixed concerns in single files
- **Solution**: Separate into focused modules

## Refactoring Tasks

### Phase 1: Extract Common Base Classes
- [ ] Create `wteg_base.py` with `WTEGSerializable` base class
- [ ] Move common `to_dict()` logic to base class
- [ ] Add validation methods to base class

### Phase 2: Separate Concerns
- [ ] Extract `wteg_formatters.py` for all formatting logic
- [ ] Extract `wteg_validators.py` for validation logic
- [ ] Move RAG conversion logic to dedicated class

### Phase 3: Simplify Complex Methods
- [ ] Break down `_convert_to_wteg_schema()` into smaller methods
- [ ] Simplify `_extract_pagedata_from_html()` with helper functions
- [ ] Reduce cyclomatic complexity in export methods

### Phase 4: Improve Naming
- [ ] Rename overly long method names
- [ ] Use consistent naming patterns
- [ ] Remove redundant prefixes/suffixes

### Phase 5: Add Type Hints and Documentation
- [ ] Ensure all methods have proper type hints
- [ ] Add missing docstrings
- [ ] Document complex logic with inline comments

## Testing Strategy
- Run all tests after each refactoring step
- Ensure 100% test coverage maintained
- No functional changes, only structural improvements