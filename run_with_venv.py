#!/usr/bin/env python3
"""
Startup script for ExploreNYC application with virtual environment support.
This script automatically activates the virtual environment and launches the app.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_venv():
    """Check if virtual environment exists and activate it."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Installing dependencies...")
        subprocess.run([str(venv_path / "bin" / "pip"), "install", "-r", "requirements.txt"], check=True)
    
    # Return the path to the python executable in venv
    if os.name == 'nt':  # Windows
        return str(venv_path / "Scripts" / "python.exe")
    else:  # Unix/Linux/macOS
        return str(venv_path / "bin" / "python")

def main():
    """Main function to run the application."""
    print("🗽 Starting ExploreNYC - AI Event Explorer (LangGraph + Cohere Edition)...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the ExploreNYC directory.")
        sys.exit(1)
    
    # Set up virtual environment
    python_path = check_venv()
    
    print("🚀 Launching Streamlit application with LangGraph + Cohere...")
    print("Open your browser to: http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("-" * 60)
    
    try:
        # Run streamlit with the virtual environment python
        subprocess.run([python_path, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using ExploreNYC!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
