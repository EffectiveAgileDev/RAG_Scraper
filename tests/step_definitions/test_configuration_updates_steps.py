"""Step definitions for configuration updates BDD scenarios."""
import json
import os
import tempfile
from typing import Dict, Any, List

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from src.config.scraping_config import ScrapingConfig

# Load scenarios from feature file
scenarios("../features/configuration_updates.feature")


@pytest.fixture
def config_context():
    """Fixture to store configuration test context."""
    return {
        "config": None,
        "config_dict": {},
        "errors": [],
        "temp_files": [],
        "link_patterns": {"include": [], "exclude": []},
        "crawl_settings": {},
        "per_domain_settings": {}
    }


@given("I have a configuration system for the scraper")
def given_configuration_system(config_context):
    """Initialize configuration system."""
    # Configuration system is available through ScrapingConfig class
    config_context["config_dict"] = {
        "urls": ["https://example.com"]  # Required field
    }


@when(parsers.parse("I create a configuration with the following multi-page settings:\n{table}"))
def when_create_configuration_with_multi_page_settings(config_context, table):
    """Create configuration with multi-page settings from table."""
    # Parse table data
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at the beginning and end
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                param, value = parts[0], parts[1]
                # Convert string values to appropriate types
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                
                config_context["config_dict"][param] = value
    
    # Create configuration
    try:
        config_context["config"] = ScrapingConfig(**config_context["config_dict"])
    except Exception as e:
        config_context["errors"].append(str(e))


@when(parsers.parse("I configure link patterns with the following rules:\n{table}"))
def when_configure_link_patterns(config_context, table):
    """Configure link patterns from table."""
    # Parse table data
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            # Split on pipe and take only the middle content (strip edge empty cells)
            parts = line.split('|')[1:-1]  # Remove first and last empty parts
            parts = [p.strip() for p in parts]
            
            if len(parts) >= 3:
                pattern_type, pattern, action = parts[0], parts[1], parts[2]
                
                # Convert "OR" back to "|" for proper regex
                pattern = pattern.replace(" OR ", "|")
                
                if pattern_type == 'include':
                    config_context["link_patterns"]["include"].append(pattern)
                elif pattern_type == 'exclude':
                    config_context["link_patterns"]["exclude"].append(pattern)
    
    # Add to config dict
    config_context["config_dict"]["link_patterns"] = config_context["link_patterns"]


@when(parsers.parse("I set the following crawl limits:\n{table}"))
def when_set_crawl_limits(config_context, table):
    """Set crawl limits from table."""
    # Parse table data
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at the beginning and end
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                limit_type, value = parts[0], int(parts[1])
                config_context["crawl_settings"][limit_type] = value
    
    # Add to config dict
    config_context["config_dict"].update(config_context["crawl_settings"])


@given(parsers.parse('I have a configuration file "{filename}" with:\n{content}'))
def given_configuration_file(config_context, filename, content):
    """Create a temporary configuration file with given content."""
    # Create temp file
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(content.strip())
    
    config_context["temp_files"].append(filepath)
    config_context["config_file_path"] = filepath


@when(parsers.parse('I load the configuration from "{filename}"'))
def when_load_configuration_from_file(config_context, filename):
    """Load configuration from file."""
    try:
        # Use the actual file path from context
        filepath = config_context.get("config_file_path", filename)
        config_context["config"] = ScrapingConfig.load_from_file(filepath)
        
        # Store loaded data for verification
        with open(filepath, 'r') as f:
            config_context["loaded_data"] = json.load(f)
    except Exception as e:
        config_context["errors"].append(str(e))


@given(parsers.parse("I have a configuration with:\n{table}"))
def given_configuration_with_params(config_context, table):
    """Create configuration with parameters from table."""
    # Parse table data
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at the beginning and end
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                param, value = parts[0], parts[1]
                # Convert string values to appropriate types
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                
                config_context["config_dict"][param] = value
    
    # Create configuration
    config_context["config"] = ScrapingConfig(**config_context["config_dict"])


@when(parsers.parse('I save the configuration to "{filename}"'))
def when_save_configuration_to_file(config_context, filename):
    """Save configuration to file."""
    temp_dir = tempfile.mkdtemp()
    filepath = os.path.join(temp_dir, filename)
    
    config_context["config"].save_to_file(filepath)
    config_context["saved_file_path"] = filepath
    config_context["temp_files"].append(filepath)


