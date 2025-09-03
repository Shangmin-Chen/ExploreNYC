#!/usr/bin/env python3
"""
Smart startup script for ExploreNYC application.
Automatically detects if virtual environment is needed and runs accordingly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    try:
        import streamlit
        import langchain_cohere
        import langgraph
        import cohere
        import requests
        import pandas
        import plotly
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e.name}")
        return False

def check_venv():
    """Check if virtual environment exists and return python path."""
    venv_path = Path("venv")
    if not venv_path.exists():
        return None
    
    # Return the path to the python executable in venv
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
    
    if python_path.exists():
        return str(python_path)
    return None

def create_venv():
    """Create virtual environment and install dependencies."""
    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    venv_python = check_venv()
    if venv_python:
        print("Installing dependencies...")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        return venv_python
    return None

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
    
    # Check if requirements are installed
    requirements_ok = check_requirements()
    
    # Determine which python to use
    python_path = sys.executable
    
    if not requirements_ok:
        print("📦 Requirements not found in current environment")
        
        # Check if venv exists
        venv_python = check_venv()
        if venv_python:
            print("✅ Found virtual environment, using it...")
            python_path = venv_python
        else:
            print("🔧 Creating virtual environment...")
            venv_python = create_venv()
            if venv_python:
                python_path = venv_python
            else:
                print("❌ Failed to create virtual environment")
                print("Please install requirements manually: pip install -r requirements.txt")
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
        # Run streamlit with the appropriate python
        subprocess.run([python_path, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using ExploreNYC!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()