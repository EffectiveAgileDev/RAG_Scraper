"""Base class for sample code generators."""

from typing import List
from abc import ABC, abstractmethod

from .integration_config import FRAMEWORK_CONFIGS


class BaseSampleGenerator(ABC):
    """Base class for sample code generators."""
    
    def __init__(self, framework: str, version: str = "1.0.0"):
        self.framework = framework
        self.version = version
        self.config = FRAMEWORK_CONFIGS.get(framework, {})
    
    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate sample code."""
        pass
    
    def _format_header(self, title: str, description: str) -> str:
        """Generate header comment."""
        return f'''"""
{title}
{description}

Generated for RAG_Scraper version {self.version}
Framework: {self.framework}
"""

'''
    
    def _format_imports(self, imports: List[str]) -> str:
        """Format import statements."""
        return '\n'.join(imports) + '\n\n'
    
    def _format_class_header(self, class_name: str, description: str) -> str:
        """Format class definition with docstring."""
        return f'''class {class_name}:
    """{description}"""
    
'''