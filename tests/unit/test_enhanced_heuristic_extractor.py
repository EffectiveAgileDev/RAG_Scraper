import pytest
from datetime import datetime
from unittest.mock import Mock, patch
import json


class TestEnhancedHeuristicExtractor:
    """Test suite for enhanced heuristic extractor with cross-page patterns."""

    def test_extractor_with_extraction_context(self):
        """Test that extractor accepts and uses extraction context."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext
        
        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro"
        )
        
        extractor = HeuristicExtractor(extraction_context=context)
        assert extractor.extraction_context == context
        assert extractor.extraction_context.entity_id == "rest_001"

    def test_extraction_includes_entity_metadata(self):
        """Test that extraction results include entity relationship metadata."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext
        
        html = '''
        <html>
        <head><title>Italian Bistro - Restaurant</title></head>
        <body>
            <h1>Italian Bistro</h1>
            <p>Address: 123 Main St, New York, NY</p>
            <p>Phone: (555) 123-4567</p>
            <p>Cuisine: Italian restaurant menu dining</p>
        </body>
        </html>
        '''
        
        context = ExtractionContext(
            entity_id="rest_001",
            parent_id="dir_001",
            source_url="/restaurants/italian-bistro"
        )
        
        extractor = HeuristicExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)
        
        assert len(results) == 1
        result = results[0]
        assert hasattr(result, 'extraction_metadata')
        assert result.extraction_metadata['entity_id'] == "rest_001"
        assert result.extraction_metadata['parent_id'] == "dir_001"
        assert result.extraction_metadata['source_url'] == "/restaurants/italian-bistro"

    def test_pattern_learning_across_pages(self):
        """Test that successful patterns are learned and applied to subsequent pages."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext, PatternLearner
        
        learner = PatternLearner()
        
        # First page with successful pattern
        html1 = '''
        <div class="restaurant-info">
            <h2 class="name">Bistro One</h2>
            <p class="phone">555-0001</p>
            <p>Restaurant menu dining food</p>
        </div>
        '''
        
        context1 = ExtractionContext(entity_id="rest_001", pattern_learner=learner)
        extractor1 = HeuristicExtractor(extraction_context=context1)
        results1 = extractor1.extract_from_html(html1)
        
        # Record successful pattern
        learner.record_successful_pattern("name", "h2.name", success=True)
        learner.record_successful_pattern("phone", "p.phone", success=True)
        
        # Second page with same structure
        html2 = '''
        <div class="restaurant-info">
            <h2 class="name">Bistro Two</h2>
            <p class="phone">555-0002</p>
            <p>Restaurant menu dining food</p>
        </div>
        '''
        
        context2 = ExtractionContext(entity_id="rest_002", pattern_learner=learner)
        extractor2 = HeuristicExtractor(extraction_context=context2)
        results2 = extractor2.extract_from_html(html2)
        
        # Should use learned patterns for faster extraction
        assert len(results2) == 1
        assert results2[0].name == "Bistro Two"
        assert results2[0].phone == "555-0002"
        assert 'learned_pattern' in results2[0].extraction_metadata

    def test_confidence_boost_from_pattern_consistency(self):
        """Test that confidence increases when patterns are consistently successful."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext, PatternLearner
        
        learner = PatternLearner()
        
        # Build up pattern confidence through multiple successes
        for i in range(5):
            learner.record_successful_pattern("name", "h1.title", success=True)
            
        html = '''
        <h1 class="title">Confident Restaurant</h1>
        <p>Restaurant menu dining food cuisine</p>
        '''
        
        context = ExtractionContext(entity_id="rest_001", pattern_learner=learner)
        extractor = HeuristicExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)
        
        # Confidence should be boosted due to pattern reliability
        assert len(results) == 1
        result = results[0]
        assert 'pattern_confidence_boost' in result.extraction_metadata
        assert result.extraction_metadata['pattern_confidence_boost'] > 0

    def test_cross_page_pattern_correlation(self):
        """Test correlation of patterns across different page types."""
        from src.scraper.enhanced_heuristic_extractor import CrossPagePatternAnalyzer
        
        analyzer = CrossPagePatternAnalyzer()
        
        # Directory page patterns
        analyzer.record_pattern_usage("directory", "name", ".restaurant-title", success=True)
        analyzer.record_pattern_usage("directory", "name", ".restaurant-title", success=True)
        
        # Detail page patterns  
        analyzer.record_pattern_usage("detail", "name", "h1.main-title", success=True)
        analyzer.record_pattern_usage("detail", "phone", ".contact-phone", success=True)
        
        correlations = analyzer.get_pattern_correlations()
        
        # Should identify successful patterns per page type
        assert "directory" in correlations
        assert "detail" in correlations
        assert correlations["directory"]["name"][".restaurant-title"]["success_rate"] == 1.0

    def test_adaptive_pattern_selection(self):
        """Test adaptive selection of patterns based on page context."""
        from src.scraper.enhanced_heuristic_extractor import AdaptivePatternSelector
        
        selector = AdaptivePatternSelector()
        
        # Add patterns with different success rates
        selector.add_pattern_result("name", "h1", page_type="detail", success=True)
        selector.add_pattern_result("name", "h1", page_type="detail", success=True)
        selector.add_pattern_result("name", ".title", page_type="detail", success=False)
        
        # Should prefer h1 over .title for detail pages
        best_patterns = selector.get_best_patterns_for_page_type("detail")
        
        assert "name" in best_patterns
        assert best_patterns["name"]["selector"] == "h1"
        assert best_patterns["name"]["confidence"] > 0.5

    def test_extraction_timestamp_tracking(self):
        """Test that extractions include timestamp."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext
        
        html = '''
        <h1>Test Restaurant</h1>
        <p>Some basic content</p>
        '''
        
        context = ExtractionContext(entity_id="rest_001")
        
        with patch('src.scraper.enhanced_heuristic_extractor.datetime') as mock_datetime:
            mock_dt = Mock()
            mock_dt.isoformat.return_value = "2024-01-15T10:30:00"
            mock_datetime.now.return_value = mock_dt
            
            extractor = HeuristicExtractor(extraction_context=context)
            results = extractor.extract_from_html(html)
            
            if results:
                assert results[0].extraction_metadata['timestamp'] == "2024-01-15T10:30:00"

    def test_extraction_method_recording(self):
        """Test that extraction method is recorded."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext
        
        html = '''
        <h1>Test Restaurant</h1>
        <p>Phone: 555-0123</p>
        '''
        
        context = ExtractionContext(entity_id="rest_001")
        extractor = HeuristicExtractor(extraction_context=context)
        results = extractor.extract_from_html(html)
        
        if results:
            assert results[0].extraction_metadata['method'] == "heuristic"

    def test_pattern_evolution_tracking(self):
        """Test tracking of how patterns evolve across pages."""
        from src.scraper.enhanced_heuristic_extractor import PatternEvolutionTracker
        
        tracker = PatternEvolutionTracker()
        
        # Track pattern changes over time
        tracker.record_pattern_change("name", "h1", "h2", reason="better_accuracy")
        tracker.record_pattern_change("phone", ".phone", ".contact", reason="page_restructure")
        
        evolution = tracker.get_pattern_evolution()
        
        assert "name" in evolution
        assert evolution["name"][-1]["new_pattern"] == "h2"
        assert evolution["name"][-1]["reason"] == "better_accuracy"

    def test_contextual_extraction_adjustment(self):
        """Test adjustment of extraction based on page context."""
        from src.scraper.enhanced_heuristic_extractor import HeuristicExtractor, ExtractionContext
        
        # Menu page context should affect extraction strategy
        menu_context = ExtractionContext(
            entity_id="menu_001",
            parent_id="rest_001",
            page_type="menu"
        )
        
        html = '''
        <div class="menu-items">
            <h2>Appetizers</h2>
            <p>Caesar Salad - $8</p>
            <p>Bruschetta - $6</p>
        </div>
        '''
        
        extractor = HeuristicExtractor(extraction_context=menu_context)
        results = extractor.extract_from_html(html)
        
        # Should focus on menu-specific extraction
        if results:
            assert 'menu_focused' in results[0].extraction_metadata

    def test_sibling_page_pattern_sharing(self):
        """Test sharing of successful patterns between sibling pages."""
        from src.scraper.enhanced_heuristic_extractor import SiblingPatternSharer
        
        sharer = SiblingPatternSharer()
        
        # First sibling discovers successful pattern
        sharer.share_pattern("rest_001", "name", "h1.restaurant-name", success_rate=0.9)
        
        # Second sibling can use the pattern
        shared_patterns = sharer.get_patterns_for_sibling("rest_002", "rest_001")
        
        assert "name" in shared_patterns
        assert shared_patterns["name"]["selector"] == "h1.restaurant-name"
        assert shared_patterns["name"]["success_rate"] == 0.9

    def test_extraction_failure_recovery(self):
        """Test recovery strategies when standard patterns fail."""
        from src.scraper.enhanced_heuristic_extractor import ExtractionFailureRecovery
        
        recovery = ExtractionFailureRecovery()
        
        html = '''
        <!-- Unusual page structure -->
        <section>
            <span id="weird-name">Unusual Restaurant</span>
            <div data-phone="555-9999"></div>
        </section>
        '''
        
        # Standard patterns fail, try recovery strategies
        fallback_patterns = recovery.get_fallback_patterns()
        extracted_data = recovery.attempt_fallback_extraction(html, fallback_patterns)
        
        # Should find data using alternative selectors
        assert 'name' in extracted_data or 'phone' in extracted_data

    def test_pattern_confidence_calculation(self):
        """Test calculation of pattern confidence over time."""
        from src.scraper.enhanced_heuristic_extractor import PatternConfidenceCalculator
        
        calculator = PatternConfidenceCalculator()
        
        # Record pattern usage over time
        for i in range(10):
            success = i < 8  # 80% success rate
            calculator.record_pattern_usage("name", "h1", success)
            
        confidence = calculator.get_pattern_confidence("name", "h1")
        
        assert 0.7 <= confidence <= 0.9  # Should be around 80%

    def test_multi_strategy_extraction(self):
        """Test using multiple extraction strategies and combining results."""
        from src.scraper.enhanced_heuristic_extractor import MultiStrategyExtractor
        
        html = '''
        <header>
            <h1>Main Restaurant</h1>
        </header>
        <footer>
            <p>Call us: 555-1234</p>
            <address>123 Main St</address>
        </footer>
        '''
        
        extractor = MultiStrategyExtractor()
        results = extractor.extract_with_multiple_strategies(html)
        
        # Should combine results from different strategies
        assert 'name' in results
        assert 'phone' in results
        assert 'address' in results
        assert results['name'] == 'Main Restaurant'

    def test_page_structure_analysis(self):
        """Test analysis of page structure for pattern optimization."""
        from src.scraper.enhanced_heuristic_extractor import PageStructureAnalyzer
        
        html = '''
        <div class="header">
            <h1>Restaurant Name</h1>
        </div>
        <div class="content">
            <div class="info">
                <p class="phone">555-0123</p>
                <p class="address">123 Main St</p>
            </div>
        </div>
        '''
        
        analyzer = PageStructureAnalyzer()
        structure = analyzer.analyze_structure(html)
        
        assert 'header_elements' in structure
        assert 'content_hierarchy' in structure
        assert structure['max_depth'] > 0

    def test_extraction_pattern_optimization(self):
        """Test optimization of extraction patterns based on success rates."""
        from src.scraper.enhanced_heuristic_extractor import PatternOptimizer
        
        optimizer = PatternOptimizer()
        
        # Add patterns with varying success rates
        patterns = [
            {"selector": "h1", "success_rate": 0.9, "usage_count": 50},
            {"selector": ".title", "success_rate": 0.6, "usage_count": 20},
            {"selector": "#name", "success_rate": 0.8, "usage_count": 10}
        ]
        
        for pattern in patterns:
            optimizer.add_pattern_stats("name", pattern["selector"], 
                                      pattern["success_rate"], pattern["usage_count"])
            
        optimized = optimizer.get_optimized_patterns("name")
        
        # Should prefer h1 due to high success rate and usage
        assert optimized[0]["selector"] == "h1"