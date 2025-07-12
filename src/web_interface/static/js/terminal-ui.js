/**
 * Terminal UI - JavaScript functionality for the RAG Scraper web interface
 * Provides terminal-style user interface with matrix effects, progress monitoring,
 * form handling, API calls, and real-time UI interactions.
 */


// =============================================================================
// Global Variables and UI Element References
// =============================================================================

// Terminal UI Elements
const form = document.getElementById('scrapeForm');
const urlsInput = document.getElementById('urls');
const submitBtn = document.getElementById('submitBtn');
const validateBtn = document.getElementById('validateBtn');
const clearBtn = document.getElementById('clearBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const currentUrl = document.getElementById('currentUrl');
const timeEstimate = document.getElementById('timeEstimate');
const memoryUsage = document.getElementById('memoryUsage');
const resultsContainer = document.getElementById('resultsContainer');
const resultsContent = document.getElementById('resultsContent');
const noResults = document.getElementById('noResults');
const sitesResults = document.getElementById('sitesResults');
const urlValidation = document.getElementById('urlValidation');
const statusBar = document.querySelector('.status-bar');
const formatOptions = document.querySelectorAll('.format-option');
const dataFlow = document.querySelector('.data-flow');

let progressInterval;
let terminalEffects = true;
let isActivelyProcessing = false;
let scrapingStartTime = null;

// =============================================================================
// Help Text Functions
// =============================================================================

/**
 * Initialize help text to be collapsed by default
 */
window.initializeHelpText = function() {
    const schemaHelpStatic = document.getElementById('schema-type-help-static');
    if (schemaHelpStatic) {
        const helpContent = schemaHelpStatic.querySelector('.help-content');
        const toggleArrow = schemaHelpStatic.querySelector('.toggle-help');
        
        if (helpContent && toggleArrow) {
            helpContent.style.display = 'none'; // Force hidden with inline style
            helpContent.classList.add('hidden');
            helpContent.classList.remove('visible');
            toggleArrow.textContent = '▶';
        }
    }
};

/**
 * Toggle help text visibility for schema type information
 */
window.toggleHelpText = function() {
    console.log('toggleHelpText called');
    const schemaHelpStatic = document.getElementById('schema-type-help-static');
    console.log('schemaHelpStatic element:', schemaHelpStatic);
    if (schemaHelpStatic) {
        const helpContent = schemaHelpStatic.querySelector('.help-content');
        const toggleArrow = schemaHelpStatic.querySelector('.toggle-help');
        console.log('helpContent:', helpContent, 'toggleArrow:', toggleArrow);
        
        if (helpContent && toggleArrow) {
            if (helpContent.style.display === 'none' || helpContent.classList.contains('hidden')) {
                console.log('Showing help content');
                helpContent.style.display = 'block';
                helpContent.classList.remove('hidden');
                helpContent.classList.add('visible');
                toggleArrow.textContent = '▼';
            } else {
                console.log('Hiding help content');
                helpContent.style.display = 'none';
                helpContent.classList.add('hidden');
                helpContent.classList.remove('visible');
                toggleArrow.textContent = '▶';
            }
        }
    }
};

// =============================================================================
// Initialization and Setup Functions
// =============================================================================

/**
 * Initialize the terminal interface on DOM content load
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeTerminalEffects();
    setupFormatSelection();
    setupSliderUpdates();
    setupModeSelection();
    setupConfigDropdownHandlers();
    fixSelectDropdownStyles();
    initializeHelpText(); // Initialize help text to be collapsed by default
    
    // Also fix styles after a short delay to catch any async changes
    setTimeout(fixSelectDropdownStyles, 100);
    setTimeout(fixSelectDropdownStyles, 500);
});

/**
 * Initialize all terminal visual effects
 */
function initializeTerminalEffects() {
    // Create matrix background effect
    createMatrixEffect();
    
    // Add terminal cursor effect to inputs
    addTerminalCursorEffect();
    
    // Initialize status updates
    updateSystemStatus('SYSTEM_READY // AWAITING_TARGET_URLs');
}

/**
 * Create animated matrix-style background effect
 */
function createMatrixEffect() {
    const matrixBg = document.querySelector('.matrix-bg');
    const chars = '01';
    const columns = Math.floor(window.innerWidth / 20);
    
    for (let i = 0; i < 50; i++) {
        const char = document.createElement('div');
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        char.style.position = 'absolute';
        char.style.left = Math.random() * 100 + '%';
        char.style.top = Math.random() * 100 + '%';
        char.style.color = 'rgba(0, 255, 136, 0.1)';
        char.style.fontSize = '12px';
        char.style.fontFamily = 'JetBrains Mono, monospace';
        char.style.animation = `float ${3 + Math.random() * 4}s ease-in-out infinite`;
        matrixBg.appendChild(char);
    }
}

/**
 * Add terminal cursor animation to input fields
 */
function addTerminalCursorEffect() {
    const inputs = document.querySelectorAll('.terminal-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.animation = 'terminal-cursor 1s ease-in-out infinite';
        });
        input.addEventListener('blur', function() {
            this.style.animation = 'none';
        });
    });
}

/**
 * Fix select dropdown background color issues
 */
function fixSelectDropdownStyles() {
    // Force background color on all select elements with terminal-input class
    const selects = document.querySelectorAll('select.terminal-input');
    const bgColor = '#1a1a1a'; // var(--bg-tertiary)
    
    selects.forEach(select => {
        // Apply styles directly to ensure they override any browser defaults
        select.style.backgroundColor = bgColor;
        select.style.background = bgColor;
        
        // Also fix the industry dropdown specifically
        if (select.id === 'industry' || select.classList.contains('industry-dropdown')) {
            select.style.backgroundColor = bgColor;
            select.style.background = bgColor;
        }
        
        // Re-apply styles on focus/blur to combat any dynamic changes
        select.addEventListener('focus', function() {
            this.style.backgroundColor = bgColor;
            this.style.background = bgColor;
        });
        
        select.addEventListener('blur', function() {
            this.style.backgroundColor = bgColor;
            this.style.background = bgColor;
        });
        
        // Fix options background
        const options = select.querySelectorAll('option');
        options.forEach(option => {
            option.style.backgroundColor = bgColor;
            option.style.background = bgColor;
        });
    });
    
    // Use MutationObserver to watch for any style changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                const target = mutation.target;
                if (target.tagName === 'SELECT' && target.classList.contains('terminal-input')) {
                    // Reapply our background color if it was changed
                    if (target.style.backgroundColor !== bgColor) {
                        target.style.backgroundColor = bgColor;
                        target.style.background = bgColor;
                    }
                }
            }
        });
    });
    
    // Observe all select elements
    selects.forEach(select => {
        observer.observe(select, { attributes: true, attributeFilter: ['style'] });
    });
}

// =============================================================================
// Format and Mode Selection Handlers
// =============================================================================

/**
 * Setup format selection radio buttons and JSON field visibility
 */
