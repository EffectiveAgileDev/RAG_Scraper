"""
Progress Monitor Configuration - Extracted configuration and setup methods.
This class handles all configuration settings for the AdvancedProgressMonitor.
"""
from typing import Dict, Any, Optional, List


class ProgressMonitorConfig:
    """
    Configuration management for AdvancedProgressMonitor.
    
    Handles all configuration settings including monitoring options,
    display formats, warning thresholds, and feature toggles.
    """

    def __init__(self):
        """Initialize configuration with default values."""
        # Feature toggles
        self.detailed_logging_enabled = False
        self.memory_monitoring_enabled = False
        self.page_notifications_enabled = False
        self.time_estimation_enabled = False
        self.accuracy_tracking_enabled = False
        self.thread_monitoring_enabled = False
        
        # Display and format settings
        self.time_display_format = "human_readable"
        
        # Configuration objects
        self.memory_monitoring_config = {
            "update_interval": 5.0,
            "warning_threshold": 400.0,
            "enable_warnings": True,
            "enable_gc": False
        }
        
        self.warning_configuration = {
            "memory_threshold": 400.0,
            "time_threshold": 300.0,
            "error_threshold": 10
        }
        
        self.thread_monitoring_config = {
            "max_threads": 4,
            "enable_individual_tracking": True,
            "track_operations": True
        }

        # Valid options for validation
        self._valid_time_formats = [
            "human_readable", "iso_8601", "seconds", "verbose", "compact"
        ]

    def enable_detailed_logging(self, enabled: bool = True):
        """
        Enable or disable detailed logging.
        
        Args:
            enabled: Whether to enable detailed logging
        """
        self.detailed_logging_enabled = enabled

    def enable_memory_monitoring(self, enabled: bool = True, config: Optional[Dict[str, Any]] = None):
        """
        Enable or disable memory monitoring.
        
        Args:
            enabled: Whether to enable memory monitoring
            config: Optional memory monitoring configuration
        """
        self.memory_monitoring_enabled = enabled
        if config is not None:
            self.memory_monitoring_config = config

    def enable_page_notifications(self, enabled: bool = True):
        """
        Enable or disable page notifications.
        
        Args:
            enabled: Whether to enable page notifications
        """
        self.page_notifications_enabled = enabled

    def enable_time_estimation(self, enabled: bool = True):
        """
        Enable or disable time estimation.
        
        Args:
            enabled: Whether to enable time estimation
        """
        self.time_estimation_enabled = enabled

    def set_time_display_format(self, format_type: str):
        """
        Set the time display format.
        
        Args:
            format_type: Time display format (human_readable, iso_8601, seconds, verbose, compact)
        """
        self.time_display_format = format_type

    def enable_accuracy_tracking(self, enabled: bool = True):
        """
        Enable or disable accuracy tracking for time estimation.
        
        Args:
            enabled: Whether to enable accuracy tracking
        """
        self.accuracy_tracking_enabled = enabled

    def set_memory_monitoring_config(self, config: Dict[str, Any]):
        """
        Set memory monitoring configuration.
        
        Args:
            config: Memory monitoring configuration dictionary
        """
        self.memory_monitoring_config = config

    def set_warning_configuration(self, config: Dict[str, Any]):
        """
        Set warning configuration.
        
        Args:
            config: Warning configuration dictionary
        """
        self.warning_configuration = config

    def enable_thread_monitoring(self, enabled: bool = True, max_threads: Optional[int] = None):
        """
        Enable or disable thread monitoring.
        
        Args:
            enabled: Whether to enable thread monitoring
            max_threads: Maximum number of threads to monitor
        """
        self.thread_monitoring_enabled = enabled
        if max_threads is not None:
            self.thread_monitoring_config["max_threads"] = max_threads

    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration as dictionary.
        
        Returns:
            Dictionary containing all configuration settings
        """
        return {
            "detailed_logging_enabled": self.detailed_logging_enabled,
            "memory_monitoring_enabled": self.memory_monitoring_enabled,
            "page_notifications_enabled": self.page_notifications_enabled,
            "time_estimation_enabled": self.time_estimation_enabled,
            "accuracy_tracking_enabled": self.accuracy_tracking_enabled,
            "thread_monitoring_enabled": self.thread_monitoring_enabled,
            "time_display_format": self.time_display_format,
            "memory_monitoring_config": self.memory_monitoring_config.copy(),
            "warning_configuration": self.warning_configuration.copy(),
            "thread_monitoring_config": self.thread_monitoring_config.copy()
        }

    def apply_configuration(self, config: Dict[str, Any]):
        """
        Apply configuration from dictionary.
        
        Args:
            config: Configuration dictionary to apply
        """
        # Apply simple boolean and string settings
        if "detailed_logging_enabled" in config:
            self.detailed_logging_enabled = config["detailed_logging_enabled"]
        if "memory_monitoring_enabled" in config:
            self.memory_monitoring_enabled = config["memory_monitoring_enabled"]
        if "page_notifications_enabled" in config:
            self.page_notifications_enabled = config["page_notifications_enabled"]
        if "time_estimation_enabled" in config:
            self.time_estimation_enabled = config["time_estimation_enabled"]
        if "accuracy_tracking_enabled" in config:
            self.accuracy_tracking_enabled = config["accuracy_tracking_enabled"]
        if "thread_monitoring_enabled" in config:
            self.thread_monitoring_enabled = config["thread_monitoring_enabled"]
        if "time_display_format" in config:
            self.time_display_format = config["time_display_format"]
        
        # Apply complex configuration objects
        if "memory_monitoring_config" in config:
            self.memory_monitoring_config.update(config["memory_monitoring_config"])
        if "warning_configuration" in config:
            self.warning_configuration.update(config["warning_configuration"])
        if "thread_monitoring_config" in config:
            self.thread_monitoring_config.update(config["thread_monitoring_config"])

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration settings.
        
        Returns:
            Validation result with 'valid' flag and 'errors' list
        """
        errors = []
        
        # Validate time display format
        if self.time_display_format not in self._valid_time_formats:
            errors.append(
                f"Invalid time_display_format '{self.time_display_format}'. "
                f"Valid options: {', '.join(self._valid_time_formats)}"
            )
        
        # Validate memory monitoring config
        if self.memory_monitoring_enabled:
            mem_config = self.memory_monitoring_config
            if mem_config.get("update_interval", 0) <= 0:
                errors.append("Memory monitoring update_interval must be positive")
            if mem_config.get("warning_threshold", 0) <= 0:
                errors.append("Memory monitoring warning_threshold must be positive")
        
        # Validate warning configuration
        warn_config = self.warning_configuration
        if warn_config.get("memory_threshold", 0) <= 0:
            errors.append("Warning memory_threshold must be positive")
        if warn_config.get("time_threshold", 0) <= 0:
            errors.append("Warning time_threshold must be positive")
        if warn_config.get("error_threshold", 0) <= 0:
            errors.append("Warning error_threshold must be positive")
        
        # Validate thread monitoring config
        if self.thread_monitoring_enabled:
            thread_config = self.thread_monitoring_config
            if thread_config.get("max_threads", 0) <= 0:
                errors.append("Thread monitoring max_threads must be positive")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def get_feature_flags(self) -> Dict[str, bool]:
        """
        Get all feature flags as dictionary.
        
        Returns:
            Dictionary of feature flags
        """
        return {
            "detailed_logging_enabled": self.detailed_logging_enabled,
            "memory_monitoring_enabled": self.memory_monitoring_enabled,
            "page_notifications_enabled": self.page_notifications_enabled,
            "time_estimation_enabled": self.time_estimation_enabled,
            "accuracy_tracking_enabled": self.accuracy_tracking_enabled,
            "thread_monitoring_enabled": self.thread_monitoring_enabled
        }

    def reset_to_defaults(self):
        """Reset all configuration to default values."""
        self.__init__()

    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a specific feature is enabled.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            True if feature is enabled, False otherwise
        """
        feature_map = {
            "detailed_logging": self.detailed_logging_enabled,
            "memory_monitoring": self.memory_monitoring_enabled,
            "page_notifications": self.page_notifications_enabled,
            "time_estimation": self.time_estimation_enabled,
            "accuracy_tracking": self.accuracy_tracking_enabled,
            "thread_monitoring": self.thread_monitoring_enabled
        }
        return feature_map.get(feature_name, False)

    def get_enabled_features(self) -> List[str]:
        """
        Get list of enabled feature names.
        
        Returns:
            List of enabled feature names
        """
        features = []
        if self.detailed_logging_enabled:
            features.append("detailed_logging")
        if self.memory_monitoring_enabled:
            features.append("memory_monitoring")
        if self.page_notifications_enabled:
            features.append("page_notifications")
        if self.time_estimation_enabled:
            features.append("time_estimation")
        if self.accuracy_tracking_enabled:
            features.append("accuracy_tracking")
        if self.thread_monitoring_enabled:
            features.append("thread_monitoring")
        return features

    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"ProgressMonitorConfig(features={sum(self.get_feature_flags().values())}/6 enabled)"