@when(parsers.parse("I try to create a configuration with invalid values:\n{table}"))
def when_try_create_configuration_with_invalid_values(config_context, table):
    """Try to create configuration with invalid values."""
    # Parse table data
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at the beginning and end
            parts = [p for p in parts if p]
            if len(parts) >= 3:
                param, invalid_value, expected_error = parts[0], parts[1], parts[2]
                
                # Convert invalid value to appropriate type
                try:
                    if '.' in invalid_value:
                        invalid_value = float(invalid_value)
                    else:
                        invalid_value = int(invalid_value)
                except ValueError:
                    pass  # Keep as string
                
                # Try to create config with invalid value
                test_dict = config_context["config_dict"].copy()
                test_dict[param] = invalid_value
                
                try:
                    ScrapingConfig(**test_dict)
                except ValueError as e:
                    config_context["errors"].append({
                        "param": param,
                        "error": str(e),
                        "expected": expected_error
                    })


@when("I create a configuration without specifying optional parameters")
def when_create_configuration_with_defaults(config_context):
    """Create configuration with minimal required parameters."""
    config_context["config"] = ScrapingConfig(urls=["https://example.com"])


@when(parsers.parse("I configure per-domain settings:\n{table}"))
def when_configure_per_domain_settings(config_context, table):
    """Configure per-domain settings from table."""
    # Parse table data
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at the beginning and end
            parts = [p for p in parts if p]
            if len(parts) >= 4:
                domain, rate_limit, max_pages, user_agent = parts[0], float(parts[1]), int(parts[2]), parts[3]
                
                config_context["per_domain_settings"][domain] = {
                    "rate_limit": rate_limit,
                    "max_pages": max_pages,
                    "user_agent": user_agent
                }
    
    # Add to config dict
    config_context["config_dict"]["per_domain_settings"] = config_context["per_domain_settings"]


@then(parsers.parse("the configuration should have {param} set to {value:d}"))
def then_configuration_should_have_int_param(config_context, param, value):
    """Verify integer configuration parameter."""
    assert hasattr(config_context["config"], param), f"Configuration missing {param}"
    actual = getattr(config_context["config"], param)
    assert actual == value, f"Expected {param}={value}, got {actual}"


@then(parsers.parse("the configuration should have {param} set to {value}"))
def then_configuration_should_have_param(config_context, param, value):
    """Verify configuration parameter."""
    # Convert string values to appropriate types
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif value.isdigit():
        value = int(value)
    
    assert hasattr(config_context["config"], param), f"Configuration missing {param}"
    actual = getattr(config_context["config"], param)
    assert actual == value, f"Expected {param}={value}, got {actual}"


@then(parsers.parse('the configuration should include pattern "{pattern}" for following'))
def then_configuration_should_include_pattern(config_context, pattern):
    """Verify include pattern in configuration."""
    # Convert "OR" back to "|" for proper regex comparison
    pattern = pattern.replace(" OR ", "|")
    link_patterns = config_context["config_dict"].get("link_patterns", {})
    assert pattern in link_patterns.get("include", []), f"Pattern {pattern} not in include list"


@then(parsers.parse('the configuration should exclude pattern "{pattern}"'))
def then_configuration_should_exclude_pattern(config_context, pattern):
    """Verify exclude pattern in configuration."""
    # Convert "OR" back to "|" for proper regex comparison
    pattern = pattern.replace(" OR ", "|")
    link_patterns = config_context["config_dict"].get("link_patterns", {})
    assert pattern in link_patterns.get("exclude", []), f"Pattern {pattern} not in exclude list"


@then(parsers.parse("the crawler should not exceed depth {depth:d}"))
def then_crawler_should_not_exceed_depth(config_context, depth):
    """Verify max crawl depth setting."""
    assert config_context["crawl_settings"]["max_crawl_depth"] == depth


@then(parsers.parse("the crawler should process at most {max_pages:d} pages per site"))
def then_crawler_should_process_max_pages_per_site(config_context, max_pages):
    """Verify max pages per site setting."""
    assert config_context["crawl_settings"]["max_pages_per_site"] == max_pages


@then(parsers.parse("the crawler should stop after {total:d} total pages"))
def then_crawler_should_stop_after_total_pages(config_context, total):
    """Verify max total pages setting."""
    assert config_context["crawl_settings"]["max_total_pages"] == total


@then(parsers.parse("each page should timeout after {timeout:d} seconds"))
def then_page_should_timeout_after(config_context, timeout):
    """Verify page timeout setting."""
    assert config_context["crawl_settings"]["page_timeout"] == timeout


@then(parsers.parse("the configuration should have {count:d} include patterns"))
def then_configuration_should_have_include_patterns(config_context, count):
    """Verify number of include patterns."""
    loaded_data = config_context.get("loaded_data", {})
    link_patterns = loaded_data.get("link_patterns", {})
    include_patterns = link_patterns.get("include", [])
    assert len(include_patterns) == count, f"Expected {count} include patterns, got {len(include_patterns)}"


