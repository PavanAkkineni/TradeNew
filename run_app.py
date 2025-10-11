#!/usr/bin/env python
"""
Trading Analytics Platform - Application Launcher
Run this script to start the FastAPI server
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import pandas
        import numpy
        print("✅ All core packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("\n📦 Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return False

def check_data_folders():
    """Check if data folders exist"""
    folders = [
        'TechnicalAnalysis',
        'FundamentalData',
        'SentimentData',
        'AlternativeData'
    ]
    
    for folder in folders:
        folder_path = Path(folder)
        if folder_path.exists():
            # Count JSON files
            json_files = list(folder_path.rglob('*.json'))
            print(f"✅ {folder}: {len(json_files)} data files")
        else:
            print(f"⚠️ {folder}: Folder not found")
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created {folder} folder")

def start_server():
    """Start the FastAPI server"""
    print("\n" + "="*60)
    print("🚀 STARTING TRADING ANALYTICS PLATFORM")
    print("="*60)
    
    # Check if app directory exists
    app_dir = Path('app')
    if not app_dir.exists():
        print("❌ Error: 'app' directory not found!")
        print("Please ensure the application structure is correct.")
        return
    
    # Check if main.py exists
    main_file = app_dir / 'main.py'
    if not main_file.exists():
        print("❌ Error: app/main.py not found!")
        return
    
    print("\n📊 Server Configuration:")
    print("   Host: localhost")
    print("   Port: 8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Dashboard: http://localhost:8000")
    
    print("\n⏳ Starting server...")
    
    # Open browser after a delay
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:8000')
    
    # Start browser opening in background
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the FastAPI server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    """Main function"""
    print("============================================================")
    print("TRADING ANALYTICS PLATFORM - STARTUP")
    print("============================================================")
    print("📊 MODE: STATIC DATA ONLY (No external API calls)")
    print("📁 Using pre-generated data from IBM/ folder")
    print("🔒 External APIs disabled for reliable demo")
    print("============================================================")
    print()
    print("\n📋 Checking requirements...")
    if not check_requirements():
        print("\n⚠️ Please run the script again after installation completes")
        return
    
    # Check data folders
    check_data_folders()
    
    # Check .env file
    print("\n🔑 Checking API keys...")
    if Path('.env').exists():
        print("✅ .env file found")
        # Check for required keys
        from dotenv import load_dotenv
        load_dotenv()
        
        alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if alpha_key:
            print("✅ Alpha Vantage API key found")
        else:
            print("⚠️ Alpha Vantage API key not found in .env")
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            print("✅ Gemini API key found")
        else:
            print("⚠️ Gemini API key not found in .env")
            
        eodhd_key = os.getenv('EODHD_API_KEY')
        if eodhd_key:
            print("✅ EODHD API key found")
        else:
            print("⚠️ EODHD API key not found in .env (optional)")
    else:
        print("⚠️ .env file not found")
        print("   Creating .env template...")
        
        env_content = """# API Keys Configuration
# Get your Alpha Vantage key from: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Get your Gemini key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Get EODHD key from: https://eodhd.com
EODHD_API_KEY=your_eodhd_api_key_here
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   .env template created. Please add your API keys.")
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
