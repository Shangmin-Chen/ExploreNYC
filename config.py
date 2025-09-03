"""Configuration settings for the ExploreNYC application."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Cohere Configuration
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    
    # NYC Open Data API
    NYC_APP_TOKEN = os.getenv("NYC_APP_TOKEN")
    
    # Event APIs
    EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
    MEETUP_API_KEY = os.getenv("MEETUP_API_KEY")
    
    # App Settings
    APP_TITLE = "ExploreNYC - AI Event Explorer"
    APP_DESCRIPTION = "Discover NYC's hidden gems and mainstream events with AI-powered recommendations"
    
    # Model Settings
    DEFAULT_MODEL = "command-r-plus"  # Cohere's latest model
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
