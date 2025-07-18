"""
Pytest configuration for marking brittle tests during refactoring.

This file contains pytest markers and configurations to identify and skip
brittle tests during the refactoring process.
"""

import pytest

# Define custom markers for brittle tests
def pytest_configure(config):
    """Configure custom pytest markers for brittle tests."""
    config.addinivalue_line(
        "markers", "brittle_critical: marks tests as critically brittle (will definitely break during refactoring)"
    )
    config.addinivalue_line(
        "markers", "brittle_likely: marks tests as likely brittle (will probably break during refactoring)"
    )
    config.addinivalue_line(
        "markers", "brittle_possible: marks tests as possibly brittle (may break during refactoring)"
    )
    config.addinivalue_line(
        "markers", "refactoring_target_multi_page: marks tests that test multi-page scraper architecture"
    )
    config.addinivalue_line(
        "markers", "refactoring_target_ai_pipeline: marks tests that test AI enhancement pipeline"
    )
    config.addinivalue_line(
        "markers", "refactoring_target_flask_app: marks tests that test Flask application structure"
    )
    config.addinivalue_line(
        "markers", "refactoring_target_format_selection: marks tests that test format selection logic"
    )
    config.addinivalue_line(
        "markers", "safe_for_refactoring: marks tests as safe during refactoring (behavior-focused)"
    )
    config.addinivalue_line(
        "markers", "characterization: marks tests as characterization tests (document current behavior)"
    )


# Brittle test files identified during analysis
BRITTLE_TEST_FILES = {
    # Multi-Page Scraper Architecture - Critical
    "test_multi_page_scraper_error_handling.py": "brittle_critical",
    "test_multi_page_scraper_concurrent.py": "brittle_critical", 
    "test_multi_page_scraper_traversal.py": "brittle_critical",
    
    # Multi-Page Scraper Architecture - Likely
    "test_multi_page_result_handler.py": "brittle_likely",
    "test_multi_page_progress.py": "brittle_likely",
    "test_page_processor.py": "brittle_likely",
    "test_page_queue_manager.py": "brittle_likely",
    "test_data_aggregator.py": "brittle_likely",
    "test_page_classifier.py": "brittle_likely",
    "test_page_discovery.py": "brittle_likely",
    "test_multi_page_scraper_config.py": "brittle_likely",
    "test_multi_page_scraper_integration.py": "brittle_likely",
    "test_multi_page_scraper_refactored.py": "brittle_likely",
    
    # AI Enhancement Pipeline - Critical
    "test_llm_extractor.py": "brittle_critical",
    "test_ai_enhanced_multi_strategy_scraper.py": "brittle_critical",
    "test_content_analyzer.py": "brittle_critical",
    
    # AI Enhancement Pipeline - Likely
    "test_ai_api_routes.py": "brittle_likely",
    "test_ai_settings_persistence.py": "brittle_likely",
    "test_pattern_learner.py": "brittle_likely",
    "test_multimodal_extractor.py": "brittle_likely",
    "test_dynamic_prompt_adjuster.py": "brittle_likely",
    "test_claude_extractor.py": "brittle_likely",
    "test_ollama_extractor.py": "brittle_likely",
    "test_custom_extractor.py": "brittle_likely",
    "test_restaurant_data_ai_integration.py": "brittle_likely",
    "test_file_upload_ai_enhancement_defect.py": "brittle_likely",
    "test_confidence_scorer.py": "brittle_likely",
    "test_content_scorer.py": "brittle_likely",
    "test_chunk_optimizer.py": "brittle_likely",
    "test_metadata_enricher.py": "brittle_likely",
    "test_semantic_structurer.py": "brittle_likely",
    
    # Flask Application Structure - Critical
    "test_flask_server.py": "brittle_critical",
    
    # Flask Application Structure - Likely
    "test_flask_pdf_integration.py": "brittle_likely",
    "test_flask_file_generation.py": "brittle_likely",
    "test_app_factory.py": "brittle_likely",
    "test_route_registration.py": "brittle_likely",
    "test_service_integration.py": "brittle_likely",
    "test_error_handling_integration.py": "brittle_likely",
    "test_configuration_loading.py": "brittle_likely",
    "test_blueprint_registration.py": "brittle_likely",
    "test_middleware_integration.py": "brittle_likely",
    "test_security_integration.py": "brittle_likely",
    "test_logging_integration.py": "brittle_likely",
    "test_session_management.py": "brittle_likely",
    "test_static_file_serving.py": "brittle_likely",
    "test_template_rendering.py": "brittle_likely",
    "test_request_handling.py": "brittle_likely",
    "test_response_formatting.py": "brittle_likely",
    
    # Format Selection Logic - Critical
    "test_format_selection_manager.py": "brittle_critical",
    "test_format_validator.py": "brittle_critical",
    
    # Format Selection Logic - Likely
    "test_format_selection_integration.py": "brittle_likely",
    "test_format_configuration.py": "brittle_likely",
    "test_format_preferences.py": "brittle_likely",
    "test_format_validation_rules.py": "brittle_likely",
    "test_format_error_handling.py": "brittle_likely",
    "test_format_callback_system.py": "brittle_likely",
    "test_format_persistence.py": "brittle_likely",
    "test_format_priority_ordering.py": "brittle_likely",
    "test_format_field_selection.py": "brittle_likely",
    "test_format_mode_switching.py": "brittle_likely",
    "test_format_state_management.py": "brittle_likely",
    "test_format_event_handling.py": "brittle_likely",
    "test_format_concurrent_access.py": "brittle_likely",
    "test_format_memory_management.py": "brittle_likely",
    "test_format_cleanup_behavior.py": "brittle_likely",
    "test_format_thread_safety.py": "brittle_likely",
    "test_format_performance.py": "brittle_likely",
    "test_format_compatibility.py": "brittle_likely",
}

