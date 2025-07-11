"""Content scorer for customer intent relevance."""

from typing import Dict, List, Any, Union


class ContentScorer:
    """Scores content relevance for customer intents."""
    
    def __init__(self):
        """Initialize ContentScorer."""
        self.scoring_algorithms = {
            "practical_planning": self._score_practical_planning,
            "evaluation": self._score_evaluation,
            "dining_decision": self._score_dining_decision,
            "immediate_decision": self._score_immediate_decision,
            "detailed_research": self._score_detailed_research,
            "visit_logistics": self._score_visit_logistics,
            "dietary_filtering": self._score_dietary_filtering
        }
        self.intent_weights = {
            "practical_planning": 0.8,
            "evaluation": 0.7,
            "dining_decision": 0.9,
            "immediate_decision": 1.0,
            "detailed_research": 0.6,
            "visit_logistics": 0.8,
            "dietary_filtering": 0.9
        }
    
    def score_content_relevance(self, restaurant_data: Dict[str, Any], query_patterns: List[Dict[str, str]]) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Score content relevance for different intent types."""
        result = {}
        
        for pattern in query_patterns:
            intent_type = pattern["intent_type"]
            if intent_type not in result:
                result[intent_type] = {}
            
            # Score each content field for this intent
            for field_name, field_value in restaurant_data.items():
                if field_value:  # Only score non-empty fields
                    score = self._calculate_field_score(field_name, field_value, intent_type)
                    confidence = self._calculate_field_confidence(field_name, field_value, intent_type)
                    
                    result[intent_type][field_name] = {
                        "score": score,
                        "confidence": confidence
                    }
        
        return result
    
    def score_for_intent(self, restaurant_data: Dict[str, Any], intent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Score restaurant data for a specific intent."""
        intent_type = intent_config["intent_type"]
        scoring_criteria = intent_config.get("scoring_criteria", [])
        
        component_scores = {}
        overall_score = 0.0
        
        if intent_type in self.scoring_algorithms:
            component_scores, overall_score = self.scoring_algorithms[intent_type](restaurant_data, scoring_criteria)
        else:
            # Generic scoring
            for criterion in scoring_criteria:
                if criterion in restaurant_data:
                    component_scores[criterion] = 0.7  # Default score
            overall_score = sum(component_scores.values()) / len(component_scores) if component_scores else 0.0
        
        return {
            "overall_score": overall_score,
            "component_scores": component_scores,
            "reasoning": f"Scored for {intent_type} intent with {len(scoring_criteria)} criteria"
        }
    
    def calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence based on data completeness."""
        if not data:
            return 0.0
        
        # Count non-empty fields
        filled_fields = sum(1 for value in data.values() if value)
        total_fields = len(data)
        
        # Base confidence on completeness ratio
        completeness_ratio = filled_fields / total_fields if total_fields > 0 else 0.0
        
        # Penalize datasets with very few fields
        field_count_factor = min(1.0, total_fields / 5.0)  # Normalize to 5 expected fields
        
        # Base confidence combines completeness and field count
        confidence = completeness_ratio * field_count_factor
        
        # Boost confidence for detailed data
        if "description" in data and len(str(data["description"])) > 50:
            confidence += 0.15
        if isinstance(data.get("reviews"), dict) and data["reviews"].get("count", 0) > 50:
            confidence += 0.15
        if "detailed_descriptions" in str(data.get("menu", {})):
            confidence += 0.15
        
        return min(1.0, confidence)
    
    def apply_intent_weights(self, base_scores: Dict[str, float], weights: Dict[str, float]) -> float:
        """Apply intent weights to base scores."""
        weighted_score = 0.0
        total_weight = 0.0
        
        for criterion, weight in weights.items():
            if criterion in base_scores:
                weighted_score += base_scores[criterion] * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def score_temporal_relevance(self, content: Dict[str, Any], time_sensitivity: str = "medium") -> float:
        """Score temporal relevance of content."""
        base_score = 0.5
        
        # Check for time-sensitive content
        time_sensitive_fields = ["hours_today", "daily_special", "live_wait_time", "current_availability"]
        time_sensitive_count = sum(1 for field in time_sensitive_fields if field in content)
        
        if time_sensitivity == "high":
            if time_sensitive_count > 0:
                base_score += 0.4 * (time_sensitive_count / len(time_sensitive_fields))
            else:
                base_score -= 0.3  # Penalize lack of current info
        elif time_sensitivity == "low":
            base_score += 0.2  # Less penalty for static content
        
        return min(1.0, max(0.0, base_score))
    
    def score_contextual_relevance(self, restaurant_data: Dict[str, Any], user_context: Dict[str, Any]) -> float:
        """Score contextual relevance based on user preferences."""
        score = 0.0
        factors = 0
        
        # Distance preference
        if "location_preference" in user_context and "location" in restaurant_data:
            distance = restaurant_data["location"].get("distance", "")
            max_distance = user_context.get("max_distance", "10 miles")
            if "0." in distance or "walking" in user_context["location_preference"]:
                score += 0.8
                factors += 1
        
        # Cuisine preference
        if "preferred_cuisines" in user_context and "cuisine" in restaurant_data:
            if restaurant_data["cuisine"] in user_context["preferred_cuisines"]:
                score += 0.9
                factors += 1
        
        # Price preference
        if "max_price" in user_context and "price_range" in restaurant_data:
            if restaurant_data["price_range"] == user_context["max_price"]:
                score += 0.85
                factors += 1
        
        # Service preference
        if "service_preference" in user_context:
            service_pref = user_context["service_preference"]
            if service_pref == "delivery" and restaurant_data.get("delivery"):
                score += 0.8
                factors += 1
        
        return score / factors if factors > 0 else 0.5
    
    def export_scoring_methodology(self) -> Dict[str, Any]:
        """Export scoring methodology for transparency."""
        return {
            "intent_types": {
                "immediate_decision": {
                    "description": "Quick decision making for immediate dining",
                    "key_factors": ["rating", "price_range", "distance", "current_availability"],
                    "weight_distribution": {"rating": 0.3, "price": 0.3, "distance": 0.2, "availability": 0.2}
                },
                "detailed_research": {
                    "description": "In-depth research for special occasions",
                    "key_factors": ["description_depth", "review_count", "menu_detail", "credentials"],
                    "weight_distribution": {"description": 0.25, "reviews": 0.25, "menu": 0.25, "credentials": 0.25}
                },
                "visit_logistics": {
                    "description": "Planning practical aspects of visit",
                    "key_factors": ["hours_clarity", "location_detail", "contact_info", "parking_info"],
                    "weight_distribution": {"hours": 0.3, "location": 0.3, "contact": 0.2, "parking": 0.2}
                },
                "dietary_filtering": {
                    "description": "Finding suitable dietary options",
                    "key_factors": ["dietary_variety", "allergen_info", "ingredient_detail", "kitchen_practices"],
                    "weight_distribution": {"variety": 0.3, "allergens": 0.3, "ingredients": 0.2, "practices": 0.2}
                }
            },
            "scoring_criteria": {
                "score_range": "0.0 to 1.0",
                "confidence_range": "0.0 to 1.0",
                "weighting_method": "weighted_average"
            },
            "weight_calculations": {
                "intent_weights": self.intent_weights,
                "algorithm": "context_aware_weighting"
            },
            "confidence_factors": {
                "data_completeness": "Primary factor",
                "detail_level": "Secondary factor",
                "review_count": "Tertiary factor"
            }
        }
    
    def batch_score_content(self, restaurants: List[Dict[str, Any]], intent_patterns: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Batch score multiple restaurants for multiple intents."""
        results = []
        
        for i, restaurant in enumerate(restaurants):
            result = {
                "restaurant_id": i,
                "restaurant_name": restaurant.get("name", f"Restaurant {i}"),
                "intent_scores": {}
            }
            
            for pattern in intent_patterns:
                intent_type = pattern["intent_type"]
                scores = self.score_content_relevance(restaurant, [pattern])
                result["intent_scores"][intent_type] = scores.get(intent_type, {})
            
            results.append(result)
        
        return results
    
    def _calculate_field_score(self, field_name: str, field_value: Any, intent_type: str) -> float:
        """Calculate score for a specific field and intent."""
        base_score = 0.5
        
        # Intent-specific scoring
        if intent_type == "practical_planning" and field_name in ["hours", "phone", "address"]:
            base_score = 0.8
        elif intent_type == "evaluation" and field_name in ["reviews", "rating", "price_range"]:
            base_score = 0.8
        elif intent_type == "dining_decision" and field_name in ["menu", "cuisine", "name"]:
            base_score = 0.8
        
        # Value-based adjustments
        if isinstance(field_value, dict) and len(field_value) > 2:
            base_score += 0.1  # Detailed data
        elif isinstance(field_value, str) and len(field_value) > 20:
            base_score += 0.1  # Detailed text
        
        return min(1.0, base_score)
    
    def _calculate_field_confidence(self, field_name: str, field_value: Any, intent_type: str) -> float:
        """Calculate confidence for a specific field."""
        if not field_value:
            return 0.0
        
        confidence = 0.7  # Base confidence
        
        # Structured data gets higher confidence
        if isinstance(field_value, dict):
            confidence += 0.2
        elif isinstance(field_value, list) and len(field_value) > 1:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _score_practical_planning(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for practical planning intent."""
        scores = {}
        for criterion in criteria:
            if criterion == "hours_clarity" and "hours" in data:
                scores[criterion] = 0.9 if isinstance(data["hours"], dict) else 0.6
            elif criterion == "contact_info" and ("phone" in data or "contact" in data):
                scores[criterion] = 0.8
            elif criterion in data:
                scores[criterion] = 0.7
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall
    
    def _score_evaluation(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for evaluation intent."""
        scores = {}
        for criterion in criteria:
            if criterion in data:
                scores[criterion] = 0.7
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall
    
    def _score_dining_decision(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for dining decision intent."""
        scores = {}
        for criterion in criteria:
            if criterion in data:
                scores[criterion] = 0.8
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall
    
    def _score_immediate_decision(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for immediate decision intent."""
        scores = {}
        for criterion in criteria:
            if criterion == "rating" and "rating" in data:
                rating = data.get("rating", 0)
                scores[criterion] = min(1.0, rating / 5.0) if isinstance(rating, (int, float)) else 0.7
            elif criterion == "price_range" and "price_range" in data:
                scores[criterion] = 0.9 if data["price_range"] == "$" else 0.7
            elif criterion == "distance" and "location" in data:
                distance = data["location"].get("distance", "")
                scores[criterion] = 0.9 if "0." in distance else 0.6
            elif criterion == "current_availability" and "hours" in data:
                scores[criterion] = 0.8 if data["hours"].get("current_status") == "open" else 0.4
            elif criterion in data:
                scores[criterion] = 0.7
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall
    
    def _score_detailed_research(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for detailed research intent."""
        scores = {}
        for criterion in criteria:
            if criterion == "description_depth" and "description" in data:
                desc_len = len(str(data["description"]))
                scores[criterion] = min(1.0, desc_len / 60.0) if desc_len > 20 else 0.3
            elif criterion == "review_count" and "reviews" in data:
                count = data["reviews"].get("count", 0)
                scores[criterion] = min(1.0, count / 100.0) if count > 10 else 0.3
            elif criterion == "menu_detail" and "menu" in data:
                has_details = data["menu"].get("detailed_descriptions", False)
                scores[criterion] = 0.9 if has_details else 0.5
            elif criterion == "credentials" and ("awards" in data or "chef_bio" in data):
                scores[criterion] = 0.8
            elif criterion in data:
                scores[criterion] = 0.6
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall
    
    def _score_visit_logistics(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for visit logistics intent."""
        scores = {}
        for criterion in criteria:
            if criterion == "hours_clarity" and "hours" in data:
                scores[criterion] = 0.9 if data["hours"].get("detailed_schedule") else 0.7
            elif criterion == "location_detail" and "location" in data:
                location = data["location"]
                has_details = "address" in location and "coordinates" in location
                scores[criterion] = 0.9 if has_details else 0.6
            elif criterion == "contact_info" and "contact" in data:
                contact = data["contact"]
                has_booking = contact.get("online_booking", False)
                scores[criterion] = 0.9 if has_booking else 0.7
            elif criterion == "parking_info" and "parking" in data:
                scores[criterion] = 0.8
            elif criterion in data:
                scores[criterion] = 0.7
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall
    
    def _score_dietary_filtering(self, data: Dict[str, Any], criteria: List[str]) -> tuple:
        """Score for dietary filtering intent."""
        scores = {}
        for criterion in criteria:
            if criterion == "dietary_variety" and "menu" in data:
                menu = data["menu"]
                variety_count = len(menu.get("dietary_options", {}))
                scores[criterion] = min(1.0, variety_count / 2.5) if variety_count > 0 else 0.2
            elif criterion == "allergen_info" and "menu" in data:
                has_allergen_info = data["menu"].get("allergen_info") == "detailed"
                scores[criterion] = 0.95 if has_allergen_info else 0.4
            elif criterion == "ingredient_detail" and "menu" in data:
                has_ingredients = data["menu"].get("ingredient_lists", False)
                scores[criterion] = 0.8 if has_ingredients else 0.3
            elif criterion == "kitchen_practices" and "kitchen_notes" in data:
                scores[criterion] = 0.9
            elif criterion in data:
                scores[criterion] = 0.6
        
        overall = sum(scores.values()) / len(scores) if scores else 0.0
        return scores, overall