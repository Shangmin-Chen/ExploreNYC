"""
ExploreNYC - AI-Powered Event Explorer
A Streamlit application using LangChain for discovering NYC events.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
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
    """Initialize session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = EventExplorerAgent()
    
    if 'event_processor' not in st.session_state:
        st.session_state.event_processor = EventProcessor()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}

def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🗽 ExploreNYC</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover NYC\'s hidden gems and mainstream events with AI-powered recommendations</p>', unsafe_allow_html=True)
    
    # Sidebar for user preferences
    with st.sidebar:
        st.header("🎯 Your Preferences")
        
        # User preferences form
        user_preferences = render_preferences_sidebar()
        st.session_state.user_preferences = user_preferences
        
        # API Status
        st.header("📊 Status")
        if Config.COHERE_API_KEY:
            st.success("✅ Cohere Connected")
        else:
            st.error("❌ Cohere API Key Missing")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with Your Event Explorer")
        
        # Chat interface
        chat_container = st.container()
        
        # Display conversation history
        with chat_container:
            for message in st.session_state.conversation_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
        
        # User input
        user_input = st.chat_input("Ask me about NYC events! e.g., 'Find underground art shows this weekend'")
        
        if user_input:
            # Add user message to history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.spinner("🤖 Finding amazing events for you..."):
                try:
                    response = st.session_state.agent.process_query(
                        user_input, 
                        st.session_state.user_preferences
                    )
                    
                    # Add AI response to history
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                    
                    # Rerun to show new messages
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.header("📅 Quick Suggestions")
        
        # Quick action buttons
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
        
        # Event statistics (placeholder)
        st.header("📊 Event Insights")
        
        # Sample data for demonstration
        sample_data = pd.DataFrame({
            'Category': ['Art', 'Music', 'Food', 'Outdoor'],
            'Events': [45, 32, 28, 15]
        })
        
        fig = px.pie(sample_data, values='Events', names='Category', 
                    title="Events by Category (This Week)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and LangChain | ExploreNYC © 2024")

if __name__ == "__main__":
    main()