function setupFormatSelection() {
    const jsonFieldSelection = document.getElementById('jsonFieldSelection');
    
    formatOptions.forEach(option => {
        option.addEventListener('click', function() {
            formatOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            
            // Show/hide JSON field selection based on format choice
            if (radio.value === 'json') {
                jsonFieldSelection.style.display = 'block';
                updateSystemStatus(`JSON_FORMAT_SELECTED // FIELD_CUSTOMIZATION_AVAILABLE`);
            } else {
                jsonFieldSelection.style.display = 'none';
                updateSystemStatus(`FORMAT_SELECTED // ${radio.value.toUpperCase()}_MODE_ACTIVE`);
            }
        });
    });
}

/**
 * Setup scraping mode selection (single vs multi-page)
 */
function setupModeSelection() {
    const modeOptions = document.querySelectorAll('.mode-option');
    const singlePageHeader = document.getElementById('singlePageHeader');
    const singlePageConfig = document.getElementById('singlePageConfig');
    const multiPageHeader = document.getElementById('multiPageHeader');
    const multiPageConfig = document.getElementById('multiPageConfig');
    
    modeOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Update active state
            modeOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            // Update radio button
            const radio = this.querySelector('input[type="radio"]');
            radio.checked = true;
            
            // Show/hide configuration panels based on mode
            const mode = radio.value;
            if (mode === 'multi') {
                // Show multi-page configuration
                multiPageHeader.style.display = 'block';
                singlePageHeader.style.display = 'none';
                // Collapse single page config
                if (singlePageConfig) {
                    singlePageConfig.classList.add('collapsed');
                    const singleExpandIcon = document.getElementById('singleConfigExpandIcon');
                    if (singleExpandIcon) singleExpandIcon.classList.remove('expanded');
                }
                // Clear single page selections to prevent cross-contamination
                clearSinglePageSelections();
                updateSystemStatus('MULTI_PAGE_MODE // ADVANCED_CRAWLING_ENABLED');
                // Update schema type display for multi-page mode
                updateSchemaTypeForMode('multi');
            } else {
                // Show single-page configuration
                singlePageHeader.style.display = 'block';
                multiPageHeader.style.display = 'none';
                // Collapse multi-page config
                if (multiPageConfig) {
                    multiPageConfig.classList.add('collapsed');
                    const multiExpandIcon = document.getElementById('configExpandIcon');
                    if (multiExpandIcon) multiExpandIcon.classList.remove('expanded');
                }
                // Clear multi-page selections to prevent cross-contamination
                clearMultiPageSelections();
                updateSystemStatus('SINGLE_PAGE_MODE // DIRECT_URL_PROCESSING');
                // Update schema type display for single-page mode
                updateSchemaTypeForMode('single');
            }
        });
    });
}

// =============================================================================
// Helper Functions for Mode Selection
// =============================================================================

/**
 * Clear all single page selections
 */
function clearSinglePageSelections() {
    // Clear single page specific inputs
    const singlePageInputs = document.querySelectorAll('#singlePageConfig input[type="checkbox"]');
    singlePageInputs.forEach(input => input.checked = false);
    
    const singlePageSelects = document.querySelectorAll('#singlePageConfig select');
    singlePageSelects.forEach(select => select.value = '');
}

/**
 * Clear all multi-page selections
 */
function clearMultiPageSelections() {
    // Clear multi-page specific inputs
    const multiPageInputs = document.querySelectorAll('#multiPageConfig input[type="checkbox"]');
    multiPageInputs.forEach(input => input.checked = false);
    
    const multiPageSelects = document.querySelectorAll('#multiPageConfig select');
    multiPageSelects.forEach(select => select.value = '');
    
    // Reset numeric inputs to defaults
    const maxPages = document.getElementById('maxPages');
    if (maxPages) maxPages.value = '50';
    
    const crawlDepth = document.getElementById('crawlDepth');
    if (crawlDepth) crawlDepth.value = '2';
}

/**
 * Update schema type display based on extraction mode
 */
function updateSchemaTypeForMode(mode) {
    const schemaDropdown = document.getElementById('schema-type-dropdown');
    const schemaHelp = document.getElementById('schema-type-help-dynamic');
    
    if (!schemaDropdown) return;
    
    // Update help text based on mode
    if (schemaHelp) {
        if (mode === 'single') {
            schemaHelp.textContent = 'Single page extraction uses focused schema for specific page content';
        } else {
            schemaHelp.textContent = 'Multi-page extraction uses comprehensive schema for entire website';
        }
    }
    
    // Trigger change event to update any dependent UI
    const event = new Event('change');
    schemaDropdown.dispatchEvent(event);
}

/**
 * Update schema type help text dynamically
 */
function updateSchemaTypeHelpText(schemaType) {
    const helpTextElement = document.getElementById('schema-type-help-dynamic');
    if (!helpTextElement) return;
    
    const mode = getSelectedScrapingMode();
    
    // Define help text based on schema type and mode
    const helpTexts = {
        'Restaurant': {
            'single': 'Standard restaurant schema - Extracts basic restaurant information from a single page',
            'multi': 'Standard restaurant schema - Comprehensive extraction across multiple pages'
        },
        'RestW': {
            'single': 'Enhanced RestW schema - Detailed extraction with location, menu, and service data from a single page',
            'multi': 'Enhanced RestW schema - Complete website analysis with structured data extraction'
        }
    };
    
    const helpText = helpTexts[schemaType]?.[mode] || 'Select a schema type for extraction';
    helpTextElement.textContent = helpText;
}

// Make function globally available
window.updateSchemaTypeHelpText = updateSchemaTypeHelpText;

/**
 * Setup configuration dropdown keyboard and click handlers
 */
function setupConfigDropdownHandlers() {
    const singlePageHeader = document.getElementById('singlePageHeader');
    const multiPageHeader = document.getElementById('multiPageHeader');
    
    // Add keyboard support for single page config
    if (singlePageHeader) {
        singlePageHeader.setAttribute('tabindex', '0');
        singlePageHeader.setAttribute('role', 'button');
        singlePageHeader.setAttribute('aria-expanded', 'false');
        
        singlePageHeader.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
                e.preventDefault();
                toggleSinglePageConfig();
            }
        });
    }
    
    // Add keyboard support for multi page config
    if (multiPageHeader) {
        multiPageHeader.setAttribute('tabindex', '0');
        multiPageHeader.setAttribute('role', 'button');
        multiPageHeader.setAttribute('aria-expanded', 'false');
        
        multiPageHeader.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
                e.preventDefault();
                toggleMultiPageConfig();
            }
        });
    }
}

// =============================================================================
// Single Page Configuration Panel Functions
// =============================================================================

/**
 * Toggle single-page configuration panel expansion
 */
function toggleSinglePageConfig() {
    const configPanel = document.getElementById('singlePageConfig');
    const expandIcon = document.getElementById('singleConfigExpandIcon');
    const header = document.getElementById('singlePageHeader');
    
    if (configPanel.classList.contains('collapsed')) {
        configPanel.classList.remove('collapsed');
        expandIcon.classList.add('expanded');
        if (header) header.setAttribute('aria-expanded', 'true');
        updateSystemStatus('SINGLE_PAGE_CONFIG // PANEL_EXPANDED');
    } else {
        configPanel.classList.add('collapsed');
        expandIcon.classList.remove('expanded');
        if (header) header.setAttribute('aria-expanded', 'false');
        updateSystemStatus('SINGLE_PAGE_CONFIG // PANEL_COLLAPSED');
    }
}

