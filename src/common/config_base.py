"""Base configuration classes and utilities."""
import os
from typing import Any, Callable, List, Dict, Optional, Union
from abc import ABC, abstractmethod


class BaseConfig(ABC):
    """Base class for configuration objects with common patterns."""

    def _get_env_value(
        self, 
        env_var: str, 
        default: Any, 
        converter: Callable[[str], Any] = str
    ) -> Any:
        """Get value from environment variable with type conversion.
        
        Args:
            env_var: Environment variable name
            default: Default value if env var not set
            converter: Function to convert string value to desired type
            
        Returns:
            Converted value or default
        """
        env_value = os.environ.get(env_var)
        if env_value is None:
            return default
        
        try:
            return converter(env_value)
        except (ValueError, TypeError):
            return default

    def _get_env_bool(self, env_var: str, default: bool) -> bool:
        """Get boolean value from environment variable.
        
        Args:
            env_var: Environment variable name
            default: Default boolean value
            
        Returns:
            Boolean value
        """
        env_value = os.environ.get(env_var, "").lower()
        if env_value in ["true", "1", "yes", "on"]:
            return True
        elif env_value in ["false", "0", "no", "off"]:
            return False
        else:
            return default

    def _get_env_int(self, env_var: str, default: int) -> int:
        """Get integer value from environment variable.
        
        Args:
            env_var: Environment variable name
            default: Default integer value
            
        Returns:
            Integer value
        """
        return self._get_env_value(env_var, default, int)

    def _get_env_float(self, env_var: str, default: float) -> float:
        """Get float value from environment variable.
        
        Args:
            env_var: Environment variable name
            default: Default float value
            
        Returns:
            Float value
        """
        return self._get_env_value(env_var, default, float)

    def _get_env_list(
        self, 
        env_var: str, 
        default: List[str], 
        separator: str = ","
    ) -> List[str]:
        """Get list value from environment variable.
        
        Args:
            env_var: Environment variable name
            default: Default list value
            separator: Character to split on
            
        Returns:
            List of strings
        """
        env_value = os.environ.get(env_var)
        if env_value is None:
            return default
        
        return [item.strip() for item in env_value.split(separator) if item.strip()]

    def _validate_positive_number(
        self, 
        value: Union[int, float], 
        name: str
    ) -> None:
        """Validate that a number is positive.
        
        Args:
            value: Number to validate
            name: Field name for error messages
            
        Raises:
            ValueError: If value is not positive
        """
        if value is None:
            raise ValueError(f"{name} cannot be None")
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number")
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")

    def _validate_range(
        self, 
        value: Union[int, float], 
        min_val: Union[int, float], 
        max_val: Union[int, float], 
        name: str
    ) -> None:
        """Validate that a number is within a range.
        
        Args:
            value: Number to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            name: Field name for error messages
            
        Raises:
            ValueError: If value is out of range
        """
        if value is None:
            raise ValueError(f"{name} cannot be None")
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number")
        if value < min_val or value > max_val:
            raise ValueError(
                f"{name} must be between {min_val} and {max_val}, got {value}"
            )

    def _validate_enum_choice(
        self, 
        value: str, 
        choices: List[str], 
        name: str
    ) -> None:
        """Validate that a value is one of the allowed choices.
        
        Args:
            value: Value to validate
            choices: List of allowed values
            name: Field name for error messages
            
        Raises:
            ValueError: If value is not in choices
        """
        if value not in choices:
            raise ValueError(
                f"{name} must be one of {choices}, got '{value}'"
            )

    def _validate_not_empty(self, value: str, name: str) -> None:
        """Validate that a string is not empty.
        
        Args:
            value: String to validate
            name: Field name for error messages
            
        Raises:
            ValueError: If value is empty or None
        """
        if not value or not value.strip():
            raise ValueError(f"{name} cannot be empty")

    def _validate_directory_exists(self, path: str, name: str) -> None:
        """Validate that a directory exists.
        
        Args:
            path: Directory path to validate
            name: Field name for error messages
            
        Raises:
            ValueError: If directory does not exist
        """
        if not os.path.exists(path):
            raise ValueError(f"{name} directory does not exist: {path}")
        if not os.path.isdir(path):
            raise ValueError(f"{name} is not a directory: {path}")

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If any configuration value is invalid
        """
        pass

    def __str__(self) -> str:
        """String representation of configuration."""
        class_name = self.__class__.__name__
        config_dict = self.to_dict()
        items = [f"{k}={v}" for k, v in config_dict.items()]
        return f"{class_name}({', '.join(items)})"

    def __repr__(self) -> str:
        """Detailed representation of configuration."""
        return self.__str__()