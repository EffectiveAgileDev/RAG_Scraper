"""AI-enhanced multi-strategy scraper combining traditional and AI extraction methods."""

import time
import threading
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import logging

from .multi_strategy_scraper import MultiStrategyScraper, RestaurantData
from ..ai.llm_extractor import LLMExtractor
from ..ai.confidence_scorer import ConfidenceScorer
from ..config.scraping_config import ScrapingConfig
from ..processors.multi_modal_processor import MultiModalProcessor

logger = logging.getLogger(__name__)


@dataclass
class AIEnhancedExtractionResult:
    """Enhanced extraction result with AI analysis and confidence scoring."""
    
    restaurant_data: Dict[str, Any]
    extraction_methods: List[str]
    confidence_scores: Dict[str, float]
    source_attribution: Dict[str, str]
    processing_stats: Dict[str, Any]
    ai_status: str = "success"
    validation_results: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class ExtractionMethodTracker:
    """Tracks performance and usage statistics for extraction methods."""
    
    def __init__(self):
        """Initialize method tracker."""
        self.total_extractions = 0
        self.method_stats = {}
        self.performance_history = []
        self._lock = threading.RLock()
    
    def track_method_usage(self, method: str, success: bool, confidence: float, 
                          processing_time: float):
        """Track usage of an extraction method."""
        with self._lock:
            if method not in self.method_stats:
                self.method_stats[method] = {
                    "usage_count": 0,
                    "success_count": 0,
                    "total_confidence": 0.0,
                    "total_processing_time": 0.0,
                    "confidence_scores": []
                }
            
            stats = self.method_stats[method]
            stats["usage_count"] += 1
            stats["total_processing_time"] += processing_time
            stats["confidence_scores"].append(confidence)
            
            if success:
                stats["success_count"] += 1
                stats["total_confidence"] += confidence
    
    def track_combination_performance(self, methods: List[str], overall_confidence: float, 
                                    data_completeness: float):
        """Track performance of method combinations."""
        with self._lock:
            combination_key = "+".join(sorted(methods))
            
            self.performance_history.append({
                "timestamp": time.time(),
                "methods": combination_key,
                "confidence": overall_confidence,
                "completeness": data_completeness
            })
    
    def get_method_statistics(self) -> Dict[str, Any]:
        """Get comprehensive method statistics."""
        with self._lock:
            stats = {}
            
            for method, data in self.method_stats.items():
                usage_count = data["usage_count"]
                success_count = data["success_count"]
                
                stats[method] = {
                    "usage_count": usage_count,
                    "success_rate": success_count / usage_count if usage_count > 0 else 0.0,
                    "average_confidence": (data["total_confidence"] / success_count 
                                         if success_count > 0 else 0.0),
                    "average_processing_time": (data["total_processing_time"] / usage_count 
                                              if usage_count > 0 else 0.0),
                    "confidence_scores": data["confidence_scores"]
                }
            
            return stats
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        trends = {}
        
        # Group by method
        method_histories = {}
        for entry in self.performance_history:
            method = entry["methods"]
            if method not in method_histories:
                method_histories[method] = []
            method_histories[method].append(entry)
        
        # Analyze trends for each method
        for method, history in method_histories.items():
            if len(history) >= 3:
                # Simple trend analysis
                recent_scores = [h["confidence"] for h in history[-5:]]
                older_scores = [h["confidence"] for h in history[-10:-5]] if len(history) >= 10 else []
                
                if older_scores:
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores)
                    
                    if recent_avg > older_avg + 0.05:
                        trend = "improving"
                    elif recent_avg < older_avg - 0.05:
                        trend = "declining"
                    else:
                        trend = "stable"
                else:
                    trend = "insufficient_data"
                
                trends[method] = {
                    "confidence_trend": trend,
                    "recent_average": sum(recent_scores) / len(recent_scores),
                    "sample_count": len(history)
                }
        
        return trends
    
    def get_method_recommendations(self) -> List[Dict[str, Any]]:
        """Get method combination recommendations based on performance."""
        recommendations = []
        
        # Analyze combination performance
        combination_performance = {}
        for entry in self.performance_history:
            method = entry["methods"]
            if method not in combination_performance:
                combination_performance[method] = []
            combination_performance[method].append({
                "confidence": entry["confidence"],
                "completeness": entry["completeness"]
            })
        
        # Score combinations
        for combination, performances in combination_performance.items():
            if len(performances) >= 3:  # Need sufficient data
                avg_confidence = sum(p["confidence"] for p in performances) / len(performances)
                avg_completeness = sum(p["completeness"] for p in performances) / len(performances)
                
                # Combined score
                score = (avg_confidence * 0.6) + (avg_completeness * 0.4)
                
                recommendations.append({
                    "methods": combination.split("+"),
                    "score": score,
                    "avg_confidence": avg_confidence,
                    "avg_completeness": avg_completeness,
                    "sample_count": len(performances)
                })
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations


