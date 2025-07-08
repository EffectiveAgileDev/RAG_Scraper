"""File upload UI components for web interface."""


class InputModeToggle:
    """UI component for toggling between URL and file upload modes."""
    
    def __init__(self, default_mode="url", css_class="input-mode-toggle"):
        """Initialize input mode toggle.
        
        Args:
            default_mode: Default mode ('url' or 'file')
            css_class: CSS class for styling
        """
        self.default_mode = default_mode
        self.current_mode = default_mode
        self.css_class = css_class
    
    def set_mode(self, mode):
        """Set the current mode.
        
        Args:
            mode: Mode to set ('url' or 'file')
        """
        self.current_mode = mode
    
    def render(self):
        """Render the input mode toggle HTML.
        
        Returns:
            HTML string for the toggle component
        """
        url_checked = 'checked' if self.current_mode == 'url' else ''
        file_checked = 'checked' if self.current_mode == 'file' else ''
        
        html = f"""
        <div id="input-mode-toggle" class="{self.css_class}" role="radiogroup" aria-label="Input mode selection">
            <label class="mode-option" for="input-mode-url">
                <input type="radio" id="input-mode-url" name="input_mode" value="url" {url_checked} onchange="window.toggleFileUploadMode('url')">
                <span>URL Mode</span>
            </label>
            <label class="mode-option" for="input-mode-file">
                <input type="radio" id="input-mode-file" name="input_mode" value="file" {file_checked} onchange="window.toggleFileUploadMode('file')">
                <span>File Upload Mode</span>
            </label>
        </div>
        """
        return html


