"""RAG module for document retrieval and context injection."""
import os
import pickle
from typing import List, Dict, Any
from pathlib import Path
import numpy as np
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langsmith import traceable
from config import (
    OPENAI_API_KEY, 
    EMBEDDING_MODEL, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    RAG_DOCUMENTS_PATH
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
)

class RAGSystem:
    """Lightweight RAG system for Adidas supply planning documents."""
    
    def __init__(self, persist_directory: str = "data/faiss_index"):
        self.persist_directory = persist_directory
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Load or create vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize FAISS vector store from existing index or create new."""
        if os.path.exists(self.persist_directory):
            try:
                self.vector_store = FAISS.load_local(
                    self.persist_directory, 
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"✓ Loaded existing FAISS index from {self.persist_directory}")
            except Exception as e:
                print(f"! Could not load existing index: {e}")
                self.vector_store = None
        
        if self.vector_store is None:
            # Create sample documents if none exist
            self._create_sample_documents()
    
    def _create_sample_documents(self):
        """Create sample Adidas supply planning documents."""
        documents = [
            Document(
                page_content="""Adidas Demand Forecasting Guidelines:
                - Use historical sales data from last 3 years
                - Account for seasonal trends: Q4 has 30% higher demand
                - Regional variations: Europe 40% of sales, North America 35%, Asia 25%
                - New product launches increase baseline demand by 15-20%
                - Promotional periods can spike demand by 50% temporarily""",
                metadata={"category": "demand_forecast", "source": "guidelines_v2"}
            ),
            Document(
                page_content="""Size Curve Optimization Best Practices:
                - Running shoes: sizes 8-10 represent 60% of sales
                - Lifestyle shoes: broader distribution, sizes 7-11 represent 70%
                - Regional differences: Asian markets need smaller sizes (shift -1.5 sizes)
                - Review size curves monthly based on sell-through rates
                - Safety stock for popular sizes should be 20% higher""",
                metadata={"category": "size_curve", "source": "optimization_guide"}
            ),
            Document(
                page_content="""Price Optimization Strategy:
                - Premium products (Ultraboost): 30% margin target
                - Core products (Superstar): 45% margin target
                - Discount thresholds: max 30% for seasonal items
                - Dynamic pricing based on competitor analysis
                - Bundle pricing: 15% discount for 2+ items""",
                metadata={"category": "price_optimization", "source": "pricing_strategy"}
            ),
            Document(
                page_content="""Inventory Management Rules:
                - Safety stock: 15% of forecasted demand
                - Reorder point: 30 days of inventory
                - Seasonal build-up: start 60 days before season
                - Clearance: 40% discount after 120 days in stock
                - Cross-docking for high-volume items""",
                metadata={"category": "inventory", "source": "inventory_policy"}
            ),
            Document(
                page_content="""Supply Chain Constraints:
                - Production lead time: 45 days from Asia
                - Air freight: 7 days (3x cost)
                - Port capacity: 20% lower during Chinese New Year
                - Raw material availability: 95% typically
                - Factory utilization target: 85%""",
                metadata={"category": "supply_chain", "source": "operations"}
            )
        ]
        
        # Create vector store
        self.add_documents(documents)
        print("✓ Created sample documents and FAISS index")
    
    @traceable(name="rag_add_documents", run_type="chain")
    def add_documents(self, documents: List[Document]):
        """Add documents to the vector store."""
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Create or update vector store
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, embeddings)
        else:
            self.vector_store.add_documents(chunks)
        
        # Save to disk
        os.makedirs(os.path.dirname(self.persist_directory), exist_ok=True)
        self.vector_store.save_local(self.persist_directory)
    
    @traceable(name="rag_retrieve", run_type="retriever")
    def retrieve_context(self, query: str, k: int = TOP_K_RESULTS) -> List[Document]:
        """Retrieve relevant documents for a query."""
        if self.vector_store is None:
            return []
        
        docs = self.vector_store.similarity_search(query, k=k)
        return docs
    
    @traceable(name="rag_get_context", run_type="chain")
    def get_context_string(self, query: str) -> str:
        """Get context as a formatted string for prompt injection."""
        docs = self.retrieve_context(query)
        
        if not docs:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            category = doc.metadata.get('category', 'General')
            context_parts.append(f"[Document {i} - {category} ({source})]:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)


# Global RAG instance
rag_system = RAGSystem()

if __name__ == "__main__":
    # Test RAG functionality
    print("Testing RAG Module...")
    
    # Test queries
    test_queries = [
        "What are the demand forecast guidelines for running shoes?",
        "How should I optimize size curves for different regions?",
        "What is the pricing strategy for premium products?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        # Get context
        context = rag_system.get_context_string(query)
        print(f"Retrieved Context:\n{context}")
        
        # Show retrieval details
        docs = rag_system.retrieve_context(query)
        print(f"\n✓ Retrieved {len(docs)} relevant documents")