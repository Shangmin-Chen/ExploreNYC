#!/usr/bin/env python3
"""
Smart startup script for ExploreNYC application.

This script automatically handles the setup and launch of the ExploreNYC application:
- Detects and activates virtual environment
- Installs dependencies if needed
- Validates configuration
- Launches the Streamlit application

Usage:
    python run.py

Author: ExploreNYC Team
Version: 1.0.0
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """
    Check if all required Python packages are installed.
    
    Returns:
        bool: True if all packages are available, False otherwise
    """
    required_packages = [
        'streamlit',
        'langchain_cohere', 
        'langgraph',
        'cohere',
        'requests',
        'pandas',
        'plotly'
    ]
    
    try:
        for package in required_packages:
            __import__(package)
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e.name}")
        return False

def check_venv():
    """
    Check if virtual environment exists and return the Python executable path.
    
    Returns:
        str or None: Path to Python executable in venv, or None if not found
    """
    venv_path = Path("venv")
    if not venv_path.exists():
        return None
    
    # Determine the correct Python executable path based on OS
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_path = venv_path / "bin" / "python"
    
    if python_path.exists():
        return str(python_path)
    return None

def create_venv():
    """
    Create a new virtual environment and install dependencies.
    
    Returns:
        str or None: Path to Python executable in new venv, or None if failed
    """
    print("Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return None
    
    # Get the Python path for the new virtual environment
    venv_python = check_venv()
    if venv_python:
        print("Installing dependencies...")
        try:
            subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            return venv_python
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return None
    return None

def check_env_file():
    """
    Check if .env file exists and has properly configured API keys.
    
    Returns:
        bool: True if environment is properly configured, False otherwise
    """
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy env.example to .env and add your API keys")
        return False
    
    # Check for placeholder API keys
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if "COHERE_API_KEY=your_cohere_api_key_here" in content:
                print("⚠️  Please update your Cohere API key in .env file")
                return False
    except IOError:
        print("❌ Error reading .env file")
        return False
    
    print("✅ Environment file configured")
    return True

def main():
    """
    Main function to run the ExploreNYC application.
    
    This function orchestrates the entire startup process:
    1. Validates the current directory
    2. Checks and installs dependencies
    3. Validates environment configuration
    4. Launches the Streamlit application
    """
    print("🗽 Starting ExploreNYC - AI Event Explorer...")
    print("=" * 50)
    
    # Validate that we're in the correct directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the ExploreNYC directory.")
        sys.exit(1)
    
    # Check if all required packages are installed
    requirements_ok = check_requirements()
    
    # Determine which Python executable to use
    python_path = sys.executable
    
    if not requirements_ok:
        print("📦 Requirements not found in current environment")
        
        # Check if virtual environment already exists
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
    
    # Validate environment configuration
    env_ok = check_env_file()
    if not env_ok:
        print("\n⚠️  Environment not fully configured, but you can still run the app.")
        print("Some features may not work without proper API keys.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Launch the Streamlit application
    print("\n🚀 Launching Streamlit application...")
    print("Open your browser to: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Run streamlit with the appropriate Python executable
        subprocess.run([python_path, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using ExploreNYC!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()