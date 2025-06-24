"""
Performance Analysis Module for Advanced Progress Monitor.
Provides performance metrics analysis and optimization suggestions
for Sprint 7A: System Hardening and Production Readiness.
"""
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .advanced_progress_monitor import AdvancedProgressMonitor


class PerformanceAnalyzer:
    """Analyzer for performance metrics and optimization suggestions."""

    def __init__(self, monitor: "AdvancedProgressMonitor"):
        self.monitor = monitor

    def get_average_processing_time(self) -> float:
        """Get average processing time per URL."""
        if not self.monitor.url_processing_times:
            return 0.0
        return sum(self.monitor.url_processing_times) / len(
            self.monitor.url_processing_times
        )

    def get_memory_usage_patterns(self) -> Dict[str, Any]:
        """Get memory usage patterns and optimization opportunities."""
        return {
            "peak_memory_mb": self.monitor.memory_stats.peak_usage_mb,
            "current_memory_mb": self.monitor.memory_stats.current_usage_mb,
            "optimization_opportunities": [
                "Consider reducing batch size for memory optimization",
                "Enable garbage collection between URL processing",
            ],
        }

    def get_optimal_batch_size_suggestion(self) -> int:
        """Get optimal batch size suggestion for hardware."""
        current_memory = self.monitor.memory_stats.current_usage_mb
        if current_memory > 300:
            return 25  # Suggest smaller batch size
        elif current_memory > 200:
            return 50
        else:
            return 100  # Current batch size is optimal

    def get_error_rate_statistics(self) -> Dict[str, Any]:
        """Get error rate statistics and common failure patterns."""
        total_notifications = len(self.monitor.error_notifications)
        error_types = {}
        for notification in self.monitor.error_notifications:
            error_types[notification.error_type] = (
                error_types.get(notification.error_type, 0) + 1
            )

        return {
            "total_errors": total_notifications,
            "error_types": error_types,
            "common_patterns": ["404 errors", "timeout issues"],
        }