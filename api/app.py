"""
FastAPI server for the Adidas Supply Planning System
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.session_manager import SessionManager, ContextStore
from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore
from rag.retriever import RAGRetriever
from agents.orchestrator import AgentOrchestrator
from config.logging_config import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Adidas Supply Planning API",
    description="Multi-agent supply planning system with RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for system components
session_manager = None
context_store = None
orchestrator = None

class DemandForecastRequest(BaseModel):
    product_type: str
    region: str
    forecast_period: str = "next_quarter"
    historical_data: Optional[Dict] = None
    market_trends: Optional[List[str]] = None

class SizeCurveRequest(BaseModel):
    product_category: str
    region: str
    historical_sizes: Optional[Dict] = None
    special_requirements: Optional[List[str]] = None

class PriceOptimizationRequest(BaseModel):
    product_name: str
    product_type: str
    current_price: float
    base_cost: float
    competitor_prices: Optional[Dict] = None
    market_segment: str
    lifecycle_stage: str
    price_elasticity: float = 1.5

class IntegratedPlanRequest(BaseModel):
    session_id: Optional[str] = None
    product_type: str
    region: str
    forecast_period: str
    product_name: str
    product_cost: float
    market_segment: str
    product_lifecycle: str

class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    status: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global session_manager, context_store, orchestrator
    
    try:
        logger.info("Initializing API server...")
        
        # Initialize memory components
        session_manager = SessionManager()
        context_store = ContextStore(session_manager)
        
        # Initialize RAG components
        embedding_manager = EmbeddingManager()
        vector_store = VectorStore(embedding_manager)
        retriever = RAGRetriever(vector_store)
        
        # Initialize knowledge base
        retriever.initialize_supply_chain_knowledge()
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(context_store, retriever)
        
        logger.info("API server initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API server: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Adidas Supply Planning API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/session/create", response_model=SessionResponse)
async def create_session(request: Request):
    """Create a new session"""
    try:
        session_id = session_manager.create_session(
            user_id=request.client.host,
            metadata={"source": "api"}
        )
        
        return SessionResponse(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            status="active"
        )
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    session_manager.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}

@app.post("/demand-forecast", response_model=Dict[str, Any])
async def demand_forecast(
    request: DemandForecastRequest,
    session_id: Optional[str] = None
):
    """Generate demand forecast"""
    try:
        # Create session if not provided
        if not session_id:
            session_id = session_manager.create_session(
                user_id="api_user",
                metadata={"source": "api"}
            )
        
        # Prepare input data
        input_data = {
            "product_type": request.product_type,
            "region": request.region,
            "time_period": request.forecast_period,
            "historical_data": request.historical_data or {},
            "market_trends": request.market_trends or []
        }
        
        # Process request
        result = orchestrator.demand_agent.process(session_id, input_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in demand forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/size-curve", response_model=Dict[str, Any])
async def size_curve(
    request: SizeCurveRequest,
    session_id: Optional[str] = None
):
    """Optimize size curve"""
    try:
        if not session_id:
            session_id = session_manager.create_session(
                user_id="api_user",
                metadata={"source": "api"}
            )
        
        input_data = {
            "product_category": request.product_category,
            "region": request.region,
            "historical_sizes": request.historical_sizes or {},
            "special_requirements": request.special_requirements or []
        }
        
        result = orchestrator.size_agent.process(session_id, input_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in size curve optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/price-optimization", response_model=Dict[str, Any])
async def price_optimization(
    request: PriceOptimizationRequest,
    session_id: Optional[str] = None
):
    """Optimize pricing"""
    try:
        if not session_id:
            session_id = session_manager.create_session(
                user_id="api_user",
                metadata={"source": "api"}
            )
        
        input_data = {
            "product": {
                "name": request.product_name,
                "type": request.product_type,
                "cost": request.base_cost,
                "current_price": request.current_price
            },
            "competitor_prices": request.competitor_prices or {},
            "market_segment": request.market_segment,
            "lifecycle_stage": request.lifecycle_stage,
            "costs": {
                "production": request.base_cost * 0.6,
                "marketing": request.base_cost * 0.2,
                "distribution": request.base_cost * 0.2
            },
            "elasticity": request.price_elasticity
        }
        
        result = orchestrator.price_agent.process(session_id, input_data)
        
        return {
            "success": True,
            "session_id": session_id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in price optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrated-plan", response_model=Dict[str, Any])
async def integrated_plan(request: IntegratedPlanRequest):
    """Generate integrated supply plan"""
    try:
        # Use provided session ID or create new one
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.create_session(
                user_id="api_user",
                metadata={"source": "api"}
            )
        
        # Prepare input data
        input_data = {
            "product_type": request.product_type,
            "region": request.region,
            "forecast_period": request.forecast_period,
            "product_name": request.product_name,
            "product_cost": request.product_cost,
            "market_segment": request.market_segment,
            "product_lifecycle": request.product_lifecycle
        }
        
        # Process request
        result = orchestrator.process_request(session_id, input_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating integrated plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "redis": "connected" if session_manager and session_manager.redis_client.ping() else "disconnected",
            "vector_store": "initialized",
            "agents": "ready"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )