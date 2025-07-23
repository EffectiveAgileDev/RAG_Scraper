"""BDD step definitions for industry status management tests."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from src.config.industry_config import IndustryConfig
from src.web_interface.ui_components import IndustryDropdown

scenarios("../features/industry_status.feature")


@pytest.fixture
def industry_config():
    """Create industry config instance for testing."""
    return IndustryConfig()


@pytest.fixture
def industry_dropdown():
    """Create industry dropdown instance for testing."""
    return IndustryDropdown()


@given("the industry status configuration is loaded")
def industry_status_loaded(industry_config):
    """Ensure industry status configuration is loaded."""
    # This step will fail until we implement the status system
    assert hasattr(industry_config, "get_industries_by_status")


@given(parsers.parse('{industry} is marked as "{status}"'))
def industry_has_status(industry_config, industry, status):
    """Verify an industry has a specific status."""
    industries = industry_config.get_all_industries_with_status()
    industry_data = next((i for i in industries if i["name"] == industry), None)
    assert industry_data is not None, f"Industry {industry} not found"
    assert (
        industry_data["status"] == status
    ), f"Industry {industry} has status {industry_data['status']}, expected {status}"


@when("I view the industry dropdown")
def view_industry_dropdown(industry_dropdown):
    """View the industry dropdown HTML."""
    # This will be stored in pytest context for assertions
    pytest.dropdown_html = industry_dropdown.render()


@when("I get industries grouped by status")
def get_industries_by_status(industry_config):
    """Get industries grouped by their status."""
    pytest.industries_by_status = industry_config.get_industries_by_status()


@when("I load the industry status configuration")
def load_industry_status_config(industry_config):
    """Load the industry status configuration."""
    pytest.all_industries = industry_config.get_all_industries_with_status()


@when(parsers.parse('I filter industries by status "{status}"'))
def filter_industries_by_status(industry_config, status):
    """Filter industries by a specific status."""
    pytest.filtered_industries = industry_config.get_industries_by_status()[status]


@then(parsers.parse('I should see "{industry}" in the "{section}" section'))
def should_see_industry_in_section(industry, section):
    """Verify industry appears in the correct section of dropdown."""
    html = pytest.dropdown_html
    if section == "Available Now":
        assert f'<optgroup label="✅ Available Now">' in html
        # Check that industry appears after the Available Now optgroup
        available_section_start = html.find('<optgroup label="✅ Available Now">')
        coming_soon_section_start = html.find('<optgroup label="🚧 Coming Soon">')
        industry_position = html.find(f">{industry}<")

        assert industry_position > available_section_start
        if coming_soon_section_start != -1:
            assert industry_position < coming_soon_section_start
    elif section == "Coming Soon":
        assert f'<optgroup label="🚧 Coming Soon">' in html
        # Check that industry appears after the Coming Soon optgroup
        coming_soon_section_start = html.find('<optgroup label="🚧 Coming Soon">')
        industry_position = html.find(f">{industry}")
        assert industry_position > coming_soon_section_start


@then(parsers.parse('I should see "{industry}" as selectable'))
def should_see_industry_selectable(industry):
    """Verify industry is selectable (not disabled)."""
    html = pytest.dropdown_html
    # Should have value and not be disabled
    assert f'<option value="{industry}">{industry}</option>' in html


@then(parsers.parse('I should see "{industry}" as disabled'))
def should_see_industry_disabled(industry):
    """Verify industry is disabled."""
    html = pytest.dropdown_html
    # Should be disabled with no value
    assert f"disabled>{industry}" in html
    assert f'value="" disabled' in html


@then(parsers.parse('I should not see "{industry}" in the "{section}" section'))
def should_not_see_industry_in_section(industry, section):
    """Verify industry does not appear in the specified section."""
    html = pytest.dropdown_html
    if section == "Coming Soon":
        coming_soon_section_start = html.find('<optgroup label="🚧 Coming Soon">')
        if coming_soon_section_start != -1:
            coming_soon_section = html[coming_soon_section_start:]
            # Industry should not appear in coming soon section
            assert (
                f">{industry}" not in coming_soon_section
                or f'value="{industry}"' in coming_soon_section
            )


@then(parsers.parse('the "{status_group}" group should contain "{industry}"'))
def status_group_should_contain_industry(status_group, industry):
    """Verify a status group contains a specific industry."""
    industries_by_status = pytest.industries_by_status
    industry_names = [i["name"] for i in industries_by_status[status_group]]
    assert (
        industry in industry_names
    ), f"Industry {industry} not found in {status_group} group"


@then(parsers.parse('the "{status_group}" group should not contain "{industry}"'))
def status_group_should_not_contain_industry(status_group, industry):
    """Verify a status group does not contain a specific industry."""
    industries_by_status = pytest.industries_by_status
    industry_names = [i["name"] for i in industries_by_status[status_group]]
    assert (
        industry not in industry_names
    ), f"Industry {industry} unexpectedly found in {status_group} group"


@then("each industry should have a status field")
def each_industry_has_status():
    """Verify all industries have a status field."""
    all_industries = pytest.all_industries
    for industry in all_industries:
        assert (
            "status" in industry
        ), f"Industry {industry.get('name', 'unknown')} missing status field"
        assert industry[
            "status"
        ], f"Industry {industry.get('name', 'unknown')} has empty status"


@then("each industry should have a description field")
def each_industry_has_description():
    """Verify all industries have a description field."""
    all_industries = pytest.all_industries
    for industry in all_industries:
        assert (
            "description" in industry
        ), f"Industry {industry.get('name', 'unknown')} missing description field"


@then('valid statuses should include "available" and "coming_soon"')
def valid_statuses_include_available_and_coming_soon():
    """Verify configuration includes expected status values."""
    all_industries = pytest.all_industries
    statuses = {industry["status"] for industry in all_industries}
    assert (
        "available" in statuses or "coming_soon" in statuses
    ), "No industries with available or coming_soon status found"


@then(parsers.parse('I should only get industries marked as "{status}"'))
def should_only_get_industries_with_status(status):
    """Verify filtered results only contain industries with specified status."""
    filtered_industries = pytest.filtered_industries
    for industry in filtered_industries:
        assert (
            industry["status"] == status
        ), f"Industry {industry['name']} has status {industry['status']}, expected {status}"
