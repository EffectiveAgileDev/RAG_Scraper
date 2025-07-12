"""Settings storage functionality for RAG_Scraper."""
from typing import Dict, Any, Optional
from flask import session


class SinglePageSettingsStorage:
    """Handles storage and retrieval of single-page mode settings."""
    
    def __init__(self):
        """Initialize single-page settings storage."""
        self.storage_key = 'single_page_settings'
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings for single-page mode.
        
        Returns:
            Dictionary of default single-page settings
        """
        return {
            'requestTimeout': 30,
            'enableJavaScript': False,
            'followRedirects': True,
            'respectRobotsTxt': True,
            'concurrentRequests': 1,  # Conservative for single page
            'jsTimeout': 30
        }
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate single-page settings.
        
        Args:
            settings: Dictionary of settings to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate request timeout
        request_timeout = settings.get('requestTimeout', 30)
        if not isinstance(request_timeout, int) or request_timeout < 5 or request_timeout > 300:
            return False
        
        # Validate concurrent requests (should be lower for single page)
        concurrent_requests = settings.get('concurrentRequests', 1)
        if not isinstance(concurrent_requests, int) or concurrent_requests < 1 or concurrent_requests > 5:
            return False
        
        # Validate JS timeout
        js_timeout = settings.get('jsTimeout', 30)
        if not isinstance(js_timeout, int) or js_timeout < 5 or js_timeout > 120:
            return False
        
        return True
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save single-page settings to session storage.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.validate_settings(settings):
                session[self.storage_key] = settings
                return True
            return False
        except Exception:
            return False
    
    def load_settings(self) -> Optional[Dict[str, Any]]:
        """Load single-page settings from session storage.
        
        Returns:
            Dictionary of saved settings or None
        """
        try:
            return session.get(self.storage_key)
        except Exception:
            return None


class MultiPageSettingsStorage:
    """Handles storage and retrieval of multi-page mode settings."""
    
    def __init__(self):
        """Initialize multi-page settings storage."""
        self.storage_key = 'multi_page_settings'
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings for multi-page mode.
        
        Returns:
            Dictionary of default multi-page settings
        """
        return {
            'maxPages': 50,
            'crawlDepth': 2,
            'rateLimit': 1000,
            'enableJavaScript': False,
            'enablePageDiscovery': True,
            'respectRobotsTxt': True,
            'includePatterns': 'menu,food,restaurant',
            'excludePatterns': 'admin,login,cart',
            'concurrentRequests': 5,
            'requestTimeout': 30
        }
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate multi-page settings.
        
        Args:
            settings: Dictionary of settings to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate max pages
        max_pages = settings.get('maxPages', 50)
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 500:
            return False
        
        # Validate crawl depth
        crawl_depth = settings.get('crawlDepth', 2)
        if not isinstance(crawl_depth, int) or crawl_depth < 1 or crawl_depth > 5:
            return False
        
        # Validate rate limit
        rate_limit = settings.get('rateLimit', 1000)
        if not isinstance(rate_limit, int) or rate_limit < 100 or rate_limit > 10000:
            return False
        
        # Validate concurrent requests
        concurrent_requests = settings.get('concurrentRequests', 5)
        if not isinstance(concurrent_requests, int) or concurrent_requests < 1 or concurrent_requests > 10:
            return False
        
        # Validate request timeout
        request_timeout = settings.get('requestTimeout', 30)
        if not isinstance(request_timeout, int) or request_timeout < 5 or request_timeout > 300:
            return False
        
        return True
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save multi-page settings to session storage.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.validate_settings(settings):
                session[self.storage_key] = settings
                return True
            return False
        except Exception:
            return False
    
    def load_settings(self) -> Optional[Dict[str, Any]]:
        """Load multi-page settings from session storage.
        
        Returns:
            Dictionary of saved settings or None
        """
        try:
            return session.get(self.storage_key)
        except Exception:
            return None


class SettingsStorage:
    """Handles storage and retrieval of user settings."""
    
    def __init__(self):
        """Initialize settings storage."""
        pass
    
    def gather_settings(self, elements: Dict[str, Any]) -> Dict[str, Any]:
        """Gather current settings from form elements.
        
        Args:
            elements: Dictionary of form element values
            
        Returns:
            Dictionary of settings
        """
        settings = {
            'scrapingMode': elements.get('scrapingMode', 'single'),
            'aggregationMode': elements.get('fileMode', 'single'),
            'outputFormat': elements.get('fileFormat', 'text'),
            'maxPages': int(elements.get('maxPages', '50')),
            'crawlDepth': int(elements.get('crawlDepth', '2')),
            'includePatterns': elements.get('includePatterns', 'menu,food,restaurant'),
            'excludePatterns': elements.get('excludePatterns', 'admin,login,cart'),
            'rateLimit': int(elements.get('rateLimit', '1000')),
            'enableJavaScript': bool(elements.get('enableJavaScript', False)),
            'respectRobotsTxt': bool(elements.get('respectRobotsTxt', True))
        }
        return settings
    
    def apply_settings(self, settings: Dict[str, Any], form: Any) -> None:
        """Apply saved settings to form.
        
        Args:
            settings: Dictionary of settings to apply
            form: Form object to update
        """
        if hasattr(form, 'set_scraping_mode'):
            form.set_scraping_mode(settings.get('scrapingMode', 'single'))
        if hasattr(form, 'set_aggregation_mode'):
            form.set_aggregation_mode(settings.get('aggregationMode', 'single'))
        if hasattr(form, 'set_output_format'):
            form.set_output_format(settings.get('outputFormat', 'text'))
        if hasattr(form, 'set_max_pages'):
            form.set_max_pages(settings.get('maxPages', 50))
        if hasattr(form, 'set_crawl_depth'):
            form.set_crawl_depth(settings.get('crawlDepth', 2))
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings.
        
        Returns:
            Dictionary of default settings
        """
        return {
            'scrapingMode': 'single',
            'aggregationMode': 'single',
            'outputFormat': 'text',
            'maxPages': 50,
            'crawlDepth': 2,
            'includePatterns': 'menu,food,restaurant',
            'excludePatterns': 'admin,login,cart',
            'rateLimit': 1000,
            'enableJavaScript': False,
            'respectRobotsTxt': True
        }
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate settings.
        
        Args:
            settings: Dictionary of settings to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Validate scraping mode
        if settings.get('scrapingMode') not in ['single', 'multi']:
            return False
        
        # Validate aggregation mode
        if settings.get('aggregationMode') not in ['single', 'multiple']:
            return False
        
        # Validate output format
        if settings.get('outputFormat') not in ['text', 'pdf', 'json']:
            return False
        
        # Validate numeric ranges
        max_pages = settings.get('maxPages', 50)
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 500:
            return False
        
        crawl_depth = settings.get('crawlDepth', 2)
        if not isinstance(crawl_depth, int) or crawl_depth < 1 or crawl_depth > 5:
            return False
        
        rate_limit = settings.get('rateLimit', 1000)
        if not isinstance(rate_limit, int) or rate_limit < 100 or rate_limit > 10000:
            return False
        
        return True
    
    def load_settings(self) -> Optional[Dict[str, Any]]:
        """Load settings from storage.
        
        Note: This is a placeholder for server-side storage.
        Actual implementation would use session storage or database.
        
        Returns:
            Dictionary of saved settings or None
        """
        # In a real implementation, this would load from session or database
        return None
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save settings to storage.
        
        Note: This is a placeholder for server-side storage.
        Actual implementation would use session storage or database.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if successful, False otherwise
        """
        # In a real implementation, this would save to session or database
        return True