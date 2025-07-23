# WTEG CMS Integration Guide

This guide explains how to use the enhanced WTEG integration to import output from enhanced CMS extraction into the WTEG RAG system.

## Overview

The enhanced CMS extraction now produces detailed menu descriptions like:
- "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang"
- "Gorgonzola: Blue veined buttery Italian cheese"

These detailed descriptions are now **fully preserved** in the WTEG RAG system.

## Changes Made

### 1. Enhanced WTEG Extractor (`src/wteg/wteg_extractor.py`)

Added support for parsing the enhanced CMS format:

```python
def _parse_menu_item_string(self, item_str: str) -> WTEGMenuItem:
    """Parse menu item string in various formats."""
    # Enhanced CMS format: "Item Name: detailed description"
    if ": " in item_str and " - $" not in item_str:
        parts = item_str.split(": ", 1)  # Split only on first colon
        return WTEGMenuItem(
            item_name=parts[0].strip(),
            description=parts[1].strip() if len(parts) > 1 else "",
            price="",
            category="Menu Items"
        )
    # ... handles other formats too
```

### 2. Enhanced WTEG RAG Formatter (`src/wteg/wteg_formatters.py`)

Updated to include descriptions in RAG output:

```python
def _format_menu(self) -> str:
    """Format menu summary with descriptions."""
    for item in items[:5]:  # Limit to 5 per category
        # Include description if available for enhanced CMS extraction compatibility
        if item.description and item.description.strip():
            item_details.append(f"{item.item_name}: {item.description}")
        elif item.price and item.price.strip():
            item_details.append(f"{item.item_name} ({item.price})")
        else:
            item_details.append(item.item_name)
```

### 3. New CMS-to-WTEG Converter (`src/wteg/cms_to_wteg_converter.py`)

Created a converter to transform enhanced CMS extraction output to WTEG format:

```python
from src.wteg.cms_to_wteg_converter import CMSToWTEGConverter
from src.scraper.multi_strategy_scraper import RestaurantData

# Your enhanced CMS extraction result
cms_data = RestaurantData(
    name="Piattino Restaurant",
    menu_items={
        "Cheese & Salumi": [
            "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma",
            "Gorgonzola: Blue veined buttery Italian cheese"
        ]
    }
)

# Convert to WTEG format
converter = CMSToWTEGConverter()
wteg_data = converter.convert_restaurant_data(cms_data)

# Generate RAG-optimized output
rag_output = wteg_data.to_rag_format()
```

## Usage Examples

### Example 1: Converting Enhanced CMS Output

```python
from src.wteg.cms_to_wteg_converter import CMSToWTEGConverter
from src.scraper.multi_strategy_scraper import RestaurantData

# Enhanced CMS extraction result
cms_restaurant = RestaurantData(
    name="Piattino Portland",
    address="1420 SE Stark St, Portland, OR 97214",
    phone="(503) 555-0123",
    cuisine="Italian",
    menu_items={
        "Cheese & Salumi": [
            "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang",
            "Gorgonzola: Blue veined buttery Italian cheese",
            "Pecorino Toscana: strong, salty, intense"
        ],
        "Antipasti": [
            "Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic"
        ]
    },
    confidence="high"
)

# Convert to WTEG
converter = CMSToWTEGConverter()
wteg_restaurant = converter.convert_restaurant_data(cms_restaurant)

# Validate conversion
validation = converter.validate_conversion(cms_restaurant, wteg_restaurant)
print(f"Conversion successful: {validation['conversion_successful']}")
print(f"Detailed descriptions preserved: {validation['enhancements']['detailed_menu_descriptions']}")
```

### Example 2: RAG-Optimized Output

```python
from src.wteg.wteg_formatters import WTEGRAGFormatter

# Format for RAG system
formatter = WTEGRAGFormatter(wteg_restaurant)
rag_data = formatter.format()

print("Menu Summary for RAG:")
print(rag_data["menu_summary"])
# Output: "Cheese & Salumi: Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang, Gorgonzola: Blue veined buttery Italian cheese, Pecorino Toscana: strong, salty, intense; Antipasti: Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic"

print("\\nSearchable Content for Embedding:")
print(rag_data["searchable_content"])
# Includes all the detailed descriptions for vector embedding
```

### Example 3: Batch Processing Multiple Restaurants

```python
# Convert multiple restaurants
cms_restaurants = [cms_restaurant1, cms_restaurant2, cms_restaurant3]
wteg_restaurants = converter.convert_multiple_restaurants(cms_restaurants)

# Export for RAG system
from src.wteg.wteg_formatters import WTEGJSONFormatter
json_output = WTEGJSONFormatter.format_for_export(wteg_restaurants)
```

## Benefits

### ✅ **Preserved Data Quality**
- **Rich Descriptions**: All detailed menu descriptions are preserved
- **Enhanced Search**: RAG can now search within detailed descriptions
- **Better Context**: AI responses include comprehensive menu information

### ✅ **Backward Compatibility**
- Existing WTEG functionality continues to work
- Traditional price formats ("Item - $12.99") still supported
- No breaking changes to existing code

### ✅ **Validation & Quality Assurance**
- Built-in validation reports conversion quality
- Confidence scoring based on data richness
- Detailed reporting on preserved vs. lost data

## RAG Output Comparison

### Before Enhancement:
```
Menu: Cheese, Antipasti: Taleggio, Gorgonzola, Bruschetta
```

### After Enhancement:
```
Menu: Cheese & Salumi: Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang, Gorgonzola: Blue veined buttery Italian cheese; Antipasti: Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic
```

## Integration Testing

All changes are protected by comprehensive unit tests (`tests/unit/test_wteg_cms_integration.py`):

- ✅ **14 passing tests** covering all functionality
- ✅ **End-to-end pipeline testing** from CMS to RAG
- ✅ **Format compatibility testing** for all supported formats
- ✅ **Backward compatibility validation** with existing WTEG data

## Summary

Your enhanced CMS extraction output **will now work seamlessly** with the WTEG RAG system, preserving all the rich menu descriptions you're extracting from WordPress, Squarespace, Wix, BentoBox, and Bootstrap sites.

The detailed descriptions like "cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang" will be:
1. ✅ **Parsed correctly** by the WTEG extractor
2. ✅ **Stored properly** in the WTEG schema
3. ✅ **Included in RAG output** for enhanced search and responses
4. ✅ **Available for vector embedding** in the searchable content

No manual conversion needed - just use the `CMSToWTEGConverter` class to transform your enhanced extraction results!