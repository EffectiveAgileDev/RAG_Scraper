"""Enhanced JSON-LD data extraction engine with multi-page context awareness."""
import json
import re
from typing import List, Dict, Any, Optional, Union, Set
from datetime import datetime
from dataclasses import dataclass, field
from bs4 import BeautifulSoup


@dataclass
class ExtractionContext:
    """Context information for extraction with relationship awareness."""

    entity_id: Optional[str] = None
    parent_id: Optional[str] = None
    source_url: Optional[str] = None
    relationships: Optional[Dict[str, Any]] = None
    parent_context: Optional[Dict[str, Any]] = None
    pattern_cache: Optional["PatternCache"] = None
    siblings_extracted: Optional[List[str]] = None
    sibling_patterns: Optional[Dict[str, Any]] = None
    page_type: Optional[str] = None
    extraction_history: Optional["ExtractionHistory"] = None
    html: Optional[str] = None
    parent_data: Optional[Any] = None
    pattern_learner: Optional[Any] = None


class PatternCache:
    """Cache for successful extraction patterns."""

    def __init__(self):
        self._patterns = {}

    def add_successful_pattern(self, pattern_type: str, pattern: str):
        """Add a successful pattern to the cache."""
        if pattern_type not in self._patterns:
            self._patterns[pattern_type] = {}
        if pattern not in self._patterns[pattern_type]:
            self._patterns[pattern_type][pattern] = {"uses": 0, "successes": 0}
        self._patterns[pattern_type][pattern]["uses"] += 1
        self._patterns[pattern_type][pattern]["successes"] += 1

    def get_pattern_stats(self) -> Dict[str, Dict]:
        """Get pattern statistics."""
        return self._patterns


class ExtractionHistory:
    """Tracks extraction history for entities."""

    def __init__(self):
        self._history = {}

    def add_extraction(self, entity_id: str, method: str, data: Dict, timestamp: str):
        """Add an extraction to history."""
        if entity_id not in self._history:
            self._history[entity_id] = []
        self._history[entity_id].append(
            {"method": method, "data": data, "timestamp": timestamp}
        )

    def get_history(self, entity_id: str) -> List[Dict]:
        """Get extraction history for an entity."""
        return self._history.get(entity_id, [])


class ExtractionAggregator:
    """Aggregates extraction results by entity."""

    def __init__(self):
        self._extractions = {}

    def add_extraction(self, result):
        """Add an extraction result."""
        entity_id = result.extraction_metadata.get("entity_id")
        if not entity_id:
            return

        if entity_id not in self._extractions:
            self._extractions[entity_id] = []
        self._extractions[entity_id].append(result)

    def get_aggregated_data(self, entity_id: str) -> Dict[str, Any]:
        """Get aggregated data for an entity."""
        if entity_id not in self._extractions:
            return {}

        extractions = sorted(
            self._extractions[entity_id],
            key=lambda x: x.extraction_metadata.get("timestamp", ""),
            reverse=True,
        )

        # Start with latest extraction
        aggregated = {
            "name": extractions[0].name,
            "phone": extractions[0].phone,
            "extraction_history": [],
        }

        # Update with non-null values from newer extractions
        for extraction in extractions:
            if extraction.phone and not aggregated.get("phone"):
                aggregated["phone"] = extraction.phone

            aggregated["extraction_history"].append(
                {
                    "timestamp": extraction.extraction_metadata.get("timestamp"),
                    "method": extraction.extraction_metadata.get("method"),
                    "confidence": extraction.extraction_metadata.get("confidence"),
                }
            )

        return aggregated


