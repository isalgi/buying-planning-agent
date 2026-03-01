from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, MessageGraph
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from config.settings import settings
from config.logging_config import get_logger
from memory.session_manager import ContextStore
from rag.retriever import RAGRetriever

logger = get_logger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, context_store: ContextStore, retriever: RAGRetriever):
        self.name = name
        self.context_store = context_store
        self.retriever = retriever
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._create_graph()
        
    @abstractmethod
    def _create_graph(self) -> StateGraph:
        """Create the agent's LangGraph"""
        pass
    
    @abstractmethod
    def process(self, session_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output"""
        pass
    
    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for session"""
        session = self.context_store.session_manager.get_session(session_id)
        return session.get("context", {}) if session else {}
    
    def _update_session_context(self, session_id: str, updates: Dict[str, Any]):
        """Update session context"""
        self.context_store.session_manager.update_session_context(session_id, updates)
    
    def _get_relevant_knowledge(self, query: str) -> str:
        """Get relevant knowledge from RAG"""
        docs = self.retriever.retrieve_relevant_context(query)
        return self.retriever.format_context(docs)