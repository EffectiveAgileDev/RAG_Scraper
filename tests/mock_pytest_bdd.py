"""Mock implementation of pytest-bdd for testing purposes."""

import functools

# Mock decorators and functions
def scenarios(feature_file, **kwargs):
    """Mock scenarios decorator."""
    def decorator(func):
        return func
    return decorator

def given(step_text, **kwargs):
    """Mock given decorator."""
    def decorator(func):
        return func
    return decorator

def when(step_text, **kwargs):
    """Mock when decorator.""" 
    def decorator(func):
        return func
    return decorator

def then(step_text, **kwargs):
    """Mock then decorator."""
    def decorator(func):
        return func
    return decorator

class parsers:
    """Mock parsers class."""
    @staticmethod
    def parse(pattern):
        """Mock parse function."""
        return pattern
    
    @staticmethod
    def cfparse(pattern):
        """Mock cfparse function."""
        return pattern