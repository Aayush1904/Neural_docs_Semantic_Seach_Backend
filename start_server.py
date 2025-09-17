#!/usr/bin/env python3
"""
Startup script for the FastAPI Semantic Search Server
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the FastAPI server"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Change to the script directory
    os.chdir(script_dir)
    
    print("🚀 Starting FastAPI Semantic Search Server...")
    print("📍 Server will run on: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    try:
        # Run the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "fastapi_server:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

