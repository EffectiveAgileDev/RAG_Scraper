"""Unit tests for file security scanner component."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO

# This will fail until we implement the actual classes
try:
    from src.file_processing.file_security_scanner import FileSecurityScanner, ScanResult
except ImportError:
    # Expected to fail in RED phase - components don't exist yet
    FileSecurityScanner = None
    ScanResult = None


class TestFileSecurityScanner:
    """Test cases for FileSecurityScanner class."""

    @pytest.fixture
    def clean_pdf_content(self):
        """Clean PDF content for testing."""
        return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n173\n%%EOF"

    @pytest.fixture
    def suspicious_content(self):
        """Suspicious content that might trigger security warnings."""
        return b"<script>alert('xss')</script>malicious content here"

    @pytest.fixture
    def clean_pdf_file(self, clean_pdf_content):
        """Clean PDF FileStorage for testing."""
        return FileStorage(
            stream=BytesIO(clean_pdf_content),
            filename="clean_menu.pdf",
            content_type="application/pdf"
        )

    @pytest.fixture
    def suspicious_file(self, suspicious_content):
        """Suspicious file for testing."""
        return FileStorage(
            stream=BytesIO(suspicious_content),
            filename="suspicious.pdf",
            content_type="application/pdf"
        )

    @pytest.fixture
    def file_security_scanner(self):
        """Create FileSecurityScanner instance for testing."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        return FileSecurityScanner(
            enable_clamav=False,  # Disable external scanner for unit tests
            enable_yara_rules=True,
            max_scan_size=50 * 1024 * 1024,  # 50MB
            scan_timeout=30
        )

    def test_file_security_scanner_initialization(self):
        """Test FileSecurityScanner initializes correctly."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        scanner = FileSecurityScanner(
            enable_clamav=True,
            enable_yara_rules=True,
            max_scan_size=100 * 1024 * 1024
        )
        
        assert scanner.enable_clamav is True
        assert scanner.enable_yara_rules is True
        assert scanner.max_scan_size == 100 * 1024 * 1024

    def test_scan_clean_file_success(self, file_security_scanner, clean_pdf_file):
        """Test scanning a clean file returns safe result."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        result = file_security_scanner.scan_file(clean_pdf_file)
        
        assert isinstance(result, ScanResult)
        assert result.is_safe is True
        assert len(result.threats_found) == 0
        assert result.scan_method is not None

    def test_scan_suspicious_file_detection(self, file_security_scanner, suspicious_file):
        """Test scanning a suspicious file detects threats."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        with patch.object(file_security_scanner, '_scan_with_yara') as mock_yara:
            mock_yara.return_value = ['Suspicious.Script.Found']
            
            result = file_security_scanner.scan_file(suspicious_file)
            
            assert result.is_safe is False
            assert len(result.threats_found) > 0
            assert 'Suspicious.Script.Found' in result.threats_found

    def test_scan_file_too_large(self, file_security_scanner):
        """Test scanning a file that exceeds size limit."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Create a large file that exceeds the scanner's limit
        large_content = b"X" * (60 * 1024 * 1024)  # 60MB
        large_file = FileStorage(
            stream=BytesIO(large_content),
            filename="large_file.pdf",
            content_type="application/pdf"
        )
        
        result = file_security_scanner.scan_file(large_file)
        
        assert result.is_safe is False
        assert any("size" in threat.lower() for threat in result.threats_found)

    @patch('src.file_processing.file_security_scanner.subprocess.run')
    def test_scan_with_clamav_clean(self, mock_subprocess, file_security_scanner, clean_pdf_content):
        """Test ClamAV scanning with clean result."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Enable ClamAV for this test
        file_security_scanner.enable_clamav = True
        
        # Mock clean ClamAV result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test_file.pdf: OK"
        mock_subprocess.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(clean_pdf_content)
            temp_file.flush()
            
            try:
                threats = file_security_scanner._scan_with_clamav(temp_file.name)
                assert threats == []
            finally:
                os.unlink(temp_file.name)

    @patch('src.file_processing.file_security_scanner.subprocess.run')
    def test_scan_with_clamav_threat_detected(self, mock_subprocess, file_security_scanner, suspicious_content):
        """Test ClamAV scanning with threat detection."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Enable ClamAV for this test
        file_security_scanner.enable_clamav = True
        
        # Mock threat detection result
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "test_file.pdf: Eicar-Test-Signature FOUND"
        mock_subprocess.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(suspicious_content)
            temp_file.flush()
            
            try:
                threats = file_security_scanner._scan_with_clamav(temp_file.name)
                assert "Eicar-Test-Signature" in threats[0]
            finally:
                os.unlink(temp_file.name)

    def test_scan_with_yara_rules_clean(self, file_security_scanner, clean_pdf_content):
        """Test YARA rule scanning with clean content."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(clean_pdf_content)
            temp_file.flush()
            
            try:
                threats = file_security_scanner._scan_with_yara(temp_file.name)
                assert threats == []
            finally:
                os.unlink(temp_file.name)

    def test_scan_with_yara_rules_threat(self, file_security_scanner, suspicious_content):
        """Test YARA rule scanning with suspicious content."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Test the actual YARA scanning logic (simulated pattern matching)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(suspicious_content)
            temp_file.flush()
            
            try:
                threats = file_security_scanner._scan_with_yara(temp_file.name)
                # Should detect SuspiciousScript from the <script> tag
                assert "SuspiciousScript" in threats
                # Should also detect the word "malicious"
                assert "SuspiciousContent" in threats
            finally:
                os.unlink(temp_file.name)

    def test_scan_file_with_timeout(self, file_security_scanner, clean_pdf_file):
        """Test file scanning with timeout configuration."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        file_security_scanner.scan_timeout = 1  # 1 second timeout
        
        with patch.object(file_security_scanner, '_scan_with_yara') as mock_yara:
            # Simulate long-running scan
            import time
            def slow_scan(filepath):
                time.sleep(2)  # Longer than timeout
                return []
            
            mock_yara.side_effect = slow_scan
            
            result = file_security_scanner.scan_file(clean_pdf_file)
            
            # Should handle timeout gracefully
            assert result.is_safe is False
            assert any("timeout" in threat.lower() for threat in result.threats_found)

    def test_get_file_hash(self, file_security_scanner, clean_pdf_content):
        """Test file hash calculation."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(clean_pdf_content)
            temp_file.flush()
            
            try:
                hash_value = file_security_scanner.get_file_hash(temp_file.name)
                assert len(hash_value) == 64  # SHA-256 hash
                assert hash_value.isalnum()
            finally:
                os.unlink(temp_file.name)

    def test_check_file_reputation(self, file_security_scanner):
        """Test file reputation checking."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Test with known safe hash
        safe_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # Empty file hash
        reputation = file_security_scanner.check_file_reputation(safe_hash)
        
        assert reputation['status'] in ['clean', 'unknown']

    def test_quarantine_suspicious_file(self, file_security_scanner, suspicious_content):
        """Test quarantining suspicious files."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(suspicious_content)
            temp_file.flush()
            original_path = temp_file.name
            
            try:
                quarantine_path = file_security_scanner.quarantine_file(original_path)
                
                assert quarantine_path is not None
                assert quarantine_path != original_path
                assert not os.path.exists(original_path)  # Original should be moved
                assert os.path.exists(quarantine_path)    # Should exist in quarantine
                
                # Cleanup quarantine
                os.unlink(quarantine_path)
            except FileNotFoundError:
                # Original file was moved, which is expected
                pass

    def test_scan_multiple_files_batch(self, file_security_scanner, clean_pdf_content):
        """Test batch scanning of multiple files."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Create multiple test files
        temp_files = []
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(clean_pdf_content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        try:
            file_storages = []
            for temp_file in temp_files:
                with open(temp_file, 'rb') as f:
                    file_storage = FileStorage(
                        stream=BytesIO(f.read()),
                        filename=os.path.basename(temp_file),
                        content_type="application/pdf"
                    )
                    file_storages.append(file_storage)
            
            results = file_security_scanner.scan_multiple_files(file_storages)
            
            assert len(results) == 3
            for result in results:
                assert result.is_safe is True
                
        finally:
            # Cleanup
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except FileNotFoundError:
                    pass

    def test_update_threat_signatures(self, file_security_scanner):
        """Test threat signature updates."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "rule TestRule { condition: true }"
            mock_get.return_value = mock_response
            
            success = file_security_scanner.update_threat_signatures()
            
            assert success is True

    def test_get_scan_statistics(self, file_security_scanner, clean_pdf_file):
        """Test retrieval of scan statistics."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        # Perform some scans
        file_security_scanner.scan_file(clean_pdf_file)
        file_security_scanner.scan_file(clean_pdf_file)
        
        stats = file_security_scanner.get_scan_statistics()
        
        assert stats['total_scans'] >= 2
        assert stats['clean_files'] >= 2
        assert 'scan_time_average' in stats

    def test_configure_custom_yara_rules(self, file_security_scanner):
        """Test configuration of custom YARA rules."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        custom_rules = """
        rule CustomRule {
            strings:
                $suspicious = "malicious"
            condition:
                $suspicious
        }
        """
        
        success = file_security_scanner.add_custom_yara_rules(custom_rules)
        assert success is True

    def test_whitelist_file_hash(self, file_security_scanner, clean_pdf_content):
        """Test whitelisting file hashes."""
        if FileSecurityScanner is None:
            pytest.skip("FileSecurityScanner not implemented yet (expected in RED phase)")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(clean_pdf_content)
            temp_file.flush()
            
            try:
                file_hash = file_security_scanner.get_file_hash(temp_file.name)
                file_security_scanner.add_to_whitelist(file_hash)
                
                # File should now be automatically considered safe
                file_storage = FileStorage(
                    stream=BytesIO(clean_pdf_content),
                    filename="whitelisted.pdf",
                    content_type="application/pdf"
                )
                
                result = file_security_scanner.scan_file(file_storage)
                assert result.is_safe is True
                assert "whitelisted" in result.scan_details.lower()
                
            finally:
                os.unlink(temp_file.name)


class TestScanResult:
    """Test cases for ScanResult class."""

    def test_scan_result_clean(self):
        """Test ScanResult for clean file."""
        if ScanResult is None:
            pytest.skip("ScanResult not implemented yet (expected in RED phase)")
        
        result = ScanResult(
            is_safe=True,
            threats_found=[],
            scan_method='yara',
            scan_time=1.2,
            file_hash='abc123'
        )
        
        assert result.is_safe is True
        assert len(result.threats_found) == 0
        assert result.scan_method == 'yara'
        assert result.scan_time == 1.2
        assert result.file_hash == 'abc123'

    def test_scan_result_threats_found(self):
        """Test ScanResult with threats detected."""
        if ScanResult is None:
            pytest.skip("ScanResult not implemented yet (expected in RED phase)")
        
        result = ScanResult(
            is_safe=False,
            threats_found=['Malware.Generic.Threat', 'Trojan.PDF.Exploit'],
            scan_method='clamav',
            scan_time=2.5,
            file_hash='def456'
        )
        
        assert result.is_safe is False
        assert len(result.threats_found) == 2
        assert 'Malware.Generic.Threat' in result.threats_found
        assert 'Trojan.PDF.Exploit' in result.threats_found

    def test_scan_result_to_dict(self):
        """Test ScanResult to dictionary conversion."""
        if ScanResult is None:
            pytest.skip("ScanResult not implemented yet (expected in RED phase)")
        
        result = ScanResult(
            is_safe=True,
            threats_found=[],
            scan_method='yara'
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['is_safe'] is True
        assert result_dict['threats_found'] == []
        assert result_dict['scan_method'] == 'yara'

    def test_scan_result_string_representation(self):
        """Test string representation of ScanResult."""
        if ScanResult is None:
            pytest.skip("ScanResult not implemented yet (expected in RED phase)")
        
        result = ScanResult(
            is_safe=False,
            threats_found=['Test.Threat'],
            scan_method='test'
        )
        
        str_repr = str(result)
        assert "Test.Threat" in str_repr
        assert "unsafe" in str_repr.lower() or "threat" in str_repr.lower()