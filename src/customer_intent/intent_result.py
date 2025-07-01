"""Intent mapping result data structures."""


class IntentMappingResult:
    """Result of intent mapping process."""
    
    def __init__(self, mappings, categories, confidence_score, processing_time):
        """Initialize IntentMappingResult."""
        self.mappings = mappings
        self.categories = categories  
        self.confidence_score = confidence_score
        self.processing_time = processing_time