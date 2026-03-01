from langchain_openai import OpenAIEmbeddings
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class EmbeddingManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def embed_text(self, text: str) -> list:
        """Generate embeddings for text"""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def embed_documents(self, documents: list) -> list:
        """Generate embeddings for multiple documents"""
        try:
            return self.embeddings.embed_documents(documents)
        except Exception as e:
            logger.error(f"Error generating document embeddings: {str(e)}")
            raise