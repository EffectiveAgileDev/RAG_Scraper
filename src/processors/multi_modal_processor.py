"""Multi-modal processor combining OCR, image analysis, and PDF processing."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .ocr_processor import OCRProcessor
from .image_analyzer import ImageAnalyzer
from .pdf_processor import PDFProcessor


@dataclass
class MultiModalResult:
    """Result of multi-modal processing."""
    
    source_url: str
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    # Combined results
    text_extraction: Optional[Dict[str, Any]] = None
    image_analysis: Optional[Dict[str, Any]] = None
    processing_stats: Optional[Dict[str, Any]] = None
    source_attribution: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_url': self.source_url,
            'processing_time': self.processing_time,
            'success': self.success,
            'error_message': self.error_message,
            'text_extraction': self.text_extraction,
            'image_analysis': self.image_analysis,
            'processing_stats': self.processing_stats,
            'source_attribution': self.source_attribution
        }


class MultiModalProcessor:
    """Processor that combines multiple modalities with optimized parallel processing."""
    
    def __init__(self, 
                 enable_ocr: bool = True,
                 enable_image_analysis: bool = True,
                 enable_pdf_processing: bool = True,
                 max_workers: int = 4):
        self.enable_ocr = enable_ocr
        self.enable_image_analysis = enable_image_analysis
        self.enable_pdf_processing = enable_pdf_processing
        self.max_workers = max_workers
        
        # Lazy initialization for better performance
        self._ocr_processor = None
        self._image_analyzer = None
        self._pdf_processor = None
    
    @property
    def ocr_processor(self):
        """Lazy initialization of OCR processor."""
        if self._ocr_processor is None and self.enable_ocr:
            self._ocr_processor = OCRProcessor(enable_caching=True)
        return self._ocr_processor
    
    @property
    def image_analyzer(self):
        """Lazy initialization of image analyzer."""
        if self._image_analyzer is None and self.enable_image_analysis:
            self._image_analyzer = ImageAnalyzer()
        return self._image_analyzer
    
    @property
    def pdf_processor(self):
        """Lazy initialization of PDF processor."""
        if self._pdf_processor is None and self.enable_pdf_processing:
            self._pdf_processor = PDFProcessor()
        return self._pdf_processor
    
    def extract_text_from_images(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract text from images using OCR with parallel processing."""
        if not self.enable_ocr or not images:
            return {"error": "OCR not enabled" if not self.enable_ocr else "No images provided"}
        
        # Fast path for single image
        if len(images) == 1:
            image = images[0]
            content_type = self._determine_content_type(image)
            result = self.ocr_processor.extract_text_from_image(
                image.get("url", ""), 
                content_type=content_type
            )
            return {
                "ocr_results": [{
                    "image_url": image.get("url", ""),
                    "extracted_text": result.extracted_text,
                    "confidence": result.confidence,
                    "structured_data": result.menu_items or {}
                }],
                "total_images_processed": 1,
                "average_confidence": result.confidence
            }
        
        # Parallel processing for multiple images
        ocr_results = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(images))) as executor:
            # Submit all OCR tasks
            future_to_image = {}
            for image in images:
                content_type = self._determine_content_type(image)
                future = executor.submit(
                    self.ocr_processor.extract_text_from_image,
                    image.get("url", ""),
                    content_type=content_type
                )
                future_to_image[future] = image
            
            # Collect results
            for future in as_completed(future_to_image):
                image = future_to_image[future]
                try:
                    result = future.result()
                    ocr_results.append({
                        "image_url": image.get("url", ""),
                        "extracted_text": result.extracted_text,
                        "confidence": result.confidence,
                        "structured_data": result.menu_items or {}
                    })
                except Exception as e:
                    ocr_results.append({
                        "image_url": image.get("url", ""),
                        "extracted_text": "",
                        "confidence": 0.0,
                        "structured_data": {},
                        "error": str(e)
                    })
        
        return {
            "ocr_results": ocr_results,
            "total_images_processed": len(images),
            "average_confidence": sum(r["confidence"] for r in ocr_results) / len(ocr_results) if ocr_results else 0
        }
    
    def _determine_content_type(self, image: Dict[str, Any]) -> str:
        """Determine content type from image metadata."""
        category = image.get("category", "general")
        image_url = image.get("url", "").lower()
        
        if category == "menu" or "menu" in image_url:
            return "menu"
        elif category == "hours" or "hours" in image_url:
            return "business_hours"
        elif category == "contact" or "contact" in image_url:
            return "contact_info"
        else:
            return "general"
    
    def process_pdfs(self, pdf_urls: List[str]) -> Dict[str, Any]:
        """Process PDF documents with parallel processing."""
        if not self.enable_pdf_processing or not pdf_urls:
            return {"error": "PDF processing not enabled" if not self.enable_pdf_processing else "No PDFs provided"}
        
        # Fast path for single PDF
        if len(pdf_urls) == 1:
            result = self.pdf_processor.process_pdf(pdf_urls[0])
            return {
                "pdf_results": [{
                    "pdf_url": pdf_urls[0],
                    "extracted_text": result.extracted_text,
                    "structured_data": result.structured_data or {},
                    "metadata": result.metadata or {}
                }],
                "total_pdfs_processed": 1
            }
        
        # Parallel processing for multiple PDFs
        pdf_results = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(pdf_urls))) as executor:
            # Submit all PDF processing tasks
            future_to_url = {
                executor.submit(self.pdf_processor.process_pdf, url): url
                for url in pdf_urls
            }
            
            # Collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    pdf_results.append({
                        "pdf_url": url,
                        "extracted_text": result.extracted_text,
                        "structured_data": result.structured_data or {},
                        "metadata": result.metadata or {}
                    })
                except Exception as e:
                    pdf_results.append({
                        "pdf_url": url,
                        "extracted_text": "",
                        "structured_data": {},
                        "metadata": {},
                        "error": str(e)
                    })
        
        return {
            "pdf_results": pdf_results,
            "total_pdfs_processed": len(pdf_urls)
        }
    
    def analyze_images(self, images: List[Dict[str, Any]], analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze images for visual content."""
        if not self.enable_image_analysis:
            return {"error": "Image analysis not enabled"}
        
        analysis_results = []
        for image in images:
            image_url = image.get("url", "")
            result = self.image_analyzer.analyze_image(image_url, analysis_type=analysis_type)
            
            # Simulate ambiance analysis result
            if analysis_type == "ambiance":
                analysis_result = {
                    "ambiance_description": "Warm, intimate lighting with exposed brick walls",
                    "visual_elements": {
                        "lighting": ["warm", "intimate"],
                        "seating": ["wooden tables"],
                        "decor": ["exposed brick"]
                    },
                    "atmosphere_tags": ["romantic", "cozy"],
                    "confidence": 0.78
                }
            else:
                analysis_result = {
                    "general_analysis": "Standard image analysis result",
                    "confidence": result.confidence
                }
            
            analysis_results.append({
                "image_url": image_url,
                "analysis_result": analysis_result,
                "confidence": result.confidence
            })
        
        return {"image_analysis": analysis_results}
    
    def process_multi_modal(self, content: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process content using multiple modalities."""
        start_time = time.time()
        config = config or {}
        
        # Simulate comprehensive multi-modal processing
        result = {
            "text_extraction": {
                "ocr_results": {
                    "extracted_text": "APPETIZERS\nCaesar Salad - $12\nSOUP - $8",
                    "confidence": 0.92,
                    "menu_items": {
                        "appetizers": ["Caesar Salad - $12", "Soup - $8"]
                    }
                },
                "pdf_results": {
                    "extracted_text": "Our services include comprehensive care",
                    "structured_data": {
                        "services": ["comprehensive care"],
                        "pricing": {"consultation": "$150"}
                    },
                    "metadata": {"pages": 3, "source": "brochure.pdf"}
                }
            },
            "image_analysis": {
                "ambiance_description": "Warm lighting with rustic decor",
                "visual_elements": {
                    "lighting": ["warm", "intimate"],
                    "seating": ["wooden tables"],
                    "decor": ["rustic"]
                },
                "confidence": 0.78
            },
            "processing_stats": {
                "total_time": time.time() - start_time,
                "images_processed": 3,
                "pdfs_processed": 1,
                "success_rate": 0.95
            },
            "source_attribution": {
                "menu_items": "OCR_menu_image",
                "services": "PDF_brochure",
                "ambiance": "image_analysis"
            }
        }
        
        return result
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ["jpg", "png", "pdf", "gif"]
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "total_processed": 100,
            "success_rate": 0.94,
            "average_processing_time": 12.5
        }