"""
UI components and utilities for the Streamlit interface.

This module contains reusable UI components for the ExploreNYC application including:
- Event card rendering and display
- User preference forms and widgets
- Interactive maps and visualizations
- Event statistics and analytics displays
- Search filters and form components

Author: ExploreNYC Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go

# Local imports
from .constants import (
    EVENT_CATEGORIES, NYC_NEIGHBORHOODS, NYC_COORDINATES, TIME_FRAME_OPTIONS,
    BUDGET_OPTIONS, ACCESSIBILITY_OPTIONS, GROUP_SIZE_OPTIONS, DEFAULT_CATEGORIES,
    DEFAULT_NEIGHBORHOODS, DEFAULT_BUDGET
)
from .date_utils import get_date_range_for_time_preference, format_date_for_display

def render_event_card(event: Dict[str, Any]) -> None:
    """Render a single event card."""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Event title
            st.markdown(f"### {event.get('title', 'Untitled Event')}")
            
            # Event details
            st.markdown(f"📅 **Date:** {format_date(event.get('date'))}")
            st.markdown(f"📍 **Location:** {event.get('location', 'TBD')}")
            st.markdown(f"💰 **Price:** {format_price(event.get('price', {}))}")
            st.markdown(f"🏷️ **Category:** {event.get('category', 'General')}")
            
            # Description
            if event.get('description'):
                with st.expander("📋 Description"):
                    st.write(event['description'])
        
        with col2:
            # Action buttons
            if event.get('url'):
                st.link_button("🎟️ Get Tickets", event['url'])
            
            # Rating if available
            if event.get('rating'):
                st.metric("⭐ Rating", f"{event['rating']}/5")
            
            # Save to favorites (placeholder)
            if st.button("❤️ Save", key=f"save_{event.get('id', hash(event.get('title', '')))}"):
                st.success("Added to favorites!")
        
        st.divider()

def render_preferences_sidebar() -> Dict[str, Any]:
    """Render the user preferences sidebar."""
    preferences = {}
    
    # Event categories
    st.subheader("🎭 Event Categories")
    preferences['categories'] = st.multiselect(
        "Select your interests:",
        EVENT_CATEGORIES,
        default=DEFAULT_CATEGORIES
    )
    
    # Budget preferences
    st.subheader("💰 Budget")
    budget_option = st.radio(
        "Price preference:",
        BUDGET_OPTIONS
    )
    
    if budget_option == "Free only":
        preferences['budget'] = {'min': 0, 'max': 0}
    elif budget_option == "Under $25":
        preferences['budget'] = {'min': 0, 'max': 25}
    elif budget_option == "Under $50":
        preferences['budget'] = {'min': 0, 'max': 50}
    elif budget_option == "Custom range":
        min_price = st.number_input("Minimum price ($)", min_value=0, value=0)
        max_price = st.number_input("Maximum price ($)", min_value=0, value=100)
        preferences['budget'] = {'min': min_price, 'max': max_price}
    else:
        preferences['budget'] = DEFAULT_BUDGET
    
    # Location preferences
    st.subheader("📍 Neighborhoods")
    preferences['neighborhoods'] = st.multiselect(
        "Preferred areas:",
        NYC_NEIGHBORHOODS,
        default=DEFAULT_NEIGHBORHOODS
    )
    
    # Time preferences
    st.subheader("⏰ When")
    time_preference = st.selectbox(
        "Time frame:",
        TIME_FRAME_OPTIONS
    )
    preferences['time_frame'] = time_preference
    
    # Date range based on time preference
    date_range = get_date_range_for_time_preference(time_preference)
    if date_range:
        preferences['date_range'] = date_range
    
    # Accessibility needs
    st.subheader("♿ Accessibility")
    accessibility_needs = st.multiselect(
        "Accessibility requirements:",
        ACCESSIBILITY_OPTIONS
    )
    preferences['accessibility_requirements'] = accessibility_needs
    
    # Group size
    st.subheader("👥 Group Size")
    group_size = st.selectbox(
        "How many people?",
        GROUP_SIZE_OPTIONS
    )
    preferences['group_size'] = group_size
    
    return preferences

def render_event_map(events: List[Dict[str, Any]]) -> None:
    """Render a map showing event locations."""
    if not events:
        st.info("No events to display on map")
        return
    
    # Create a simple map visualization
    # This is a placeholder - in a real app, you'd use actual coordinates
    map_data = []
    for event in events:
        if event.get('location'):
            # Mock coordinates for demonstration
            lat, lon = get_mock_coordinates(event['location'])
            map_data.append({
                'lat': lat,
                'lon': lon,
                'title': event.get('title', ''),
                'location': event.get('location', '')
            })
    
    if map_data:
        df = pd.DataFrame(map_data)
        st.map(df[['lat', 'lon']])

def get_mock_coordinates(location: str) -> tuple:
    """Get mock coordinates for a location (for demonstration)."""
    location_lower = location.lower()
    for key, coords in NYC_COORDINATES.items():
        if key in location_lower:
            return coords
    
    # Default to Manhattan if location not found
    return NYC_COORDINATES['manhattan']

def render_event_statistics(stats: Dict[str, Any]) -> None:
    """Render event statistics and visualizations."""
    if not stats:
        st.info("No statistics available")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", stats.get('total_events', 0))
    
    with col2:
        st.metric("This Week", stats.get('this_week', 0))
    
    with col3:
        st.metric("Free Events", stats.get('price_distribution', {}).get('free', 0))
    
    with col4:
        st.metric("Upcoming", stats.get('upcoming_events', 0))
    
    # Category distribution
    if stats.get('categories'):
        st.subheader("📊 Events by Category")
        categories_df = pd.DataFrame(
            list(stats['categories'].items()),
            columns=['Category', 'Count']
        )
        fig = px.pie(categories_df, values='Count', names='Category',
                    title="Event Categories Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Neighborhood distribution
    if stats.get('neighborhoods'):
        st.subheader("🗺️ Events by Area")
        neighborhoods_df = pd.DataFrame(
            list(stats['neighborhoods'].items()),
            columns=['Neighborhood', 'Count']
        )
        fig = px.bar(neighborhoods_df, x='Neighborhood', y='Count',
                    title="Events by Neighborhood")
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

def format_date(date_obj) -> str:
    """Format a date object for display."""
    return format_date_for_display(date_obj)

def format_price(price_dict: Dict[str, Any]) -> str:
    """Format price information for display."""
    if not price_dict:
        return "Free"
    
    if price_dict.get('display'):
        return price_dict['display']
    
    min_price = price_dict.get('min', 0)
    max_price = price_dict.get('max', 0)
    
    if min_price == 0 and max_price == 0:
        return "Free"
    elif min_price == max_price:
        return f"${min_price:.0f}"
    else:
        return f"${min_price:.0f} - ${max_price:.0f}"

def render_search_filters() -> Dict[str, Any]:
    """Render advanced search filters."""
    filters = {}
    
    with st.expander("🔍 Advanced Search"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date filters
            st.subheader("📅 Date Range")
            date_option = st.radio(
                "Select date range:",
                ["Today", "This week", "This month", "Custom range"],
                key="search_date"
            )
            
            if date_option == "Custom range":
                start_date = st.date_input("Start date")
                end_date = st.date_input("End date")
                filters['date_range'] = (start_date, end_date)
            
            # Price filters
            st.subheader("💰 Price Range")
            price_range = st.slider(
                "Price range ($)",
                min_value=0,
                max_value=200,
                value=(0, 50),
                step=5
            )
            filters['price_range'] = price_range
        
        with col2:
            # Category filters
            st.subheader("🎭 Categories")
            selected_categories = st.multiselect(
                "Filter by category:",
                EVENT_CATEGORIES,
                key="search_categories"
            )
            filters['categories'] = selected_categories
            
            # Location filters
            st.subheader("📍 Location")
            selected_neighborhoods = st.multiselect(
                "Filter by area:",
                NYC_NEIGHBORHOODS,
                key="search_neighborhoods"
            )
            filters['neighborhoods'] = selected_neighborhoods
    
    return filters
