"""JavaScript rendering configuration."""

from dataclasses import dataclass


@dataclass
class JavaScriptConfig:
    """Configuration for JavaScript rendering and browser automation."""
    
    enable_javascript_rendering: bool = False
    javascript_timeout: int = 30
    enable_popup_detection: bool = True
    popup_handling_strategy: str = "auto"  # 'auto', 'skip', 'manual'
    enable_browser_automation: bool = False  # Enable Playwright browser automation
    browser_type: str = "chromium"  # 'chromium', 'firefox', 'webkit'
    headless_browser: bool = True
    
    def __post_init__(self):
        """Validate JavaScript configuration options."""
        if self.javascript_timeout <= 0:
            raise ValueError("javascript_timeout must be positive")
        
        if self.popup_handling_strategy not in ['auto', 'skip', 'manual']:
            raise ValueError("popup_handling_strategy must be 'auto', 'skip', or 'manual'")
        
        if self.browser_type not in ['chromium', 'firefox', 'webkit']:
            raise ValueError("browser_type must be 'chromium', 'firefox', or 'webkit'")
    
    def is_browser_automation_enabled(self) -> bool:
        """Check if browser automation should be used."""
        return self.enable_browser_automation or self.enable_javascript_rendering
    
    def get_browser_options(self) -> dict:
        """Get browser configuration options."""
        return {
            "headless": self.headless_browser,
            "timeout": self.javascript_timeout * 1000,  # Convert to milliseconds
            "browser_type": self.browser_type
        }
    
    def should_handle_popups(self) -> bool:
        """Check if popup handling is enabled."""
        return self.enable_popup_detection and self.popup_handling_strategy != 'skip'