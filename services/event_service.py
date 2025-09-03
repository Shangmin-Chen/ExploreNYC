"""
Unified event service that combines multiple event sources.

This module provides a single interface for fetching events from multiple sources
including NYC Open Data. It handles data aggregation, deduplication,
and provides a consistent API for event discovery.

Features:
- Multi-source event aggregation
- Automatic deduplication
- Concurrent API calls for performance
- Keyword-based filtering
- Event sorting and ranking

Author: ExploreNYC Team
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import concurrent.futures

# Local imports
from config import Config
from utils.error_handling import log_error
from .nyc_open_data_service import NYCOpenDataService

class EventService:
    """
    Unified service for fetching events from multiple sources.
    
    This class provides a single interface to access events from various sources
    including NYC Open Data. It handles service initialization,
    data aggregation, and provides consistent event data format.
    """
    
    def __init__(self):
        """
        Initialize the event service with available API services.
        
        Raises:
            ValueError: If no event services are available
        """
        self.services = {}
        
        # Initialize NYC Open Data service (always available - free)
        try:
            self.services['nyc_open_data'] = NYCOpenDataService()
        except Exception as e:
            log_error(e, "NYC Open Data service not available")
        
        # Ensure at least one service is available
        if not self.services:
            raise ValueError("No event services available. NYC Open Data service should be available.")
    
    def search_events(self, 
                     location: str = "New York, NY",
                     categories: List[str] = None,
                     start_date: str = None,
                     end_date: str = None,
                     keywords: str = None,
                     limit_per_service: int = 25) -> List[Dict[str, Any]]:
        """
        Search for events across all available services.
        
        This method searches for events from all configured services, aggregates
        the results, removes duplicates, and returns a sorted list of events.
        
        Args:
            location (str): Location to search in (default: "New York, NY")
            categories (List[str], optional): List of category names to filter by
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            keywords (str, optional): Search keywords for filtering events
            limit_per_service (int): Maximum events per service (default: 25)
            
        Returns:
            List[Dict[str, Any]]: Combined and deduplicated list of events from all services
        """
        all_events = []
        
        # Search each configured service
        for service_name, service in self.services.items():
            try:
                # Get events from this service
                events = service.search_events(
                    location=location,
                    categories=categories,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit_per_service
                )
                
                # Apply keyword filtering if specified
                if keywords and events:
                    events = self._filter_by_keywords(events, keywords)
                
                # Add events to the combined list
                all_events.extend(events)
                
            except Exception as e:
                # Log error but continue with other services
                log_error(e, f"Error searching {service_name} events")
                continue
        
        # Process and return the combined results
        unique_events = self._remove_duplicates(all_events)
        sorted_events = self._sort_events(unique_events)
        
        return sorted_events
    
    def _filter_by_keywords(self, events: List[Dict[str, Any]], keywords: str) -> List[Dict[str, Any]]:
        """
        Filter events by keywords in title, description, or tags.
        
        Args:
            events (List[Dict[str, Any]]): List of events to filter
            keywords (str): Space-separated keywords to search for
            
        Returns:
            List[Dict[str, Any]]: Filtered list of events matching keywords
        """
        if not keywords:
            return events
        
        # Convert keywords to lowercase list for case-insensitive matching
        keywords_lower = keywords.lower().split()
        filtered_events = []
        
        for event in events:
            # Combine searchable text from title, description, and tags
            searchable_text = f"{event.get('title', '')} {event.get('description', '')} {' '.join(event.get('tags', []))}".lower()
            
            # Check if any keyword matches
            if any(keyword in searchable_text for keyword in keywords_lower):
                filtered_events.append(event)
        
        return filtered_events
    
    def _remove_duplicates(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate events based on title, date, and location.
        
        Args:
            events (List[Dict[str, Any]]): List of events to deduplicate
            
        Returns:
            List[Dict[str, Any]]: List of unique events
        """
        seen = set()
        unique_events = []
        
        for event in events:
            # Create a composite key for duplicate detection
            key = (
                event.get('title', '').lower().strip(),
                event.get('date'),
                event.get('location', '').lower().strip()
            )
            
            # Only add if we haven't seen this combination before
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def _sort_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort events by date, with upcoming events first.
        
        Args:
            events (List[Dict[str, Any]]): List of events to sort
            
        Returns:
            List[Dict[str, Any]]: Sorted list of events (earliest first)
        """
        def sort_key(event):
            """Helper function to extract sort key from event."""
            event_date = event.get('date')
            if event_date:
                return event_date
            else:
                # Put events without dates at the end
                return datetime.max
        
        return sorted(events, key=sort_key)
    
    def get_event_by_id(self, event_id: str, source: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID from a specific source.
        
        Note: This method is not currently implemented as the APIs don't support
        single event lookup. This is a placeholder for future functionality.
        
        Args:
            event_id (str): Unique identifier for the event
            source (str, optional): Specific service to query
            
        Returns:
            Optional[Dict[str, Any]]: Event data if found, None otherwise
        """
        if source and source in self.services:
            # This would need to be implemented in individual services
            # For now, return None as the APIs don't support single event lookup
            pass
        
        return None
    
    def get_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get available categories from all services.
        
        Returns:
            Dict[str, List[Dict[str, str]]]: Dictionary mapping service names to their categories
        """
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
        """
        Get the status of each service.
        
        Returns:
            Dict[str, bool]: Dictionary mapping service names to their availability status
        """
        return {
            service_name: service is not None
            for service_name, service in self.services.items()
        }
    
    def get_available_services(self) -> List[str]:
        """
        Get list of available service names.
        
        Returns:
            List[str]: List of service names that are currently available
        """
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
        
        This method uses concurrent execution to search multiple services simultaneously,
        which can be significantly faster than sequential searches.
        
        Args:
            location (str): Location to search in (default: "New York, NY")
            categories (List[str], optional): List of category names to filter by
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            keywords (str, optional): Search keywords for filtering events
            limit_per_service (int): Maximum events per service (default: 25)
            
        Returns:
            List[Dict[str, Any]]: Combined and deduplicated list of events from all services
        """
        def search_service(service_name, service):
            """
            Helper function to search a single service.
            
            Args:
                service_name (str): Name of the service
                service: Service instance to search
                
            Returns:
                List[Dict[str, Any]]: Events from this service
            """
            try:
                events = service.search_events(
                    location=location,
                    categories=categories,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit_per_service
                )
                
                # Apply keyword filtering if specified
                if keywords and events:
                    events = self._filter_by_keywords(events, keywords)
                
                return events
            except Exception as e:
                log_error(e, f"Error searching {service_name} events")
                return []
        
        # Use ThreadPoolExecutor for concurrent API calls
        all_events = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.services)) as executor:
            # Submit all service searches concurrently
            future_to_service = {
                executor.submit(search_service, name, service): name
                for name, service in self.services.items()
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_service):
                service_name = future_to_service[future]
                try:
                    events = future.result()
                    all_events.extend(events)
                except Exception as e:
                    log_error(e, f"Error in async search for {service_name}")
        
        # Process and return the combined results
        unique_events = self._remove_duplicates(all_events)
        sorted_events = self._sort_events(unique_events)
        
        return sorted_events
