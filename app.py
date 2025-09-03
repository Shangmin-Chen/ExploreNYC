"""
ExploreNYC - AI-Powered Event Explorer

A Streamlit application that uses LangChain and AI to help users discover
NYC events from multiple sources including Eventbrite and NYC Open Data.

Features:
- AI-powered event recommendations using Cohere
- Real-time event data from multiple APIs
- Interactive chat interface
- Personalized event filtering
- Beautiful, responsive UI

Author: ExploreNYC Team
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Local imports
from config import Config
from langchain_integration import EventExplorerAgent
from utils.event_utils import EventProcessor
from utils.ui_components import render_event_card, render_preferences_sidebar

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .event-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """
    Initialize Streamlit session state variables.
    
    This function sets up the core components needed for the application:
    - AI agent for processing user queries
    - Event processor for handling event data
    - Conversation history for chat functionality
    - User preferences for personalized recommendations
    
    Returns:
        None
    """
    # Initialize AI agent if not already present
    if 'agent' not in st.session_state:
        st.session_state.agent = EventExplorerAgent()
    
    # Initialize event processor for data handling
    if 'event_processor' not in st.session_state:
        st.session_state.event_processor = EventProcessor()
    
    # Initialize conversation history for chat interface
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Initialize user preferences for personalization
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}

def main():
    """
    Main application function that orchestrates the entire Streamlit app.
    
    This function:
    1. Initializes session state
    2. Sets up the UI layout with header and sidebar
    3. Handles user interactions and chat functionality
    4. Manages the conversation flow and AI responses
    
    Returns:
        None
    """
    # Initialize all required session state variables
    initialize_session_state()
    
    # Application header with branding
    st.markdown('<h1 class="main-header">🗽 ExploreNYC</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover NYC\'s hidden gems and mainstream events with AI-powered recommendations</p>', unsafe_allow_html=True)
    
    # Sidebar for user preferences and system status
    with st.sidebar:
        st.header("🎯 Your Preferences")
        
        # Render user preferences form and store in session state
        user_preferences = render_preferences_sidebar()
        st.session_state.user_preferences = user_preferences
        
        # Display API connection status
        st.header("📊 Status")
        if Config.COHERE_API_KEY:
            st.success("✅ Cohere Connected")
        else:
            st.error("❌ Cohere API Key Missing")
    
    # Main content area with two-column layout
    col1, col2 = st.columns([2, 1])
    
    # Left column: Chat interface
    with col1:
        st.header("💬 Chat with Your Event Explorer")
        
        # Chat interface container
        chat_container = st.container()
        
        # Display conversation history
        with chat_container:
            for message in st.session_state.conversation_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # User input field for chat
        user_input = st.chat_input("Ask me about NYC events! e.g., 'Find underground art shows this weekend'")
        
        # Process user input when provided
        if user_input:
            # Add user message to conversation history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response with loading indicator
            with st.spinner("🤖 Finding amazing events for you..."):
                try:
                    # Process query through AI agent with user preferences
                    response = st.session_state.agent.process_query(
                        user_input, 
                        st.session_state.user_preferences
                    )
                    
                    # Add AI response to conversation history
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                    
                    # Rerun to display new messages
                    st.rerun()
                    
                except Exception as e:
                    # Display error message if query processing fails
                    st.error(f"Error: {str(e)}")
    
    # Right column: Quick suggestions and insights
    with col2:
        st.header("📅 Quick Suggestions")
        
        # Quick action buttons for common event categories
        if st.button("🎨 Art & Culture"):
            suggested_query = "Find art galleries and cultural events happening this week"
            st.session_state.conversation_history.append({"role": "user", "content": suggested_query})
            st.rerun()
        
        if st.button("🎵 Music & Nightlife"):
            suggested_query = "Show me live music venues and nightlife events"
            st.session_state.conversation_history.append({"role": "user", "content": suggested_query})
            st.rerun()
        
        if st.button("🍕 Food & Dining"):
            suggested_query = "Find unique dining experiences and food events"
            st.session_state.conversation_history.append({"role": "user", "content": suggested_query})
            st.rerun()
        
        if st.button("🌳 Outdoor Activities"):
            suggested_query = "What outdoor events and activities are available?"
            st.session_state.conversation_history.append({"role": "user", "content": suggested_query})
            st.rerun()
        
        # Event statistics section
        st.header("📊 Event Insights")
        st.info("📈 Event statistics will be available once you search for events!")
    
    # Application footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and LangChain | ExploreNYC © 2024")

if __name__ == "__main__":
    main()
