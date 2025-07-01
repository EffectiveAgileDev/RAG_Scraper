#!/usr/bin/env python3
"""
Performance test for optimized multi-modal processing.

This script demonstrates the performance improvements made during refactoring:
1. Parallel processing for multiple images/PDFs
2. Lazy initialization of processors
3. Optimized regex patterns and text processing
4. Caching and memoization
5. Fast-path optimizations for single items
"""

import sys
import os
import time
from unittest.mock import Mock

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.processors.multi_modal_processor import MultiModalProcessor
from src.processors.ocr_processor import OCRProcessor, TextLayoutAnalyzer
from src.scraper.ai_enhanced_multi_strategy_scraper import AIEnhancedMultiStrategyScraper


def benchmark_ocr_processing():
    """Benchmark OCR processing improvements."""
    print("🔬 OCR Processing Performance Test")
    print("-" * 40)
    
    # Test text layout analyzer with optimized patterns
    analyzer = TextLayoutAnalyzer()
    
    sample_text = """
    APPETIZERS
    Caesar Salad - $12.00
    Soup of the Day - $8.00
    
    MAIN COURSES
    • Grilled Salmon - $24.00
    • Pasta Primavera - $18.00
    • Grass-fed Burger - $16.00
    
    DESSERTS
    1. Chocolate Cake - $8.00
    2. Ice Cream - $6.00
    
    CONTACT INFO
    John Smith, Manager
    Phone: (555) 123-4567
    Email: john@restaurant.com
    123 Main Street, Downtown
    """
    
    # Benchmark text block detection
    start_time = time.time()
    for _ in range(100):  # Run 100 times
        blocks = analyzer.detect_text_blocks(sample_text)
    block_time = time.time() - start_time
    
    print(f"✓ Text block detection (100 runs): {block_time:.4f}s")
    print(f"  • Found {len(blocks)} text blocks")
    
    # Benchmark price extraction
    start_time = time.time()
    for _ in range(100):
        prices = analyzer.extract_price_patterns(sample_text)
    price_time = time.time() - start_time
    
    print(f"✓ Price extraction (100 runs): {price_time:.4f}s")
    print(f"  • Found {len(prices)} prices: {prices}")
    
    # Benchmark contact extraction
    start_time = time.time()
    for _ in range(100):
        contacts = analyzer.extract_contact_patterns(sample_text)
    contact_time = time.time() - start_time
    
    print(f"✓ Contact extraction (100 runs): {contact_time:.4f}s")
    print(f"  • Found phones: {contacts['phones']}")
    print(f"  • Found emails: {contacts['emails']}")
    

def benchmark_parallel_processing():
    """Benchmark parallel vs sequential processing."""
    print("\n🚀 Parallel Processing Performance Test")
    print("-" * 40)
    
    processor = MultiModalProcessor(max_workers=4)
    
    # Create test data for multiple images
    test_images = [
        {"url": f"menu-{i}.jpg", "category": "menu", "alt": "Restaurant menu"}
        for i in range(10)
    ]
    
    test_pdfs = [f"brochure-{i}.pdf" for i in range(5)]
    
    # Test single image processing (fast path)
    start_time = time.time()
    single_result = processor.extract_text_from_images([test_images[0]])
    single_time = time.time() - start_time
    print(f"✓ Single image OCR: {single_time:.4f}s")
    
    # Test multiple image processing (parallel)
    start_time = time.time()
    multi_result = processor.extract_text_from_images(test_images)
    multi_time = time.time() - start_time
    print(f"✓ Multiple images OCR (10 images): {multi_time:.4f}s")
    print(f"  • Average per image: {multi_time/len(test_images):.4f}s")
    
    # Test PDF processing
    start_time = time.time()
    pdf_result = processor.process_pdfs(test_pdfs)
    pdf_time = time.time() - start_time
    print(f"✓ Multiple PDFs processing (5 PDFs): {pdf_time:.4f}s")
    print(f"  • Average per PDF: {pdf_time/len(test_pdfs):.4f}s")
    