/**
 * Toggle single-page advanced options panel expansion
 */
window.toggleSinglePageAdvancedOptions = function() {
    try {
        console.log('toggleSinglePageAdvancedOptions called');
        
        const advancedPanel = document.getElementById('singleAdvancedOptionsPanel');
        const expandIcon = document.getElementById('singleAdvancedOptionsIcon');
        
        if (!advancedPanel) {
            console.error('Cannot find singleAdvancedOptionsPanel');
            return;
        }
        
        if (!expandIcon) {
            console.error('Cannot find singleAdvancedOptionsIcon');
            return;
        }
        
        console.log('Found elements, toggling...');
        
        const isCollapsed = advancedPanel.classList.contains('collapsed');
        
        if (isCollapsed) {
            // EXPAND
            advancedPanel.classList.remove('collapsed');
            advancedPanel.style.display = 'block';
            advancedPanel.style.maxHeight = '600px';
            advancedPanel.style.opacity = '1';
            advancedPanel.style.padding = '1.5rem';
            expandIcon.textContent = '▲';
            console.log('Panel expanded');
        } else {
            // COLLAPSE
            advancedPanel.classList.add('collapsed');
            advancedPanel.style.maxHeight = '0px';
            advancedPanel.style.opacity = '0';
            advancedPanel.style.padding = '0 1.5rem';
            expandIcon.textContent = '▼';
            console.log('Panel collapsed');
        }
    } catch (error) {
        console.error('Error in toggleSinglePageAdvancedOptions:', error);
        alert('Error: ' + error.message);
    }
}

// Make sure the function is available globally
window.toggleSinglePageAdvancedOptions = toggleSinglePageAdvancedOptions;

// Debug function to check if elements exist
window.checkSinglePageElements = function() {
    const panel = document.getElementById('singleAdvancedOptionsPanel');
    const icon = document.getElementById('singleAdvancedOptionsIcon');
    console.log('Element check:', {
        panel: panel,
        icon: icon,
        panelExists: !!panel,
        iconExists: !!icon,
        panelClasses: panel?.className,
        iconText: icon?.textContent
    });
    return {panel, icon};
};

// =============================================================================
// Multi-Page Configuration Panel Functions
// =============================================================================

/**
 * Toggle multi-page configuration panel expansion
 */
function toggleMultiPageConfig() {
    const configPanel = document.getElementById('multiPageConfig');
    const expandIcon = document.getElementById('configExpandIcon');
    const header = document.getElementById('multiPageHeader');
    
    if (configPanel.classList.contains('collapsed')) {
        configPanel.classList.remove('collapsed');
        expandIcon.classList.add('expanded');
        if (header) header.setAttribute('aria-expanded', 'true');
        updateSystemStatus('MULTI_PAGE_CONFIG // PANEL_EXPANDED');
    } else {
        configPanel.classList.add('collapsed');
        expandIcon.classList.remove('expanded');
        if (header) header.setAttribute('aria-expanded', 'false');
        updateSystemStatus('MULTI_PAGE_CONFIG // PANEL_COLLAPSED');
    }
}

/**
 * Setup all slider inputs and their value displays
 */
function setupSliderUpdates() {
    // Crawl depth slider
    const crawlDepthSlider = document.getElementById('crawlDepth');
    const depthValue = document.getElementById('depthValue');
    
    if (crawlDepthSlider && depthValue) {
        crawlDepthSlider.addEventListener('input', function() {
            depthValue.textContent = this.value;
            updateSystemStatus(`CRAWL_DEPTH_SET // LEVEL_${this.value}`);
        });
    }

    // Rate limit slider
    const rateLimitSlider = document.getElementById('rateLimit');
    const rateLimitValue = document.getElementById('rateLimitValue');
    
    if (rateLimitSlider && rateLimitValue) {
        rateLimitSlider.addEventListener('input', function() {
            rateLimitValue.textContent = this.value + 'ms';
            updateSystemStatus(`RATE_LIMIT_SET // ${this.value}MS_DELAY`);
        });
    }

    // JavaScript timeout slider
    const jsTimeoutSlider = document.getElementById('jsTimeout');
    const jsTimeoutValue = document.getElementById('jsTimeoutValue');
    
    if (jsTimeoutSlider && jsTimeoutValue) {
        jsTimeoutSlider.addEventListener('input', function() {
            jsTimeoutValue.textContent = this.value + 's';
            updateSystemStatus(`JS_TIMEOUT_SET // ${this.value}S_LIMIT`);
        });
    }

    // JavaScript rendering checkbox
    const enableJavaScript = document.getElementById('enableJavaScript');
    if (enableJavaScript) {
        enableJavaScript.addEventListener('change', function() {
            const status = this.checked ? 'ENABLED' : 'DISABLED';
            updateSystemStatus(`JAVASCRIPT_RENDERING // ${status}`);
        });
    }

    // Popup handling checkbox
    const enablePopupHandling = document.getElementById('enablePopupHandling');
    if (enablePopupHandling) {
        enablePopupHandling.addEventListener('change', function() {
            const status = this.checked ? 'ENABLED' : 'DISABLED';
            updateSystemStatus(`POPUP_HANDLING // ${status}`);
        });
    }

    // Max pages input
    const maxPagesInput = document.getElementById('maxPages');
    if (maxPagesInput) {
        maxPagesInput.addEventListener('input', function() {
            updateSystemStatus(`MAX_PAGES_SET // LIMIT_${this.value}_PAGES`);
        });
    }

    // Pattern inputs
    const includePatterns = document.getElementById('includePatterns');
    const excludePatterns = document.getElementById('excludePatterns');
    
    if (includePatterns) {
        includePatterns.addEventListener('input', function() {
            const patterns = this.value.split(',').length;
            updateSystemStatus(`INCLUDE_PATTERNS_SET // ${patterns}_FILTERS_ACTIVE`);
        });
    }

    if (excludePatterns) {
        excludePatterns.addEventListener('input', function() {
            const patterns = this.value.split(',').length;
            updateSystemStatus(`EXCLUDE_PATTERNS_SET // ${patterns}_FILTERS_ACTIVE`);
        });
    }

    // Single Page Configuration Sliders
    // Single page JavaScript timeout slider
    const singleJsTimeoutSlider = document.getElementById('singleJsTimeout');
    const singleJsTimeoutValue = document.getElementById('singleJsTimeoutValue');
    
    if (singleJsTimeoutSlider && singleJsTimeoutValue) {
        singleJsTimeoutSlider.addEventListener('input', function() {
            singleJsTimeoutValue.textContent = this.value + 's';
            updateSystemStatus(`SINGLE_JS_TIMEOUT_SET // ${this.value}S_LIMIT`);
        });
    }

    // Single page concurrent requests slider
    const singleConcurrentRequestsSlider = document.getElementById('singleConcurrentRequests');
    const singleConcurrentRequestsValue = document.getElementById('singleConcurrentRequestsValue');
    
    if (singleConcurrentRequestsSlider && singleConcurrentRequestsValue) {
        singleConcurrentRequestsSlider.addEventListener('input', function() {
            singleConcurrentRequestsValue.textContent = this.value;
            updateSystemStatus(`SINGLE_CONCURRENT_REQUESTS_SET // ${this.value}_PARALLEL`);
        });
    }

    // Single page JavaScript rendering checkbox
    const singleEnableJavaScript = document.getElementById('singleEnableJavaScript');
    if (singleEnableJavaScript) {
        singleEnableJavaScript.addEventListener('change', function() {
            const status = this.checked ? 'ENABLED' : 'DISABLED';
            updateSystemStatus(`SINGLE_JAVASCRIPT_RENDERING // ${status}`);
        });
    }

    // Single page popup handling checkbox
    const singleEnablePopupHandling = document.getElementById('singleEnablePopupHandling');
    if (singleEnablePopupHandling) {
        singleEnablePopupHandling.addEventListener('change', function() {
            const status = this.checked ? 'ENABLED' : 'DISABLED';
            updateSystemStatus(`SINGLE_POPUP_HANDLING // ${status}`);
        });
    }

    // Single page follow redirects checkbox
    const singleFollowRedirects = document.getElementById('singleFollowRedirects');
    if (singleFollowRedirects) {
        singleFollowRedirects.addEventListener('change', function() {
            const status = this.checked ? 'ENABLED' : 'DISABLED';
            updateSystemStatus(`SINGLE_FOLLOW_REDIRECTS // ${status}`);
        });
    }

    // Single page request timeout input
    const singleRequestTimeout = document.getElementById('singleRequestTimeout');
    if (singleRequestTimeout) {
        singleRequestTimeout.addEventListener('input', function() {
            updateSystemStatus(`SINGLE_REQUEST_TIMEOUT_SET // ${this.value}S_LIMIT`);
        });
    }
}

