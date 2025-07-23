#!/usr/bin/env python3
"""Demo script to show industry status system functionality."""

from src.config.industry_config import IndustryConfig
from src.web_interface.ui_components import IndustryDropdown


def main():
    """Demonstrate the industry status system."""
    print("🎯 RAG Scraper Industry Status System Demo")
    print("=" * 50)
    
    # Initialize industry config
    config = IndustryConfig()
    
    # Show all industries with status
    print("\n📋 All Industries with Status:")
    all_industries = config.get_all_industries_with_status()
    for industry in all_industries:
        status_emoji = {
            'available': '✅',
            'beta': '🔬', 
            'coming_soon': '🚧',
            'planned': '📅'
        }
        emoji = status_emoji.get(industry['status'], '❓')
        eta = f" (ETA: {industry.get('eta', 'TBD')})" if industry['status'] == 'coming_soon' else ""
        print(f"  {emoji} {industry['name']}: {industry['status']}{eta}")
    
    # Show industries grouped by status
    print("\n🔄 Industries Grouped by Status:")
    industries_by_status = config.get_industries_by_status()
    
    for status, industries in industries_by_status.items():
        if industries:  # Only show non-empty groups
            status_names = {
                'available': '✅ Available Now',
                'beta': '🔬 Beta',
                'coming_soon': '🚧 Coming Soon',
                'planned': '📅 Planned'
            }
            print(f"\n  {status_names.get(status, status.title())}:")
            for industry in industries:
                print(f"    • {industry['name']}")
    
    # Show status definitions
    print("\n📖 Status Definitions:")
    definitions = config.get_status_definitions()
    for status, definition in definitions.items():
        print(f"  • {status}: {definition}")
    
    # Show dropdown HTML sample
    print("\n🎨 Industry Dropdown HTML Preview:")
    dropdown = IndustryDropdown()
    html = dropdown.render()
    print("HTML Output (truncated):")
    print(html[:500] + "..." if len(html) > 500 else html)
    
    # Test specific industry status lookup
    print("\n🔍 Individual Industry Status Lookup:")
    test_industries = ['Restaurant', 'Medical', 'NonExistent']
    for industry in test_industries:
        status = config.get_industry_status(industry)
        if status:
            print(f"  • {industry}: {status}")
        else:
            print(f"  • {industry}: Not found")
    
    print("\n✨ Demo completed successfully!")


if __name__ == "__main__":
    main()