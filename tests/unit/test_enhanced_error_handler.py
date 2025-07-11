"""Unit tests for EnhancedErrorHandler."""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the module we're testing
try:
    from src.scraper.enhanced_error_handler import EnhancedErrorHandler
    from src.scraper.enhanced_error_handler import ErrorRecoveryStrategy
    from src.scraper.enhanced_error_handler import ErrorDetails
    from src.scraper.enhanced_error_handler import FallbackManager
except ImportError:
    EnhancedErrorHandler = None
    ErrorRecoveryStrategy = None
    ErrorDetails = None
    FallbackManager = None


class TestEnhancedErrorHandler:
    """Test cases for EnhancedErrorHandler."""

    def test_error_handler_initialization(self):
        """Test that error handler initializes correctly."""
        if EnhancedErrorHandler is None:
            pytest.fail("EnhancedErrorHandler not implemented - TDD RED phase")
        
        handler = EnhancedErrorHandler()
        assert handler is not None
        assert handler.fallback_manager is not None
        assert handler.recovery_strategies is not None
        assert handler.error_statistics is not None

    def test_error_handler_initialization_with_config(self):
        """Test error handler initialization with custom configuration."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        config = {
            'max_retries': 5,
            'retry_delay': 2.0,
            'enable_fallback': True,
            'javascript_timeout': 30.0
        }
        
        handler = EnhancedErrorHandler(config=config)
        assert handler.config == config
        assert handler.max_retries == 5
        assert handler.retry_delay == 2.0
        assert handler.enable_fallback is True

    def test_handle_javascript_error_with_retry(self):
        """Test handling JavaScript errors with retry mechanism."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("JavaScript timeout")
        url = "https://test-restaurant.com"
        
        with patch.object(handler, 'retry_manager') as mock_retry:
            mock_retry.should_retry.return_value = True
            mock_retry.get_retry_delay.return_value = 1.0
            
            result = handler.handle_javascript_error(error, url)
            
            assert result.should_retry is True
            assert result.retry_delay == 1.0
            assert result.error_type == "javascript_timeout"
            mock_retry.should_retry.assert_called_once()

    def test_handle_javascript_error_with_fallback(self):
        """Test handling JavaScript errors with fallback strategies."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("JavaScript rendering failed")
        url = "https://test-restaurant.com"
        
        with patch.object(handler, 'fallback_manager') as mock_fallback:
            mock_fallback.get_fallback_strategy.return_value = "disable_javascript"
            mock_fallback.apply_fallback.return_value = True
            
            result = handler.handle_javascript_error(error, url)
            
            assert result.fallback_strategy == "disable_javascript"
            assert result.fallback_applied is True
            mock_fallback.get_fallback_strategy.assert_called_once()
            mock_fallback.apply_fallback.assert_called_once()

    def test_handle_network_error_with_exponential_backoff(self):
        """Test handling network errors with exponential backoff."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("Connection timeout")
        url = "https://test-restaurant.com"
        retry_count = 2
        
        result = handler.handle_network_error(error, url, retry_count)
        
        assert result.should_retry is True
        assert result.retry_delay == 4.0  # 2^2 = 4 seconds for exponential backoff
        assert result.error_type == "network_timeout"
        assert result.retry_count == retry_count

    def test_handle_parsing_error_with_fallback_extraction(self):
        """Test handling parsing errors with fallback extraction."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("JSON parsing failed")
        content = "<html><body>Restaurant content</body></html>"
        
        with patch.object(handler, 'fallback_parser') as mock_parser:
            mock_parser.extract_with_heuristics.return_value = {"name": "Test Restaurant"}
            
            result = handler.handle_parsing_error(error, content)
            
            assert result.fallback_applied is True
            assert result.partial_data is not None
            assert result.partial_data["name"] == "Test Restaurant"
            mock_parser.extract_with_heuristics.assert_called_once_with(content)

    def test_handle_rate_limit_error_with_backoff(self):
        """Test handling rate limit errors with appropriate backoff."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("Rate limit exceeded")
        url = "https://test-restaurant.com"
        retry_after = 60  # Server suggests 60 seconds
        
        result = handler.handle_rate_limit_error(error, url, retry_after)
        
        assert result.should_retry is True
        assert result.retry_delay == 60  # Should respect server's retry-after
        assert result.error_type == "rate_limit"
        assert result.server_retry_after == 60

    def test_handle_memory_error_with_cleanup(self):
        """Test handling memory errors with cleanup strategies."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("Out of memory")
        
        with patch.object(handler, 'memory_manager') as mock_memory:
            mock_memory.cleanup_resources.return_value = True
            mock_memory.get_memory_usage.return_value = 85.5  # 85.5% memory usage
            
            result = handler.handle_memory_error(error)
            
            assert result.cleanup_applied is True
            assert result.memory_usage_before > 80  # High memory usage
            assert result.error_type == "memory_error"
            mock_memory.cleanup_resources.assert_called_once()

    def test_get_error_details_comprehensive(self):
        """Test getting comprehensive error details."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("Test error")
        url = "https://test-restaurant.com"
        
        with patch.object(handler, 'error_analyzer') as mock_analyzer:
            mock_analyzer.analyze_error.return_value = {
                'error_type': 'javascript_timeout',
                'error_category': 'rendering',
                'severity': 'medium',
                'suggested_actions': ['retry', 'disable_javascript'],
                'similar_errors': 5
            }
            
            details = handler.get_error_details(error, url)
            
            assert isinstance(details, ErrorDetails)
            assert details.error_type == 'javascript_timeout'
            assert details.error_category == 'rendering'
            assert details.severity == 'medium'
            assert 'retry' in details.suggested_actions
            mock_analyzer.analyze_error.assert_called_once()

    def test_error_statistics_tracking(self):
        """Test error statistics tracking."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        
        # Simulate handling multiple errors
        handler.handle_javascript_error(Exception("JS error 1"), "https://test1.com")
        handler.handle_javascript_error(Exception("JS error 2"), "https://test2.com")
        handler.handle_network_error(Exception("Network error"), "https://test3.com", 1)
        
        stats = handler.get_error_statistics()
        
        assert stats.total_errors == 3
        assert stats.javascript_errors == 2
        assert stats.network_errors == 1
        assert stats.recovery_success_rate >= 0
        assert stats.average_retry_count >= 0

    def test_fallback_strategies_prioritization(self):
        """Test fallback strategies prioritization."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error_type = "javascript_timeout"
        
        strategies = handler.get_fallback_strategies(error_type)
        
        assert len(strategies) > 0
        assert strategies[0].priority > strategies[-1].priority  # Highest priority first
        assert all(isinstance(s, ErrorRecoveryStrategy) for s in strategies)

    def test_error_recovery_success_tracking(self):
        """Test tracking of error recovery success."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        
        # Simulate successful recovery
        handler.record_recovery_success("javascript_timeout", "disable_javascript")
        handler.record_recovery_success("network_timeout", "retry")
        
        # Simulate failed recovery
        handler.record_recovery_failure("parsing_error", "fallback_extraction")
        
        stats = handler.get_recovery_statistics()
        
        assert stats.successful_recoveries == 2
        assert stats.failed_recoveries == 1
        assert stats.recovery_success_rate == 0.67  # 2/3 = 0.67

    def test_error_pattern_detection(self):
        """Test error pattern detection."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        
        # Simulate repeated errors from same domain
        for i in range(5):
            handler.handle_javascript_error(
                Exception("JS timeout"), 
                f"https://problematic-domain.com/page{i}"
            )
        
        patterns = handler.detect_error_patterns()
        
        assert len(patterns) > 0
        domain_pattern = next(p for p in patterns if p.pattern_type == "domain")
        assert domain_pattern.domain == "problematic-domain.com"
        assert domain_pattern.error_count == 5
        assert domain_pattern.error_type == "javascript_timeout"

    def test_cross_mode_error_handling_consistency(self):
        """Test error handling consistency across single-page and multi-page modes."""
        if EnhancedErrorHandler is None:
            pytest.skip("EnhancedErrorHandler not implemented yet")
        
        handler = EnhancedErrorHandler()
        error = Exception("Test error")
        url = "https://test-restaurant.com"
        
        # Test single-page mode
        single_page_result = handler.handle_error(error, url, mode="single_page")
        
        # Test multi-page mode
        multi_page_result = handler.handle_error(error, url, mode="multi_page")
        
        # Error handling should be consistent
        assert single_page_result.error_type == multi_page_result.error_type
        assert single_page_result.fallback_strategy == multi_page_result.fallback_strategy
        assert single_page_result.retry_logic == multi_page_result.retry_logic


