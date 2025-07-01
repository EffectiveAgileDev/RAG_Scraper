#!/usr/bin/env python3
"""
Demonstration script showing multi-modal processing integration with the main scraper.

This script demonstrates how the AI-enhanced scraper now includes multi-modal processing
alongside traditional extraction methods (JSON-LD, Microdata, Heuristic).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scraper.ai_enhanced_multi_strategy_scraper import AIEnhancedMultiStrategyScraper
from unittest.mock import Mock


def demo_multi_modal_integration():
    """Demonstrate multi-modal processing integration."""
    
    print("🔧 Multi-Modal Processing Integration Demo")
    print("=" * 50)
    
    # Sample restaurant HTML with images and PDFs
    sample_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Bistro Deluxe - Fine Dining Restaurant</title>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Restaurant",
                "name": "Bistro Deluxe",
                "telephone": "(555) 123-4567"
            }
            </script>
        </head>
        <body>
            <h1>Welcome to Bistro Deluxe</h1>
            
            <!-- Images for multi-modal processing -->
            <div class="gallery">
                <img src="/images/menu-board.jpg" alt="Daily menu with appetizers and entrees">
                <img src="/images/dining-room.jpg" alt="Elegant dining room with warm ambiance">
                <img src="/images/business-hours.png" alt="Store hours Monday through Sunday">
            </div>
            
            <!-- PDF documents -->
            <div class="documents">
                <a href="/brochures/catering-services.pdf">Catering Services Menu</a>
                <a href="/menus/wine-list.pdf">Complete Wine Selection</a>
            </div>
            
            <!-- Traditional structured data -->
            <div itemscope itemtype="http://schema.org/Restaurant">
                <span itemprop="name">Bistro Deluxe</span>
                <span itemprop="telephone">(555) 123-4567</span>
            </div>
        </body>
    </html>
    """
    
    print("1. 🚀 Initializing AI-Enhanced Scraper with Multi-Modal Processing")
    
    # Initialize scraper with multi-modal enabled
    scraper = AIEnhancedMultiStrategyScraper(
        enable_multi_modal=True,        # Enable multi-modal processing
        enable_ai_extraction=False,     # Disable AI for this demo
        parallel_processing=True        # Use parallel processing
    )
    
    print(f"   ✓ Multi-modal enabled: {scraper.enable_multi_modal}")
    print(f"   ✓ Multi-modal processor: {type(scraper.multi_modal_processor).__name__}")
    print(f"   ✓ Parallel processing: {scraper.parallel_processing}")
    
    print("\n2. 📄 Analyzing HTML Content for Media Files")
    
    # Extract media files from HTML
    media_files = scraper._extract_media_from_html(sample_html)
    
    print(f"   Found {len(media_files)} media files:")
    for media in media_files:
        print(f"   • {media['type'].upper()}: {media['url']} (category: {media['category']})")
    
    print("\n3. 🔄 Running Complete Extraction Pipeline")
    
    config = {
        "industry": "Restaurant",
        "confidence_threshold": 0.6
    }
    
    # Mock the traditional extractors for demonstration
    mock_json_ld = Mock()
    mock_json_ld.extract_from_html.return_value = [{
        "name": "Bistro Deluxe",
        "telephone": "(555) 123-4567",
        "type": "Restaurant"
    }]
    
    mock_microdata = Mock()
    mock_microdata.extract_from_html.return_value = [{
        "name": "Bistro Deluxe",
        "telephone": "(555) 123-4567"
    }]
    
    mock_heuristic = Mock()
    mock_heuristic.extract_from_html.return_value = [{
        "name": "Bistro Deluxe",
        "address": "Downtown Location"
    }]
    
    # Override extractors
    scraper.json_ld_extractor = mock_json_ld
    scraper.microdata_extractor = mock_microdata
    scraper.heuristic_extractor = mock_heuristic
    
    # Run extraction
    try:
        result = scraper.extract_from_html(sample_html, config)
        
        print(f"   ✓ Extraction Status: {result.ai_status}")
        print(f"   ✓ Methods Used: {', '.join(result.extraction_methods)}")
        print(f"   ✓ Overall Confidence: {result.confidence_scores.get('overall', 0):.2f}")
        
        print("\n4. 📊 Extracted Data Summary")
        
        restaurant_data = result.restaurant_data
        print(f"   • Restaurant Name: {restaurant_data.get('name', 'Not found')}")
        print(f"   • Phone: {restaurant_data.get('telephone', 'Not found')}")
        
        # Check for multi-modal data
        if 'menu' in restaurant_data:
            print(f"   • Menu Items (OCR): {len(restaurant_data['menu'])} categories found")
        
        if 'ambiance' in restaurant_data:
            ambiance = restaurant_data['ambiance']
            print(f"   • Ambiance (Image Analysis): {ambiance.get('description', 'Not analyzed')}")
        
        if 'services' in restaurant_data:
            print(f"   • Services (PDF): {len(restaurant_data['services'])} services found")
        
        print("\n5. 📈 Processing Statistics")
        
        stats = result.processing_stats
        print(f"   • Total Processing Time: {stats.get('total_time', 0):.2f}s")
        print(f"   • Traditional Methods Time: {stats.get('traditional_time', 0):.2f}s")
        print(f"   • Parallel Execution: {stats.get('parallel_execution', False)}")
        
        print("\n6. 🎯 Source Attribution")
        
        attribution = result.source_attribution
        if attribution:
            for data_type, source in attribution.items():
                print(f"   • {data_type}: {source}")
        
        print("\n7. 📊 Extraction Method Statistics")
        
        extraction_stats = scraper.get_extraction_statistics()
        print(f"   • Total Extractions: {extraction_stats['total_extractions']}")
        print(f"   • Traditional Extractions: {extraction_stats['traditional_extractions']}")
        print(f"   • Multi-Modal Extractions: {extraction_stats['multi_modal_extractions']}")
        
        print("\n✨ Integration Demo Complete!")
        print("\nKey Integration Features:")
        print("  ✓ Multi-modal processing runs alongside traditional methods")
        print("  ✓ Automatic media file detection and categorization")
        print("  ✓ OCR for menu items, business hours, and contact info")
        print("  ✓ Image analysis for ambiance and visual elements")
        print("  ✓ PDF processing for services and pricing information")
        print("  ✓ Parallel processing for improved performance")
        print("  ✓ Confidence scoring and source attribution")
        print("  ✓ Graceful error handling and fallback to traditional methods")
        
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_multi_modal_integration()