// =============================================================================
// System Status and Terminal UI Functions
// =============================================================================

/**
 * Update system status bar with terminal-style message
 */
function updateSystemStatus(message) {
    if (statusBar) {
        statusBar.textContent = message;
        statusBar.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => {
            if (statusBar) statusBar.style.animation = '';
        }, 500);
    }
}

/**
 * Format terminal log message with timestamp and prefix
 */
function terminalLog(message, type = 'info') {
    const timestamp = new Date().toISOString().substr(11, 8);
    const prefix = type === 'error' ? '[ERROR]' : 
                 type === 'success' ? '[SUCCESS]' : '[INFO]';
    return `[${timestamp}] ${prefix} ${message}`;
}

/**
 * Show terminal-style alert notification
 */
function showTerminalAlert(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'terminal-alert';
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 85, 85, 0.9);
        border: 1px solid #ff5555;
        color: white;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875rem;
        z-index: 1000;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 4000);
}

// =============================================================================
// Form Event Handlers
// =============================================================================

// Validate URLs on input with debounced validation
urlsInput.addEventListener('input', debounce(validateURLsInput, 500));

// Form submission with terminal aesthetics
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Check input mode first - only process URLs in URL mode
    const inputModeElement = document.querySelector('input[name="input_mode"]:checked');
    const inputMode = inputModeElement ? inputModeElement.value : 'url';
    
    if (inputMode === 'file') {
        console.log('File upload mode detected in terminal-ui.js - processing uploaded files');
        updateSystemStatus('FILE_MODE // PROCESSING_UPLOADED_FILES');
        await processUploadedFiles(outputDir, fileMode, fileFormat, jsonFieldSelections, scrapingMode, multiPageConfig);
        return;
    }
    
    // Extract URLs using regex to handle quotes and other text
    const urlPattern = /https?:\/\/[^\s"']+(?:\/[^\s"']*)*\/?/g;
    const urls = urlsInput.value.match(urlPattern) || [];
    
    // If no URLs found with regex, fall back to newline splitting
    if (urls.length === 0) {
        const lines = urlsInput.value.trim().split('\n').filter(line => line.trim());
        urls.push(...lines);
    }
    const outputDir = document.getElementById('outputDir').value.trim();
    const fileMode = document.getElementById('fileMode').value;
    const fileFormat = document.querySelector('input[name="fileFormat"]:checked').value;
    const scrapingMode = document.querySelector('input[name="scrapingMode"]:checked').value;
    
    // Collect JSON field selections if JSON format is selected
    let jsonFieldSelections = null;
    if (fileFormat === 'json') {
        const selectedFields = Array.from(document.querySelectorAll('input[name="jsonFields"]:checked'))
            .map(input => input.value);
        if (selectedFields.length > 0) {
            jsonFieldSelections = selectedFields;
        }
    }
    
    if (urls.length === 0) {
        updateSystemStatus('ERROR // NO_TARGET_URLs_DETECTED');
        showTerminalAlert('CRITICAL ERROR: No target URLs detected. Please input valid restaurant URLs.');
        return;
    }
    
    // Collect multi-page configuration if multi-page mode is selected
    let multiPageConfig = null;
    if (scrapingMode === 'multi') {
        multiPageConfig = {
            maxPages: parseInt(document.getElementById('maxPages').value) || 50,
            crawlDepth: parseInt(document.getElementById('crawlDepth').value) || 2,
            includePatterns: document.getElementById('includePatterns').value || 'menu,food,restaurant',
            excludePatterns: document.getElementById('excludePatterns').value || 'admin,login,cart',
            rateLimit: parseInt(document.getElementById('rateLimit').value) || 1000
        };
    }
    
    updateSystemStatus(`INITIATING_EXTRACTION // ${urls.length}_TARGETS_QUEUED // ${scrapingMode.toUpperCase()}_MODE`);
    await startScraping(urls, outputDir, fileMode, fileFormat, jsonFieldSelections, scrapingMode, multiPageConfig);
});

// Validate button with terminal feedback
validateBtn.addEventListener('click', () => {
    // Check input mode first
    const inputModeElement = document.querySelector('input[name="input_mode"]:checked');
    const inputMode = inputModeElement ? inputModeElement.value : 'url';
    
    if (inputMode === 'file') {
        updateSystemStatus('FILE_MODE // VALIDATION_NOT_APPLICABLE_TERMINAL_UI');
        showTerminalAlert('URL validation is not applicable in file upload mode.');
        return;
    }
    
    updateSystemStatus('VALIDATING_TARGETS // SCANNING_URLs...');
    validateURLsInput();
});

// Clear button with terminal reset
clearBtn.addEventListener('click', () => {
    form.reset();
    urlValidation.innerHTML = '';
    hideResults();
    hideProgress();
    // Reset format selection
    formatOptions.forEach(opt => opt.classList.remove('selected'));
    formatOptions[0].classList.add('selected');
    updateSystemStatus('TERMINAL_RESET // AWAITING_NEW_TARGETS');
});

// =============================================================================
// URL Validation Functions
// =============================================================================

/**
 * Validate URLs input field and display results
 */