class TestErrorRecoveryStrategy:
    """Test cases for ErrorRecoveryStrategy."""

    def test_error_recovery_strategy_initialization(self):
        """Test error recovery strategy initialization."""
        if ErrorRecoveryStrategy is None:
            pytest.skip("ErrorRecoveryStrategy not implemented yet")
        
        strategy = ErrorRecoveryStrategy(
            name="disable_javascript",
            priority=1,
            applicable_errors=["javascript_timeout", "javascript_error"],
            recovery_function=lambda: True
        )
        
        assert strategy.name == "disable_javascript"
        assert strategy.priority == 1
        assert "javascript_timeout" in strategy.applicable_errors
        assert strategy.recovery_function is not None

    def test_error_recovery_strategy_applicability(self):
        """Test error recovery strategy applicability check."""
        if ErrorRecoveryStrategy is None:
            pytest.skip("ErrorRecoveryStrategy not implemented yet")
        
        strategy = ErrorRecoveryStrategy(
            name="retry_with_delay",
            priority=2,
            applicable_errors=["network_timeout", "connection_error"],
            recovery_function=lambda: True
        )
        
        assert strategy.is_applicable("network_timeout") is True
        assert strategy.is_applicable("javascript_error") is False

    def test_error_recovery_strategy_execution(self):
        """Test error recovery strategy execution."""
        if ErrorRecoveryStrategy is None:
            pytest.skip("ErrorRecoveryStrategy not implemented yet")
        
        recovery_called = False
        
        def mock_recovery_function():
            nonlocal recovery_called
            recovery_called = True
            return True
        
        strategy = ErrorRecoveryStrategy(
            name="test_recovery",
            priority=1,
            applicable_errors=["test_error"],
            recovery_function=mock_recovery_function
        )
        
        result = strategy.execute()
        
        assert recovery_called is True
        assert result is True


