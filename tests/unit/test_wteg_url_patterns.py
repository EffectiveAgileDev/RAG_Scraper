"""Unit tests for WTEG URL pattern recognition system.

Following TDD approach: Write failing tests first for URL pattern matching.
"""
import pytest
from typing import List, Dict


class TestWTEGURLPatterns:
    """Test WTEG URL pattern recognition and construction."""
    
    def test_wteg_url_pattern_parser_exists(self):
        """Test that WTEGURLPatternParser class exists."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            assert parser is not None, "WTEGURLPatternParser should be instantiable"
            
        except ImportError:
            pytest.fail("WTEGURLPatternParser class not implemented yet")
    
    def test_pattern_name_and_city_input(self):
        """Test pattern name and city input functionality."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            
            # Test setting pattern and city
            parser.set_pattern("WTEG")
            parser.set_city("Portland")
            
            assert parser.pattern_name == "wteg", "Pattern name should be normalized to lowercase"
            assert parser.city_name == "portland", "City name should be normalized to lowercase"
            
        except ImportError:
            pytest.fail("Pattern and city input not implemented yet")
    
    def test_url_construction_format(self):
        """Test URL construction with pattern/city/page_id format."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            parser.set_pattern("WTEG")
            parser.set_city("Portland")
            
            # Test URL construction
            url_1 = parser.construct_url(1)
            url_21 = parser.construct_url(21)
            url_16 = parser.construct_url(16)
            
            expected_1 = "https://mobimag.co/wteg/portland/1"
            expected_21 = "https://mobimag.co/wteg/portland/21"
            expected_16 = "https://mobimag.co/wteg/portland/16"
            
            assert url_1 == expected_1, f"URL 1 should be {expected_1}, got {url_1}"
            assert url_21 == expected_21, f"URL 21 should be {expected_21}, got {url_21}"
            assert url_16 == expected_16, f"URL 16 should be {expected_16}, got {url_16}"
            
        except ImportError:
            pytest.fail("URL construction not implemented yet")
    
    def test_url_pattern_validation(self):
        """Test validation of WTEG URL patterns."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            
            # Test valid WTEG URLs
            valid_urls = [
                "https://mobimag.co/wteg/portland/1",
                "https://mobimag.co/wteg/portland/21",
                "https://mobimag.co/wteg/portland/16",
                "https://mobimag.co/wteg/seattle/5",
                "https://mobimag.co/wteg/denver/10"
            ]
            
            for url in valid_urls:
                assert parser.is_wteg_url(url), f"URL should be valid WTEG URL: {url}"
            
            # Test invalid URLs
            invalid_urls = [
                "https://example.com/restaurant",
                "https://mobimag.co/other/portland/1",
                "https://mobimag.co/wteg/portland",  # Missing page ID
                "https://different-site.com/wteg/portland/1"
            ]
            
            for url in invalid_urls:
                assert not parser.is_wteg_url(url), f"URL should be invalid WTEG URL: {url}"
                
        except ImportError:
            pytest.fail("URL pattern validation not implemented yet")
    
    def test_extract_pattern_city_page_from_url(self):
        """Test extraction of pattern, city, and page ID from WTEG URLs."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            
            test_cases = [
                {
                    "url": "https://mobimag.co/wteg/portland/21",
                    "expected": {"pattern": "wteg", "city": "portland", "page_id": "21"}
                },
                {
                    "url": "https://mobimag.co/wteg/seattle/5",
                    "expected": {"pattern": "wteg", "city": "seattle", "page_id": "5"}
                },
                {
                    "url": "https://mobimag.co/wteg/denver/10",
                    "expected": {"pattern": "wteg", "city": "denver", "page_id": "10"}
                }
            ]
            
            for test_case in test_cases:
                result = parser.parse_url(test_case["url"])
                expected = test_case["expected"]
                
                assert result["pattern"] == expected["pattern"], f"Pattern mismatch for {test_case['url']}"
                assert result["city"] == expected["city"], f"City mismatch for {test_case['url']}"
                assert result["page_id"] == expected["page_id"], f"Page ID mismatch for {test_case['url']}"
                
        except ImportError:
            pytest.fail("URL parsing not implemented yet")
    
    def test_multi_page_url_generation(self):
        """Test generation of multiple page URLs for complete scraping."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            parser.set_pattern("WTEG")
            parser.set_city("Portland")
            
            # Test generating multiple URLs
            page_range = [1, 2, 3, 4, 5]
            urls = parser.generate_url_range(page_range)
            
            expected_urls = [
                "https://mobimag.co/wteg/portland/1",
                "https://mobimag.co/wteg/portland/2",
                "https://mobimag.co/wteg/portland/3",
                "https://mobimag.co/wteg/portland/4",
                "https://mobimag.co/wteg/portland/5"
            ]
            
            assert urls == expected_urls, f"URL range should match expected URLs"
            
            # Test with specific page IDs (like client's 21, 16)
            specific_pages = [16, 21]
            specific_urls = parser.generate_url_range(specific_pages)
            
            expected_specific = [
                "https://mobimag.co/wteg/portland/16",
                "https://mobimag.co/wteg/portland/21"
            ]
            
            assert specific_urls == expected_specific, f"Specific URLs should match expected URLs"
            
        except ImportError:
            pytest.fail("Multi-page URL generation not implemented yet")
    
    def test_wteg_page_aggregation_strategy(self):
        """Test strategy for aggregating data from multiple WTEG pages."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            
            # Test aggregation modes
            aggregation_modes = ["single_page", "multi_page", "page_range", "all_available"]
            
            for mode in aggregation_modes:
                assert hasattr(parser, f"set_{mode}_mode"), f"Parser should have {mode}_mode method"
            
            # Test single page mode (just scrape one URL)
            parser.set_pattern("WTEG")
            parser.set_city("Portland")
            parser.set_single_page_mode(21)
            urls = parser.get_urls_to_scrape()
            assert len(urls) == 1, "Single page mode should return one URL"
            assert "21" in urls[0], "Single page mode should include specified page ID"
            
            # Test page range mode (scrape specific range)
            parser.set_page_range_mode([16, 21])
            urls = parser.get_urls_to_scrape()
            assert len(urls) == 2, "Page range mode should return specified number of URLs"
            
        except ImportError:
            pytest.fail("Page aggregation strategy not implemented yet")
    
    def test_wteg_pattern_case_handling(self):
        """Test handling of different case variations for pattern and city."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            
            # Test case normalization
            test_cases = [
                {"input_pattern": "WTEG", "input_city": "PORTLAND", "expected_pattern": "wteg", "expected_city": "portland"},
                {"input_pattern": "wteg", "input_city": "portland", "expected_pattern": "wteg", "expected_city": "portland"},
                {"input_pattern": "Wteg", "input_city": "Portland", "expected_pattern": "wteg", "expected_city": "portland"}
            ]
            
            for test_case in test_cases:
                parser.set_pattern(test_case["input_pattern"])
                parser.set_city(test_case["input_city"])
                
                url = parser.construct_url(1)
                
                assert test_case["expected_pattern"] in url, f"Pattern should be normalized to lowercase"
                assert test_case["expected_city"] in url, f"City should be normalized to lowercase"
                
        except ImportError:
            pytest.fail("Case handling not implemented yet")
    
    def test_wteg_url_validation_edge_cases(self):
        """Test edge cases for WTEG URL validation."""
        try:
            from src.wteg.wteg_url_patterns import WTEGURLPatternParser
            
            parser = WTEGURLPatternParser()
            
            # Test edge cases
            edge_cases = [
                {"url": "https://mobimag.co/wteg/portland/0", "valid": True, "reason": "Page 0 should be valid"},
                {"url": "https://mobimag.co/wteg/portland/999", "valid": True, "reason": "High page numbers should be valid"},
                {"url": "https://mobimag.co/wteg/portland/-1", "valid": False, "reason": "Negative page numbers should be invalid"},
                {"url": "https://mobimag.co/wteg/portland/abc", "valid": False, "reason": "Non-numeric page IDs should be invalid"},
                {"url": "https://mobimag.co/wteg//1", "valid": False, "reason": "Empty city should be invalid"},
                {"url": "https://mobimag.co//portland/1", "valid": False, "reason": "Empty pattern should be invalid"}
            ]
            
            for case in edge_cases:
                result = parser.is_wteg_url(case["url"])
                assert result == case["valid"], f"{case['reason']}: {case['url']}"
                
        except ImportError:
            pytest.fail("Edge case validation not implemented yet")


if __name__ == "__main__":
    pytest.main([__file__])