class FileUploadArea:
    """UI component for file upload area with drag and drop support."""
    
    def __init__(self, accept_types=None, max_file_size="50MB", enable_multiple=False):
        """Initialize file upload area.
        
        Args:
            accept_types: List of accepted MIME types
            max_file_size: Maximum file size
            enable_multiple: Whether to enable multiple file uploads
        """
        self.accept_types = accept_types or ["application/pdf"]
        self.max_file_size = max_file_size
        self.enable_multiple = enable_multiple
    
    def render(self):
        """Render the file upload area HTML.
        
        Returns:
            HTML string for the upload area
        """
        accept_attr = ",".join(self.accept_types)
        multiple_attr = 'multiple' if self.enable_multiple else ''
        
        html = f"""
        <!-- File Path Input -->
        <div class="file-path-section">
            <label for="file-path-input" class="input-label">FILE_PATH:</label>
            <input type="text" id="file-path-input" class="terminal-input" 
                   placeholder="Enter full path to PDF file (e.g., /home/user/document.pdf)"
                   onchange="handleFilePathInput(event)">
        </div>
        
        <div class="input-separator">OR</div>
        
        <div id="file-upload-area" class="file-upload-area" 
             ondragover="handleDragOver(event)" 
             ondrop="handleDrop(event)">
            <div class="upload-icon">📁</div>
            <div class="upload-text">
                <p>Drag and drop PDF files here</p>
                <p>or</p>
                <button type="button" id="browse-files-btn" onclick="triggerFileInput()" tabindex="0">
                    Browse Files
                </button>
            </div>
            <input type="file" id="file-input" accept="{accept_attr}" {multiple_attr} 
                   style="display: none;" onchange="handleFileSelect(event)">
        </div>
        
        <div id="upload-queue" class="upload-queue">
            <!-- File items will be dynamically added here -->
        </div>
        
        <div id="upload-progress" class="upload-progress" style="display: none;">
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div class="progress-text">Uploading...</div>
        </div>
        
        <div class="validation-output error-message" id="file-validation-errors"></div>
        """
        return html
    
    def get_javascript(self):
        """Get JavaScript for file upload functionality.
        
        Returns:
            JavaScript code as string
        """
        js = """
        // Initialize event listeners when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            const uploadArea = document.getElementById('file-upload-area');
            const fileInput = document.getElementById('file-input');
            
            if (uploadArea) {
                uploadArea.addEventListener('dragover', handleDragOver);
                uploadArea.addEventListener('drop', handleDrop);
            }
            
            if (fileInput) {
                fileInput.addEventListener('change', handleFileSelect);
            }
        });
        
        function handleDragOver(event) {
            event.preventDefault();
            event.currentTarget.classList.add('drag-over');
        }
        
        function handleDrop(event) {
            event.preventDefault();
            event.currentTarget.classList.remove('drag-over');
            const files = event.dataTransfer.files;
            processFiles(files);
        }
        
        function triggerFileInput() {
            document.getElementById('file-input').click();
        }
        
        function handleFileSelect(event) {
            const files = event.target.files;
            processFiles(files);
        }
        
        function processFiles(files) {
            for (let file of files) {
                if (validateFile(file)) {
                    addFileToQueue(file);
                }
            }
        }
        
        function validateFile(file) {
            // Check file type
            if (!file.type.includes('application/pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
                showError('Only PDF files are supported');
                return false;
            }
            
            // Check file size (50MB limit)
            if (file.size > 50 * 1024 * 1024) {
                showError('File size exceeds maximum limit of 50MB');
                return false;
            }
            
            return true;
        }
        
        function addFileToQueue(file) {
            const queue = document.getElementById('upload-queue');
            const fileId = 'file-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <span class="filename">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                </div>
                <button type="button" class="remove-file-btn" onclick="removeFile('${fileId}')">
                    Remove
                </button>
            `;
            fileItem.id = fileId;
            
            queue.appendChild(fileItem);
        }
        
        function removeFile(fileId) {
            const fileItem = document.getElementById(fileId);
            if (fileItem) {
                fileItem.remove();
            }
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('file-validation-errors');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
        
        function handleFilePathInput(event) {
            const filePath = event.target.value.trim();
            if (filePath) {
                // Clear any uploaded files when a path is entered
                const fileInput = document.getElementById('file-input');
                if (fileInput) {
                    fileInput.value = '';
                }
                
                // Clear upload queue
                const queue = document.getElementById('upload-queue');
                if (queue) {
                    queue.innerHTML = '';
                }
                
                // Add file path to queue display
                addFilePathToQueue(filePath);
            }
        }
        
        function addFilePathToQueue(filePath) {
            const queue = document.getElementById('upload-queue');
            const fileName = filePath.split('/').pop() || filePath;
            const fileId = 'file-path-' + Date.now();
            
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <span class="filename">${fileName}</span>
                    <span class="file-size">File Path: ${filePath}</span>
                </div>
                <button type="button" class="remove-file-btn" onclick="removeFilePath('${fileId}')">
                    Remove
                </button>
            `;
            fileItem.id = fileId;
            
            queue.innerHTML = ''; // Clear any existing items
            queue.appendChild(fileItem);
        }
        
        function removeFilePath(fileId) {
            const fileItem = document.getElementById(fileId);
            if (fileItem) {
                fileItem.remove();
            }
            
            // Clear the file path input
            const filePathInput = document.getElementById('file-path-input');
            if (filePathInput) {
                filePathInput.value = '';
            }
        }
        """
        return js
    
    def get_css(self):
        """Get CSS for file upload area styling.
        
        Returns:
            CSS code as string
        """
        css = """
        .file-upload-area {
            border: 2px dashed var(--border-glow);
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            background: var(--bg-secondary);
            transition: all 0.3s ease;
        }
        
        .file-upload-area.drag-over {
            border-color: var(--accent-green);
            background: rgba(0, 255, 136, 0.1);
        }
        
        .upload-queue {
            margin-top: 1rem;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border: 1px solid var(--border-glow);
            border-radius: 4px;
            margin-bottom: 0.5rem;
            background: var(--bg-tertiary);
        }
        
        .file-info {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }
        
        .filename {
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .file-size {
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        
        .remove-file-btn {
            background: var(--accent-amber);
            color: var(--bg-primary);
            border: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.875rem;
        }
        
        .remove-file-btn:hover {
            background: var(--accent-green);
        }
        
        .file-path-section {
            margin-bottom: 1rem;
        }
        
        .file-path-section .input-label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-primary);
            font-weight: 500;
        }
        
        .terminal-input {
            width: 100%;
            padding: 0.75rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-glow);
            border-radius: 4px;
            color: var(--text-primary);
            font-family: 'Courier New', monospace;
            font-size: 0.875rem;
        }
        
        .terminal-input:focus {
            outline: none;
            border-color: var(--accent-green);
            box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
        }
        
        .input-separator {
            text-align: center;
            margin: 1rem 0;
            color: var(--text-muted);
            font-weight: 500;
            position: relative;
        }
        
        .input-separator::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: var(--border-glow);
            z-index: 1;
        }
        
        .input-separator::after {
            content: 'OR';
            background: var(--bg-primary);
            padding: 0 1rem;
            position: relative;
            z-index: 2;
        }
        """
        return css


