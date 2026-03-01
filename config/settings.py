import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Redis Configuration for Session Management
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    
    # Vector Store Configuration
    VECTOR_STORE_PATH: str = "data/vector_store"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Session Configuration
    SESSION_TTL: int = 3600  # 1 hour
    MAX_SESSIONS: int = 10000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"

settings = Settings()