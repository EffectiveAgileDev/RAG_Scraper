#!/usr/bin/env python3
"""Debug script to analyze WordPress structure on Piattino."""

import requests
from bs4 import BeautifulSoup

def analyze_wordpress_structure():
    """Analyze the actual WordPress structure of the Piattino menu."""
    
    response = requests.get('https://piattinopdx.com/menus/', timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("WordPress Structure Analysis for Piattino")
    print("=" * 50)
    
    # Find Taleggio and analyze its context
    taleggio = soup.find('h3', string=lambda text: text and 'taleggio' in text.lower())
    if not taleggio:
        # Try finding by text content instead
        all_h3 = soup.find_all('h3')
        for h3 in all_h3:
            if 'taleggio' in h3.get_text().lower():
                taleggio = h3
                break
    
    if taleggio:
        print("Found Taleggio element:")
        print(f"  Tag: {taleggio.name}")
        print(f"  Text: '{taleggio.get_text().strip()}'")
        print(f"  Classes: {taleggio.get('class', [])}")
        
        # Analyze parent structure
        parent = taleggio.parent
        print(f"\nParent element:")
        print(f"  Tag: {parent.name}")
        print(f"  Classes: {parent.get('class', [])}")
        
        # Look at next few siblings
        print("\nNext siblings after Taleggio:")
        current = taleggio
        for i in range(5):
            current = current.find_next_sibling()
            if not current:
                break
            
            text = current.get_text().strip()
            classes = current.get('class', [])
            print(f"  {i+1}. <{current.name}> classes={classes}")
            print(f"      Text: '{text[:100]}...'")
            
            # Check if this looks like a description
            if ':' in text and any(word in text.lower() for word in ['milk', 'cheese', 'flavor', 'aroma']):
                print(f"      *** THIS LOOKS LIKE THE CHEESE DESCRIPTION! ***")
        
        # Also check within parent for description elements
        print(f"\nLooking within parent div for description elements:")
        desc_candidates = parent.find_all(['p', 'div', 'span'], 
                                        string=lambda text: text and ':' in text and 
                                        any(word in text.lower() for word in ['milk', 'cheese', 'flavor']))
        
        for desc in desc_candidates:
            print(f"  Found description candidate: '{desc.get_text().strip()[:100]}...'")
            
        # Look at the grandparent structure too
        grandparent = parent.parent if parent else None
        if grandparent:
            print(f"\nGrandparent element:")
            print(f"  Tag: {grandparent.name}")
            print(f"  Classes: {grandparent.get('class', [])}")
            
            # Look for description divs as siblings of the parent AND grandparent
            print(f"\nLooking for description elements as siblings of parent:")
            for sibling in parent.find_next_siblings():
                sibling_text = sibling.get_text().strip()
                sibling_classes = sibling.get('class', [])
                print(f"  Sibling <{sibling.name}> classes={sibling_classes}")
                print(f"    Text: '{sibling_text[:200]}...'")
                
                # Check if this looks like our cheese description
                if any(word in sibling_text.lower() for word in ['cow milk', 'semi-soft', 'aroma', 'tang']):
                    print(f"    *** THIS IS THE CHEESE DESCRIPTION! ***")
                    
            print(f"\nLooking for description elements as siblings of grandparent:")
            for sibling in grandparent.find_next_siblings():
                sibling_text = sibling.get_text().strip()
                sibling_classes = sibling.get('class', [])
                print(f"  GP Sibling <{sibling.name}> classes={sibling_classes}")
                print(f"    Text: '{sibling_text[:200]}...'")
                
                # Check if this looks like our cheese description  
                if any(word in sibling_text.lower() for word in ['cow milk', 'semi-soft', 'aroma', 'tang']):
                    print(f"    *** THIS IS THE CHEESE DESCRIPTION! ***")
                    
            # Also search within grandparent for any elements containing description keywords
            print(f"\nSearching within grandparent for description keywords:")
            desc_elements = grandparent.find_all(string=lambda text: text and 
                                               any(word in text.lower() for word in ['cow milk', 'semi-soft', 'aroma', 'tang']))
            for desc in desc_elements:
                parent_elem = desc.parent
                print(f"  Found in <{parent_elem.name}> classes={parent_elem.get('class', [])}")
                print(f"    Full text: '{desc.strip()}'")
                print(f"    *** FOUND THE DESCRIPTION! ***")
            
    else:
        print("Could not find Taleggio element")
        
        # Show all h3 elements to debug
        all_h3 = soup.find_all('h3')
        print(f"\nAll h3 elements found ({len(all_h3)}):")
        for i, h3 in enumerate(all_h3[:10]):
            print(f"  {i+1}. '{h3.get_text().strip()}'")

if __name__ == "__main__":
    analyze_wordpress_structure()