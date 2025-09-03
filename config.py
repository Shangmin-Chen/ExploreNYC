"""
Configuration settings for the ExploreNYC application.

This module handles all application configuration including:
- API keys and credentials
- Model settings
- Application metadata
- Environment-specific settings

Author: ExploreNYC Team
Version: 1.0.0
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Application configuration class.
    
    This class centralizes all configuration settings for the ExploreNYC application.
    It loads settings from environment variables and provides default values.
    """
    
    # =============================================================================
    # API Configuration
    # =============================================================================
    
    # Cohere AI API Configuration
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    
    # Eventbrite API Configuration
    EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
    
    # NYC Open Data API (no token required - completely free and open)
    # No configuration needed for NYC Open Data API
    
    # =============================================================================
    # Application Settings
    # =============================================================================
    
    # Application metadata
    APP_TITLE = "ExploreNYC - AI Event Explorer"
    APP_DESCRIPTION = "Discover NYC's hidden gems and mainstream events with AI-powered recommendations"
    APP_VERSION = "1.0.0"
    
    # =============================================================================
    # AI Model Configuration
    # =============================================================================
    
    # Cohere model settings
    DEFAULT_MODEL = "command-r-plus"  # Cohere's latest model
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7  # Controls randomness in AI responses (0.0 = deterministic, 1.0 = very random)
