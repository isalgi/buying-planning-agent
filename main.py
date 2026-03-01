#!/usr/bin/env python3
"""
Adidas Supply Planning System - Main Entry Point
A scalable multi-agent system for supply chain optimization using LangGraph, OpenAI, and RAG.
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

def check_environment():
    """Check if all environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please set them in .env file or environment")
        return False
    
    # Optional Redis check
    if not os.getenv("REDIS_HOST"):
        logger.warning("Redis not configured, using in-memory session storage (not recommended for production)")
    
    return True

def initialize_system():
    """Initialize the supply planning system"""
    try:
        logger.info("Initializing Adidas Supply Planning System...")
        
        # Create necessary directories
        directories = ["logs", "data", "data/vector_store"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Created directory: {directory}")
        
        logger.info("System initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        return False

def run_streamlit():
    """Run the Streamlit UI"""
    import streamlit.web.cli as stcli
    import sys
    
    logger.info("Starting Streamlit UI...")
    
    # Get the path to the Streamlit app
    app_path = Path(__file__).parent / "streamlit_app" / "app.py"
    
    # Run Streamlit
    sys.argv = ["streamlit", "run", str(app_path), "--server.port=8501", "--server.address=0.0.0.0"]
    sys.exit(stcli.main())

def run_api():
    """Run the FastAPI server"""
    logger.info("Starting API server...")
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Adidas Supply Planning System")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["streamlit", "api", "both"],
        default="streamlit",
        help="Run mode: streamlit UI, API server, or both"
    )
    
    args = parser.parse_args()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Initialize system
    if not initialize_system():
        sys.exit(1)
    
    # Run in specified mode
    if args.mode == "streamlit":
        run_streamlit()
    elif args.mode == "api":
        run_api()
    elif args.mode == "both":
        import threading
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        run_streamlit()

if __name__ == "__main__":
    main()