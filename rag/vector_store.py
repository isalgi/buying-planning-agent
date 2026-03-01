import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from config.settings import settings
from config.logging_config import get_logger
from .embeddings import EmbeddingManager

logger = get_logger(__name__)

@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class VectorStore:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.index = None
        self.documents = []
        self.dimension = 1536  # OpenAI embedding dimension
        self.store_path = settings.VECTOR_STORE_PATH
        
        # Create directory if it doesn't exist
        os.makedirs(self.store_path, exist_ok=True)
        
        # Load existing index if available
        self._load_index()
    
    def add_documents(self, documents: List[Document]):
        """Add documents to vector store"""
        try:
            # Generate embeddings for documents without them
            texts_to_embed = []
            docs_to_process = []
            
            for doc in documents:
                if doc.embedding is None:
                    texts_to_embed.append(doc.content)
                    docs_to_process.append(doc)
                else:
                    self.documents.append(doc)
            
            if texts_to_embed:
                embeddings = self.embedding_manager.embed_documents(texts_to_embed)
                for doc, embedding in zip(docs_to_process, embeddings):
                    doc.embedding = embedding
                    self.documents.append(doc)
            
            # Update FAISS index
            self._build_index()
            self._save_index()
            
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        try:
            if not self.index or self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_manager.embed_text(query)
            
            # Search
            query_vector = np.array([query_embedding]).astype('float32')
            distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
            
            # Return documents
            results = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    results.append(self.documents[idx])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def _build_index(self):
        """Build FAISS index from documents"""
        if not self.documents:
            self.index = None
            return
        
        embeddings = np.array([doc.embedding for doc in self.documents]).astype('float32')
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)
    
    def _save_index(self):
        """Save index and documents to disk"""
        try:
            if self.index:
                faiss.write_index(self.index, f"{self.store_path}/index.faiss")
            
            with open(f"{self.store_path}/documents.pkl", 'wb') as f:
                pickle.dump(self.documents, f)
                
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
    
    def _load_index(self):
        """Load index and documents from disk"""
        try:
            index_path = f"{self.store_path}/index.faiss"
            docs_path = f"{self.store_path}/documents.pkl"
            
            if os.path.exists(index_path) and os.path.exists(docs_path):
                self.index = faiss.read_index(index_path)
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                logger.info(f"Loaded {len(self.documents)} documents from disk")
                
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            self.index = None
            self.documents = []