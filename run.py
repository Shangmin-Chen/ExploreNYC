#!/usr/bin/env python3
"""
Startup script for ExploreNYC application.
This script provides a convenient way to launch the app with proper error handling.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import streamlit
        import langchain
        import cohere
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e.name}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy env.example to .env and add your API keys")
        return False
    
    # Check for Cohere API key
    with open(env_file, 'r') as f:
        content = f.read()
        if "COHERE_API_KEY=your_cohere_api_key_here" in content:
            print("⚠️  Please update your Cohere API key in .env file")
            return False
    
    print("✅ Environment file configured")
    return True

def main():
    """Main function to run the application."""
    print("🗽 Starting ExploreNYC - AI Event Explorer...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the ExploreNYC directory.")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment setup
    env_ok = check_env_file()
    if not env_ok:
        print("\n⚠️  Environment not fully configured, but you can still run the app.")
        print("Some features may not work without proper API keys.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🚀 Launching Streamlit application...")
    print("Open your browser to: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using ExploreNYC!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
