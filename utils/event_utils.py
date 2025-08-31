"""
Event processing utilities for the ExploreNYC application.
Handles event data processing, filtering, and management.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import json
from config import Config

class EventProcessor:
    """Handles event data processing and management."""
    
    def __init__(self):
        """Initialize the EventProcessor."""
        self.events_cache = []
        self.last_update = None
        
    def process_event_data(self, raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw event data into standardized format."""
        processed_events = []
        
        for event in raw_events:
            processed_event = {
                'id': event.get('id', ''),
                'title': event.get('title', '').strip(),
                'description': event.get('description', '').strip(),
                'category': event.get('category', 'Other'),
                'location': event.get('location', ''),
                'venue': event.get('venue', ''),
                'date': self._parse_date(event.get('date', '')),
                'time': event.get('time', ''),
                'price': self._parse_price(event.get('price', '')),
                'url': event.get('url', ''),
                'image_url': event.get('image_url', ''),
                'tags': event.get('tags', []),
                'accessibility': event.get('accessibility', {}),
                'rating': event.get('rating', 0),
                'source': event.get('source', 'Unknown')
            }
            processed_events.append(processed_event)
        
        return processed_events
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object."""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def _parse_price(self, price_str: str) -> Dict[str, Any]:
        """Parse price information."""
        if not price_str:
            return {'min': 0, 'max': 0, 'currency': 'USD', 'display': 'Free'}
        
        # Handle common price formats
        price_str = price_str.lower().strip()
        
        if 'free' in price_str or price_str == '0':
            return {'min': 0, 'max': 0, 'currency': 'USD', 'display': 'Free'}
        
        # Extract numeric values
        import re
        numbers = re.findall(r'\d+\.?\d*', price_str)
        
        if numbers:
            min_price = float(numbers[0])
            max_price = float(numbers[-1]) if len(numbers) > 1 else min_price
            return {
                'min': min_price,
                'max': max_price,
                'currency': 'USD',
                'display': price_str.title()
            }
        
        return {'min': 0, 'max': 0, 'currency': 'USD', 'display': price_str.title()}
    
    def filter_events(self, events: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter events based on user criteria."""
        filtered_events = events.copy()
        
        # Date range filter
        if filters.get('date_range'):
            start_date, end_date = filters['date_range']
            filtered_events = [
                event for event in filtered_events
                if event.get('date') and start_date <= event['date'] <= end_date
            ]
        
        # Category filter
        if filters.get('categories'):
            filtered_events = [
                event for event in filtered_events
                if event.get('category') in filters['categories']
            ]
        
        # Price range filter
        if filters.get('price_range'):
            min_price, max_price = filters['price_range']
            filtered_events = [
                event for event in filtered_events
                if (event.get('price', {}).get('min', 0) >= min_price and
                    event.get('price', {}).get('max', 0) <= max_price)
            ]
        
        # Location filter
        if filters.get('neighborhoods'):
            filtered_events = [
                event for event in filtered_events
                if any(neighborhood.lower() in event.get('location', '').lower()
                      for neighborhood in filters['neighborhoods'])
            ]
        
        # Accessibility filter
        if filters.get('accessibility_requirements'):
            for req in filters['accessibility_requirements']:
                filtered_events = [
                    event for event in filtered_events
                    if event.get('accessibility', {}).get(req, False)
                ]
        
        return filtered_events
    
    def sort_events(self, events: List[Dict[str, Any]], sort_by: str = 'date') -> List[Dict[str, Any]]:
        """Sort events by specified criteria."""
        if sort_by == 'date':
            return sorted(events, key=lambda x: x.get('date') or datetime.min)
        elif sort_by == 'price':
            return sorted(events, key=lambda x: x.get('price', {}).get('min', 0))
        elif sort_by == 'rating':
            return sorted(events, key=lambda x: x.get('rating', 0), reverse=True)
        elif sort_by == 'title':
            return sorted(events, key=lambda x: x.get('title', '').lower())
        else:
            return events
    
    def get_event_statistics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the events."""
        if not events:
            return {}
        
        stats = {
            'total_events': len(events),
            'categories': {},
            'neighborhoods': {},
            'price_distribution': {'free': 0, 'paid': 0},
            'upcoming_events': 0,
            'this_week': 0
        }
        
        now = datetime.now()
        week_end = now + timedelta(days=7)
        
        for event in events:
            # Category statistics
            category = event.get('category', 'Other')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Location statistics
            location = event.get('location', 'Unknown')
            stats['neighborhoods'][location] = stats['neighborhoods'].get(location, 0) + 1
            
            # Price statistics
            price = event.get('price', {})
            if price.get('min', 0) == 0:
                stats['price_distribution']['free'] += 1
            else:
                stats['price_distribution']['paid'] += 1
            
            # Date statistics
            event_date = event.get('date')
            if event_date:
                if event_date >= now:
                    stats['upcoming_events'] += 1
                if now <= event_date <= week_end:
                    stats['this_week'] += 1
        
        return stats
    
    def search_events_by_keywords(self, events: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Search events by keywords in title and description."""
        if not keywords:
            return events
        
        matching_events = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for event in events:
            title = event.get('title', '').lower()
            description = event.get('description', '').lower()
            tags = [tag.lower() for tag in event.get('tags', [])]
            
            # Check if any keyword matches
            if any(keyword in title or keyword in description or keyword in tags
                   for keyword in keywords_lower):
                matching_events.append(event)
        
        return matching_events
    
    def get_recommendations(self, events: List[Dict[str, Any]], 
                          user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get personalized event recommendations based on user preferences."""
        if not events or not user_preferences:
            return events[:10]  # Return first 10 if no preferences
        
        scored_events = []
        
        for event in events:
            score = 0
            
            # Category preference scoring
            preferred_categories = user_preferences.get('categories', [])
            if event.get('category') in preferred_categories:
                score += 10
            
            # Price preference scoring
            budget = user_preferences.get('budget', {})
            event_price = event.get('price', {}).get('min', 0)
            if budget.get('min', 0) <= event_price <= budget.get('max', 1000):
                score += 5
            
            # Location preference scoring
            preferred_neighborhoods = user_preferences.get('neighborhoods', [])
            if any(neighborhood.lower() in event.get('location', '').lower()
                   for neighborhood in preferred_neighborhoods):
                score += 8
            
            # Time preference scoring
            preferred_times = user_preferences.get('preferred_times', [])
            # This would need more sophisticated time parsing
            
            scored_events.append((event, score))
        
        # Sort by score and return top recommendations
        scored_events.sort(key=lambda x: x[1], reverse=True)
        return [event for event, score in scored_events[:20]]
