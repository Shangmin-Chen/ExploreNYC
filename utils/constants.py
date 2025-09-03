"""
Constants and configuration values for the ExploreNYC application.
"""

from typing import Dict, List, Tuple

# Event Categories
EVENT_CATEGORIES = [
    'Art & Culture', 'Music & Concerts', 'Food & Dining', 
    'Outdoor Activities', 'Sports', 'Nightlife', 'Education', 'Family'
]

# NYC Neighborhoods
NYC_NEIGHBORHOODS = [
    'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island',
    'Greenwich Village', 'SoHo', 'Williamsburg', 'LES', 'Upper East Side'
]

# Mock coordinates for NYC areas
NYC_COORDINATES: Dict[str, Tuple[float, float]] = {
    'manhattan': (40.7831, -73.9712),
    'brooklyn': (40.6782, -73.9442),
    'queens': (40.7282, -73.7949),
    'bronx': (40.8448, -73.8648),
    'staten island': (40.5795, -74.1502),
    'central park': (40.7829, -73.9654),
    'times square': (40.7580, -73.9855),
    'williamsburg': (40.7081, -73.9571),
    'soho': (40.7230, -73.9991),
    'greenwich village': (40.7335, -73.9976)
}

# Default event data for MVP
DEFAULT_EVENTS = [
    {
        "title": "Underground Art Show",
        "description": "Emerging artists showcase at secret Brooklyn location",
        "category": "Art",
        "location": "Brooklyn",
        "price": "Free",
        "url": "https://example.com/event1",
        "venue": "Secret Brooklyn Gallery",
        "time": "7:00 PM",
        "tags": ["art", "underground", "emerging artists"]
    },
    {
        "title": "Jazz Night at Blue Note",
        "description": "Live jazz performance with local musicians",
        "category": "Music",
        "location": "Manhattan",
        "price": "$25",
        "url": "https://example.com/event2",
        "venue": "Blue Note Jazz Club",
        "time": "8:00 PM",
        "tags": ["jazz", "live music", "nightlife"]
    },
    {
        "title": "Food Truck Festival",
        "description": "50+ food trucks in Central Park",
        "category": "Food",
        "location": "Central Park",
        "price": "Free entry",
        "url": "https://example.com/event3",
        "venue": "Central Park",
        "time": "12:00 PM",
        "tags": ["food", "outdoor", "family-friendly"]
    },
    {
        "title": "Comedy Night at The Comedy Cellar",
        "description": "Stand-up comedy featuring NYC's best comedians",
        "category": "Entertainment",
        "location": "Manhattan",
        "price": "$20",
        "url": "https://example.com/event4",
        "venue": "The Comedy Cellar",
        "time": "9:00 PM",
        "tags": ["comedy", "stand-up", "nightlife"]
    },
    {
        "title": "Brooklyn Bridge Walking Tour",
        "description": "Guided historical walking tour of the Brooklyn Bridge",
        "category": "Outdoor",
        "location": "Brooklyn",
        "price": "$15",
        "url": "https://example.com/event5",
        "venue": "Brooklyn Bridge",
        "time": "10:00 AM",
        "tags": ["outdoor", "history", "walking tour"]
    }
]

# Time frame options
TIME_FRAME_OPTIONS = [
    "Today", "This weekend", "This week", "Next week", "This month", "Anytime"
]

# Budget options
BUDGET_OPTIONS = [
    "Any budget", "Free only", "Under $25", "Under $50", "Custom range"
]

# Accessibility options
ACCESSIBILITY_OPTIONS = [
    "Wheelchair accessible", "Sign language interpretation", 
    "Audio description", "Large print materials"
]

# Group size options
GROUP_SIZE_OPTIONS = [
    "Just me", "2 people", "Small group (3-6)", "Large group (7+)"
]

# Date formats for parsing
DATE_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%Y-%m-%d %H:%M:%S'
]

# Rate limiting settings
RATE_LIMIT_SECONDS = 6  # 6 seconds between requests = 10 per minute
MAX_RECOMMENDATIONS = 3
MAX_EVENTS_DISPLAY = 20

# UI Configuration
DEFAULT_CATEGORIES = ['Art & Culture', 'Food & Dining']
DEFAULT_NEIGHBORHOODS = ['Manhattan']
DEFAULT_BUDGET = {'min': 0, 'max': 1000}