async function validateURLsInput() {
    // Check input mode first - only validate URLs in URL mode
    const inputModeElement = document.querySelector('input[name="input_mode"]:checked');
    const inputMode = inputModeElement ? inputModeElement.value : 'url';
    
    if (inputMode === 'file') {
        // In file mode, clear any URL validation and don't validate
        urlValidation.innerHTML = '';
        updateSystemStatus('FILE_MODE // URL_VALIDATION_SKIPPED_TERMINAL_UI');
        return;
    }
    
    // Extract URLs using regex to handle quotes and other text
    const urlPattern = /https?:\/\/[^\s"']+(?:\/[^\s"']*)*\/?/g;
    const urls = urlsInput.value.match(urlPattern) || [];
    
    // If no URLs found with regex, fall back to newline splitting
    if (urls.length === 0) {
        const lines = urlsInput.value.trim().split('\n').filter(line => line.trim());
        urls.push(...lines);
    }
    
    if (urls.length === 0) {
        urlValidation.innerHTML = '';
        updateSystemStatus('SYSTEM_READY // AWAITING_TARGET_URLs');
        return;
    }
    
    updateSystemStatus(`VALIDATING // ${urls.length}_TARGETS_SCANNING...`);
    
    try {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ urls: urls })
        });
        
        const data = await response.json();
        
        if (data.results) {
            displayValidationResults(data.results);
        }
    } catch (error) {
        console.error('Validation error:', error);
        urlValidation.innerHTML = terminalLog('VALIDATION_FAILED // Network error', 'error');
        updateSystemStatus('ERROR // VALIDATION_SYSTEM_OFFLINE');
    }
}

/**
 * Display URL validation results in terminal format
 */
function displayValidationResults(results) {
    const validCount = results.filter(r => r.is_valid).length;
    const totalCount = results.length;
    const status = validCount === totalCount ? 'ALL_VALID' : `${validCount}/${totalCount}_VALID`;
    
    updateSystemStatus(`VALIDATION_COMPLETE // ${status}`);
    
    let html = `<div style="margin-bottom: 0.5rem;">${terminalLog(`Target analysis: ${validCount}/${totalCount} URLs validated`, 'info')}</div>`;
    
    results.forEach((result, index) => {
        const cssClass = result.is_valid ? 'valid-url' : 'invalid-url';
        const status = result.is_valid ? '[VALID]' : '[INVALID]';
        const error = result.error ? ` // ${result.error}` : '';
        
        html += `<div class="${cssClass}">${status} TARGET_${index + 1}${error}</div>`;
    });
    
    urlValidation.innerHTML = html;
}

// =============================================================================
// File Upload Processing Functions
// =============================================================================

/**
 * Process uploaded files through the scraping pipeline
 */
async function processUploadedFiles(outputDir, fileMode, fileFormat, jsonFieldSelections, scrapingMode, multiPageConfig) {
    try {
        // Get uploaded files or file paths
        const uploadedFiles = getUploadedFiles();
        const filePaths = getEnteredFilePaths();
        
        if (uploadedFiles.length === 0 && filePaths.length === 0) {
            updateSystemStatus('ERROR // NO_FILES_DETECTED');
            showTerminalAlert('CRITICAL ERROR: No files uploaded or paths entered. Please upload PDF files or enter file paths.');
            return;
        }
        
        // Disable submit button and show progress
        submitBtn.disabled = true;
        submitBtn.textContent = 'PROCESSING_FILES...';
        isActivelyProcessing = true;
        scrapingStartTime = Date.now();
        showProgress();
        hideResults();
        
        updateSystemStatus(`FILE_PROCESSING_INITIATED // ${uploadedFiles.length + filePaths.length}_FILES_QUEUED`);
        
        // First, handle file uploads if any
        let fileIds = [];
        if (uploadedFiles.length > 0) {
            const uploadResults = await uploadFiles(uploadedFiles);
            fileIds = uploadResults.filter(result => result.success).map(result => result.file_id);
        }
        
        // Process uploaded files and/or file paths through scraping pipeline
        const response = await fetch('/api/process-uploaded-files-for-rag', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_ids: fileIds,
                file_paths: filePaths,
                output_dir: outputDir,
                file_mode: fileMode,
                file_format: fileFormat,
                json_field_selections: jsonFieldSelections,
                scraping_mode: scrapingMode,
                multi_page_config: multiPageConfig,
                industry: 'Restaurant'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateSystemStatus(`FILE_PROCESSING_COMPLETE // ${data.processed_count || 0}_FILES_PROCESSED`);
            showResults(data, true);
            // Clear the file upload area after successful processing
            clearFileUploadArea();
        } else {
            updateSystemStatus('FILE_PROCESSING_FAILED // SYSTEM_ERROR');
            showResults(data, false);
        }
        
    } catch (error) {
        console.error('File processing error:', error);
        
        let errorMessage = 'Unknown error during file processing';
        let statusMessage = 'CRITICAL_ERROR // UNKNOWN_FAILURE';
        
        if (error.message && error.message.includes('fetch')) {
            errorMessage = 'Network connection failure during file processing';
            statusMessage = 'NETWORK_ERROR // CONNECTION_FAILURE';
        } else if (error.message) {
            errorMessage = error.message;
            statusMessage = 'REQUEST_ERROR // ' + error.name;
        }
        
        updateSystemStatus(statusMessage);
        showResults({ error: errorMessage }, false);
    } finally {
        isActivelyProcessing = false;
        scrapingStartTime = null;
        submitBtn.disabled = false;
        submitBtn.textContent = 'EXECUTE_EXTRACTION';
        hideProgress();
    }
}

/**
 * Get uploaded files from the file upload area
 */
function getUploadedFiles() {
    const fileInput = document.getElementById('file-input');
    if (fileInput && fileInput.files) {
        return Array.from(fileInput.files);
    }
    return [];
}

/**
 * Get entered file paths from the file path input
 */
function getEnteredFilePaths() {
    const filePathInput = document.getElementById('file-path-input');
    if (filePathInput && filePathInput.value.trim()) {
        return [filePathInput.value.trim()];
    }
    return [];
}

/**
 * Upload files to the server
 */
async function uploadFiles(files) {
    const results = [];
    
    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            results.push(result);
            
        } catch (error) {
            console.error('Upload error for file:', file.name, error);
            results.push({
                success: false,
                error: `Upload failed for ${file.name}: ${error.message}`,
                filename: file.name
            });
        }
    }
    
    return results;
}

/**
 * Clear the file upload area
 */
function clearFileUploadArea() {
    const fileInput = document.getElementById('file-input');
    const filePathInput = document.getElementById('file-path-input');
    const uploadQueue = document.getElementById('upload-queue');
    
    if (fileInput) {
        fileInput.value = '';
    }
    
    if (filePathInput) {
        filePathInput.value = '';
    }
    
    if (uploadQueue) {
        uploadQueue.innerHTML = '';
    }
}

// =============================================================================
// Scraping and API Functions
// =============================================================================

/**
 * Start the scraping process with all configured options
 */
