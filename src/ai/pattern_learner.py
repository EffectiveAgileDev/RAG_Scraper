"""Pattern learning system for site-specific extraction optimization."""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import re

logger = logging.getLogger(__name__)


class PatternLearner:
    """Learns and applies extraction patterns from successful extractions."""

    def __init__(self):
        """Initialize pattern learner."""
        self.pattern_database = {}
        self.success_threshold = 0.8
        self.learning_enabled = True

    def apply_learned_patterns(
        self, content: str, historical_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply learned patterns to extract content.

        Args:
            content: Content to extract from
            historical_patterns: Historical successful patterns

        Returns:
            Extraction results with pattern application
        """
        try:
            # Analyze content for pattern matches
            applicable_patterns = self._find_applicable_patterns(
                content, historical_patterns
            )

            if not applicable_patterns:
                return self._baseline_extraction(content)

            # Apply best patterns
            extraction_result = self._apply_patterns(
                content, applicable_patterns
            )

            # Compare with baseline
            baseline_result = self._baseline_extraction(content)

            return {
                "applied_patterns": applicable_patterns,
                "pattern_confidence": self._calculate_pattern_confidence(
                    applicable_patterns
                ),
                "extraction_improved": extraction_result["accuracy"]
                > baseline_result["accuracy"],
                "baseline_accuracy": baseline_result["accuracy"],
                "pattern_accuracy": extraction_result["accuracy"],
                "extracted_data": extraction_result["data"],
            }

        except Exception as e:
            logger.error(f"Pattern learning application failed: {str(e)}")
            return self._baseline_extraction(content)

    def _find_applicable_patterns(
        self, content: str, historical_patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """Find patterns applicable to the current content."""
        applicable = []

        for pattern_data in historical_patterns:
            patterns = pattern_data.get("patterns", [])
            success_rate = pattern_data.get("success_rate", 0)

            if success_rate >= self.success_threshold:
                for pattern in patterns:
                    if self._pattern_matches_content(pattern, content):
                        applicable.append(pattern)

        return list(set(applicable))  # Remove duplicates

    def _pattern_matches_content(self, pattern: str, content: str) -> bool:
        """Check if a pattern matches the content structure."""
        # Simple pattern matching - in practice this would be more sophisticated
        if "menu_class:" in pattern:
            class_name = pattern.split("menu_class:")[1]
            return (
                f'class="{class_name}"' in content
                or f"class='{class_name}'" in content
            )

        if "menu_id:" in pattern:
            id_name = pattern.split("menu_id:")[1]
            return f'id="{id_name}"' in content or f"id='{id_name}'" in content

        if "tag:" in pattern:
            tag_name = pattern.split("tag:")[1]
            return f"<{tag_name}" in content

        return False

    def _apply_patterns(
        self, content: str, patterns: List[str]
    ) -> Dict[str, Any]:
        """Apply patterns to extract content."""
        extracted_items = []

        for pattern in patterns:
            items = self._extract_with_pattern(content, pattern)
            extracted_items.extend(items)

        # Calculate accuracy based on extraction success
        accuracy = min(0.95, 0.6 + len(extracted_items) * 0.1)

        return {
            "data": extracted_items,
            "accuracy": accuracy,
            "patterns_used": patterns,
        }

    def _extract_with_pattern(
        self, content: str, pattern: str
    ) -> List[Dict[str, Any]]:
        """Extract content using a specific pattern."""
        items = []

        if "menu_class:" in pattern:
            class_name = pattern.split("menu_class:")[1]
            # Look for elements with this class
            class_pattern = rf'class=["\'].*{re.escape(class_name)}.*["\'][^>]*>(.*?)</[^>]+>'
            matches = re.findall(
                class_pattern, content, re.DOTALL | re.IGNORECASE
            )

            for match in matches[:5]:  # Limit to prevent overwhelming results
                # Try to extract menu item from the match
                item = self._parse_menu_item(match)
                if item:
                    items.append(item)

        return items

    def _parse_menu_item(self, html_fragment: str) -> Optional[Dict[str, Any]]:
        """Parse a menu item from HTML fragment."""
        # Simple parsing - look for text that might be menu items
        text = re.sub(r"<[^>]+>", " ", html_fragment).strip()

        if len(text) > 10 and len(text) < 200:
            # Look for price indicators
            price_match = re.search(r"\$\d+(?:\.\d{2})?", text)
            price = price_match.group() if price_match else None

            # Extract name (text before price or first significant portion)
            if price:
                name = text.split(price)[0].strip()
            else:
                name = text.split(".")[0].strip()

            if name and len(name) > 3:
                return {
                    "name": name,
                    "price": price,
                    "source": "pattern_extraction",
                    "raw_text": text,
                }

        return None

    def _baseline_extraction(self, content: str) -> Dict[str, Any]:
        """Perform baseline extraction without patterns."""
        # Simple heuristic extraction
        items = []

        # Look for common menu indicators
        menu_indicators = ["menu", "dish", "item", "special"]
        for indicator in menu_indicators:
            pattern = (
                rf'<[^>]*class="[^"]*{indicator}[^"]*"[^>]*>(.*?)</[^>]*>'
            )
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

            for match in matches[:3]:  # Limit baseline results
                item = self._parse_menu_item(match)
                if item:
                    items.append(item)

        accuracy = 0.65  # Baseline accuracy

        return {
            "data": items,
            "accuracy": accuracy,
            "method": "baseline_heuristics",
        }

    def _calculate_pattern_confidence(self, patterns: List[str]) -> float:
        """Calculate confidence score for applied patterns."""
        if not patterns:
            return 0.0

        # Base confidence increases with number of applicable patterns
        base_confidence = min(0.95, 0.7 + len(patterns) * 0.05)

        return base_confidence

    def learn_from_feedback(
        self,
        content: str,
        extracted_data: Dict[str, Any],
        user_corrections: Dict[str, Any],
    ) -> None:
        """Learn from user feedback to improve patterns."""
        if not self.learning_enabled:
            return

        try:
            # Analyze what went wrong and what patterns might work better
            content_hash = hashlib.md5(content[:1000].encode()).hexdigest()

            learning_data = {
                "content_hash": content_hash,
                "timestamp": datetime.now().isoformat(),
                "original_extraction": extracted_data,
                "user_corrections": user_corrections,
                "improvement_areas": self._identify_improvement_areas(
                    extracted_data, user_corrections
                ),
            }

            # Store learning data for future pattern generation
            self.pattern_database[content_hash] = learning_data

            logger.info(
                f"Learned from feedback for content {content_hash[:8]}"
            )

        except Exception as e:
            logger.error(f"Learning from feedback failed: {str(e)}")

    def _identify_improvement_areas(
        self, original: Dict[str, Any], corrections: Dict[str, Any]
    ) -> List[str]:
        """Identify areas where extraction can be improved."""
        improvements = []

        if "missed_items" in corrections:
            improvements.append("item_detection")

        if "incorrect_prices" in corrections:
            improvements.append("price_extraction")

        if "wrong_categories" in corrections:
            improvements.append("categorization")

        return improvements