class ResultMerger:
    """Merges extraction results from multiple methods using confidence scoring."""
    
    def __init__(self, confidence_scorer: ConfidenceScorer, 
                 merge_strategy: str = "confidence_weighted"):
        """Initialize result merger."""
        self.confidence_scorer = confidence_scorer
        self.merge_strategy = merge_strategy
    
    def merge_results(self, extraction_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results from multiple extraction methods."""
        if not extraction_results:
            return {"data": {}, "source_attribution": {}, "confidence_scores": {}}
        
        merged_data = {}
        source_attribution = {}
        confidence_scores = {}
        
        # Calculate confidence for each result
        for result in extraction_results:
            method = result.get("method", "unknown")
            confidence = result.get("confidence", 0.5)
            confidence_scores[method] = confidence
        
        # Merge based on strategy
        if self.merge_strategy == "confidence_weighted":
            merged_data, source_attribution = self._merge_confidence_weighted(extraction_results)
        elif self.merge_strategy == "completeness_optimized":
            merged_data, source_attribution = self._merge_completeness_optimized(extraction_results)
        else:
            # Default strategy
            merged_data, source_attribution = self._merge_confidence_weighted(extraction_results)
        
        return {
            "data": merged_data,
            "source_attribution": source_attribution,
            "confidence_scores": confidence_scores
        }
    
    def _merge_confidence_weighted(self, results: List[Dict[str, Any]]) -> tuple:
        """Merge results using confidence weighting."""
        merged_data = {}
        source_attribution = {}
        
        # Group by field name
        field_sources = {}
        for result in results:
            method = result.get("method", "unknown")
            confidence = result.get("confidence", 0.5)
            data = result.get("data", {})
            
            for field, value in data.items():
                if field not in field_sources:
                    field_sources[field] = []
                field_sources[field].append({
                    "method": method,
                    "value": value,
                    "confidence": confidence
                })
        
        # Select best source for each field
        for field, sources in field_sources.items():
            # Sort by confidence descending
            sources.sort(key=lambda x: x["confidence"], reverse=True)
            best_source = sources[0]
            
            merged_data[field] = best_source["value"]
            source_attribution[field] = best_source["method"]
        
        return merged_data, source_attribution
    
    def _merge_completeness_optimized(self, results: List[Dict[str, Any]]) -> tuple:
        """Merge results optimizing for data completeness."""
        merged_data = {}
        source_attribution = {}
        
        # Combine all unique fields
        for result in results:
            method = result.get("method", "unknown")
            data = result.get("data", {})
            
            for field, value in data.items():
                if field not in merged_data:
                    merged_data[field] = value
                    source_attribution[field] = method
                elif not merged_data[field] and value:
                    # Replace empty values with non-empty ones
                    merged_data[field] = value
                    source_attribution[field] = method
        
        return merged_data, source_attribution


class AIEnhancedMultiStrategyScraper(MultiStrategyScraper):
    """Enhanced scraper that combines traditional methods with AI analysis."""
    
    def __init__(self, llm_extractor: LLMExtractor = None, 
                 confidence_scorer: ConfidenceScorer = None,
                 traditional_extractors: Dict[str, Any] = None,
                 enable_ai_extraction: bool = True,
                 enable_multi_modal: bool = True,
                 parallel_processing: bool = True,
                 **kwargs):
        """Initialize AI-enhanced scraper."""
        super().__init__(**kwargs)
        
        self.llm_extractor = llm_extractor
        self.confidence_scorer = confidence_scorer or ConfidenceScorer()
        self.enable_ai_extraction = enable_ai_extraction
        self.enable_multi_modal = enable_multi_modal
        self.parallel_processing = parallel_processing
        
        # Initialize multi-modal processor
        if enable_multi_modal:
            self.multi_modal_processor = MultiModalProcessor(
                enable_ocr=True,
                enable_image_analysis=True,
                enable_pdf_processing=True
            )
        else:
            self.multi_modal_processor = None
        
        # Override traditional extractors if provided
        if traditional_extractors:
            self.json_ld_extractor = traditional_extractors.get("json_ld", self.json_ld_extractor)
            self.microdata_extractor = traditional_extractors.get("microdata", self.microdata_extractor)
            self.heuristic_extractor = traditional_extractors.get("heuristic", self.heuristic_extractor)
        
        # Initialize components
        self.method_tracker = ExtractionMethodTracker()
        self.result_merger = ResultMerger(self.confidence_scorer)
        self.result_cache = {} if getattr(self.config, 'enable_result_caching', False) else None
        self._cache_lock = threading.RLock()
        
        # Performance tracking
        self.extraction_stats = {
            "total_extractions": 0,
            "ai_extractions": 0,
            "traditional_extractions": 0,
            "multi_modal_extractions": 0,
            "errors": []
        }
    
    def extract_from_html(self, html_content: str, config: Dict[str, Any] = None) -> AIEnhancedExtractionResult:
        """Extract data using AI-enhanced pipeline."""
        start_time = time.time()
        config = config or {}
        
        # Check cache first
        if self.result_cache is not None:
            cache_key = self._generate_cache_key(html_content, config)
            with self._cache_lock:
                if cache_key in self.result_cache:
                    if not hasattr(self, "_cache_hits"):
                        self._cache_hits = 0
                    self._cache_hits += 1
                    return self.result_cache[cache_key]
                else:
                    if not hasattr(self, "_cache_misses"):
                        self._cache_misses = 0
                    self._cache_misses += 1
        
        # Track extraction
        self.extraction_stats["total_extractions"] += 1
        
        extraction_methods = []
        method_results = []
        processing_stats = {
            "total_time": 0,
            "traditional_time": 0,
            "llm_time": 0,
            "merging_time": 0,
            "parallel_execution": self.parallel_processing
        }
        errors = []
        ai_status = "success"
        
        try:
            # Run extractions
            if self.parallel_processing:
                method_results = self._extract_parallel(html_content, config, processing_stats)
            else:
                method_results = self._extract_sequential(html_content, config, processing_stats)
            
            # Filter successful results
            successful_results = [r for r in method_results if r.get("success", False)]
            extraction_methods = [r.get("method", "unknown") for r in successful_results]
            
            # AI extraction
            if self.enable_ai_extraction and self.llm_extractor:
                try:
                    ai_start = time.time()
                    ai_result = self._extract_with_ai(html_content, config)
                    processing_stats["llm_time"] = time.time() - ai_start
                    
                    if ai_result.get("success", False):
                        successful_results.append(ai_result)
                        extraction_methods.append("llm")
                        self.extraction_stats["ai_extractions"] += 1
                except Exception as e:
                    ai_status = "failed"
                    errors.append(f"AI extraction failed: {str(e)}")
                    logger.error(f"AI extraction failed: {e}")
            
            # Merge results
            merge_start = time.time()
            merged_result = self.result_merger.merge_results(successful_results)
            processing_stats["merging_time"] = time.time() - merge_start
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(merged_result, config)
            merged_result["confidence_scores"]["overall"] = overall_confidence
            
            # Create final result
            processing_stats["total_time"] = time.time() - start_time
            
            result = AIEnhancedExtractionResult(
                restaurant_data=merged_result["data"],
                extraction_methods=extraction_methods,
                confidence_scores=merged_result["confidence_scores"],
                source_attribution=merged_result["source_attribution"],
                processing_stats=processing_stats,
                ai_status=ai_status,
                validation_results=self._validate_extraction_result(merged_result, config),
                errors=errors if errors else None
            )
            
            # Track method performance
            self._track_extraction_performance(extraction_methods, result, processing_stats)
            
            # Cache result
            if self.result_cache is not None:
                with self._cache_lock:
                    self.result_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            # Handle extraction failure
            import traceback
            errors.append(f"Extraction pipeline failed: {str(e)}")
            logger.error(f"AI-enhanced extraction failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            processing_stats["total_time"] = time.time() - start_time
            
            return AIEnhancedExtractionResult(
                restaurant_data={},
                extraction_methods=[],
                confidence_scores={},
                source_attribution={},
                processing_stats=processing_stats,
                ai_status="failed",
                errors=errors
            )
    
    def _extract_parallel(self, html_content: str, config: Dict[str, Any], 
                         processing_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract using all methods in parallel."""
        traditional_start = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit traditional extraction tasks
            futures = {
                executor.submit(self._extract_json_ld, html_content): "json_ld",
                executor.submit(self._extract_microdata, html_content): "microdata", 
                executor.submit(self._extract_heuristic, html_content): "heuristic"
            }
            
            # Submit multi-modal extraction if enabled
            if self.enable_multi_modal and self.multi_modal_processor:
                futures[executor.submit(self._extract_multi_modal, html_content, config)] = "multi_modal"
            
            # Collect results
            for future in as_completed(futures):
                method = futures[future]
                try:
                    result = future.result()
                    result["method"] = method
                    results.append(result)
                except Exception as e:
                    logger.error(f"{method} extraction failed: {e}")
                    results.append({"method": method, "success": False, "error": str(e)})
        
        processing_stats["traditional_time"] = time.time() - traditional_start
        self.extraction_stats["traditional_extractions"] += len(results)
        
        return results
    
    def _extract_sequential(self, html_content: str, config: Dict[str, Any],
                           processing_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract using all methods sequentially."""
        traditional_start = time.time()
        results = []
        
        # Run traditional extractions
        methods = [
            ("json_ld", self._extract_json_ld),
            ("microdata", self._extract_microdata),
            ("heuristic", self._extract_heuristic)
        ]
        
        # Add multi-modal extraction if enabled
        if self.enable_multi_modal and self.multi_modal_processor:
            methods.append(("multi_modal", lambda html: self._extract_multi_modal(html, config)))
        
        for method_name, extract_func in methods:
            try:
                result = extract_func(html_content)
                result["method"] = method_name
                results.append(result)
            except Exception as e:
                logger.error(f"{method_name} extraction failed: {e}")
                results.append({"method": method_name, "success": False, "error": str(e)})
        
        processing_stats["traditional_time"] = time.time() - traditional_start
        self.extraction_stats["traditional_extractions"] += len(results)
        
        return results
    
    def _extract_json_ld(self, html_content: str) -> Dict[str, Any]:
        """Extract using JSON-LD method."""
        results = self.json_ld_extractor.extract_from_html(html_content)
        
        if results and isinstance(results, list) and len(results) > 0:
            # Take the first result if multiple
            result = results[0]
            if hasattr(result, 'to_dict'):
                data = result.to_dict()
            else:
                data = result
            return {"data": data, "success": True, "confidence": 0.95}
        elif results and not isinstance(results, list):
            # Handle case where a single result is returned
            if hasattr(results, 'to_dict'):
                data = results.to_dict()
            else:
                data = results
            return {"data": data, "success": True, "confidence": 0.95}
        else:
            return {"data": {}, "success": False, "confidence": 0.0}
    
    def _extract_microdata(self, html_content: str) -> Dict[str, Any]:
        """Extract using microdata method."""
        results = self.microdata_extractor.extract_from_html(html_content)
        
        if results and isinstance(results, list) and len(results) > 0:
            # Take the first result if multiple
            result = results[0]
            if hasattr(result, 'to_dict'):
                data = result.to_dict()
            else:
                data = result
            return {"data": data, "success": True, "confidence": 0.85}
        elif results and not isinstance(results, list):
            # Handle case where a single result is returned
            if hasattr(results, 'to_dict'):
                data = results.to_dict()
            else:
                data = results
            return {"data": data, "success": True, "confidence": 0.85}
        else:
            return {"data": {}, "success": False, "confidence": 0.0}
    
    def _extract_heuristic(self, html_content: str) -> Dict[str, Any]:
        """Extract using heuristic method."""
        results = self.heuristic_extractor.extract_from_html(html_content)
        
        if results and isinstance(results, list) and len(results) > 0:
            # Take the first result if multiple
            result = results[0]
            if hasattr(result, 'to_dict'):
                data = result.to_dict()
            else:
                data = result
            return {"data": data, "success": True, "confidence": 0.70}
        elif results and not isinstance(results, list):
            # Handle case where a single result is returned
            if hasattr(results, 'to_dict'):
                data = results.to_dict()
            else:
                data = results
            return {"data": data, "success": True, "confidence": 0.70}
        else:
            return {"data": {}, "success": False, "confidence": 0.0}
    
    def _extract_multi_modal(self, html_content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract using multi-modal processing."""
        if not self.multi_modal_processor:
            return {"data": {}, "success": False, "confidence": 0.0}
        
        try:
            # Extract media URLs from HTML content
            media_files = self._extract_media_from_html(html_content)
            
            # Process with multi-modal processor
            multi_modal_result = self.multi_modal_processor.process_multi_modal(
                html_content, 
                config=config
            )
            
            # Convert multi-modal results to standard format
            mm_data = self._convert_multi_modal_to_data(multi_modal_result, media_files)
            
            # Calculate confidence based on processing stats
            confidence = multi_modal_result.get("processing_stats", {}).get("success_rate", 0.8)
            
            # Track multi-modal extraction
            self.extraction_stats["multi_modal_extractions"] += 1
            
            return {
                "method": "multi_modal",
                "data": mm_data,
                "success": True,
                "confidence": confidence,
                "raw_result": multi_modal_result,
                "media_files": media_files
            }
            
        except Exception as e:
            logger.error(f"Multi-modal extraction failed: {e}")
            return {
                "method": "multi_modal",
                "data": {},
                "success": False,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _extract_with_ai(self, html_content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract using AI/LLM method."""
        industry = config.get("industry", "Restaurant")
        industry_config = config.get("industry_config", {"industry": industry})
        confidence_threshold = config.get("confidence_threshold", 0.6)
        
        # Handle large content by chunking
        chunks = self._chunk_content_for_llm(html_content)
        all_extractions = []
        
        for chunk in chunks:
            ai_result = self.llm_extractor.extract(
                chunk, 
                industry, 
                industry_config,
                confidence_threshold=confidence_threshold
            )
            
            if ai_result.get("extractions"):
                all_extractions.extend(ai_result["extractions"])
        
        if all_extractions:
            # Convert AI extractions to standard format
            ai_data = self._convert_ai_extractions_to_data(all_extractions)
            avg_confidence = sum(e.get("confidence", 0) for e in all_extractions) / len(all_extractions)
            
            return {
                "method": "llm",
                "data": ai_data,
                "success": True,
                "confidence": avg_confidence,
                "raw_extractions": all_extractions
            }
        else:
            return {"method": "llm", "data": {}, "success": False, "confidence": 0.0}
    
    def _chunk_content_for_llm(self, html_content: str, max_chunk_size: int = 8000) -> List[str]:
        """Chunk large content for LLM processing."""
        if len(html_content) <= max_chunk_size:
            return [html_content]
        
        # Simple chunking by splitting on major HTML elements
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs and sections
        import re
        sections = re.split(r'(<(?:div|section|article|p)[^>]*>.*?</(?:div|section|article|p)>)', html_content, flags=re.DOTALL)
        
        for section in sections:
            if len(current_chunk) + len(section) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = section
                else:
                    # Section itself is too large, split it further
                    chunks.append(section[:max_chunk_size])
            else:
                current_chunk += section
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [html_content]
    
    def _convert_ai_extractions_to_data(self, extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert AI extractions to standard data format."""
        data = {}
        
        for extraction in extractions:
            category = extraction.get("category", "").lower()
            extracted_data = extraction.get("extracted_data", {})
            
            # Map AI categories to standard fields
            if "menu" in category or "food" in category:
                if "characteristics" in extracted_data:
                    data["menu_characteristics"] = extracted_data["characteristics"]
                if "items" in extracted_data:
                    data["menu_items"] = extracted_data["items"]
            
            elif "ambiance" in category or "atmosphere" in category:
                if "atmosphere" in extracted_data:
                    data["ambiance"] = extracted_data["atmosphere"]
                if "features" in extracted_data:
                    data["ambiance_features"] = extracted_data["features"]
            
            elif "basic" in category or "info" in category:
                # Map basic information fields
                for key, value in extracted_data.items():
                    if key in ["name", "address", "phone", "cuisine"]:
                        data[key] = value
            
            elif "staff" in category:
                if "qualifications" in extracted_data:
                    data["staff_qualifications"] = extracted_data["qualifications"]
            
            elif "service" in category:
                if "services" in extracted_data:
                    data["services"] = extracted_data["services"]
            
            elif "appointment" in category:
                if "options" in extracted_data:
                    data["appointment_options"] = extracted_data["options"]
        
        return data
    
    def _calculate_overall_confidence(self, merged_result: Dict[str, Any], 
                                    config: Dict[str, Any]) -> float:
        """Calculate overall confidence score."""
        confidence_scores = merged_result.get("confidence_scores", {})
        
        if not confidence_scores:
            return 0.0
        
        # Weight by number of fields from each method
        source_attribution = merged_result.get("source_attribution", {})
        method_field_counts = {}
        
        for field, method in source_attribution.items():
            method_field_counts[method] = method_field_counts.get(method, 0) + 1
        
        total_fields = sum(method_field_counts.values())
        if total_fields == 0:
            return 0.0
        
        # Calculate weighted average
        weighted_confidence = 0.0
        for method, confidence in confidence_scores.items():
            if method != "overall" and method in method_field_counts:
                weight = method_field_counts[method] / total_fields
                weighted_confidence += confidence * weight
        
        return weighted_confidence
    
    def _validate_extraction_result(self, merged_result: Dict[str, Any], 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extraction result quality."""
        data = merged_result.get("data", {})
        
        validation = {
            "schema_compliance": True,
            "data_quality_score": 0.0,
            "missing_fields": [],
            "data_completeness": 0.0
        }
        
        # Check required fields based on industry
        industry = config.get("industry", "Restaurant")
        if industry == "Restaurant":
            required_fields = ["name", "address"]
            optional_fields = ["phone", "cuisine", "hours", "menu_items"]
        elif industry == "Medical":
            required_fields = ["name", "address"]
            optional_fields = ["phone", "services", "staff_qualifications"]
        else:
            required_fields = ["name"]
            optional_fields = ["address", "phone"]
        
        # Check missing required fields
        for field in required_fields:
            if field not in data or not data[field]:
                validation["missing_fields"].append(field)
                validation["schema_compliance"] = False
        
        # Calculate completeness
        all_fields = required_fields + optional_fields
        present_fields = sum(1 for field in all_fields if field in data and data[field])
        validation["data_completeness"] = present_fields / len(all_fields)
        
        # Calculate quality score
        completeness_score = validation["data_completeness"]
        compliance_score = 1.0 if validation["schema_compliance"] else 0.5
        validation["data_quality_score"] = (completeness_score + compliance_score) / 2
        
        return validation
    
    def _track_extraction_performance(self, methods: List[str], result: AIEnhancedExtractionResult,
                                    processing_stats: Dict[str, Any]):
        """Track extraction performance for optimization."""
        overall_confidence = result.confidence_scores.get("overall", 0.0)
        data_completeness = result.validation_results.get("data_completeness", 0.0) if result.validation_results else 0.0
        
        # Track individual methods
        for method in methods:
            confidence = result.confidence_scores.get(method, 0.0)
            processing_time = processing_stats.get(f"{method}_time", 0.0)
            success = confidence > 0.5
            
            self.method_tracker.track_method_usage(method, success, confidence, processing_time)
        
        # Track combination
        if methods:
            self.method_tracker.track_combination_performance(methods, overall_confidence, data_completeness)
    
    def _generate_cache_key(self, html_content: str, config: Dict[str, Any]) -> str:
        """Generate cache key for content and config."""
        content_hash = hashlib.md5(html_content.encode()).hexdigest()
        config_str = str(sorted(config.items()))
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        return f"{content_hash}:{config_hash}"
    
    def extract_batch(self, html_contents: List[str], config: Dict[str, Any]) -> List[AIEnhancedExtractionResult]:
        """Extract data from multiple HTML contents in batch."""
        if config.get("batch_mode", False) and self.parallel_processing:
            # Parallel batch processing
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.extract_from_html, content, config) 
                          for content in html_contents]
                
                results = []
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Batch extraction failed: {e}")
                        results.append(AIEnhancedExtractionResult(
                            restaurant_data={},
                            extraction_methods=[],
                            confidence_scores={},
                            source_attribution={},
                            processing_stats={},
                            errors=[str(e)]
                        ))
                
                return results
        else:
            # Sequential batch processing
            return [self.extract_from_html(content, config) for content in html_contents]
    
    def get_extraction_statistics(self) -> Dict[str, Any]:
        """Get comprehensive extraction statistics."""
        method_stats = self.method_tracker.get_method_statistics()
        
        stats = {
            "total_extractions": self.extraction_stats["total_extractions"],
            "ai_extractions": self.extraction_stats["ai_extractions"],
            "traditional_extractions": self.extraction_stats["traditional_extractions"],
            "multi_modal_extractions": self.extraction_stats["multi_modal_extractions"],
            "method_usage_count": {method: data["usage_count"] for method, data in method_stats.items()},
            "method_success_rates": {method: data["success_rate"] for method, data in method_stats.items()},
            "average_confidence_by_method": {method: data["average_confidence"] for method, data in method_stats.items()}
        }
        
        return stats
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for optimization."""
        return self.method_tracker.get_method_statistics()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        if self.result_cache is None:
            return {"cache_enabled": False}
        
        with self._cache_lock:
            return {
                "cache_enabled": True,
                "cache_size": len(self.result_cache),
                "cache_hits": getattr(self, "_cache_hits", 0),
                "cache_misses": getattr(self, "_cache_misses", 0)
            }
    
    def _reset_extractors(self):
        """Reset extractors for testing."""
        # This method is for testing purposes
        pass
    
    def _extract_media_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract media files (images, PDFs) from HTML content with optimized processing."""
        if not html_content or len(html_content.strip()) < 10:
            return []
        
        try:
            from bs4 import BeautifulSoup
            import re
            
            # Pre-compiled patterns for better performance
            pdf_pattern = re.compile(r'href="([^"]*\.pdf)"', re.IGNORECASE)
            
            # Category keyword sets for fast lookup
            menu_keywords = {'menu', 'food', 'dish', 'wine', 'drink'}
            hours_keywords = {'hours', 'time', 'schedule'}
            contact_keywords = {'contact', 'phone', 'email'}
            ambiance_keywords = {'interior', 'ambiance', 'dining', 'atmosphere'}
            service_keywords = {'brochure', 'service', 'catering'}
            
            soup = BeautifulSoup(html_content, 'html.parser')
            media_files = []
            
            # Fast image extraction with optimized categorization
            for img in soup.find_all('img', src=True):
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                # Fast category determination using set intersection
                combined_text = (src + alt).lower()
                if any(kw in combined_text for kw in menu_keywords):
                    category = "menu"
                elif any(kw in combined_text for kw in hours_keywords):
                    category = "hours"
                elif any(kw in combined_text for kw in contact_keywords):
                    category = "contact"
                elif any(kw in combined_text for kw in ambiance_keywords):
                    category = "ambiance"
                else:
                    category = "general"
                
                media_files.append({
                    "type": "image",
                    "url": src,
                    "alt": alt,
                    "category": category
                })
            
            # Fast PDF extraction
            pdf_matches = pdf_pattern.findall(html_content)
            for pdf_url in pdf_matches:
                pdf_lower = pdf_url.lower()
                if any(kw in pdf_lower for kw in menu_keywords):
                    category = "menu"
                elif any(kw in pdf_lower for kw in service_keywords):
                    category = "services"
                else:
                    category = "general"
                
                media_files.append({
                    "type": "pdf",
                    "url": pdf_url,
                    "category": category
                })
            
            return media_files
            
        except Exception as e:
            logger.error(f"Failed to extract media from HTML: {e}")
            return []
    
    def _convert_multi_modal_to_data(self, multi_modal_result: Dict[str, Any], 
                                   media_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert multi-modal processing results to standard restaurant data format."""
        try:
            mm_data = {}
            
            # Extract text content from OCR results
            text_extraction = multi_modal_result.get("text_extraction", {})
            ocr_results = text_extraction.get("ocr_results", {})
            
            # Extract menu items
            if "menu_items" in ocr_results:
                mm_data["menu"] = ocr_results["menu_items"]
            
            # Extract business hours from OCR
            if "business_hours" in ocr_results:
                mm_data["hours"] = ocr_results["business_hours"]
            
            # Extract contact information from OCR
            if "contact_info" in ocr_results:
                mm_data["contact"] = ocr_results["contact_info"]
            
            # Extract services from PDF processing
            pdf_results = text_extraction.get("pdf_results", {})
            if "structured_data" in pdf_results:
                pdf_data = pdf_results["structured_data"]
                if "services" in pdf_data:
                    mm_data["services"] = pdf_data["services"]
                if "pricing" in pdf_data:
                    mm_data["pricing"] = pdf_data["pricing"]
            
            # Extract ambiance information from image analysis
            image_analysis = multi_modal_result.get("image_analysis", {})
            if "ambiance_description" in image_analysis:
                mm_data["ambiance"] = {
                    "description": image_analysis["ambiance_description"],
                    "visual_elements": image_analysis.get("visual_elements", {}),
                    "atmosphere_tags": image_analysis.get("atmosphere_tags", [])
                }
            
            # Add source attribution
            source_attribution = multi_modal_result.get("source_attribution", {})
            if source_attribution:
                mm_data["_source_attribution"] = source_attribution
            
            # Add processing metadata
            processing_stats = multi_modal_result.get("processing_stats", {})
            if processing_stats:
                mm_data["_processing_stats"] = {
                    "images_processed": processing_stats.get("images_processed", 0),
                    "pdfs_processed": processing_stats.get("pdfs_processed", 0),
                    "total_time": processing_stats.get("total_time", 0),
                    "success_rate": processing_stats.get("success_rate", 0)
                }
            
            return mm_data
            
        except Exception as e:
            logger.error(f"Failed to convert multi-modal results: {e}")
            return {}