async function startScraping(urls, outputDir, fileMode, fileFormat, jsonFieldSelections, scrapingMode, multiPageConfig) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'EXTRACTION_IN_PROGRESS...';
    isActivelyProcessing = true;
    scrapingStartTime = Date.now();
    showProgress();
    hideResults();
    
    updateSystemStatus(`EXTRACTION_INITIATED // ${urls.length}_TARGETS_PROCESSING`);
    
    try {
        // Create AbortController for longer timeout (10 minutes for multi-page scraping)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minutes
        
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: controller.signal,
            body: JSON.stringify({
                urls: urls,
                output_dir: outputDir,
                file_mode: fileMode,
                file_format: fileFormat,
                json_field_selections: jsonFieldSelections,
                scraping_mode: scrapingMode,
                multi_page_config: multiPageConfig,
                enableJavaScript: document.getElementById('enableJavaScript')?.checked || false,
                jsTimeout: parseInt(document.getElementById('jsTimeout')?.value || '30'),
                enablePopupHandling: document.getElementById('enablePopupHandling')?.checked || true,
                industry: 'Restaurant'
            })
        });
        
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (data.success) {
            updateSystemStatus(`EXTRACTION_COMPLETE // ${data.processed_count || 0}_TARGETS_PROCESSED`);
            showResults(data, true);
            // Clear the URLs input field after successful scraping
            urlsInput.value = '';
        } else {
            updateSystemStatus('EXTRACTION_FAILED // SYSTEM_ERROR');
            showResults(data, false);
        }
    } catch (error) {
        console.error('Scraping error:', error);
        
        let errorMessage = 'Unknown error during extraction';
        let statusMessage = 'CRITICAL_ERROR // UNKNOWN_FAILURE';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Request timeout - multi-page scraping took longer than 10 minutes';
            statusMessage = 'TIMEOUT_ERROR // PROCESSING_TIMEOUT';
        } else if (error.message && error.message.includes('fetch')) {
            errorMessage = 'Network connection failure during extraction';
            statusMessage = 'NETWORK_ERROR // CONNECTION_FAILURE';
        } else if (error.message) {
            errorMessage = error.message;
            statusMessage = 'REQUEST_ERROR // ' + error.name;
        }
        
        updateSystemStatus(statusMessage);
        showResults({ error: errorMessage }, false);
    } finally {
        isActivelyProcessing = false;
        scrapingStartTime = null;
        submitBtn.disabled = false;
        submitBtn.textContent = 'EXECUTE_EXTRACTION';
        hideProgress();
    }
}

// =============================================================================
// Progress Monitoring Functions
// =============================================================================

/**
 * Show progress container and start monitoring
 */
function showProgress() {
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = terminalLog('Initializing extraction sequence...', 'info');
    currentUrl.textContent = '';
    timeEstimate.textContent = '';
    memoryUsage.textContent = '';
    
    // Activate the data flow pipeline
    if (dataFlow) {
        dataFlow.classList.add('active');
    }
    
    // Start progress polling
    progressInterval = setInterval(updateProgress, 1000);
}

/**
 * Hide progress container and stop monitoring
 */
