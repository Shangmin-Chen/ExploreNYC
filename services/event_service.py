"""
Unified event service that combines multiple event sources.
Provides a single interface for fetching events from Eventbrite and NYC Open Data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import concurrent.futures
from config import Config
from utils.error_handling import log_error
from .eventbrite_service import EventbriteService
from .nyc_open_data_service import NYCOpenDataService

class EventService:
    """Unified service for fetching events from multiple sources."""
    
    def __init__(self):
        """Initialize the event service with available API services."""
        self.services = {}
        
        # Initialize available services
        try:
            if Config.EVENTBRITE_API_KEY:
                self.services['eventbrite'] = EventbriteService()
        except ValueError as e:
            log_error(e, "Eventbrite service not available")
        
        # NYC Open Data is always available (free)
        try:
            self.services['nyc_open_data'] = NYCOpenDataService()
        except Exception as e:
            log_error(e, "NYC Open Data service not available")
        
        if not self.services:
            raise ValueError("No event services available. Please configure at least one API key or use NYC Open Data.")
    
    def search_events(self, 
                     location: str = "New York, NY",
                     categories: List[str] = None,
                     start_date: str = None,
                     end_date: str = None,
                     keywords: str = None,
                     limit_per_service: int = 25) -> List[Dict[str, Any]]:
        """
        Search for events across all available services.
        
        Args:
            location: Location to search in
            categories: List of category names to filter by
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            keywords: Search keywords
            limit_per_service: Maximum events per service
            
        Returns:
            Combined list of events from all services
        """
        all_events = []
        
        # Search each service
        for service_name, service in self.services.items():
            try:
                events = service.search_events(
                    location=location,
                    categories=categories,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit_per_service
                )
                
                # Filter by keywords if provided
                if keywords and events:
                    events = self._filter_by_keywords(events, keywords)
                
                all_events.extend(events)
                
            except Exception as e:
                log_error(e, f"Error searching {service_name} events")
                continue
        
        # Remove duplicates and sort
        unique_events = self._remove_duplicates(all_events)
        sorted_events = self._sort_events(unique_events)
        
        return sorted_events
    
    def _filter_by_keywords(self, events: List[Dict[str, Any]], keywords: str) -> List[Dict[str, Any]]:
        """Filter events by keywords in title, description, or tags."""
        if not keywords:
            return events
        
        keywords_lower = keywords.lower().split()
        filtered_events = []
        
        for event in events:
            # Check title, description, and tags
            searchable_text = f"{event.get('title', '')} {event.get('description', '')} {' '.join(event.get('tags', []))}".lower()
            
            if any(keyword in searchable_text for keyword in keywords_lower):
                filtered_events.append(event)
        
        return filtered_events
    
    def _remove_duplicates(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on title, date, and location."""
        seen = set()
        unique_events = []
        
        for event in events:
            # Create a key for duplicate detection
            key = (
                event.get('title', '').lower().strip(),
                event.get('date'),
                event.get('location', '').lower().strip()
            )
            
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def _sort_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort events by date, with upcoming events first."""
        def sort_key(event):
            event_date = event.get('date')
            if event_date:
                return event_date
            else:
                # Put events without dates at the end
                return datetime.max
        
        return sorted(events, key=sort_key)
    
    def get_event_by_id(self, event_id: str, source: str = None) -> Optional[Dict[str, Any]]:
        """Get a specific event by ID from a specific source."""
        if source and source in self.services:
            # This would need to be implemented in individual services
            # For now, return None as the APIs don't support single event lookup
            pass
        
        return None
    
    def get_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """Get available categories from all services."""
        categories = {}
        
        for service_name, service in self.services.items():
            try:
                service_categories = service.get_categories()
                categories[service_name] = service_categories
            except Exception as e:
                log_error(e, f"Error fetching categories from {service_name}")
                categories[service_name] = []
        
        return categories
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get the status of each service."""
        return {
            service_name: service is not None
            for service_name, service in self.services.items()
        }
    
    def get_available_services(self) -> List[str]:
        """Get list of available service names."""
        return list(self.services.keys())
    
    def search_events_async(self, 
                           location: str = "New York, NY",
                           categories: List[str] = None,
                           start_date: str = None,
                           end_date: str = None,
                           keywords: str = None,
                           limit_per_service: int = 25) -> List[Dict[str, Any]]:
        """
        Asynchronously search for events across all available services.
        This can be faster for multiple API calls.
        """
        def search_service(service_name, service):
            try:
                events = service.search_events(
                    location=location,
                    categories=categories,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit_per_service
                )
                
                if keywords and events:
                    events = self._filter_by_keywords(events, keywords)
                
                return events
            except Exception as e:
                log_error(e, f"Error searching {service_name} events")
                return []
        
        # Use ThreadPoolExecutor for concurrent API calls
        all_events = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.services)) as executor:
            future_to_service = {
                executor.submit(search_service, name, service): name
                for name, service in self.services.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_service):
                service_name = future_to_service[future]
                try:
                    events = future.result()
                    all_events.extend(events)
                except Exception as e:
                    log_error(e, f"Error in async search for {service_name}")
        
        # Remove duplicates and sort
        unique_events = self._remove_duplicates(all_events)
        sorted_events = self._sort_events(unique_events)
        
        return sorted_events