def benchmark_lazy_initialization():
    """Benchmark lazy initialization performance."""
    print("\n⚡ Lazy Initialization Performance Test")
    print("-" * 40)
    
    # Test cold start (first access to processors)
    start_time = time.time()
    processor = MultiModalProcessor()
    init_time = time.time() - start_time
    print(f"✓ MultiModalProcessor creation: {init_time:.4f}s")
    
    # Test lazy OCR processor access
    start_time = time.time()
    ocr = processor.ocr_processor  # First access triggers initialization
    ocr_init_time = time.time() - start_time
    print(f"✓ OCR processor lazy init: {ocr_init_time:.4f}s")
    
    # Test subsequent access (should be instant)
    start_time = time.time()
    ocr2 = processor.ocr_processor  # Subsequent access
    ocr_cached_time = time.time() - start_time
    print(f"✓ OCR processor cached access: {ocr_cached_time:.6f}s")
    
    # Test image analyzer lazy init
    start_time = time.time()
    analyzer = processor.image_analyzer
    analyzer_time = time.time() - start_time
    print(f"✓ Image analyzer lazy init: {analyzer_time:.4f}s")
    
    # Test PDF processor lazy init
    start_time = time.time()
    pdf = processor.pdf_processor
    pdf_time = time.time() - start_time
    print(f"✓ PDF processor lazy init: {pdf_time:.4f}s")