# Safe test files (behavior-focused)
SAFE_TEST_FILES = {
    "test_pdf_text_extractor.py": "safe_for_refactoring",
    "test_industry_database.py": "safe_for_refactoring", 
    "test_synonym_expander.py": "safe_for_refactoring",
    "test_end_to_end_multi_modal.py": "safe_for_refactoring",
    "test_multi_modal_integration.py": "safe_for_refactoring",
    "test_ui_fixes_integration.py": "safe_for_refactoring",
}

# Characterization test files
CHARACTERIZATION_TEST_FILES = {
    "test_multi_page_scraper_characterization.py": "characterization",
    "test_ai_pipeline_characterization.py": "characterization",
    "test_flask_app_characterization.py": "characterization",
    "test_format_selection_characterization_simple.py": "characterization",
}


def pytest_collection_modifyitems(config, items):
    """Automatically mark test items based on filename patterns."""
    for item in items:
        # Get the test file name
        test_file = item.fspath.basename
        
        # Mark brittle tests
        if test_file in BRITTLE_TEST_FILES:
            marker_name = BRITTLE_TEST_FILES[test_file]
            marker = getattr(pytest.mark, marker_name)
            item.add_marker(marker)
            
            # Add refactoring target markers
            if "multi_page" in test_file:
                item.add_marker(pytest.mark.refactoring_target_multi_page)
            elif "ai" in test_file or "llm" in test_file:
                item.add_marker(pytest.mark.refactoring_target_ai_pipeline)
            elif "flask" in test_file or "app" in test_file:
                item.add_marker(pytest.mark.refactoring_target_flask_app)
            elif "format" in test_file:
                item.add_marker(pytest.mark.refactoring_target_format_selection)
                
        # Mark safe tests
        elif test_file in SAFE_TEST_FILES:
            marker_name = SAFE_TEST_FILES[test_file]
            marker = getattr(pytest.mark, marker_name)
            item.add_marker(marker)
            
        # Mark characterization tests
        elif test_file in CHARACTERIZATION_TEST_FILES:
            marker_name = CHARACTERIZATION_TEST_FILES[test_file]
            marker = getattr(pytest.mark, marker_name)
            item.add_marker(marker)


# Helper functions for running specific test categories
def run_safe_tests_only():
    """Command to run only safe tests during refactoring."""
    return "pytest -m 'safe_for_refactoring or characterization' --tb=short"

def run_brittle_tests_only():
    """Command to run only brittle tests to see what breaks."""
    return "pytest -m 'brittle_critical or brittle_likely' --tb=short"

def skip_brittle_tests():
    """Command to skip brittle tests during refactoring."""
    return "pytest -m 'not (brittle_critical or brittle_likely)' --tb=short"

def run_characterization_tests():
    """Command to run characterization tests to verify behavior."""
    return "pytest -m 'characterization' --tb=short"

def run_refactoring_target_tests(target):
    """Command to run tests for a specific refactoring target."""
    return f"pytest -m 'refactoring_target_{target}' --tb=short"


if __name__ == "__main__":
    print("Brittle Test Marking Configuration")
    print("=" * 50)
    print(f"Total brittle test files marked: {len(BRITTLE_TEST_FILES)}")
    print(f"Safe test files marked: {len(SAFE_TEST_FILES)}")
    print(f"Characterization test files marked: {len(CHARACTERIZATION_TEST_FILES)}")
    print()
    print("Example commands:")
    print(f"  Safe tests only: {run_safe_tests_only()}")
    print(f"  Skip brittle tests: {skip_brittle_tests()}")
    print(f"  Run characterization: {run_characterization_tests()}")
    print(f"  Multi-page target: {run_refactoring_target_tests('multi_page')}")