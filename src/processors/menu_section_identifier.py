"""Menu section identification for restaurant PDF data."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MenuSection:
    """Represents a menu section with items."""
    name: str
    items: List[Dict[str, str]] = field(default_factory=list)
    description: str = ""
    confidence: float = 0.0


class MenuSectionIdentifier:
    """Identifies and extracts menu sections from restaurant text."""
    
    def __init__(self):
        """Initialize menu section identifier."""
        self.section_patterns = self._initialize_section_patterns()
        self.bullet_patterns = [r'^\*\s*', r'^•\s*', r'^-\s*', r'^\d+\.\s*']
        
    def _initialize_section_patterns(self) -> List[str]:
        """Initialize patterns for menu section headers."""
        return [
            r'APPETIZERS?(?:\s*&\s*STARTERS?)?',
            r'STARTERS?(?:\s*&\s*APPETIZERS?)?',
            r'MAIN\s*COURSES?',
            r'ENTREES?',
            r'MAINS?',
            r'DESSERTS?(?:\s*&\s*SWEETS?)?',
            r'SWEETS?(?:\s*&\s*DESSERTS?)?',
            r'BEVERAGES?(?:\s*&\s*DRINKS?)?',
            r'DRINKS?(?:\s*&\s*BEVERAGES?)?',
            r'SALADS?(?:\s*&\s*LIGHT\s*FARE)?',
            r'SOUPS?(?:\s*&\s*SALADS?)?',
            r'SEAFOOD(?:\s*SPECIALTIES?)?',
            r'MEAT(?:\s*&\s*POULTRY)?',
            r'POULTRY(?:\s*&\s*MEAT)?',
            r'PASTA(?:\s*&\s*PIZZA)?',
            r'PIZZA(?:\s*&\s*PASTA)?',
            r'BURGERS?(?:\s*&\s*SANDWICHES?)?',
            r'SANDWICHES?(?:\s*&\s*BURGERS?)?',
            r'SIDES?(?:\s*&\s*EXTRAS?)?',
            r'SPECIALS?',
            r'DAILY\s*SPECIALS?',
            r'CHEF\'?S?\s*SPECIALS?',
            r'BREAKFAST',
            r'LUNCH',
            r'DINNER',
            r'BRUNCH'
        ]
    
    def identify_menu_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify menu sections from text.
        
        Args:
            text: Text to analyze for menu sections
            
        Returns:
            List of menu sections with items
        """
        if not text:
            return []
        
        sections = []
        lines = text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            section_info = self._identify_section_header(line)
            if section_info:
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'name': section_info['name'],
                    'items': [],
                    'confidence': section_info['confidence']
                }
                
                # Look for section description on next line
                if i + 1 < len(lines) and lines[i + 1].strip():
                    next_line = lines[i + 1].strip()
                    if not self._is_menu_item(next_line) and not self._identify_section_header(next_line):
                        current_section['description'] = next_line
                
            elif current_section:
                # Check if this line is a menu item
                item_info = self._extract_menu_item(line)
                if item_info:
                    current_section['items'].append(item_info)
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _identify_section_header(self, line: str) -> Optional[Dict[str, Any]]:
        """Identify if a line is a section header.
        
        Args:
            line: Line to check
            
        Returns:
            Section info if identified, None otherwise
        """
        # Skip lines that look like menu items
        if '$' in line or self._is_menu_item(line):
            return None
        
        # Skip restaurant names (usually contain restaurant, cafe, etc.)
        # But be more selective - only skip if it looks like a restaurant name, not a menu section
        restaurant_keywords = ['restaurant', 'cafe', 'diner', 'bistro', 'kitchen', 'grill', 'bar', 'place']
        if any(keyword in line.lower() for keyword in restaurant_keywords):
            return None
        
        # Special handling for "pizza" - only skip if it's a restaurant name, not a menu section
        if 'pizza' in line.lower() and not any(food_keyword in line.lower() for food_keyword in ['pasta', 'food', 'menu']):
            return None
        
        # Check for all caps section headers
        if line.isupper() and len(line) > 3:
            # Check against known section patterns
            for pattern in self.section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return {
                        'name': line,
                        'confidence': 0.9
                    }
            
            # Generic all-caps header that might be a section, but be more restrictive
            if (not any(char.isdigit() for char in line) and 
                len(line.split()) <= 5 and
                not any(keyword in line.lower() for keyword in restaurant_keywords)):
                # Only accept if it looks like a food section
                food_keywords = ['food', 'menu', 'course', 'item', 'special']
                if any(keyword in line.lower() for keyword in food_keywords):
                    return {
                        'name': line,
                        'confidence': 0.7
                    }
        
        # Check for title case section headers
        if line.istitle() and len(line) > 3:
            for pattern in self.section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return {
                        'name': line,
                        'confidence': 0.8
                    }
        
        # Check for lowercase section headers (case-insensitive)
        if line.islower() and len(line) > 3:
            for pattern in self.section_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return {
                        'name': line,
                        'confidence': 0.7
                    }
        
        return None
    
    def _is_menu_item(self, line: str) -> bool:
        """Check if a line appears to be a menu item.
        
        Args:
            line: Line to check
            
        Returns:
            True if line appears to be a menu item
        """
        # Contains price
        if re.search(r'\$\d+\.\d{2}', line):
            return True
        
        # Starts with bullet point
        for pattern in self.bullet_patterns:
            if re.search(pattern, line):
                return True
        
        # Contains dash separator (common in menu items)
        if ' - ' in line and not line.isupper():
            return True
        
        return False
    
    def _extract_menu_item(self, line: str) -> Optional[Dict[str, str]]:
        """Extract menu item information from a line.
        
        Args:
            line: Line to extract from
            
        Returns:
            Menu item info if found, None otherwise
        """
        # Clean bullet points
        cleaned_line = line
        for pattern in self.bullet_patterns:
            cleaned_line = re.sub(pattern, '', cleaned_line).strip()
        
        # Pattern: Item Name - $Price
        dash_match = re.search(r'^([^-]+?)\s*-\s*(\$\d+\.\d{2})', cleaned_line)
        if dash_match:
            return {
                'name': dash_match.group(1).strip(),
                'price': dash_match.group(2).strip()
            }
        
        # Pattern: Item Name $Price (no dash)
        price_match = re.search(r'^(.+?)\s+(\$\d+\.\d{2})$', cleaned_line)
        if price_match:
            return {
                'name': price_match.group(1).strip(),
                'price': price_match.group(2).strip()
            }
        
        # If no price found but looks like item, return name only
        if cleaned_line and not cleaned_line.isupper() and len(cleaned_line) > 3:
            return {
                'name': cleaned_line,
                'price': ''
            }
        
        return None