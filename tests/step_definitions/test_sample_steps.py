"""Sample BDD step definitions to test pytest-bdd setup."""
import pytest
from pytest_bdd import scenarios, given, when, then

# Load scenarios from the feature file
scenarios('../features/sample_test.feature')

@given('I have a working pytest-bdd setup')
def pytest_bdd_setup():
    """Verify pytest-bdd is properly configured."""
    return True

@when('I run a simple test')
def run_simple_test():
    """Execute a simple test operation."""
    return "test_executed"

@then('the test should pass')
def test_should_pass():
    """Verify the test passes successfully."""
    assert True