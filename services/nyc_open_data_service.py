"""
NYC Open Data service for fetching free public event data.

This module handles interaction with the NYC Open Data API, providing access to:
- Public events and activities
- Community events and permits
- Free event data without API key requirements
- Real-time event information from NYC agencies

The NYC Open Data API is completely free and open, requiring no authentication.

Author: ExploreNYC Team
Version: 1.0.0
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import time

# Local imports
from config import Config
from utils.error_handling import log_error, handle_api_error, APIError
from utils.date_utils import parse_date_string

class NYCOpenDataService:
    """
    Service for interacting with the NYC Open Data API.
    
    This class provides access to NYC's open data portal, specifically the
    NYC Events API which contains information about public events, permits,
    and activities throughout the city.
    """
    
    def __init__(self):
        """
        Initialize the NYC Open Data service.
        
        Note: No API key is required for NYC Open Data API access.
        """
        self.base_url = "https://data.cityofnewyork.us/resource"
        self.rate_limit_delay = 1  # 1 second between requests
        self.last_request_time = 0
        
        # NYC Open Data is completely free and open - no API key required
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a rate-limited request to the NYC Open Data API."""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
        
        # Prepare request
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_error(e, f"NYC Open Data API request failed: {endpoint}")
            raise APIError(handle_api_error(e))
    
    def search_events(self, 
                     location: str = "New York, NY",
                     categories: List[str] = None,
                     start_date: str = None,
                     end_date: str = None,
                     limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for events from NYC Open Data.
        
        Args:
            location: Location to search in (default: "New York, NY")
            categories: List of category names to filter by
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            # Use the NYC Events API endpoint
            params = {
                "$limit": min(limit, 1000),  # NYC Open Data limit
                "$order": "start_date_time DESC"
            }
            
            # Add date filters if provided
            if start_date:
                params["$where"] = f"start_date_time >= '{start_date}T00:00:00.000'"
            if end_date:
                if "$where" in params:
                    params["$where"] += f" AND end_date_time <= '{end_date}T23:59:59.000'"
                else:
                    params["$where"] = f"end_date_time <= '{end_date}T23:59:59.000'"
            
            # Make the request to the NYC Events API
            response = self._make_request("tvpp-9vvx.json", params)
            
            # Process and return events
            events = response if isinstance(response, list) else []
            processed_events = [self._process_event(event) for event in events]
            
            # Filter by categories if provided
            if categories:
                processed_events = self._filter_by_categories(processed_events, categories)
            
            return processed_events[:limit]
            
        except Exception as e:
            log_error(e, "NYC Open Data search failed")
            return []
    
    def _process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw NYC Events API data into our standard format."""
        try:
            # Extract basic information from the NYC Events API structure
            event = {
                "id": event_data.get("event_id", ""),
                "title": event_data.get("event_name", "NYC Event"),
                "description": self._generate_description(event_data),
                "category": self._map_event_type(event_data.get("event_type", "")),
                "location": self._format_location(event_data),
                "venue": event_data.get("event_location", ""),
                "date": self._parse_nyc_date(event_data.get("start_date_time")),
                "time": self._extract_time(event_data.get("start_date_time")),
                "price": {"min": 0, "max": 0, "currency": "USD", "display": "Free"},
                "url": "",
                "image_url": "",
                "tags": self._generate_tags(event_data),
                "accessibility": {"wheelchair_accessible": False, "sign_language_interpretation": False, "audio_description": False, "large_print_materials": False},
                "source": "NYC Open Data"
            }
            
            return event
            
        except Exception as e:
            log_error(e, f"Error processing NYC Events API event: {event_data.get('event_id', 'unknown')}")
            return {}
    
    def _generate_description(self, event_data: Dict[str, Any]) -> str:
        """Generate a description from event data."""
        event_name = event_data.get("event_name", "")
        event_type = event_data.get("event_type", "")
        borough = event_data.get("event_borough", "")
        
        description = f"{event_name}"
        if event_type:
            description += f" - {event_type}"
        if borough:
            description += f" in {borough}"
        
        return description
    
    def _map_event_type(self, event_type: str) -> str:
        """Map NYC event types to our categories."""
        if not event_type:
            return "Other"
        
        event_type_lower = event_type.lower()
        
        if "sport" in event_type_lower:
            return "Sports"
        elif "special event" in event_type_lower:
            return "Entertainment"
        elif "yoga" in event_type_lower:
            return "Health & Wellness"
        elif "celebration" in event_type_lower:
            return "Community"
        else:
            return "Other"
    
    def _format_location(self, event_data: Dict[str, Any]) -> str:
        """Format location information."""
        borough = event_data.get("event_borough", "")
        if borough:
            return f"{borough}, NY"
        return "New York, NY"
    
    def _extract_time(self, date_time_str: str) -> str:
        """Extract time from datetime string."""
        if not date_time_str:
            return ""
        
        try:
            dt = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
            return dt.strftime("%I:%M %p")
        except:
            return ""
    
    def _generate_tags(self, event_data: Dict[str, Any]) -> List[str]:
        """Generate tags from event data."""
        tags = []
        
        # Add event type as tag
        event_type = event_data.get("event_type", "").lower()
        if event_type:
            tags.append(event_type.replace(" ", "_"))
        
        # Add borough as tag
        borough = event_data.get("event_borough", "").lower()
        if borough:
            tags.append(borough)
        
        # Add agency as tag
        agency = event_data.get("event_agency", "").lower()
        if agency:
            tags.append(agency.replace(" ", "_"))
        
        return tags
    
    def _parse_nyc_date(self, date_str: str) -> Optional[datetime]:
        """Parse NYC Events API date format."""
        if not date_str:
            return None
        
        try:
            # NYC Events API uses ISO format: 2025-09-21T08:00:00.000
            return parse_date_string(date_str)
        except:
            return None
    
    def _filter_by_categories(self, events: List[Dict[str, Any]], categories: List[str]) -> List[Dict[str, Any]]:
        """Filter events by categories."""
        if not categories:
            return events
        
        categories_lower = [cat.lower() for cat in categories]
        filtered_events = []
        
        for event in events:
            event_category = event.get("category", "").lower()
            if any(cat in event_category for cat in categories_lower):
                filtered_events.append(event)
        
        return filtered_events
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get available categories from NYC Events API."""
        return [
            {"id": "sports", "name": "Sports", "short_name": "sports"},
            {"id": "entertainment", "name": "Entertainment", "short_name": "entertainment"},
            {"id": "health_wellness", "name": "Health & Wellness", "short_name": "health"},
            {"id": "community", "name": "Community", "short_name": "community"},
            {"id": "other", "name": "Other", "short_name": "other"}
        ]
