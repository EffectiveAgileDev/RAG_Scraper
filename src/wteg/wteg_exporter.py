"""WTEG export format for client RAG system integration.

This module provides specialized export formats for WTEG restaurant data
optimized for client ChatBot and RAG system consumption.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .wteg_schema import WTEGRestaurantData


class WTEGExporter:
    """Exporter for WTEG restaurant data to client RAG system format."""
    
    def __init__(self):
        """Initialize WTEG exporter."""
        self.export_version = "1.0"
        self.export_format = "wteg_rag_optimized"
    
    def export_to_rag_format(self, restaurants: List[WTEGRestaurantData]) -> Dict[str, Any]:
        """Export WTEG data to RAG-optimized format for client ChatBot."""
        export_data = {
            "restaurants": [],
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "export_version": self.export_version,
                "export_format": self.export_format,
                "restaurant_count": len(restaurants),
                "extraction_method": "wteg_specific"
            }
        }
        
        for restaurant in restaurants:
            rag_restaurant = self._convert_to_rag_format(restaurant)
            export_data["restaurants"].append(rag_restaurant)
        
        return export_data
    
    def export_for_chatbot(self, restaurants: List[WTEGRestaurantData]) -> Dict[str, Any]:
        """Export data specifically formatted for client ChatBot integration."""
        chatbot_data = {
            "conversation_ready_data": [],
            "query_responses": {
                "location_queries": [],
                "cuisine_queries": [],
                "menu_queries": [],
                "contact_queries": [],
                "service_queries": []
            },
            "metadata": {
                "format": "chatbot_optimized",
                "timestamp": datetime.now().isoformat(),
                "restaurant_count": len(restaurants)
            }
        }
        
        for restaurant in restaurants:
            # Convert to conversation-ready format
            conv_data = self._create_conversation_data(restaurant)
            chatbot_data["conversation_ready_data"].append(conv_data)
            
            # Pre-generate query responses
            self._add_query_responses(restaurant, chatbot_data["query_responses"])
        
        return chatbot_data
    
    def export_with_raw_preservation(self, restaurants: List[WTEGRestaurantData]) -> Dict[str, Any]:
        """Export with raw data preservation (no AI interpretation)."""
        raw_export = {
            "restaurants": [],
            "metadata": {
                "export_type": "raw_preservation",
                "ai_interpretation": False,
                "data_fidelity": "original",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        for restaurant in restaurants:
            raw_restaurant = self._preserve_raw_data(restaurant)
            raw_export["restaurants"].append(raw_restaurant)
        
        return raw_export
    
    def export_for_client(self, restaurants: List[WTEGRestaurantData]) -> Dict[str, Any]:
        """Export with client's specific field mapping requirements."""
        client_export = {
            "restaurants": [],
            "metadata": {
                "client_format": "wteg_specification",
                "field_mapping": "client_requirements",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        for restaurant in restaurants:
            client_restaurant = self._map_to_client_fields(restaurant)
            client_export["restaurants"].append(client_restaurant)
        
        return client_export
    
    def export_batch_to_rag_format(self, restaurants: List[WTEGRestaurantData]) -> Dict[str, Any]:
        """Export multiple restaurants in batch format."""
        batch_export = {
            "restaurants": [],
            "batch_metadata": {
                "batch_timestamp": datetime.now().isoformat(),
                "restaurant_count": len(restaurants),
                "processing_mode": "batch",
                "extraction_urls": [r.source_url for r in restaurants if r.source_url],
                "avg_confidence": sum(r.confidence_score for r in restaurants) / len(restaurants) if restaurants else 0.0
            }
        }
        
        for i, restaurant in enumerate(restaurants):
            rag_restaurant = self._convert_to_rag_format(restaurant)
            rag_restaurant["batch_index"] = i
            batch_export["restaurants"].append(rag_restaurant)
        
        return batch_export
    
    def export_with_quality_scoring(self, restaurants: List[WTEGRestaurantData]) -> Dict[str, Any]:
        """Export with quality metrics and scoring."""
        quality_export = {
            "restaurants": [],
            "metadata": {
                "includes_quality_metrics": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        for restaurant in restaurants:
            quality_restaurant = self._add_quality_metrics(restaurant)
            quality_export["restaurants"].append(quality_restaurant)
        
        return quality_export
    
    def validate_export_format(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate export format structure and completeness."""
        validation_result = {
            "is_valid": True,
            "schema_errors": [],
            "completeness_score": 0.0,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Check required top-level fields
        required_fields = ["restaurants", "metadata"]
        for field in required_fields:
            if field not in export_data:
                validation_result["schema_errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False
        
        # Validate restaurants array
        if "restaurants" in export_data:
            restaurants = export_data["restaurants"]
            if not isinstance(restaurants, list):
                validation_result["schema_errors"].append("Restaurants must be an array")
                validation_result["is_valid"] = False
            else:
                # Calculate completeness
                if restaurants:
                    total_completeness = 0.0
                    for restaurant in restaurants:
                        restaurant_completeness = self._calculate_restaurant_completeness(restaurant)
                        total_completeness += restaurant_completeness
                    validation_result["completeness_score"] = total_completeness / len(restaurants)
                else:
                    validation_result["completeness_score"] = 0.0
        
        return validation_result
    
    def _convert_to_rag_format(self, restaurant: WTEGRestaurantData) -> Dict[str, Any]:
        """Convert WTEG restaurant to RAG format."""
        rag_format = restaurant.to_rag_format()
        
        # Add additional RAG-specific fields
        rag_format.update({
            "searchable_content": rag_format.get("searchable_content", ""),
            "location_summary": rag_format.get("location_summary", ""),
            "contact_methods": rag_format.get("contact_methods", ""),
            "embedding_text": self._create_embedding_text(restaurant),
            "query_keywords": self._extract_query_keywords(restaurant),
            "rag_chunking": self._create_rag_chunks(restaurant)
        })
        
        return rag_format
    
    def _create_conversation_data(self, restaurant: WTEGRestaurantData) -> Dict[str, Any]:
        """Create conversation-ready data for ChatBot."""
        return {
            "restaurant_id": restaurant.source_url,
            "natural_language_description": self._create_natural_description(restaurant),
            "menu_summary": restaurant._create_menu_summary(),
            "quick_facts": {
                "cuisine": restaurant.cuisine,
                "location": restaurant._create_location_summary(),
                "phone": restaurant.click_to_call.primary_phone if restaurant.click_to_call else "",
                "website": restaurant.click_for_website.official_website if restaurant.click_for_website else ""
            },
            "conversation_starters": self._generate_conversation_starters(restaurant),
            "faq_responses": self._generate_faq_responses(restaurant)
        }
    
    def _add_query_responses(self, restaurant: WTEGRestaurantData, query_responses: Dict[str, List]) -> None:
        """Add pre-generated query responses for different types."""
        # Location queries
        if restaurant.location:
            query_responses["location_queries"].append({
                "restaurant": restaurant.brief_description or "Restaurant",
                "response": f"Located at {restaurant._create_location_summary()}"
            })
        
        # Cuisine queries
        if restaurant.cuisine:
            query_responses["cuisine_queries"].append({
                "restaurant": restaurant.brief_description or "Restaurant",
                "response": f"Serves {restaurant.cuisine} cuisine"
            })
        
        # Menu queries
        if restaurant.menu_items:
            query_responses["menu_queries"].append({
                "restaurant": restaurant.brief_description or "Restaurant",
                "response": restaurant._create_menu_summary()
            })
        
        # Contact queries
        if restaurant.click_to_call and restaurant.click_to_call.primary_phone:
            query_responses["contact_queries"].append({
                "restaurant": restaurant.brief_description or "Restaurant",
                "response": f"Phone: {restaurant.click_to_call.primary_phone}"
            })
        
        # Service queries
        if restaurant.services_offered:
            query_responses["service_queries"].append({
                "restaurant": restaurant.brief_description or "Restaurant",
                "response": restaurant._create_services_summary()
            })
    
    def _preserve_raw_data(self, restaurant: WTEGRestaurantData) -> Dict[str, Any]:
        """Preserve raw data without any AI interpretation."""
        raw_data = restaurant.to_dict()
        
        return {
            "raw_data": raw_data,
            "extraction_metadata": {
                "extraction_method": restaurant.extraction_method,
                "confidence_score": restaurant.confidence_score,
                "source_url": restaurant.source_url,
                "extraction_timestamp": restaurant.extraction_timestamp
            },
            "data_integrity": {
                "ai_enhanced": False,
                "raw_preservation": True,
                "original_format": "wteg_specific"
            }
        }
    
    def _map_to_client_fields(self, restaurant: WTEGRestaurantData) -> Dict[str, Any]:
        """Map to client's specific field requirements."""
        return {
            "Location": restaurant._create_location_summary(),
            "Cuisine": restaurant.cuisine,
            "Brief_Description": restaurant.brief_description,
            "Menu_items": [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in restaurant.menu_items],
            "Click_to_Call": restaurant.click_to_call.primary_phone if restaurant.click_to_call else "",
            "Click_to_Link": [link.to_dict() if hasattr(link, 'to_dict') else str(link) for link in restaurant.click_to_link],
            "Services_Offered": restaurant.services_offered.to_dict() if restaurant.services_offered else {},
            "Click_for_Website": restaurant.click_for_website.official_website if restaurant.click_for_website else "",
            "Click_for_Map": restaurant.click_for_map.map_url if restaurant.click_for_map else "",
            "source_metadata": {
                "url": restaurant.source_url,
                "confidence": restaurant.confidence_score,
                "extraction_method": restaurant.extraction_method
            }
        }
    
    def _add_quality_metrics(self, restaurant: WTEGRestaurantData) -> Dict[str, Any]:
        """Add quality metrics to restaurant data."""
        base_data = self._convert_to_rag_format(restaurant)
        
        # Calculate quality metrics
        quality_metrics = {
            "completeness_score": self._calculate_completeness_score(restaurant),
            "export_quality": self._calculate_export_quality(restaurant),
            "rag_readiness": self._calculate_rag_readiness(restaurant),
            "data_richness": self._calculate_data_richness(restaurant),
            "client_suitability": self._calculate_client_suitability(restaurant)
        }
        
        base_data["quality_metrics"] = quality_metrics
        return base_data
    
    def _create_embedding_text(self, restaurant: WTEGRestaurantData) -> str:
        """Create optimized text for embedding generation."""
        embedding_parts = []
        
        if restaurant.brief_description:
            embedding_parts.append(restaurant.brief_description)
        
        if restaurant.cuisine:
            embedding_parts.append(f"Cuisine: {restaurant.cuisine}")
        
        if restaurant.location:
            embedding_parts.append(restaurant._create_location_summary())
        
        if restaurant.menu_items:
            menu_text = restaurant._create_menu_summary()
            if menu_text and "not available" not in menu_text.lower():
                embedding_parts.append(menu_text)
        
        return " | ".join(embedding_parts)
    
    def _extract_query_keywords(self, restaurant: WTEGRestaurantData) -> List[str]:
        """Extract keywords for query matching."""
        keywords = []
        
        if restaurant.cuisine:
            keywords.extend(restaurant.cuisine.lower().split())
        
        if restaurant.location and restaurant.location.city:
            keywords.append(restaurant.location.city.lower())
        
        if restaurant.location and restaurant.location.neighborhood:
            keywords.append(restaurant.location.neighborhood.lower())
        
        # Add menu-based keywords
        for item in restaurant.menu_items:
            if hasattr(item, 'item_name') and item.item_name:
                keywords.extend(item.item_name.lower().split()[:2])  # First 2 words
        
        return list(set(keywords))  # Remove duplicates
    
    def _create_rag_chunks(self, restaurant: WTEGRestaurantData) -> List[Dict[str, Any]]:
        """Create RAG-optimized chunks for vector storage."""
        chunks = []
        
        # Main description chunk
        if restaurant.brief_description:
            chunks.append({
                "chunk_type": "description",
                "content": restaurant.brief_description,
                "metadata": {"cuisine": restaurant.cuisine, "source": "description"}
            })
        
        # Location chunk
        location_summary = restaurant._create_location_summary()
        if location_summary:
            chunks.append({
                "chunk_type": "location",
                "content": location_summary,
                "metadata": {"city": restaurant.location.city if restaurant.location else "", "source": "location"}
            })
        
        # Menu chunks (grouped by category)
        if restaurant.menu_items:
            menu_summary = restaurant._create_menu_summary()
            if menu_summary and "not available" not in menu_summary.lower():
                chunks.append({
                    "chunk_type": "menu",
                    "content": menu_summary,
                    "metadata": {"cuisine": restaurant.cuisine, "source": "menu"}
                })
        
        return chunks
    
    def _create_natural_description(self, restaurant: WTEGRestaurantData) -> str:
        """Create natural language description for ChatBot."""
        parts = []
        
        if restaurant.brief_description:
            parts.append(restaurant.brief_description)
        
        if restaurant.cuisine:
            parts.append(f"This {restaurant.cuisine} restaurant")
        
        if restaurant.location:
            location = restaurant._create_location_summary()
            if location:
                parts.append(f"located at {location}")
        
        if restaurant.click_to_call and restaurant.click_to_call.primary_phone:
            parts.append(f"You can reach them at {restaurant.click_to_call.primary_phone}")
        
        return ". ".join(parts) + "." if parts else "Restaurant information available."
    
    def _generate_conversation_starters(self, restaurant: WTEGRestaurantData) -> List[str]:
        """Generate conversation starters for ChatBot."""
        starters = []
        
        if restaurant.cuisine:
            starters.append(f"Tell me about {restaurant.cuisine} restaurants")
        
        if restaurant.menu_items:
            starters.append("What's on the menu?")
            starters.append("What are the popular dishes?")
        
        if restaurant.location:
            starters.append("Where is this restaurant located?")
        
        starters.append("How can I contact this restaurant?")
        starters.append("What services do they offer?")
        
        return starters
    
    def _generate_faq_responses(self, restaurant: WTEGRestaurantData) -> Dict[str, str]:
        """Generate FAQ responses for common questions."""
        faq = {}
        
        if restaurant.location:
            faq["Where are you located?"] = restaurant._create_location_summary()
        
        if restaurant.click_to_call and restaurant.click_to_call.primary_phone:
            faq["What's your phone number?"] = restaurant.click_to_call.primary_phone
        
        if restaurant.cuisine:
            faq["What type of cuisine do you serve?"] = restaurant.cuisine
        
        if restaurant.menu_items:
            faq["What's on your menu?"] = restaurant._create_menu_summary()
        
        if restaurant.services_offered:
            faq["What services do you offer?"] = restaurant._create_services_summary()
        
        return faq
    
    def _calculate_restaurant_completeness(self, restaurant_data: Dict[str, Any]) -> float:
        """Calculate completeness score for a restaurant export."""
        required_fields = [
            "restaurant_name", "location_summary", "cuisine_type", "description"
        ]
        
        present_fields = 0
        for field in required_fields:
            if field in restaurant_data and restaurant_data[field]:
                present_fields += 1
        
        return present_fields / len(required_fields)
    
    def _calculate_completeness_score(self, restaurant: WTEGRestaurantData) -> float:
        """Calculate overall completeness score."""
        total_weight = 0.0
        present_weight = 0.0
        
        field_weights = {
            "brief_description": 0.2,
            "cuisine": 0.15,
            "location": 0.2,
            "menu_items": 0.2,
            "click_to_call": 0.15,
            "click_for_website": 0.1
        }
        
        for field, weight in field_weights.items():
            total_weight += weight
            
            if field == "location" and restaurant.location and restaurant.location.street_address:
                present_weight += weight
            elif field == "menu_items" and restaurant.menu_items and len(restaurant.menu_items) > 0:
                present_weight += weight
            elif field == "click_to_call" and restaurant.click_to_call and restaurant.click_to_call.primary_phone:
                present_weight += weight
            elif field == "click_for_website" and restaurant.click_for_website and restaurant.click_for_website.official_website:
                present_weight += weight
            elif hasattr(restaurant, field) and getattr(restaurant, field):
                present_weight += weight
        
        return present_weight / total_weight if total_weight > 0 else 0.0
    
    def _calculate_export_quality(self, restaurant: WTEGRestaurantData) -> float:
        """Calculate export quality score."""
        return min(1.0, restaurant.confidence_score + 0.1)  # Slight boost for export
    
    def _calculate_rag_readiness(self, restaurant: WTEGRestaurantData) -> float:
        """Calculate RAG system readiness score."""
        rag_score = 0.0
        
        # Text content quality for embeddings
        if restaurant.brief_description and len(restaurant.brief_description) > 20:
            rag_score += 0.3
        
        # Structured data availability
        if restaurant.menu_items and len(restaurant.menu_items) > 0:
            rag_score += 0.3
        
        # Contact information for responses
        if restaurant.click_to_call and restaurant.click_to_call.primary_phone:
            rag_score += 0.2
        
        # Location for geographical queries
        if restaurant.location and restaurant.location.street_address:
            rag_score += 0.2
        
        return min(1.0, rag_score)
    
    def _calculate_data_richness(self, restaurant: WTEGRestaurantData) -> float:
        """Calculate data richness score."""
        richness = 0.0
        
        if restaurant.services_offered:
            richness += 0.2
        
        if restaurant.click_to_link and len(restaurant.click_to_link) > 0:
            richness += 0.2
        
        if restaurant.click_for_website and restaurant.click_for_website.official_website:
            richness += 0.2
        
        if restaurant.click_for_map and restaurant.click_for_map.map_url:
            richness += 0.2
        
        if restaurant.location and restaurant.location.neighborhood:
            richness += 0.2
        
        return min(1.0, richness)
    
    def _calculate_client_suitability(self, restaurant: WTEGRestaurantData) -> float:
        """Calculate suitability for client's RAG system."""
        # Based on client's specific requirements
        suitability = 0.0
        
        # Client needs all main fields populated
        if restaurant.brief_description:
            suitability += 0.25
        if restaurant.cuisine:
            suitability += 0.15
        if restaurant.click_to_call and restaurant.click_to_call.primary_phone:
            suitability += 0.25
        if restaurant.menu_items and len(restaurant.menu_items) > 0:
            suitability += 0.35
        
        return min(1.0, suitability)