def benchmark_media_extraction():
    """Benchmark optimized media extraction."""
    print("\n📋 Media Extraction Performance Test")
    print("-" * 40)
    
    scraper = AIEnhancedMultiStrategyScraper(enable_multi_modal=True)
    
    # Large HTML sample with many media files
    large_html = """
    <!DOCTYPE html>
    <html><body>
    """ + "\n".join([
        f'<img src="/images/menu-{i}.jpg" alt="Menu item {i}">'
        f'<img src="/images/interior-{i}.jpg" alt="Restaurant ambiance {i}">'
        f'<img src="/images/hours-{i}.png" alt="Business hours {i}">'
        f'<a href="/docs/brochure-{i}.pdf">Services Brochure {i}</a>'
        f'<a href="/menus/wine-{i}.pdf">Wine Menu {i}</a>'
        for i in range(20)  # 100 media files total
    ]) + """
    </body></html>
    """
    
    # Benchmark media extraction
    start_time = time.time()
    media_files = scraper._extract_media_from_html(large_html)
    extraction_time = time.time() - start_time
    
    print(f"✓ Media extraction from large HTML: {extraction_time:.4f}s")
    print(f"  • Found {len(media_files)} media files")
    
    # Count by type and category
    images = [m for m in media_files if m["type"] == "image"]
    pdfs = [m for m in media_files if m["type"] == "pdf"]
    
    print(f"  • Images: {len(images)}")
    print(f"  • PDFs: {len(pdfs)}")
    
    # Test category distribution
    categories = {}
    for media in media_files:
        cat = media["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"  • Categories: {categories}")


def benchmark_caching():
    """Benchmark caching performance."""
    print("\n💾 Caching Performance Test")
    print("-" * 40)
    
    # Create OCR processor with caching enabled
    processor = OCRProcessor(enable_caching=True)
    
    test_url = "menu-sample.jpg"
    
    # First extraction (cache miss)
    start_time = time.time()
    result1 = processor.extract_text_from_image(test_url, content_type="menu")
    first_time = time.time() - start_time
    print(f"✓ First OCR extraction (cache miss): {first_time:.4f}s")
    
    # Second extraction (cache hit)
    start_time = time.time()
    result2 = processor.extract_text_from_image(test_url, content_type="menu")
    second_time = time.time() - start_time
    print(f"✓ Second OCR extraction (cache hit): {second_time:.6f}s")
    
    # Verify cache effectiveness
    speedup = first_time / second_time if second_time > 0 else float('inf')
    print(f"✓ Cache speedup: {speedup:.1f}x faster")
    
    # Check cache statistics
    cache_stats = processor.get_cache_stats()
    print(f"✓ Cache stats: {cache_stats}")


def benchmark_full_pipeline():
    """Benchmark the complete optimized pipeline."""
    print("\n🏁 Complete Pipeline Performance Test")
    print("-" * 40)
    
    # Create scraper with optimizations
    scraper = AIEnhancedMultiStrategyScraper(
        enable_multi_modal=True,
        enable_ai_extraction=False,
        parallel_processing=True
    )
    
    # Mock traditional extractors for consistent testing
    mock_json_ld = Mock()
    mock_json_ld.extract_from_html.return_value = [{"name": "Test Restaurant"}]
    
    mock_microdata = Mock()
    mock_microdata.extract_from_html.return_value = [{"phone": "(555) 123-4567"}]
    
    mock_heuristic = Mock()
    mock_heuristic.extract_from_html.return_value = [{"address": "123 Main St"}]
    
    scraper.json_ld_extractor = mock_json_ld
    scraper.microdata_extractor = mock_microdata
    scraper.heuristic_extractor = mock_heuristic
    
    # Complex HTML with multiple media types
    complex_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Restaurant Test</title>
            <script type="application/ld+json">
            {"@type": "Restaurant", "name": "Test Restaurant"}
            </script>
        </head>
        <body>
            <h1>Welcome</h1>
            <img src="/menu1.jpg" alt="Daily menu">
            <img src="/menu2.jpg" alt="Wine selection">
            <img src="/interior1.jpg" alt="Dining room">
            <img src="/interior2.jpg" alt="Bar area">
            <img src="/hours.png" alt="Business hours">
            <a href="/services.pdf">Catering Services</a>
            <a href="/wine.pdf">Wine List</a>
        </body>
    </html>
    """
    
    config = {"industry": "Restaurant"}
    
    # Run complete extraction pipeline
    start_time = time.time()
    result = scraper.extract_from_html(complex_html, config)
    total_time = time.time() - start_time
    
    print(f"✓ Complete extraction pipeline: {total_time:.4f}s")
    print(f"  • Methods used: {', '.join(result.extraction_methods)}")
    print(f"  • Overall confidence: {result.confidence_scores.get('overall', 0):.2f}")
    print(f"  • Processing stats: {result.processing_stats}")
    
    # Get performance statistics
    stats = scraper.get_extraction_statistics()
    print(f"  • Total extractions: {stats['total_extractions']}")
    print(f"  • Multi-modal extractions: {stats['multi_modal_extractions']}")


def main():
    """Run all performance benchmarks."""
    print("🎯 Multi-Modal Processing Optimization Benchmarks")
    print("=" * 60)
    print("Testing performance improvements from refactoring:")
    print("• Parallel processing for multiple files")
    print("• Lazy initialization of processors")
    print("• Optimized regex patterns and text processing")
    print("• LRU caching and memoization")
    print("• Fast-path optimizations")
    print("=" * 60)
    
    try:
        benchmark_ocr_processing()
        benchmark_parallel_processing()
        benchmark_lazy_initialization()
        benchmark_media_extraction()
        benchmark_caching()
        benchmark_full_pipeline()
        
        print("\n🎉 Performance Benchmark Complete!")
        print("\nKey Optimizations Implemented:")
        print("✓ Class-level compiled regex patterns for shared performance")
        print("✓ Parallel ThreadPoolExecutor for multiple images/PDFs")
        print("✓ Lazy initialization to avoid unnecessary processor creation")
        print("✓ LRU caching for frequently accessed templates")
        print("✓ Fast-path optimizations for single-item processing")
        print("✓ Optimized text processing with early returns")
        print("✓ Pre-compiled keyword sets for category detection")
        print("✓ Efficient memory usage and reduced redundant operations")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()