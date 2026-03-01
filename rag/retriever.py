from typing import List, Dict, Any
from .vector_store import VectorStore, Document
from config.logging_config import get_logger

logger = get_logger(__name__)

class RAGRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
    def retrieve_relevant_context(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve relevant documents for a query"""
        try:
            documents = self.vector_store.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(documents)} relevant documents for query: {query[:50]}...")
            return documents
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return []
    
    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents as context string"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"[Document {i} - Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.content}\n")
        
        return "\n".join(context_parts)
    
    def initialize_supply_chain_knowledge(self):
        """Initialize with sample supply chain knowledge"""
        sample_docs = [
            Document(
                content="Demand forecasting for athletic footwear requires consideration of seasonal trends, sports events, and fashion cycles. Historical sales data shows peak demand during Q4 (holiday season) and Q2 (spring running season).",
                metadata={"source": "demand_forecasting_guide", "category": "forecasting"}
            ),
            Document(
                content="Size curve optimization in footwear involves analyzing regional preferences. European markets typically require more sizes 40-44, while Asian markets have higher demand for sizes 36-40. US markets show balanced distribution with peaks at sizes 8-10.",
                metadata={"source": "size_curve_analysis", "category": "size_optimization"}
            ),
            Document(
                content="Price optimization strategies for Adidas products consider competitor pricing (Nike, Puma), product lifecycle stage, and brand positioning. Premium products maintain higher price elasticity during new releases.",
                metadata={"source": "pricing_strategy", "category": "price_optimization"}
            ),
            Document(
                content="Adidas supply chain KPIs include forecast accuracy (>85% target), inventory turnover (4-6x annually), and fill rate (>95%). Regional distribution centers in Europe, North America, and Asia serve local markets.",
                metadata={"source": "supply_chain_metrics", "category": "general"}
            )
        ]
        
        self.vector_store.add_documents(sample_docs)
        logger.info("Initialized supply chain knowledge base")