class TestErrorDetails:
    """Test cases for ErrorDetails."""

    def test_error_details_initialization(self):
        """Test error details initialization."""
        if ErrorDetails is None:
            pytest.skip("ErrorDetails not implemented yet")
        
        details = ErrorDetails(
            error_type="javascript_timeout",
            error_message="JavaScript rendering timed out",
            error_category="rendering",
            severity="medium",
            suggested_actions=["retry", "disable_javascript"],
            fallback_strategies_used=True,
            retry_count=2
        )
        
        assert details.error_type == "javascript_timeout"
        assert details.error_category == "rendering"
        assert details.severity == "medium"
        assert details.retry_count == 2
        assert details.fallback_strategies_used is True

    def test_error_details_json_serialization(self):
        """Test error details JSON serialization."""
        if ErrorDetails is None:
            pytest.skip("ErrorDetails not implemented yet")
        
        details = ErrorDetails(
            error_type="network_error",
            error_message="Connection failed",
            error_category="network",
            severity="high"
        )
        
        json_data = details.to_json()
        
        assert json_data["error_type"] == "network_error"
        assert json_data["error_message"] == "Connection failed"
        assert json_data["error_category"] == "network"
        assert json_data["severity"] == "high"

    def test_error_details_user_friendly_message(self):
        """Test error details user-friendly message generation."""
        if ErrorDetails is None:
            pytest.skip("ErrorDetails not implemented yet")
        
        details = ErrorDetails(
            error_type="javascript_timeout",
            error_message="JavaScript rendering timed out after 30 seconds",
            error_category="rendering",
            severity="medium",
            suggested_actions=["retry", "disable_javascript"]
        )
        
        user_message = details.get_user_friendly_message()
        
        assert "JavaScript" in user_message
        assert "timed out" in user_message
        assert "retry" in user_message.lower()


class TestFallbackManager:
    """Test cases for FallbackManager."""

    def test_fallback_manager_initialization(self):
        """Test fallback manager initialization."""
        if FallbackManager is None:
            pytest.skip("FallbackManager not implemented yet")
        
        manager = FallbackManager()
        assert manager.fallback_strategies is not None
        assert len(manager.fallback_strategies) > 0

    def test_fallback_manager_strategy_selection(self):
        """Test fallback manager strategy selection."""
        if FallbackManager is None:
            pytest.skip("FallbackManager not implemented yet")
        
        manager = FallbackManager()
        
        strategy = manager.get_fallback_strategy("javascript_timeout")
        
        assert strategy is not None
        assert strategy.is_applicable("javascript_timeout") is True

    def test_fallback_manager_strategy_application(self):
        """Test fallback manager strategy application."""
        if FallbackManager is None:
            pytest.skip("FallbackManager not implemented yet")
        
        manager = FallbackManager()
        error_type = "javascript_timeout"
        context = {"url": "https://test.com", "retry_count": 1}
        
        with patch.object(manager, 'strategy_executor') as mock_executor:
            mock_executor.execute.return_value = True
            
            result = manager.apply_fallback(error_type, context)
            
            assert result is True
            mock_executor.execute.assert_called_once()

    def test_fallback_manager_strategy_chaining(self):
        """Test fallback manager strategy chaining."""
        if FallbackManager is None:
            pytest.skip("FallbackManager not implemented yet")
        
        manager = FallbackManager()
        
        # Test that if first strategy fails, second strategy is tried
        def first_strategy_fails():
            return False
        
        def second_strategy_succeeds():
            return True
        
        manager.add_strategy("first", first_strategy_fails, priority=1)
        manager.add_strategy("second", second_strategy_succeeds, priority=2)
        
        result = manager.apply_fallback_chain("test_error")
        
        assert result is True