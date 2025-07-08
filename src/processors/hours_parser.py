"""Hours parsing for restaurant operating hours from PDF text."""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class HoursResult:
    """Result of hours parsing."""
    hours: Dict[str, str]
    weekday_hours: str = ""
    weekend_hours: str = ""
    special_hours: str = ""
    confidence: float = 0.0


class HoursParser:
    """Parses restaurant operating hours from text."""
    
    def __init__(self):
        """Initialize hours parser."""
        self.day_patterns = self._initialize_day_patterns()
        self.time_patterns = self._initialize_time_patterns()
    
    def _initialize_day_patterns(self) -> Dict[str, str]:
        """Initialize day name patterns."""
        return {
            'monday': r'(?:Monday|Mon)',
            'tuesday': r'(?:Tuesday|Tue)',
            'wednesday': r'(?:Wednesday|Wed)',
            'thursday': r'(?:Thursday|Thu)',
            'friday': r'(?:Friday|Fri)',
            'saturday': r'(?:Saturday|Sat)',
            'sunday': r'(?:Sunday|Sun)'
        }
    
    def _initialize_time_patterns(self) -> List[str]:
        """Initialize time format patterns."""
        return [
            r'\d{1,2}:\d{2}\s*(?:AM|PM)',
            r'\d{1,2}(?::\d{2})?(?:am|pm)',
            r'\d{1,2}(?::\d{2})?\s*(?:AM|PM)'
        ]
    
    def parse_hours_from_text(self, text: str) -> Dict[str, Any]:
        """Parse hours from text.
        
        Args:
            text: Text containing hours information
            
        Returns:
            Dictionary with parsed hours information
        """
        if not text:
            return {'hours': {}, 'weekday_hours': '', 'weekend_hours': '', 'special_hours': ''}
        
        hours_dict = {}
        hours_section = self._extract_hours_section(text)
        
        if not hours_section:
            return {'hours': {}, 'weekday_hours': '', 'weekend_hours': '', 'special_hours': ''}
        
        # Parse individual day hours
        parsed_hours = self._parse_individual_hours(hours_section)
        hours_dict.update(parsed_hours)
        
        # Parse range hours (e.g., "Monday-Thursday")
        range_hours = self._parse_range_hours(hours_section)
        hours_dict.update(range_hours)
        
        # Categorize hours
        weekday_hours = self._extract_weekday_hours(hours_dict)
        weekend_hours = self._extract_weekend_hours(hours_dict)
        special_hours = self._extract_special_hours(hours_section)
        
        return {
            'hours': hours_dict,
            'weekday_hours': weekday_hours,
            'weekend_hours': weekend_hours,
            'special_hours': special_hours
        }
    
    def _extract_hours_section(self, text: str) -> str:
        """Extract the hours section from text.
        
        Args:
            text: Full text
            
        Returns:
            Hours section text
        """
        # Look for HOURS section
        hours_match = re.search(r'HOURS?\s*\n(.*?)(?:\n\s*\n|\n[A-Z]|\Z)', text, re.DOTALL | re.IGNORECASE)
        if hours_match:
            return hours_match.group(1).strip()
        
        # Look for any line containing hours information
        lines = text.split('\n')
        hours_lines = []
        
        for line in lines:
            line = line.strip()
            if self._contains_hours_info(line):
                hours_lines.append(line)
        
        return '\n'.join(hours_lines)
    
    def _contains_hours_info(self, line: str) -> bool:
        """Check if line contains hours information.
        
        Args:
            line: Line to check
            
        Returns:
            True if line contains hours info
        """
        # Contains day names and times
        has_day = any(re.search(pattern, line, re.IGNORECASE) for pattern in self.day_patterns.values())
        has_time = any(re.search(pattern, line, re.IGNORECASE) for pattern in self.time_patterns)
        
        return has_day and has_time
    
    def _parse_individual_hours(self, hours_text: str) -> Dict[str, str]:
        """Parse individual day hours.
        
        Args:
            hours_text: Hours section text
            
        Returns:
            Dictionary mapping days to hours
        """
        hours_dict = {}
        
        # Pattern: Day: Time - Time
        for day_name, day_pattern in self.day_patterns.items():
            pattern = rf'{day_pattern}\s*:\s*(.+?)(?:\n|$)'
            match = re.search(pattern, hours_text, re.IGNORECASE)
            if match:
                hours_dict[day_name] = match.group(1).strip()
        
        return hours_dict
    
    def _parse_range_hours(self, hours_text: str) -> Dict[str, str]:
        """Parse range hours (e.g., Monday-Thursday).
        
        Args:
            hours_text: Hours section text
            
        Returns:
            Dictionary mapping days to hours
        """
        hours_dict = {}
        
        # Pattern: Day-Day: Time - Time
        day_names = list(self.day_patterns.keys())
        
        for line in hours_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Monday-Thursday pattern
            monday_thu_match = re.search(r'(Monday|Mon)(?:day)?\s*-\s*(Thursday|Thu)(?:rsday)?\s*:\s*(.+)', line, re.IGNORECASE)
            if monday_thu_match:
                time_range = monday_thu_match.group(3).strip()
                for day in ['monday', 'tuesday', 'wednesday', 'thursday']:
                    hours_dict[day] = time_range
                continue
            
            # Friday-Saturday pattern
            fri_sat_match = re.search(r'(Friday|Fri)(?:day)?\s*-\s*(Saturday|Sat)(?:urday)?\s*:\s*(.+)', line, re.IGNORECASE)
            if fri_sat_match:
                time_range = fri_sat_match.group(3).strip()
                for day in ['friday', 'saturday']:
                    hours_dict[day] = time_range
                continue
            
            # Generic range pattern
            range_match = re.search(r'(\w+)\s*-\s*(\w+)\s*:\s*(.+)', line, re.IGNORECASE)
            if range_match:
                start_day = range_match.group(1).lower()
                end_day = range_match.group(2).lower()
                time_range = range_match.group(3).strip()
                
                # Map abbreviated days to full names
                day_mapping = {
                    'mon': 'monday', 'tue': 'tuesday', 'wed': 'wednesday', 
                    'thu': 'thursday', 'fri': 'friday', 'sat': 'saturday', 'sun': 'sunday'
                }
                
                start_day = day_mapping.get(start_day, start_day)
                end_day = day_mapping.get(end_day, end_day)
                
                if start_day in day_names and end_day in day_names:
                    start_idx = day_names.index(start_day)
                    end_idx = day_names.index(end_day)
                    
                    for i in range(start_idx, end_idx + 1):
                        hours_dict[day_names[i]] = time_range
        
        return hours_dict
    
    def _extract_weekday_hours(self, hours_dict: Dict[str, str]) -> str:
        """Extract weekday hours summary.
        
        Args:
            hours_dict: Dictionary of day to hours
            
        Returns:
            Weekday hours summary
        """
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        weekday_hours = []
        
        for day in weekdays:
            if day in hours_dict:
                weekday_hours.append(f"{day.title()}: {hours_dict[day]}")
        
        return '; '.join(weekday_hours)
    
    def _extract_weekend_hours(self, hours_dict: Dict[str, str]) -> str:
        """Extract weekend hours summary.
        
        Args:
            hours_dict: Dictionary of day to hours
            
        Returns:
            Weekend hours summary
        """
        weekend_hours = []
        
        if 'saturday' in hours_dict:
            weekend_hours.append(f"Saturday: {hours_dict['saturday']}")
        if 'sunday' in hours_dict:
            weekend_hours.append(f"Sunday: {hours_dict['sunday']}")
        
        return '; '.join(weekend_hours)
    
    def _extract_special_hours(self, hours_text: str) -> str:
        """Extract special hours or notes.
        
        Args:
            hours_text: Hours section text
            
        Returns:
            Special hours notes
        """
        special_indicators = ['holiday', 'closed', 'special', 'note', 'except']
        
        for line in hours_text.split('\n'):
            line = line.strip()
            if any(indicator in line.lower() for indicator in special_indicators):
                return line
        
        return ''