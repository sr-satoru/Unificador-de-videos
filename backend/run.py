#!/usr/bin/env python3
"""
Script to run the Video Editor Backend
"""
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Add the backend directory to Python path
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Get port and host from environment variable (sem fallback)
    port = int(os.getenv("PORT"))
    host = os.getenv("HOST")
    
    print("🎬 Starting Video Editor Backend...")
    print("📁 Created directories: uploads/, outputs/, temp/")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"📚 API documentation: http://localhost:{port}/docs")
    print(f"🔌 WebSocket endpoint: ws://localhost:{port}/ws/{{client_id}}")
    print("\n" + "="*50)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