class FileUploadUI:
    """Main file upload UI component that combines toggle and upload area."""
    
    def __init__(self):
        """Initialize the complete file upload UI."""
        self.toggle = InputModeToggle()
        self.upload_area = FileUploadArea(enable_multiple=True)
    
    def render(self):
        """Render the complete file upload interface.
        
        Returns:
            HTML string for the complete interface
        """
        toggle_html = self.toggle.render()
        upload_area_html = self.upload_area.render()
        
        html = f"""
        <!-- Input Mode Toggle -->
        {toggle_html}
        
        <!-- File Upload Area (initially hidden) -->
        <div id="file-upload-container" style="display: none;">
            {upload_area_html}
        </div>
        
        <script>
        // Define toggle function globally to avoid conflicts
        window.toggleFileUploadMode = function(mode) {{
            const urlContainer = document.getElementById('url-input-group');
            const fileContainer = document.getElementById('file-upload-container');
            
            if (urlContainer && fileContainer) {{
                if (mode === 'url') {{
                    urlContainer.style.display = 'block';
                    fileContainer.style.display = 'none';
                    const urlsInput = document.getElementById('urls');
                    if (urlsInput) {{
                        urlsInput.required = true;
                    }}
                }} else {{
                    urlContainer.style.display = 'none';
                    fileContainer.style.display = 'block';
                    const urlsInput = document.getElementById('urls');
                    if (urlsInput) {{
                        urlsInput.required = false;
                    }}
                }}
            }}
        }}
        
        // Keep backward compatibility
        function toggleInputMode(mode) {{
            return window.toggleFileUploadMode(mode);
        }}
        
        {self.upload_area.get_javascript()}
        
        // Fix radio button event handling
        document.addEventListener('DOMContentLoaded', function() {{
            const fileRadio = document.getElementById('input-mode-file');
            const urlRadio = document.getElementById('input-mode-url');
            
            if (fileRadio) {{
                fileRadio.addEventListener('click', function() {{
                    console.log('File mode clicked');
                    window.toggleFileUploadMode('file');
                }});
            }}
            
            if (urlRadio) {{
                urlRadio.addEventListener('click', function() {{
                    console.log('URL mode clicked');
                    window.toggleFileUploadMode('url');
                }});
            }}
        }});
        </script>
        
        <style>
        {self.get_css()}
        </style>
        """
        return html
    
    def get_css(self):
        """Get CSS for the complete UI.
        
        Returns:
            CSS code as string
        """
        base_css = self.upload_area.get_css()
        
        additional_css = """
        #input-mode-toggle {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            padding: 0.5rem;
            background: var(--bg-secondary);
            border-radius: 8px;
            border: 1px solid var(--border-glow);
        }
        
        .mode-option {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 4px;
            transition: background 0.3s ease;
        }
        
        .mode-option:hover {
            background: var(--bg-tertiary);
        }
        
        .mode-option input[type="radio"] {
            accent-color: var(--accent-green);
        }
        
        .mode-option span {
            color: var(--text-primary);
            font-weight: 500;
        }
        
        @media (max-width: 768px) {
            #input-mode-toggle {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
        """
        
        return base_css + additional_css