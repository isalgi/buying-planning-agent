"""Configuration module for environment variables and settings."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Gemini Configuration (used via Google's OpenAI-compatible endpoint, free tier)
OPENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# LangSmith Configuration
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "adidas-supply-planning")
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"

# Database Configuration
DB_PATH = Path("data/adidas_supply.db")
DB_PATH.parent.mkdir(exist_ok=True)

# RAG Configuration
RAG_DOCUMENTS_PATH = Path("data/supply_docs")
RAG_DOCUMENTS_PATH.mkdir(exist_ok=True)
EMBEDDING_MODEL = "gemini-embedding-001"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 3

# Model Configuration
LLM_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.7

if __name__ == "__main__":
    # Test configuration
    print("✓ Configuration loaded successfully")
    print(f"  LangSmith Project: {LANGSMITH_PROJECT}")
    print(f"  Database Path: {DB_PATH}")
    print(f"  RAG Documents Path: {RAG_DOCUMENTS_PATH}")
    print(f"  LLM Model: {LLM_MODEL}")