function hideProgress() {
    progressContainer.style.display = 'none';
    
    // Deactivate the data flow pipeline
    if (dataFlow) {
        dataFlow.classList.remove('active');
    }
    
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

/**
 * Update progress display with data from API
 */
async function updateProgress() {
    try {
        const response = await fetch('/api/progress');
        const data = await response.json();
        
        if (data.progress_percentage !== undefined) {
            progressFill.style.width = data.progress_percentage + '%';
            
            // Show meaningful message based on the situation
            const isRecentlyStarted = scrapingStartTime && (Date.now() - scrapingStartTime < 30000); // Within 30 seconds
            
            
            if (data.progress_percentage === 0 && data.urls_total > 1) {
                // Multi-page or batch processing with known total
                progressText.textContent = terminalLog(`Processing pages: ${data.urls_completed}/${data.urls_total}`, 'info');
            } else if (data.progress_percentage === 0 && (data.urls_total === 1 || data.status === 'processing' || isActivelyProcessing || isRecentlyStarted)) {
                // Single URL processing with no progress tracking or recently started
                const elapsed = scrapingStartTime ? Math.floor((Date.now() - scrapingStartTime) / 1000) : 0;
                if (elapsed > 0) {
                    progressText.textContent = terminalLog(`Processing extraction... (${elapsed}s)`, 'info');
                } else {
                    progressText.textContent = terminalLog(`Processing extraction...`, 'info');
                }
            } else if (data.progress_percentage === 0) {
                // No active processing
                progressText.textContent = terminalLog(`Ready for extraction`, 'info');
            } else {
                // Normal progress display
                progressText.textContent = terminalLog(`Extraction progress: ${data.progress_percentage}% (${data.urls_completed}/${data.urls_total})`, 'info');
            }
            
            if (data.current_url) {
                currentUrl.textContent = terminalLog(`Processing target: ${data.current_url}`, 'info');
            }
            
            if (data.estimated_time_remaining > 0) {
                const minutes = Math.floor(data.estimated_time_remaining / 60);
                const seconds = Math.floor(data.estimated_time_remaining % 60);
                timeEstimate.textContent = terminalLog(`ETA: ${minutes}m ${seconds}s`, 'info');
            } else if (data.urls_completed > 0) {
                timeEstimate.textContent = terminalLog('Calculating time estimate...', 'info');
            }
            
            if (data.memory_usage_mb > 0) {
                memoryUsage.textContent = terminalLog(`Memory usage: ${data.memory_usage_mb.toFixed(1)} MB`, 'info');
            }
            
            if (data.current_operation && data.current_operation.trim() !== '') {
                progressText.textContent = terminalLog(data.current_operation, 'info');
            }
        }
    } catch (error) {
        console.error('Progress update error:', error);
    }
}

// =============================================================================
// Results Display Functions
// =============================================================================

/**
 * Show results container with appropriate display mode
 */
function showResults(data, success) {
    resultsContainer.style.display = 'block';
    
    // Get current scraping mode
    const scrapingMode = getSelectedScrapingMode();
    
    if (success && data.sites_data) {
        // Show enhanced results display
        showEnhancedResults(data);
    } else if (success) {
        // Show legacy results display for backward compatibility
        showLegacyResults(data, success);
    } else {
        // Show error results
        showErrorResults(data);
    }
    
    // Ensure results are visible for single page mode
    if (scrapingMode === 'single') {
        // Scroll to results for better visibility
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Show enhanced results with site-by-site breakdown
 */
function showEnhancedResults(data) {
    noResults.style.display = 'none';
    sitesResults.style.display = 'block';
    
    const scrapingMode = getSelectedScrapingMode();
    const sitesData = data.sites_data || [];
    
    // Store sites data globally for "Show all pages" functionality
    window.currentSitesData = sitesData;
    
    let html = '';
    
    // Add mode-specific header
    if (scrapingMode === 'single') {
        html += '<div class="results-header single-page-header">';
        html += '<h3>SINGLE PAGE EXTRACTION RESULTS</h3>';
        html += '</div>';
    }
    
    sitesData.forEach((siteData, index) => {
        html += generateSiteResultHTML(siteData, index, scrapingMode);
    });
    
    sitesResults.innerHTML = html;
    
    // Set up event listeners for interactive elements
    setupResultsInteractivity();
}

/**
 * Show legacy results format for backward compatibility
 */
function showLegacyResults(data, success) {
    // Keep existing functionality for backward compatibility
    noResults.style.display = 'none';
    sitesResults.style.display = 'none';
    
    let html = '';
    
    html += `<div style="margin-bottom: 1rem;">${terminalLog('EXTRACTION_COMPLETE // All targets processed successfully', 'success')}</div>`;
    
    if (data.processed_count) {
        html += `<div>${terminalLog(`Targets processed: ${data.processed_count}`, 'info')}</div>`;
    }
    
    if (data.output_files && data.output_files.length > 0) {
        html += `<div style="margin: 1rem 0;">${terminalLog('Generated output files:', 'info')}</div>`;
        html += '<div class="file-links">';
        data.output_files.forEach(file => {
            const fileName = file.split('/').pop();
            const fileExtension = fileName.split('.').pop().toLowerCase();
            
            // For text files, create a view link that opens in browser
            // For PDF files, create a download link
            if (fileExtension === 'txt' || fileExtension === 'json') {
                const viewUrl = `/api/view-file/${encodeURIComponent(fileName)}`;
                html += `<a href="${viewUrl}" target="_blank" class="file-link">${fileName}</a>`;
            } else {
                const downloadUrl = `/api/download/${encodeURIComponent(fileName)}`;
                html += `<a href="${downloadUrl}" target="_blank" class="file-link">${fileName}</a>`;
            }
        });
        html += '</div>';
    }
    
    if (data.failed_count && data.failed_count > 0) {
        html += `<div style="margin-top: 1rem;">${terminalLog(`Failed targets: ${data.failed_count}`, 'error')}</div>`;
    }
    
    if (data.processing_time) {
        html += `<div>${terminalLog(`Processing time: ${data.processing_time.toFixed(2)}s`, 'info')}</div>`;
    }
    
    resultsContent.innerHTML = html;
}

/**
 * Show error results
 */
function showErrorResults(data) {
    noResults.style.display = 'none';
    sitesResults.style.display = 'none';
    
    let html = '';
    html += `<div>${terminalLog('EXTRACTION_FAILED // System error detected', 'error')}</div>`;
    html += `<div style="margin-top: 0.5rem;">${terminalLog(`Error details: ${data.error || 'Unknown system failure'}`, 'error')}</div>`;
    
    resultsContent.innerHTML = html;
}

/**
 * Generate HTML for site result display
 */
function generateSiteResultHTML(siteData, index, scrapingMode) {
    const { site_url, pages_processed, pages } = siteData;
    const successCount = pages.filter(p => p.status === 'success').length;
    const failedCount = pages.filter(p => p.status === 'failed').length;
    
    // Check if any pages have relationship data
    const hasRelationships = pages.some(p => p.relationship);
    const isMultiPageMode = scrapingMode === 'multi';
    
    let html = `
        <div class="site-result ${hasRelationships && isMultiPageMode ? 'relationship-enabled' : ''}">
            <div class="site-header" onclick="toggleSiteExpansion(${index})">
                <div class="site-url">${site_url}</div>
                <div class="pages-summary">
                    <span>Pages Processed: ${pages_processed}</span>
                    <div class="processing-stats">
                        <div class="stat-item">
                            <div class="stat-icon success"></div>
                            <span>${successCount} success</span>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon failed"></div>
                            <span>${failedCount} failed</span>
                        </div>
                    </div>
                    <div class="expand-toggle" id="toggle-${index}">▼</div>
                </div>
            </div>
            <div class="pages-list" id="pages-${index}">
    `;
    
    if (hasRelationships && isMultiPageMode) {
        // Generate relationship tree for multi-page mode
        html += generateRelationshipTree(pages, index);
    } else {
        // Generate simple page list for single-page mode or no relationships
        const pagesToShow = pages.slice(0, 5);
        const hasMorePages = pages.length > 5;
        
        pagesToShow.forEach(page => {
            html += generatePageItemHTML(page, isMultiPageMode);
        });
        
        if (hasMorePages) {
            html += `
                <div class="show-all-link" onclick="showAllPages(${index})">
                    Show all ${pages.length} pages
                </div>
            `;
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

/**
 * Generate HTML for individual page items
 */
function generatePageItemHTML(page, showRelationships = false) {
    const statusClass = `status-${page.status}`;
    const statusText = page.status === 'success' ? 'SUCCESS' : 'FAILED';
    const statusClassName = page.status === 'success' ? 'success' : 'failed';
    
    let relationshipClasses = '';
    let relationshipContent = '';
    
    if (page.relationship && showRelationships) {
        const rel = page.relationship;
        relationshipClasses = `relationship-${rel.type} depth-${rel.depth || 0}`;
        
        if (rel.error) {
            relationshipClasses += ' broken-relationship';
        }
        
        // Add relationship indicator
        if (rel.type === 'root') {
            relationshipContent += '<span class="relationship-indicator ROOT">ROOT</span>';
            relationshipContent += '<span class="discovery-info">Entry point</span>';
        } else if (rel.type === 'child') {
            relationshipContent += '<span class="indentation"></span>';
            relationshipContent += '<span class="relationship-indicator child">↳</span>';
            if (rel.parent_url) {
                relationshipContent += `<span class="parent-reference">from: ${rel.parent_url}</span>`;
                relationshipContent += `<span class="discovery-info">Discovered from: ${rel.parent_url}</span>`;
            }
        } else if (rel.type === 'orphaned') {
            relationshipContent += '<span class="relationship-indicator orphaned">⚠ ORPHANED</span>';
        }
        
        // Add children count if applicable
        if (rel.children_count > 0) {
            relationshipContent += `<span class="children-count">Children discovered: ${rel.children_count}</span>`;
        }
        
        // Add depth level
        if (rel.depth !== undefined) {
            relationshipContent += `<span class="depth-level">Depth level: ${rel.depth}</span>`;
        }
        
        // Add discovery method
        if (rel.discovery_method) {
            relationshipContent += `<span class="discovery-info">${rel.discovery_method}</span>`;
        }
        
        // Add error indicators
        if (rel.error) {
            relationshipContent += '<span class="relationship-warning">⚠ Relationship broken</span>';
        }
        
        // Add tooltip
        const tooltipText = `Type: ${rel.type}, Depth: ${rel.depth || 0}, Discovery: ${rel.discovery_method || 'unknown'}`;
        relationshipContent += `<span class="relationship-tooltip" data-tooltip="${tooltipText}">ℹ</span>`;
    }
    
    return `
        <div class="page-item ${statusClass} ${relationshipClasses}" 
             onmouseover="highlightRelationshipChain('${page.url}')"
             onmouseout="clearRelationshipHighlight()">
            ${relationshipContent}
            <div class="page-url">${page.url}</div>
            <div class="page-status ${statusClassName}">${statusText}</div>
            <div class="page-time">${page.processing_time.toFixed(1)}s</div>
        </div>
    `;
}

/**
 * Hide results container
 */
function hideResults() {
    resultsContainer.style.display = 'none';
}

// =============================================================================
// Results Interactivity Functions
// =============================================================================

/**
 * Setup event listeners for interactive results elements
 */
function setupResultsInteractivity() {
    // Event listeners are set up via onclick attributes in HTML
    // This function can be extended for additional interactivity
}

/**
 * Toggle site expansion in results display
 */
function toggleSiteExpansion(siteIndex) {
    const pagesList = document.getElementById(`pages-${siteIndex}`);
    const toggle = document.getElementById(`toggle-${siteIndex}`);
    
    if (pagesList.classList.contains('expanded')) {
        pagesList.classList.remove('expanded');
        toggle.classList.remove('expanded');
    } else {
        pagesList.classList.add('expanded');
        toggle.classList.add('expanded');
    }
}

/**
 * Show all pages for a specific site
 */
function showAllPages(siteIndex) {
    const pagesList = document.getElementById(`pages-${siteIndex}`);
    
    // Get the site's data from the global sites results
    if (window.currentSitesData && window.currentSitesData[siteIndex]) {
        const siteData = window.currentSitesData[siteIndex];
        const isMultiPageMode = getSelectedScrapingMode() === 'multi';
        
        // Clear current content
        pagesList.innerHTML = '';
        
        // Show all pages
        siteData.pages.forEach(page => {
            pagesList.innerHTML += generatePageItemHTML(page, isMultiPageMode);
        });
        
        // Add a "Show less" link
        pagesList.innerHTML += `
            <div class="show-all-link" onclick="showLessPages(${siteIndex})">
                Show less
            </div>
        `;
    }
}

/**
 * Show only first 5 pages again
 */
function showLessPages(siteIndex) {
    const pagesList = document.getElementById(`pages-${siteIndex}`);
    
    if (window.currentSitesData && window.currentSitesData[siteIndex]) {
        const siteData = window.currentSitesData[siteIndex];
        const isMultiPageMode = getSelectedScrapingMode() === 'multi';
        const pagesToShow = siteData.pages.slice(0, 5);
        const hasMorePages = siteData.pages.length > 5;
        
        // Clear and regenerate limited view
        pagesList.innerHTML = '';
        
        pagesToShow.forEach(page => {
            pagesList.innerHTML += generatePageItemHTML(page, isMultiPageMode);
        });
        
        if (hasMorePages) {
            pagesList.innerHTML += `
                <div class="show-all-link" onclick="showAllPages(${siteIndex})">
                    Show all ${siteData.pages.length} pages
                </div>
            `;
        }
    }
}

/**
 * Get currently selected scraping mode
 */
function getSelectedScrapingMode() {
    const modeInput = document.querySelector('input[name="scrapingMode"]:checked');
    return modeInput ? modeInput.value : 'single';
}

// =============================================================================
// Page Relationship Functions
// =============================================================================

/**
 * Generate relationship tree HTML for multi-page results
 */
function generateRelationshipTree(pages, siteIndex) {
    let html = '<div class="relationship-tree">';
    html += '<div class="relationship-tree-header">🌳 PAGE RELATIONSHIP TREE</div>';
    
    // Sort pages by depth for hierarchical display
    const sortedPages = pages.slice().sort((a, b) => {
        const depthA = a.relationship?.depth || 0;
        const depthB = b.relationship?.depth || 0;
        return depthA - depthB;
    });
    
    // Group orphaned pages separately
    const orphanedPages = pages.filter(p => p.relationship?.type === 'orphaned');
    const hierarchicalPages = pages.filter(p => p.relationship?.type !== 'orphaned');
    
    // Generate hierarchical pages
    hierarchicalPages.forEach((page, index) => {
        html += generatePageItemHTML(page, true);
    });
    
    // Generate orphaned pages section if any exist
    if (orphanedPages.length > 0) {
        html += '<div class="orphaned-section">';
        html += '<div class="orphaned-section-header">⚠ ORPHANED PAGES</div>';
        orphanedPages.forEach(page => {
            html += generatePageItemHTML(page, true);
        });
        html += '</div>';
    }
    
    // Add relationship statistics
    html += generateRelationshipStats(pages);
    
    html += '</div>';
    return html;
}

/**
 * Generate relationship statistics display
 */
function generateRelationshipStats(pages) {
    const stats = {
        total: pages.length,
        root: pages.filter(p => p.relationship?.type === 'root').length,
        children: pages.filter(p => p.relationship?.type === 'child').length,
        orphaned: pages.filter(p => p.relationship?.type === 'orphaned').length,
        maxDepth: Math.max(...pages.map(p => p.relationship?.depth || 0)),
        totalRelationships: pages.filter(p => p.relationship?.parent_url).length
    };
    
    return `
        <div class="relationship-stats">
            <div class="relationship-stats-grid">
                <div class="stat-row">
                    <span class="stat-label">Total Pages:</span>
                    <span class="stat-value">${stats.total}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Root Pages:</span>
                    <span class="stat-value">${stats.root}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Child Pages:</span>
                    <span class="stat-value">${stats.children}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Orphaned Pages:</span>
                    <span class="stat-value">${stats.orphaned}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Max Depth:</span>
                    <span class="stat-value">${stats.maxDepth}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Total Relationships:</span>
                    <span class="stat-value">${stats.totalRelationships}</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * Highlight relationship chain on hover
 */
function highlightRelationshipChain(targetUrl) {
    // Get all page items in the current site
    const pageItems = document.querySelectorAll('.page-item');
    
    // Clear existing highlights
    pageItems.forEach(item => {
        item.classList.remove('highlighted');
    });
    
    // Find related pages and highlight them
    const relatedUrls = findRelatedPages(targetUrl);
    
    pageItems.forEach(item => {
        const urlElement = item.querySelector('.page-url');
        if (urlElement && relatedUrls.includes(urlElement.textContent)) {
            item.classList.add('highlighted');
        }
    });
    
    // Add highlighting effect to container
    const container = document.querySelector('.relationship-enabled');
    if (container) {
        container.classList.add('highlight-relationship-chain');
    }
}

/**
 * Clear relationship highlighting
 */
function clearRelationshipHighlight() {
    const pageItems = document.querySelectorAll('.page-item');
    pageItems.forEach(item => {
        item.classList.remove('highlighted');
    });
    
    const container = document.querySelector('.relationship-enabled');
    if (container) {
        container.classList.remove('highlight-relationship-chain');
    }
}

/**
 * Find related pages for relationship highlighting
 */
function findRelatedPages(targetUrl) {
    // This is a simplified version - in a real implementation,
    // this would traverse the actual relationship data
    const related = [targetUrl];
    
    // Find pages that mention this URL as parent
    const pageItems = document.querySelectorAll('.page-item');
    pageItems.forEach(item => {
        const parentRef = item.querySelector('.parent-reference');
        if (parentRef && parentRef.textContent.includes(targetUrl)) {
            const urlElement = item.querySelector('.page-url');
            if (urlElement) {
                related.push(urlElement.textContent);
            }
        }
    });
    
    return related;
}

/**
 * Toggle relationship tree expansion
 */
function toggleRelationshipTreeExpansion(siteIndex) {
    const tree = document.querySelector(`#pages-${siteIndex} .relationship-tree`);
    if (tree) {
        tree.classList.toggle('expanded');
    }
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Debounce function to limit rapid function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// =============================================================================
// CSS Animations - Dynamically Added Styles
// =============================================================================

// Add CSS animations for terminal effects
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.1; }
        50% { transform: translateY(-10px) rotate(180deg); opacity: 0.3; }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes terminal-cursor {
        0%, 50% { box-shadow: inset 0 0 0 2px var(--accent-green); }
        51%, 100% { box-shadow: inset 0 0 0 2px transparent; }
    }
`;
document.head.appendChild(styleSheet);