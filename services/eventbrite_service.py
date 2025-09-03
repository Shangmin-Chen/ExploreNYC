"""
Eventbrite API service for fetching real event data.

This module handles interaction with the Eventbrite API, including:
- Authentication and API key management
- Rate limiting and request throttling
- Event data fetching and processing
- Data transformation to standardized format

Note: Currently experiencing API endpoint issues (404 errors) that need resolution.

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

class EventbriteService:
    """
    Service for interacting with the Eventbrite API.
    
    This class handles all communication with the Eventbrite API, including
    authentication, rate limiting, and data processing.
    """
    
    def __init__(self):
        """
        Initialize the Eventbrite service.
        
        Raises:
            ValueError: If Eventbrite API key is not configured
        """
        self.api_key = Config.EVENTBRITE_API_KEY
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.rate_limit_delay = 1  # 1 second between requests
        self.last_request_time = 0
        
        if not self.api_key:
            raise ValueError("Eventbrite API key not found. Please set EVENTBRITE_API_KEY in your environment.")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a rate-limited request to the Eventbrite API.
        
        Args:
            endpoint (str): API endpoint to call
            params (Dict[str, Any], optional): Query parameters
            
        Returns:
            Dict[str, Any]: JSON response from the API
            
        Raises:
            APIError: If the API request fails
        """
        # Implement rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
        
        # Prepare request
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_error(e, f"Eventbrite API request failed: {endpoint}")
            raise APIError(handle_api_error(e))
    
    def search_events(self, 
                     location: str = "New York, NY",
                     categories: List[str] = None,
                     start_date: str = None,
                     end_date: str = None,
                     price: str = "free,paid",
                     limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for events on Eventbrite.
        
        Args:
            location: Location to search in (default: "New York, NY")
            categories: List of category IDs to filter by
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            price: Price filter ("free", "paid", or "free,paid")
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            # Build search parameters
            params = {
                "location.address": location,
                "price": price,
                "expand": "venue,organizer",
                "status": "live"
            }
            
            # Add date filters if provided
            if start_date:
                params["start_date.range_start"] = f"{start_date}T00:00:00"
            if end_date:
                params["start_date.range_end"] = f"{end_date}T23:59:59"
            
            # Add category filter if provided
            if categories:
                params["categories"] = ",".join(categories)
            
            # Make the request
            response = self._make_request("events/search/", params)
            
            # Process and return events
            events = response.get("events", [])
            return [self._process_event(event) for event in events[:limit]]
            
        except Exception as e:
            log_error(e, "Eventbrite search failed")
            return []
    
    def _process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Eventbrite event data into our standard format."""
        try:
            # Extract basic information
            event = {
                "id": event_data.get("id", ""),
                "title": event_data.get("name", {}).get("text", "").strip(),
                "description": event_data.get("description", {}).get("text", "").strip(),
                "category": self._get_category_name(event_data.get("category_id", "")),
                "location": self._get_location(event_data),
                "venue": self._get_venue_name(event_data),
                "date": self._parse_event_date(event_data),
                "time": self._get_event_time(event_data),
                "price": self._get_price_info(event_data),
                "url": event_data.get("url", ""),
                "image_url": self._get_image_url(event_data),
                "tags": self._extract_tags(event_data),
                "accessibility": self._get_accessibility_info(event_data),
                "rating": 0,  # Eventbrite doesn't provide ratings
                "source": "Eventbrite"
            }
            
            return event
            
        except Exception as e:
            log_error(e, f"Error processing Eventbrite event: {event_data.get('id', 'unknown')}")
            return {}
    
    def _get_category_name(self, category_id: str) -> str:
        """Get category name from category ID."""
        if not category_id:
            return "Other"
        
        # Eventbrite category mapping
        category_map = {
            "103": "Music",
            "105": "Food & Drink",
            "110": "Art",
            "111": "Film & Media",
            "113": "Sports & Fitness",
            "114": "Health",
            "115": "Science & Technology",
            "116": "Travel & Outdoor",
            "117": "Charity & Causes",
            "118": "Religion & Spirituality",
            "119": "Family & Education",
            "120": "Seasonal & Holiday",
            "121": "Government & Politics",
            "122": "Fashion & Beauty",
            "123": "Home & Lifestyle",
            "124": "Auto, Boat & Air",
            "125": "Hobbies & Special Interest",
            "126": "School Activities",
            "127": "Other"
        }
        
        return category_map.get(category_id, "Other")
    
    def _get_location(self, event_data: Dict[str, Any]) -> str:
        """Extract location information from event data."""
        venue = event_data.get("venue", {})
        if venue:
            address = venue.get("address", {})
            city = address.get("city", "")
            region = address.get("region", "")
            if city and region:
                return f"{city}, {region}"
            elif city:
                return city
        
        return "New York, NY"
    
    def _get_venue_name(self, event_data: Dict[str, Any]) -> str:
        """Extract venue name from event data."""
        venue = event_data.get("venue", {})
        if venue:
            return venue.get("name", "")
        return ""
    
    def _parse_event_date(self, event_data: Dict[str, Any]) -> Optional[datetime]:
        """Parse event date from Eventbrite data."""
        start = event_data.get("start", {})
        if start:
            date_str = start.get("local", "")
            if date_str:
                return parse_date_string(date_str)
        return None
    
    def _get_event_time(self, event_data: Dict[str, Any]) -> str:
        """Extract event time from event data."""
        start = event_data.get("start", {})
        if start:
            date_str = start.get("local", "")
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return dt.strftime("%I:%M %p")
                except:
                    pass
        return ""
    
    def _get_price_info(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract price information from event data."""
        ticket_availability = event_data.get("ticket_availability", {})
        is_free = ticket_availability.get("is_free", False)
        
        if is_free:
            return {
                "min": 0,
                "max": 0,
                "currency": "USD",
                "display": "Free"
            }
        
        # Try to get price from ticket classes
        ticket_classes = event_data.get("ticket_classes", [])
        if ticket_classes:
            prices = []
            for ticket_class in ticket_classes:
                cost = ticket_class.get("cost", {})
                if cost:
                    amount = cost.get("major_value", 0)
                    if amount:
                        prices.append(amount)
            
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                return {
                    "min": min_price,
                    "max": max_price,
                    "currency": "USD",
                    "display": f"${min_price}" + (f" - ${max_price}" if min_price != max_price else "")
                }
        
        return {
            "min": 0,
            "max": 0,
            "currency": "USD",
            "display": "Price varies"
        }
    
    def _get_image_url(self, event_data: Dict[str, Any]) -> str:
        """Extract image URL from event data."""
        logo = event_data.get("logo", {})
        if logo:
            return logo.get("url", "")
        return ""
    
    def _extract_tags(self, event_data: Dict[str, Any]) -> List[str]:
        """Extract tags from event data."""
        tags = []
        
        # Add category as a tag
        category = self._get_category_name(event_data.get("category_id", ""))
        if category:
            tags.append(category.lower())
        
        # Add format as a tag
        format_info = event_data.get("format", {})
        if format_info:
            format_name = format_info.get("name", "").lower()
            if format_name:
                tags.append(format_name)
        
        return tags
    
    def _get_accessibility_info(self, event_data: Dict[str, Any]) -> Dict[str, bool]:
        """Extract accessibility information from event data."""
        # Eventbrite doesn't provide detailed accessibility info in the basic API
        # This would need to be enhanced with additional API calls or manual data
        return {
            "wheelchair_accessible": False,
            "sign_language_interpretation": False,
            "audio_description": False,
            "large_print_materials": False
        }
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get available event categories from Eventbrite."""
        try:
            response = self._make_request("categories/")
            categories = response.get("categories", [])
            
            return [
                {
                    "id": cat.get("id", ""),
                    "name": cat.get("name", ""),
                    "short_name": cat.get("short_name", "")
                }
                for cat in categories
            ]
        except Exception as e:
            log_error(e, "Failed to fetch Eventbrite categories")
            return []
