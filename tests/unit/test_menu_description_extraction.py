"""TDD tests for menu description extraction from plain text format menus.

These tests expose the issue where only menu item names are captured
but rich descriptions are lost during extraction.
"""

import pytest
from bs4 import BeautifulSoup
from src.scraper.heuristic_extractor import HeuristicExtractor


class TestMenuDescriptionExtraction:
    """Tests that expose menu description extraction failures."""
    
    def test_colon_separated_menu_items_should_capture_full_descriptions(self):
        """Test that menu items with colon-separated descriptions are fully captured.
        
        This test exposes the current bug where only the item name before 
        the colon is captured, but the rich description after the colon is lost.
        
        THIS TEST SHOULD FAIL until the extractor is enhanced.
        """
        # Sample HTML that represents the plain text menu format
        # from Piattino restaurant that's currently failing
        html_content = """
        <html>
        <body>
            <div class="menu-section">
                <h3>Cheese Selection</h3>
                <p>Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang</p>
                <p>Gorgonzola: cow milk, semi-soft, blue cheese with a creamy texture and tangy flavor</p>
                <p>Pecorino Romano: sheep milk, hard cheese with a sharp, salty flavor</p>
            </div>
            <div class="menu-section">
                <h3>Salads</h3>  
                <p>Organic roasted beet salad: red & gold beets, organic arugula, granola, carrots purée, crème fraiche</p>
                <p>Caesar salad: romaine lettuce, parmesan cheese, croutons, classic caesar dressing</p>
            </div>
        </body>
        </html>
        """
        
        # Arrange
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = HeuristicExtractor()
        
        # Act
        menu_items = extractor._extract_menu_items(soup)
        
        # Assert - The current implementation FAILS these assertions
        # because it only captures item names, not full descriptions
        assert "Cheese Selection" in menu_items
        assert "Salads" in menu_items
        
        # BUG: Current implementation only captures "Taleggio", not the full description
        cheese_items = menu_items.get("Cheese Selection", [])
        assert len(cheese_items) == 3
        
        # These should pass when the bug is fixed:
        expected_taleggio = "Taleggio: cow milk, semi-soft, wash rind, strong, bold aroma with an unusual fruity tang"
        expected_gorgonzola = "Gorgonzola: cow milk, semi-soft, blue cheese with a creamy texture and tangy flavor"
        expected_pecorino = "Pecorino Romano: sheep milk, hard cheese with a sharp, salty flavor"
        
        assert expected_taleggio in cheese_items, f"Expected full description, got: {cheese_items}"
        assert expected_gorgonzola in cheese_items, f"Expected full description, got: {cheese_items}"
        assert expected_pecorino in cheese_items, f"Expected full description, got: {cheese_items}"
        
        # Check salad items
        salad_items = menu_items.get("Salads", [])
        assert len(salad_items) == 2
        
        expected_beet_salad = "Organic roasted beet salad: red & gold beets, organic arugula, granola, carrots purée, crème fraiche"
        expected_caesar = "Caesar salad: romaine lettuce, parmesan cheese, croutons, classic caesar dressing"
        
        assert expected_beet_salad in salad_items, f"Expected full description, got: {salad_items}"
        assert expected_caesar in salad_items, f"Expected full description, got: {salad_items}"
        
    def test_paragraph_menu_items_without_prices_should_be_captured(self):
        """Test that menu items in paragraph format without explicit prices are captured.
        
        Many restaurants use plain text format without prices on their menu pages.
        The current extraction logic requires dollar signs to identify menu items,
        but this fails for descriptive menu formats.
        
        THIS TEST SHOULD FAIL until enhanced extraction patterns are added.
        """
        # HTML representing menu content without explicit prices
        html_content = """
        <html>
        <body>
            <div class="menu-content">
                <h3>Antipasti</h3>
                <p>Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic</p>
                <p>Carpaccio di Manzo: thin sliced raw beef with arugula, capers, and lemon</p>
                <p>Antipasto della Casa: selection of cured meats, cheeses, and marinated vegetables</p>
            </div>
            <div class="menu-content">
                <h3>Pasta</h3>
                <p>Spaghetti Carbonara: traditional Roman pasta with pancetta, eggs, and pecorino cheese</p>
                <p>Penne Arrabbiata: spicy tomato sauce with garlic, red peppers, and fresh basil</p>
            </div>
        </body>
        </html>
        """
        
        # Arrange
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = HeuristicExtractor()
        
        # Act
        menu_items = extractor._extract_menu_items(soup)
        
        # Assert - Current implementation likely FAILS because it looks for "$" symbols
        assert "Antipasti" in menu_items
        assert "Pasta" in menu_items
        
        antipasti_items = menu_items.get("Antipasti", [])
        pasta_items = menu_items.get("Pasta", [])
        
        # Should capture all items with full descriptions
        assert len(antipasti_items) == 3, f"Expected 3 antipasti items, got {len(antipasti_items)}: {antipasti_items}"
        assert len(pasta_items) == 2, f"Expected 2 pasta items, got {len(pasta_items)}: {pasta_items}"
        
        # Verify full descriptions are preserved
        assert "Bruschetta alla Napoletana: grilled bread with fresh tomatoes, basil, and garlic" in antipasti_items
        assert "Spaghetti Carbonara: traditional Roman pasta with pancetta, eggs, and pecorino cheese" in pasta_items
        
    def test_mixed_format_menu_should_handle_both_prices_and_descriptions(self):
        """Test handling of mixed menu format with both priced and unpriced items.
        
        Real restaurant menus often mix formats - some items have prices,
        others are descriptive only. The extractor should handle both.
        
        THIS TEST SHOULD FAIL until extraction logic is enhanced.
        """
        html_content = """
        <html>
        <body>
            <div>
                <h3>Specialties</h3>
                <p>Osso Buco: braised veal shanks with vegetables and wine sauce $32</p>
                <p>Fresh Catch of the Day: prepared with seasonal ingredients and chef's selection</p>
                <p>Risotto del Giorno: daily risotto creation with market-fresh ingredients $28</p>
                <p>Vegetarian Tasting Plate: seasonal vegetable selection with house-made sauces</p>
            </div>
        </body>
        </html>
        """
        
        # Arrange
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = HeuristicExtractor()
        
        # Act
        menu_items = extractor._extract_menu_items(soup)
        
        # Assert
        assert "Specialties" in menu_items
        specialty_items = menu_items.get("Specialties", [])
        assert len(specialty_items) == 4
        
        # Should preserve full descriptions even for items with prices
        expected_osso_buco = "Osso Buco: braised veal shanks with vegetables and wine sauce"
        expected_fresh_catch = "Fresh Catch of the Day: prepared with seasonal ingredients and chef's selection" 
        expected_risotto = "Risotto del Giorno: daily risotto creation with market-fresh ingredients"
        expected_vegetarian = "Vegetarian Tasting Plate: seasonal vegetable selection with house-made sauces"
        
        # Current implementation strips everything after "$" so this will fail
        assert expected_osso_buco in specialty_items, f"Price should be removed but description preserved: {specialty_items}"
        assert expected_fresh_catch in specialty_items, f"No price items should be fully captured: {specialty_items}"
        assert expected_risotto in specialty_items, f"Price should be removed but description preserved: {specialty_items}"
        assert expected_vegetarian in specialty_items, f"No price items should be fully captured: {specialty_items}"
        
    def test_enhanced_implementation_preserves_full_descriptions(self):
        """Test that enhanced implementation correctly preserves full descriptions.
        
        This test verifies that our enhancement works correctly:
        - Captures full menu item descriptions including colons
        - Removes prices but keeps all descriptive content
        - Handles both priced and unpriced items properly
        """
        html_content = """
        <html>
        <body>
            <h3>Appetizers</h3>
            <p>Bruschetta: toasted bread with tomatoes and basil $12</p>
        </body>
        </html>
        """
        
        # Arrange
        soup = BeautifulSoup(html_content, 'html.parser')
        extractor = HeuristicExtractor()
        
        # Act
        menu_items = extractor._extract_menu_items(soup)
        
        # Assert - Verify enhanced implementation works correctly
        assert "Appetizers" in menu_items
        appetizer_items = menu_items.get("Appetizers", [])
        assert len(appetizer_items) == 1
        
        # Should preserve full description including colon, but remove price
        actual_item = appetizer_items[0]
        expected_item = "Bruschetta: toasted bread with tomatoes and basil"
        assert actual_item == expected_item, f"Expected full description without price, got: '{actual_item}'"
        
        # Verify description is preserved (contains colon)
        assert ":" in actual_item, "Description with colon should be preserved"
        assert "toasted bread with tomatoes and basil" in actual_item, "Full description should be captured"
        
        # Verify price is removed
        assert "$" not in actual_item, "Price should be removed from final content"


if __name__ == "__main__":
    # Run the tests to see them fail
    pytest.main([__file__, "-v"])