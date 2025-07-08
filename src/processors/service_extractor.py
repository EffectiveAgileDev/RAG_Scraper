"""Service extraction for restaurant services from PDF text."""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import WTEG Services for type compatibility
from src.wteg.wteg_schema import WTEGServices


@dataclass
class ServiceResult:
    """Result of service extraction."""
    services: WTEGServices
    confidence: float = 0.0
    extracted_text: str = ""


class ServiceExtractor:
    """Extracts restaurant service offerings from text."""
    
    def __init__(self):
        """Initialize service extractor."""
        self.service_patterns = self._initialize_service_patterns()
    
    def _initialize_service_patterns(self) -> Dict[str, List[str]]:
        """Initialize service detection patterns."""
        return {
            'delivery': [
                r'delivery\s*(?:available|offered|provided)?',
                r'we\s*deliver',
                r'free\s*delivery',
                r'delivery\s*fee',
                r'door\s*dash',
                r'uber\s*eats',
                r'grub\s*hub'
            ],
            'takeout': [
                r'take\s*out\s*(?:available|offered)?',
                r'pickup\s*(?:available|offered)?',
                r'to\s*go\s*(?:orders|available)?',
                r'carry\s*out',
                r'takeaway'
            ],
            'catering': [
                r'catering\s*(?:available|offered|services)?',
                r'cater\s*(?:events|parties)?',
                r'party\s*platters?',
                r'group\s*orders?',
                r'special\s*events?',
                r'office\s*catering'
            ],
            'reservations': [
                r'reservations?\s*(?:accepted|available|required)?',
                r'book\s*(?:a\s*)?table',
                r'call\s*(?:ahead|for\s*reservations?)',
                r'reserve\s*(?:a\s*)?table',
                r'make\s*(?:a\s*)?reservation'
            ],
            'online_ordering': [
                r'online\s*ordering?',
                r'order\s*online',
                r'web\s*ordering?',
                r'mobile\s*(?:app|ordering?)',
                r'app\s*ordering?'
            ],
            'curbside_pickup': [
                r'curbside\s*pickup',
                r'curb\s*side\s*service',
                r'pickup\s*service',
                r'contactless\s*pickup'
            ],
            'outdoor_seating': [
                r'outdoor\s*seating',
                r'patio\s*seating',
                r'al\s*fresco',
                r'garden\s*seating',
                r'terrace\s*seating',
                r'sidewalk\s*seating'
            ],
            'private_dining': [
                r'private\s*dining',
                r'private\s*room',
                r'event\s*space',
                r'banquet\s*room',
                r'party\s*room'
            ]
        }
    
    def extract_services_from_text(self, text: str) -> WTEGServices:
        """Extract services from text.
        
        Args:
            text: Text to extract services from
            
        Returns:
            WTEGServices object with detected services
        """
        if not text:
            return WTEGServices()
        
        services = WTEGServices()
        
        # Convert text to lowercase for pattern matching
        text_lower = text.lower()
        
        # Check for delivery services
        services.delivery_available = self._check_service_available(text_lower, 'delivery')
        
        # Check for takeout services
        services.takeout_available = self._check_service_available(text_lower, 'takeout')
        
        # Check for catering services
        services.catering_available = self._check_service_available(text_lower, 'catering')
        
        # Check for reservations
        services.reservations_accepted = self._check_service_available(text_lower, 'reservations')
        
        # Check for online ordering
        services.online_ordering = self._check_service_available(text_lower, 'online_ordering')
        
        # Check for curbside pickup
        services.curbside_pickup = self._check_service_available(text_lower, 'curbside_pickup')
        
        # Check for outdoor seating
        services.outdoor_seating = self._check_service_available(text_lower, 'outdoor_seating')
        
        # Check for private dining
        services.private_dining = self._check_service_available(text_lower, 'private_dining')
        
        return services
    
    def _check_service_available(self, text: str, service_type: str) -> bool:
        """Check if a service is available based on text patterns.
        
        Args:
            text: Text to check (should be lowercase)
            service_type: Type of service to check for
            
        Returns:
            True if service appears to be available
        """
        patterns = self.service_patterns.get(service_type, [])
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def extract_services_with_confidence(self, text: str) -> ServiceResult:
        """Extract services with confidence scoring.
        
        Args:
            text: Text to extract services from
            
        Returns:
            ServiceResult with services and confidence
        """
        services = self.extract_services_from_text(text)
        
        # Calculate confidence based on number of matches
        service_count = sum([
            services.delivery_available,
            services.takeout_available,
            services.catering_available,
            services.reservations_accepted,
            services.online_ordering,
            services.curbside_pickup,
            services.outdoor_seating,
            services.private_dining
        ])
        
        # Higher confidence if more services found
        confidence = min(0.9, service_count * 0.15)
        
        return ServiceResult(
            services=services,
            confidence=confidence,
            extracted_text=self._extract_services_section(text)
        )
    
    def _extract_services_section(self, text: str) -> str:
        """Extract the services section from text.
        
        Args:
            text: Full text
            
        Returns:
            Services section text
        """
        # Look for SERVICES section
        services_match = re.search(r'SERVICES?\s*\n(.*?)(?:\n\s*\n|\n[A-Z]|\Z)', text, re.DOTALL | re.IGNORECASE)
        if services_match:
            return services_match.group(1).strip()
        
        # Look for any lines containing service information
        lines = text.split('\n')
        service_lines = []
        
        for line in lines:
            line = line.strip()
            if self._contains_service_info(line):
                service_lines.append(line)
        
        return '\n'.join(service_lines)
    
    def _contains_service_info(self, line: str) -> bool:
        """Check if line contains service information.
        
        Args:
            line: Line to check
            
        Returns:
            True if line contains service info
        """
        service_keywords = [
            'delivery', 'takeout', 'catering', 'reservations', 'pickup',
            'online', 'curbside', 'outdoor', 'private', 'seating'
        ]
        
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in service_keywords)
    
    def get_service_summary(self, services: WTEGServices) -> str:
        """Get a summary of available services.
        
        Args:
            services: WTEGServices object
            
        Returns:
            Summary string of available services
        """
        available_services = services.get_available_services()
        
        if not available_services:
            return "No services listed"
        
        if len(available_services) == 1:
            return f"Service: {available_services[0]}"
        elif len(available_services) == 2:
            return f"Services: {available_services[0]} and {available_services[1]}"
        else:
            return f"Services: {', '.join(available_services[:-1])}, and {available_services[-1]}"