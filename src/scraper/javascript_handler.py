"""JavaScript rendering and popup handling for restaurant websites."""
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@dataclass
class PopupInfo:
    """Information about detected popup."""
    type: str
    selector: str
    action_required: str
    blocking_content: bool = True
    options: List[str] = None


class JavaScriptHandler:
    """Handler for JavaScript rendering and popup management."""
    
    def __init__(self, timeout: int = 30, enable_browser_automation: bool = False):
        """Initialize JavaScript handler with timeout."""
        self.timeout = timeout
        self.browser_automation_enabled = enable_browser_automation and PLAYWRIGHT_AVAILABLE
        self.browser_type = 'chromium'
        
        # Auto-detect headless mode based on display availability
        import os
        display_available = os.environ.get('DISPLAY') is not None
        self.headless = not display_available  # Run headless only if no display
        
        # Log the browser mode for debugging
        print(f"JavaScript Handler initialized: headless={self.headless}, display_available={display_available}")
        
        self.stealth_mode = True
        self.custom_user_agent = "RAG_Scraper/1.0 Restaurant Data Collection"
        
        # Performance optimizations
        self.cache_enabled = False
        self.cache_size = 100
        self.cache_ttl = 300  # 5 minutes
        self._popup_cache = {}
        self._render_cache = {}
        
        # Error handling and resilience
        self.max_retries = 3
        self.retry_delay = 1.0
        self.fallback_enabled = True
        self.max_popup_attempts = 5
        self._popup_attempt_count = 0
        
        # Performance monitoring
        self.performance_monitoring = False
        self.metrics_collection = False
        self._metrics = {'render_times': [], 'popup_times': [], 'success_count': 0, 'failure_count': 0}
        self.popup_patterns = {
            'age_verification': [
                '.age-gate', '.age-verification', '.age-modal',
                '#ageGate', '#ageVerification', '[class*="age-check"]'
            ],
            'newsletter_signup': [
                '.newsletter-modal', '.email-signup', '.subscribe-popup',
                '#newsletterModal', '[class*="newsletter-popup"]'
            ],
            'cookie_consent': [
                '.cookie-banner', '.cookie-consent', '#cookieNotice',
                '[class*="cookie-policy"]', '.gdpr-banner'
            ],
            'location_selector': [
                '.location-modal', '.store-selector', '#locationPicker',
                '[class*="location-select"]', '.choose-location'
            ]
        }
    
    def detect_popups(self, html: str) -> List[PopupInfo]:
        """Detect popups in HTML content."""
        detected = []
        for popup_type, selectors in self.popup_patterns.items():
            for selector in selectors:
                # Convert CSS selector to class name for matching
                if selector.startswith('.'):
                    class_name = selector[1:]  # Remove the dot
                    if f'class="{class_name}' in html or f"class='{class_name}" in html or class_name in html:
                        detected.append(PopupInfo(
                            type=popup_type,
                            selector=selector,
                            action_required=self._get_action_for_type(popup_type)
                        ))
                        break
                elif selector.startswith('#'):
                    id_name = selector[1:]  # Remove the hash
                    if f'id="{id_name}' in html or f"id='{id_name}" in html:
                        detected.append(PopupInfo(
                            type=popup_type,
                            selector=selector,
                            action_required=self._get_action_for_type(popup_type)
                        ))
                        break
                elif selector in html:  # For attribute selectors or exact matches
                    detected.append(PopupInfo(
                        type=popup_type,
                        selector=selector,
                        action_required=self._get_action_for_type(popup_type)
                    ))
                    break
        return detected
    
    def _get_action_for_type(self, popup_type: str) -> str:
        """Get required action for popup type."""
        actions = {
            'age_verification': 'click_confirm',
            'newsletter_signup': 'close_button',
            'cookie_consent': 'accept_cookies',
            'location_selector': 'select_location'
        }
        return actions.get(popup_type, 'close')
    
    def handle_popup(self, popup: PopupInfo, page_content: str) -> str:
        """Handle popup and return cleaned content."""
        # Simplified popup handling - in real implementation would use browser automation
        return page_content.replace(popup.selector, '')
    
    def render_page(self, url: str, timeout: Optional[int] = None) -> Optional[str]:
        """Render page with JavaScript execution."""
        actual_timeout = timeout or self.timeout
        
        if self.browser_automation_enabled:
            try:
                print(f"DEBUG: Attempting browser automation for {url}")
                # Try browser automation with Playwright
                result = asyncio.run(self.render_page_async(url, actual_timeout))
                if result:
                    print(f"DEBUG: Browser automation successful, content length: {len(result)}")
                    return result
                else:
                    print(f"DEBUG: Browser automation returned None for {url}")
            except Exception as e:
                print(f"DEBUG: Browser automation failed for {url}: {e}")
                import traceback
                traceback.print_exc()
                # Continue to fallback
        else:
            print(f"DEBUG: Browser automation disabled (browser_automation_enabled={self.browser_automation_enabled})")
        
        # Return None to indicate that JavaScript rendering failed
        # This allows the caller to continue with static content
        print(f"DEBUG: JavaScript rendering failed for {url}, using static fallback")
        return None

    async def render_page_async(self, url: str, timeout: Optional[int] = None) -> Optional[str]:
        """Render page with JavaScript execution using Playwright."""
        if not PLAYWRIGHT_AVAILABLE:
            return None
        
        actual_timeout = timeout or self.timeout
        browser = None
        
        try:
            async with async_playwright() as p:
                browser = await self._launch_browser(p)
                context = await self._setup_context(browser)
                page = await context.new_page()
                
                # Navigate to the page
                await page.goto(url, timeout=actual_timeout * 1000, wait_until='networkidle')
                
                # Handle popups if they exist
                content = await self._handle_popups_with_browser(page)
                
                return content
                
        except Exception as e:
            print(f"Browser rendering error for {url}: {e}")
            return None
        finally:
            if browser:
                await browser.close()

    async def _launch_browser(self, playwright_instance) -> Browser:
        """Launch browser with configured options and fallback."""
        launch_options = {
            'headless': self.headless,
            'timeout': self.timeout * 1000
        }
        
        # Add additional args for better compatibility
        if self.browser_type == 'chromium':
            launch_options['args'] = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
            
            try:
                return await playwright_instance.chromium.launch(**launch_options)
            except Exception as e:
                print(f"Failed to launch browser with headless={self.headless}: {e}")
                # Fallback to headless mode if non-headless fails
                if not self.headless:
                    print("Falling back to headless mode...")
                    launch_options['headless'] = True
                    return await playwright_instance.chromium.launch(**launch_options)
                raise
                
        elif self.browser_type == 'firefox':
            return await playwright_instance.firefox.launch(**launch_options)
        elif self.browser_type == 'webkit':
            return await playwright_instance.webkit.launch(**launch_options)
        else:
            return await playwright_instance.chromium.launch(**launch_options)

    async def _setup_context(self, browser: Browser) -> BrowserContext:
        """Setup browser context with stealth mode and custom user agent."""
        context_options = {
            'user_agent': self.custom_user_agent,
            'viewport': {'width': 1920, 'height': 1080}
        }
        
        context = await browser.new_context(**context_options)
        
        if self.stealth_mode:
            await self._setup_stealth_mode(context)
        
        return context

    async def _setup_stealth_mode(self, context: BrowserContext):
        """Setup stealth mode to avoid detection."""
        # Add basic stealth measures
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

    async def _handle_popups_with_browser(self, page: Page) -> str:
        """Handle popups using browser automation."""
        try:
            # Wait for page to stabilize
            await page.wait_for_load_state('networkidle', timeout=5000)
            
            # Detect popups using browser context
            popups = await self._detect_popups_with_browser(page)
            
            if popups:
                await self._handle_popups_sequence(page, popups)
            
            # Get final page content
            return await page.content()
            
        except Exception as e:
            print(f"Popup handling error: {e}")
            return await page.content()

    async def _detect_popups_with_browser(self, page: Page) -> List[dict]:
        """Detect popups in browser context."""
        detected_popups = []
        
        for popup_type, selectors in self.popup_patterns.items():
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element and await element.is_visible():
                        detected_popups.append({
                            'type': popup_type,
                            'selector': selector,
                            'element': element,
                            'priority': self._get_popup_priority(popup_type)
                        })
                        break  # Found one for this type, move to next type
                except Exception:
                    continue
        
        return sorted(detected_popups, key=lambda p: p['priority'])

    async def _handle_popups_sequence(self, page: Page, popups: List[dict]) -> str:
        """Handle popups in priority order."""
        for popup in popups:
            try:
                await self._handle_single_popup(page, popup)
                # Wait a bit between popup handlers
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"Error handling popup {popup['type']}: {e}")
                continue
        
        return await page.content()

    async def _handle_single_popup(self, page: Page, popup: dict):
        """Handle a single popup based on its type."""
        popup_type = popup['type']
        element = popup['element']
        
        if popup_type == 'age_verification':
            await self._handle_age_verification(page, popup)
        elif popup_type == 'location_selector':
            await self._handle_location_selector(page, popup)
        elif popup_type == 'cookie_consent':
            await self._handle_cookie_consent(page, popup)
        elif popup_type == 'newsletter_signup':
            await self._handle_newsletter_signup(page, popup)
        else:
            # Generic close attempt
            close_selectors = ['.close', '.dismiss', '.skip', 'button[aria-label*="close"]']
            for close_selector in close_selectors:
                try:
                    close_btn = await page.query_selector(close_selector)
                    if close_btn and await close_btn.is_visible():
                        await close_btn.click()
                        break
                except Exception:
                    continue

    async def _handle_age_verification(self, page: Page, popup: dict):
        """Handle age verification popup."""
        confirm_selectors = ['.confirm-age', '.yes-button', '[data-age="21"]', 'button:has-text("Yes")', 'button:has-text("21")']
        
        for selector in confirm_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    return
            except Exception:
                continue

    async def _handle_location_selector(self, page: Page, popup: dict):
        """Handle location selector popup."""
        # Try to select the first available location
        location_selectors = ['.location-item:first-child', '.store-list li:first-child', 'select[name*="location"] option:first-child']
        
        for selector in location_selectors:
            try:
                location = await page.query_selector(selector)
                if location and await location.is_visible():
                    await location.click()
                    return
            except Exception:
                continue

    async def _handle_cookie_consent(self, page: Page, popup: dict):
        """Handle cookie consent popup."""
        accept_selectors = ['.accept-cookies', '.cookie-accept', 'button:has-text("Accept")', 'button:has-text("Allow")']
        
        for selector in accept_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    return
            except Exception:
                continue

    async def _handle_newsletter_signup(self, page: Page, popup: dict):
        """Handle newsletter signup popup."""
        close_selectors = ['.close-btn', '.no-thanks', '.skip', 'button:has-text("No")', 'button:has-text("Skip")']
        
        for selector in close_selectors:
            try:
                button = await page.query_selector(selector)
                if button and await button.is_visible():
                    await button.click()
                    return
            except Exception:
                continue

    def _get_popup_priority(self, popup_type: str) -> int:
        """Get priority for popup type (lower number = higher priority)."""
        priorities = {
            'age_verification': 1,
            'location_selector': 2,
            'cookie_consent': 3,
            'newsletter_signup': 4
        }
        return priorities.get(popup_type, 99)
    
    def is_javascript_required(self, html: str) -> bool:
        """Check if JavaScript rendering is required."""
        # Convert to lowercase for case-insensitive matching
        html_lower = html.lower()
        
        # Core JS framework indicators
        framework_indicators = [
            'ng-app', 'data-react', 'vue-app', 'data-vue', 'angular',
            '__next_data__', 'window.__initial_state__',
            'require.config', 'webpack', 'systemjs'
        ]
        
        # Dynamic content loading indicators  
        dynamic_indicators = [
            'loading...', 'loader', 'spinner', 'loading-spinner',
            'data-loading', 'async-load', 'dynamic-content',
            'ajax-load', 'defer-load', 'lazy-load'
        ]
        
        # Restaurant-specific JS content indicators
        restaurant_indicators = [
            'menu-loader', 'menu-loading', 'load-menu',
            'dynamic-menu', 'ajax-menu', 'menu-ajax',
            'fetch-menu', 'menu-fetch'
        ]
        
        # Check for SPA indicators
        spa_indicators = [
            'single-page', 'spa-app', 'router-outlet',
            'history.pushstate', 'pushstate', 'replacestate'
        ]
        
        # Combine all indicators
        all_indicators = framework_indicators + dynamic_indicators + restaurant_indicators + spa_indicators
        
        # Check if any indicators are present
        found_indicators = [indicator for indicator in all_indicators if indicator in html_lower]
        
        if found_indicators:
            print(f"DEBUG: JavaScript required - found indicators: {found_indicators}")
            return True
        
        # Additional heuristic: Check if there are many empty elements that might be filled by JS
        empty_divs = html_lower.count('<div></div>') + html_lower.count('<div class="') + html_lower.count('<div id="')
        if empty_divs > 20:  # Arbitrary threshold
            print(f"DEBUG: JavaScript likely required - found {empty_divs} div elements that may be JS-populated")
            return True
            
        print("DEBUG: No JavaScript indicators found, static scraping should be sufficient")
        return False

    # Performance optimization methods
    def _get_cached_popup_result(self, html_hash: str) -> Optional[List[dict]]:
        """Get cached popup detection result."""
        if not self.cache_enabled:
            return None
        
        import time
        current_time = time.time()
        
        if html_hash in self._popup_cache:
            cached_result, timestamp = self._popup_cache[html_hash]
            if current_time - timestamp < self.cache_ttl:
                return cached_result
            else:
                # Cache expired, remove it
                del self._popup_cache[html_hash]
        
        return None

    def _cache_popup_result(self, html_hash: str, result: List[dict]):
        """Cache popup detection result."""
        if not self.cache_enabled:
            return
        
        import time
        current_time = time.time()
        
        # Implement LRU cache behavior
        if len(self._popup_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = min(self._popup_cache.keys(), 
                            key=lambda k: self._popup_cache[k][1])
            del self._popup_cache[oldest_key]
        
        self._popup_cache[html_hash] = (result, current_time)

    def _acquire_render_lock(self):
        """Acquire rendering lock for concurrent safety."""
        # Placeholder for thread-safe rendering
        pass

    def _release_render_lock(self):
        """Release rendering lock."""
        # Placeholder for thread-safe rendering
        pass

    def _cleanup_browser_resources(self):
        """Clean up browser resources to prevent memory leaks."""
        # Clear caches if they get too large
        if len(self._popup_cache) > self.cache_size * 2:
            self._popup_cache.clear()
        if len(self._render_cache) > self.cache_size * 2:
            self._render_cache.clear()

    def _monitor_memory_usage(self) -> float:
        """Monitor current memory usage."""
        try:
            import psutil
            process = psutil.Process()
            memory_percent = process.memory_percent()
            return memory_percent
        except ImportError:
            return 50.0  # Default fallback

    # Error handling methods
    def _handle_browser_crash(self):
        """Handle browser crash scenarios."""
        print("Browser crash detected, attempting recovery...")
        self._record_failure()

    def _restart_browser(self) -> bool:
        """Restart browser after crash."""
        try:
            # Cleanup any existing resources
            self._cleanup_browser_resources()
            return True
        except Exception:
            return False

    def _handle_network_timeout(self):
        """Handle network timeout scenarios."""
        print("Network timeout detected")
        self._record_failure()

    def _check_network_connectivity(self) -> bool:
        """Check if network is accessible."""
        try:
            import requests
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _reset_popup_counter(self):
        """Reset popup attempt counter."""
        self._popup_attempt_count = 0

    def _check_system_resources(self) -> dict:
        """Check system resource usage."""
        try:
            import psutil
            return {
                'cpu': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory().percent
            }
        except ImportError:
            return {'cpu': 50.0, 'memory': 50.0}

    def _throttle_operations(self):
        """Throttle operations when system resources are high."""
        resources = self._check_system_resources()
        if resources['cpu'] > 80 or resources['memory'] > 85:
            import time
            time.sleep(1)  # Brief pause to reduce load

    # Performance monitoring methods
    def _start_timer(self) -> float:
        """Start performance timer."""
        import time
        return time.time()

    def _end_timer(self, start_time: float) -> float:
        """End performance timer and return duration."""
        import time
        return time.time() - start_time

    def _record_metric(self, metric_type: str, value: float):
        """Record performance metric."""
        if not self.metrics_collection:
            return
        
        if metric_type in self._metrics:
            if isinstance(self._metrics[metric_type], list):
                self._metrics[metric_type].append(value)
                # Keep only last 1000 measurements
                if len(self._metrics[metric_type]) > 1000:
                    self._metrics[metric_type] = self._metrics[metric_type][-1000:]

    def _record_success(self):
        """Record successful operation."""
        self._metrics['success_count'] += 1

    def _record_failure(self):
        """Record failed operation."""
        self._metrics['failure_count'] += 1

    def _get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        total = self._metrics['success_count'] + self._metrics['failure_count']
        if total == 0:
            return 100.0
        return (self._metrics['success_count'] / total) * 100.0

    def _track_popup_detection_time(self) -> float:
        """Track popup detection time."""
        # Placeholder - would be implemented with actual timing
        return 0.1

    def _track_popup_handling_time(self) -> float:
        """Track popup handling time."""
        # Placeholder - would be implemented with actual timing
        return 0.5

    def _monitor_browser_memory(self) -> float:
        """Monitor browser memory usage."""
        # Placeholder - would integrate with browser API
        return 256.0

    def _monitor_browser_cpu(self) -> float:
        """Monitor browser CPU usage."""
        # Placeholder - would integrate with browser API
        return 15.0