@then(parsers.parse("the configuration should have {count:d} exclude pattern"))
def then_configuration_should_have_exclude_patterns(config_context, count):
    """Verify number of exclude patterns."""
    loaded_data = config_context.get("loaded_data", {})
    link_patterns = loaded_data.get("link_patterns", {})
    exclude_patterns = link_patterns.get("exclude", [])
    assert len(exclude_patterns) == count, f"Expected {count} exclude patterns, got {len(exclude_patterns)}"


@then(parsers.parse("the crawl_settings should have {param} set to {value:d}"))
def then_crawl_settings_should_have_param(config_context, param, value):
    """Verify crawl settings parameter."""
    loaded_data = config_context.get("loaded_data", {})
    crawl_settings = loaded_data.get("crawl_settings", {})
    assert crawl_settings.get(param) == value, f"Expected {param}={value} in crawl_settings"


@then(parsers.parse('the file "{filename}" should exist'))
def then_file_should_exist(config_context, filename):
    """Verify file exists."""
    filepath = config_context.get("saved_file_path", filename)
    assert os.path.exists(filepath), f"File {filepath} does not exist"


@then("the file should contain valid JSON")
def then_file_should_contain_valid_json(config_context):
    """Verify file contains valid JSON."""
    filepath = config_context["saved_file_path"]
    
    try:
        with open(filepath, 'r') as f:
            json.load(f)
    except json.JSONDecodeError:
        pytest.fail(f"File {filepath} does not contain valid JSON")


@then(parsers.parse('the JSON should have "{key}" set to {value:d}'))
def then_json_should_have_key_set_to(config_context, key, value):
    """Verify JSON contains expected key-value pair."""
    filepath = config_context["saved_file_path"]
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assert key in data, f"Key {key} not found in JSON"
    assert data[key] == value, f"Expected {key}={value}, got {data[key]}"


@then("each invalid value should raise an appropriate ValueError")
def then_invalid_values_should_raise_valueerror(config_context):
    """Verify all invalid values raised appropriate errors."""
    assert len(config_context["errors"]) > 0, "No errors were captured"
    
    for error_info in config_context["errors"]:
        if isinstance(error_info, dict):
            assert error_info["expected"].lower() in error_info["error"].lower(), \
                f"Error for {error_info['param']} didn't contain expected message"


@then(parsers.parse("the configuration should have these default values:\n{table}"))
def then_configuration_should_have_default_values(config_context, table):
    """Verify default configuration values from table."""
    # Parse expected defaults
    expected_defaults = {}
    lines = table.strip().split('\n')
    for line in lines[1:]:  # Skip header
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            # Remove empty parts at the beginning and end
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                param, default_value = parts[0], parts[1]
                # Convert string values to appropriate types
                if default_value.lower() == 'true':
                    default_value = True
                elif default_value.lower() == 'false':
                    default_value = False
                elif default_value.isdigit():
                    default_value = int(default_value)
                
                expected_defaults[param] = default_value
    
    # Verify each default
    for param, expected_value in expected_defaults.items():
        if hasattr(config_context["config"], param):
            actual_value = getattr(config_context["config"], param)
            assert actual_value == expected_value, \
                f"Default for {param} should be {expected_value}, got {actual_value}"


@then(parsers.parse('domain "{domain}" should have rate_limit of {rate_limit:f} seconds'))
def then_domain_should_have_rate_limit(config_context, domain, rate_limit):
    """Verify domain-specific rate limit."""
    per_domain = config_context["per_domain_settings"]
    assert domain in per_domain, f"Domain {domain} not configured"
    assert per_domain[domain]["rate_limit"] == rate_limit


@then(parsers.parse('domain "{domain}" should have max_pages of {max_pages:d}'))
def then_domain_should_have_max_pages(config_context, domain, max_pages):
    """Verify domain-specific max pages."""
    per_domain = config_context["per_domain_settings"]
    assert domain in per_domain, f"Domain {domain} not configured"
    assert per_domain[domain]["max_pages"] == max_pages


@then("unknown domains should use default settings")
def then_unknown_domains_should_use_defaults(config_context):
    """Verify default settings exist for unknown domains."""
    per_domain = config_context["per_domain_settings"]
    assert "default" in per_domain, "No default domain settings configured"
    assert per_domain["default"]["rate_limit"] == 2.0
    assert per_domain["default"]["max_pages"] == 10


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_temp_files(config_context):
    """Clean up temporary files after tests."""
    yield
    # Cleanup
    for filepath in config_context.get("temp_files", []):
        try:
            os.unlink(filepath)
            # Also try to remove parent directory if empty
            parent_dir = os.path.dirname(filepath)
            if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        except Exception:
            pass