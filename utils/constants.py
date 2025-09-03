"""
Constants and configuration values for the ExploreNYC application.

This module contains all application constants including:
- Event categories and types
- NYC neighborhoods and locations
- UI configuration options
- API rate limiting settings
- Default values and preferences

Author: ExploreNYC Team
Version: 1.0.0
"""

from typing import Dict, List, Tuple

# =============================================================================
# Event Categories
# =============================================================================

EVENT_CATEGORIES = [
    'Art & Culture', 'Music & Concerts', 'Food & Dining', 
    'Outdoor Activities', 'Sports', 'Nightlife', 'Education', 'Family'
]

# =============================================================================
# NYC Locations and Neighborhoods
# =============================================================================

NYC_NEIGHBORHOODS = [
    'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island',
    'Greenwich Village', 'SoHo', 'Williamsburg', 'LES', 'Upper East Side'
]

# Geographic coordinates for NYC areas (used for mapping)
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

# =============================================================================
# User Interface Options
# =============================================================================

# Time frame selection options
TIME_FRAME_OPTIONS = [
    "Today", "This weekend", "This week", "Next week", "This month", "Anytime"
]

# Budget preference options
BUDGET_OPTIONS = [
    "Any budget", "Free only", "Under $25", "Under $50", "Custom range"
]

# Accessibility requirement options
ACCESSIBILITY_OPTIONS = [
    "Wheelchair accessible", "Sign language interpretation", 
    "Audio description", "Large print materials"
]

# Group size options
GROUP_SIZE_OPTIONS = [
    "Just me", "2 people", "Small group (3-6)", "Large group (7+)"
]

# =============================================================================
# Date and Time Configuration
# =============================================================================

# Supported date formats for parsing
DATE_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%Y-%m-%d %H:%M:%S'
]

# =============================================================================
# API and Performance Settings
# =============================================================================

# Rate limiting configuration
RATE_LIMIT_SECONDS = 6  # 6 seconds between requests = 10 per minute
MAX_RECOMMENDATIONS = 3
MAX_EVENTS_DISPLAY = 20

# =============================================================================
# Default Configuration Values
# =============================================================================

# Default user preferences
DEFAULT_CATEGORIES = ['Art & Culture', 'Food & Dining']
DEFAULT_NEIGHBORHOODS = ['Manhattan']
DEFAULT_BUDGET = {'min': 0, 'max': 1000}
