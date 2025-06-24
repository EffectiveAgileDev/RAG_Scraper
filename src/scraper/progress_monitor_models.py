"""
Progress Monitor Data Models.
Contains all data classes and enums used by the Advanced Progress Monitor.
"""
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class OperationType(Enum):
    """Types of operations being monitored."""

    ANALYZING_PAGE_STRUCTURE = "Analyzing page structure"
    EXTRACTING_DATA = "Extracting data"
    PROCESSING_MENU_ITEMS = "Processing menu items"
    HANDLING_NAVIGATION = "Handling navigation"
    VALIDATING_DATA = "Validating data"
    GENERATING_OUTPUT = "Generating output"


class URLStatus(Enum):
    """Status of individual URLs in processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MonitoringUpdate:
    """Data class for monitoring updates."""

    current_url: str
    progress_percentage: float
    urls_completed: int
    urls_total: int
    current_operation: str
    memory_usage_mb: float
    estimated_time_remaining: float
    errors: List[str]
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    thread_info: Optional[Dict[str, Any]] = None
    update_interval: float = 2.0


@dataclass
class PageProgress:
    """Progress tracking for multi-page websites."""

    current_page: int
    total_pages: int
    current_url: str
    page_urls: List[str]
    completed_pages: List[str]
    failed_pages: List[str]


@dataclass
class ErrorNotification:
    """Error notification data."""

    url: str
    error_type: str
    error_message: str
    timestamp: datetime
    notification_type: str = "real_time_error"
    can_continue: bool = True


@dataclass
class MemoryStats:
    """Memory usage statistics."""

    current_usage_mb: float
    peak_usage_mb: float
    warning_threshold_mb: float = 400.0
    update_interval: float = 5.0


@dataclass
class TimeEstimation:
    """Time estimation data."""

    estimated_seconds_remaining: float
    accuracy_confidence: float
    calculation_method: str
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessStatus:
    """Overall process status."""

    is_running: bool
    is_stopped: bool
    is_paused: bool
    total_urls: int
    completed_urls: int
    failed_urls: int
    start_time: datetime
    estimated_end_time: Optional[datetime] = None