class ExtractionConflictResolver:
    """Resolves conflicts between extraction results."""

    def resolve_conflicts(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts between multiple data sources."""
        if not data_list:
            return {}

        # Sort by priority: json-ld > microdata > heuristic, then by timestamp
        sorted_data = sorted(
            data_list,
            key=lambda x: (
                self._method_priority(x["extraction_metadata"]["method"]),
                x["extraction_metadata"]["timestamp"],
            ),
            reverse=True,
        )

        resolved = sorted_data[0].copy()
        resolved["conflicts"] = {}

        # Check for conflicts
        for field in ["name", "phone", "address"]:
            values = [d.get(field) for d in data_list if d.get(field)]
            unique_values = list(set(values))
            if len(unique_values) > 1:
                resolved["conflicts"][field] = unique_values

        return resolved

    def _method_priority(self, method: str) -> int:
        """Get priority for extraction method."""
        priorities = {"json-ld": 3, "microdata": 2, "heuristic": 1}
        return priorities.get(method, 0)


class ExtractionMetricsTracker:
    """Tracks extraction metrics."""

    def __init__(self):
        self._metrics = {
            "total_pages": 0,
            "successful_extractions": 0,
            "structured_data_pages": 0,
            "heuristic_only_pages": 0,
            "confidence_scores": [],
        }

    def record_extraction(
        self, entity_id: str, method: str, success: bool, confidence: str = None
    ):
        """Record an extraction attempt."""
        self._metrics["total_pages"] += 1

        if success:
            self._metrics["successful_extractions"] += 1

        if method in ["json-ld", "microdata"]:
            self._metrics["structured_data_pages"] += 1
        elif method == "heuristic":
            self._metrics["heuristic_only_pages"] += 1

        if confidence:
            confidence_values = {"low": 0.3, "medium": 0.6, "high": 0.9}
            self._metrics["confidence_scores"].append(
                confidence_values.get(confidence, 0.5)
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get extraction metrics."""
        metrics = self._metrics.copy()

        if metrics["total_pages"] > 0:
            metrics["extraction_success_rate"] = (
                metrics["successful_extractions"] / metrics["total_pages"]
            )
        else:
            metrics["extraction_success_rate"] = 0

        if metrics["confidence_scores"]:
            metrics["average_confidence"] = sum(metrics["confidence_scores"]) / len(
                metrics["confidence_scores"]
            )
        else:
            metrics["average_confidence"] = 0

        # Correct count for pages with structured data (not heuristic only)
        metrics["pages_with_structured_data"] = metrics["structured_data_pages"]

        return metrics


class PatternEffectivenessTracker:
    """Tracks effectiveness of extraction patterns."""

    def __init__(self):
        self._patterns = {}

    def record_pattern_use(self, pattern: str, success: bool):
        """Record pattern usage."""
        if pattern not in self._patterns:
            self._patterns[pattern] = {"uses": 0, "successes": 0}

        self._patterns[pattern]["uses"] += 1
        if success:
            self._patterns[pattern]["successes"] += 1

    def get_pattern_effectiveness(self) -> Dict[str, Dict]:
        """Get pattern effectiveness statistics."""
        effectiveness = {}

        for pattern, stats in self._patterns.items():
            effectiveness[pattern] = {
                "uses": stats["uses"],
                "successes": stats["successes"],
                "success_rate": stats["successes"] / stats["uses"]
                if stats["uses"] > 0
                else 0,
            }

        return effectiveness


class EnhancedJSONLDExtractionResult:
    """Enhanced extraction result with metadata tracking."""

    def __init__(
        self,
        name: str = "",
        address: str = "",
        phone: str = "",
        hours: str = "",
        price_range: str = "",
        cuisine: str = "",
        menu_items: Optional[Dict[str, List[str]]] = None,
        social_media: Optional[List[str]] = None,
        confidence: str = "medium",
        source: str = "json-ld",
        extraction_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.address = address
        self.phone = phone
        self.hours = hours
        self.price_range = price_range
        self.cuisine = cuisine
        self.menu_items = menu_items or {}
        self.social_media = social_media or []
        self.confidence = confidence
        self.source = source
        self.extraction_metadata = extraction_metadata or {}

    def is_valid(self) -> bool:
        """Check if extraction result has valid data."""
        return bool(self.name and self.name.strip())

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "name": self.name,
            "address": self.address,
            "phone": self.phone,
            "hours": self.hours,
            "price_range": self.price_range,
            "cuisine": self.cuisine,
            "menu_items": self.menu_items,
            "social_media": self.social_media,
            "confidence": self.confidence,
            "source": self.source,
            "extraction_metadata": self.extraction_metadata,
        }


class JSONLDExtractor:
    """Enhanced JSON-LD extractor with relationship awareness."""

    RELEVANT_TYPES = {
        "restaurant",
        "foodestablishment",
        "localbusiness",
        "Restaurant",
        "FoodEstablishment",
        "LocalBusiness",
    }

    def __init__(self, extraction_context: Optional[ExtractionContext] = None):
        """Initialize with optional extraction context."""
        self.extraction_context = extraction_context or ExtractionContext()

    def extract_from_html(
        self, html_content: str
    ) -> List[EnhancedJSONLDExtractionResult]:
        """Extract restaurant data from HTML containing JSON-LD."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
        except Exception:
            return []

        results = []

        # Find all JSON-LD script tags
        json_ld_scripts = soup.find_all("script", type="application/ld+json")

        for script in json_ld_scripts:
            try:
                json_data = json.loads(script.string or script.text or "")

                # Handle both single objects and arrays
                if isinstance(json_data, list):
                    for item in json_data:
                        result = self.extract_restaurant_data(item)
                        if result and result.is_valid():
                            results.append(result)
                else:
                    result = self.extract_restaurant_data(json_data)
                    if result and result.is_valid():
                        results.append(result)

            except (json.JSONDecodeError, AttributeError):
                continue

        # Filter results based on page type if context available
        if self.extraction_context.page_type == "detail" and results:
            # Prioritize Restaurant type for detail pages
            restaurant_results = [
                r for r in results if "restaurant" in r.source.lower()
            ]
            if restaurant_results:
                results = restaurant_results[:1]  # Take only the most relevant

        return results

    def extract_restaurant_data(
        self, json_data: Any
    ) -> Optional[EnhancedJSONLDExtractionResult]:
        """Extract restaurant data from JSON-LD object."""
        if not isinstance(json_data, dict):
            return None

        # Check if this is a relevant schema type
        schema_type = json_data.get("@type", "")
        if not self.is_relevant_schema_type(schema_type):
            return None

        # Extract basic information
        name = json_data.get("name", "").strip()
        if not name:
            return None

        # Standard extractions
        address = self._extract_address(json_data)
        phone = self._extract_phone(json_data)
        hours = self._extract_hours(json_data)
        price_range = self._extract_price_range(json_data)
        cuisine = self._extract_cuisine(json_data)
        menu_items = self._extract_menu(json_data)
        social_media = self._extract_social_media(json_data)

        # Calculate confidence with context awareness
        confidence = self._calculate_confidence_with_context(json_data)

        # Build extraction metadata
        extraction_metadata = self._build_extraction_metadata(json_data)

        # Update pattern cache if available
        if self.extraction_context.pattern_cache:
            self.extraction_context.pattern_cache.add_successful_pattern(
                "json_ld_path", f"{schema_type}/@type"
            )

        return EnhancedJSONLDExtractionResult(
            name=name,
            address=address,
            phone=phone,
            hours=hours,
            price_range=price_range,
            cuisine=cuisine,
            menu_items=menu_items,
            social_media=social_media,
            confidence=confidence,
            source="json-ld",
            extraction_metadata=extraction_metadata,
        )

    def _build_extraction_metadata(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build extraction metadata including relationships and tracking info."""
        metadata = {
            "method": "json-ld",
            "timestamp": datetime.now().isoformat(),
        }

        # Add entity relationship info
        if self.extraction_context.entity_id:
            metadata["entity_id"] = self.extraction_context.entity_id
        if self.extraction_context.parent_id:
            metadata["parent_id"] = self.extraction_context.parent_id
        if self.extraction_context.source_url:
            metadata["source_url"] = self.extraction_context.source_url

        # Add inherited context
        if self.extraction_context.parent_context:
            metadata["inherited_context"] = self.extraction_context.parent_context

        # Check for previous extractions
        if self.extraction_context.extraction_history:
            history = self.extraction_context.extraction_history.get_history(
                self.extraction_context.entity_id
            )
            if history:
                metadata["previous_extraction"] = history[-1]
                metadata["is_update"] = True

        # Detect referenced pages
        referenced_pages = self._detect_referenced_pages(json_data)
        if referenced_pages:
            metadata["referenced_pages"] = referenced_pages

        # Add confidence boost information if applicable
        if hasattr(self, "_confidence_boost") and self._confidence_boost:
            metadata["confidence_boost"] = self._confidence_boost

        return metadata

    def _detect_referenced_pages(self, json_data: Dict[str, Any]) -> List[str]:
        """Detect references to other pages in the data."""
        references = []

        # Check for menu references
        if "menu" in json_data:
            menu_url = json_data["menu"]
            if isinstance(menu_url, str) and menu_url.startswith("/"):
                references.append(menu_url)

        # Check hasMenu structure
        has_menu = json_data.get("hasMenu", {})
        if isinstance(has_menu, dict) and "url" in has_menu:
            references.append(has_menu["url"])

        return references

    def _calculate_confidence_with_context(self, json_data: Dict[str, Any]) -> str:
        """Calculate confidence with context awareness."""
        # Base confidence calculation
        base_confidence = self._calculate_confidence(json_data)

        # Store whether confidence was boosted for metadata
        self._confidence_boost = None

        # Boost confidence if sibling patterns match
        if self.extraction_context.sibling_patterns and json_data.get(
            "@type"
        ) == self.extraction_context.sibling_patterns.get("@type"):
            self._confidence_boost = "sibling_pattern_match"
            # Boost confidence by one level if possible
            if base_confidence == "medium":
                return "high"

        return base_confidence

    def is_relevant_schema_type(self, schema_type: str) -> bool:
        """Check if schema type is relevant for restaurant extraction."""
        if isinstance(schema_type, list):
            return any(
                t.lower() in {"restaurant", "foodestablishment", "localbusiness"}
                for t in schema_type
            )
        return schema_type.lower() in {
            "restaurant",
            "foodestablishment",
            "localbusiness",
        }

    def normalize_address(self, address_data: Union[str, Dict[str, Any]]) -> str:
        """Normalize address to standard format."""
        if isinstance(address_data, str):
            return address_data.strip()

        if isinstance(address_data, dict):
            parts = []

            # Street address
            street = address_data.get("streetAddress", "").strip()
            if street:
                parts.append(street)

            # City, State ZIP format
            city = address_data.get("addressLocality", "").strip()
            state = address_data.get("addressRegion", "").strip()
            postal_code = address_data.get("postalCode", "").strip()

            # Combine city, state, and zip in standard format
            location_parts = []
            if city:
                location_parts.append(city)
            if state:
                if city:
                    location_parts.append(f", {state}")
                else:
                    location_parts.append(state)
            if postal_code:
                location_parts.append(f" {postal_code}")

            if location_parts:
                parts.append("".join(location_parts))

            return ", ".join(parts)

        return ""

    def normalize_hours(self, hours_data: Union[str, List[str]]) -> str:
        """Normalize operating hours to standard format."""
        if isinstance(hours_data, str):
            return hours_data.strip()

        if isinstance(hours_data, list):
            return ", ".join(str(h).strip() for h in hours_data if h)

        return ""

    def normalize_price_range(self, price_data: str) -> str:
        """Normalize price range to standard format."""
        if not price_data:
            return ""

        price_str = str(price_data).strip()
        return price_str

    def _extract_address(self, json_data: Dict[str, Any]) -> str:
        """Extract and normalize address from JSON-LD."""
        address_data = json_data.get("address")
        if address_data:
            return self.normalize_address(address_data)
        return ""

    def _extract_phone(self, json_data: Dict[str, Any]) -> str:
        """Extract phone number from JSON-LD."""
        return json_data.get("telephone", "").strip()

    def _extract_hours(self, json_data: Dict[str, Any]) -> str:
        """Extract operating hours from JSON-LD."""
        hours_data = json_data.get("openingHours")
        if hours_data:
            return self.normalize_hours(hours_data)
        return ""

    def _extract_price_range(self, json_data: Dict[str, Any]) -> str:
        """Extract price range from JSON-LD."""
        price_data = json_data.get("priceRange")
        if price_data:
            return self.normalize_price_range(price_data)
        return ""

    def _extract_cuisine(self, json_data: Dict[str, Any]) -> str:
        """Extract cuisine type from JSON-LD."""
        cuisine = json_data.get("servesCuisine")
        if isinstance(cuisine, list):
            return ", ".join(str(c).strip() for c in cuisine if c)
        elif isinstance(cuisine, str):
            return cuisine.strip()
        return ""

    def _extract_menu(self, json_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract menu items from JSON-LD."""
        menu_items = {}

        menu_data = json_data.get("hasMenu")
        if not menu_data:
            return menu_items

        menu_sections = menu_data.get("hasMenuSection", [])
        if not isinstance(menu_sections, list):
            menu_sections = [menu_sections]

        for section in menu_sections:
            if not isinstance(section, dict):
                continue

            section_name = section.get("name", "Menu Items")
            menu_items[section_name] = []

            menu_items_list = section.get("hasMenuItem", [])
            if not isinstance(menu_items_list, list):
                menu_items_list = [menu_items_list]

            for item in menu_items_list:
                if isinstance(item, dict):
                    item_name = item.get("name", "").strip()
                    if item_name:
                        menu_items[section_name].append(item_name)

        return menu_items

    def _extract_social_media(self, json_data: Dict[str, Any]) -> List[str]:
        """Extract social media links from JSON-LD."""
        same_as = json_data.get("sameAs", [])
        if isinstance(same_as, str):
            return [same_as]
        elif isinstance(same_as, list):
            return [str(url).strip() for url in same_as if url]
        return []

    def _calculate_confidence(self, json_data: Dict[str, Any]) -> str:
        """Calculate confidence score based on data completeness."""
        required_fields = ["name"]
        important_fields = [
            "address",
            "telephone",
            "openingHours",
            "priceRange",
            "servesCuisine",
            "hasMenu",
        ]

        has_required = all(json_data.get(field) for field in required_fields)
        if not has_required:
            return "low"

        important_count = sum(1 for field in important_fields if json_data.get(field))

        # More lenient scoring for high confidence - JSON-LD is inherently structured
        if important_count >= 1:
            return "high"
        else:
            return "medium"
