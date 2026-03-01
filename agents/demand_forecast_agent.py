from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langchain.schema import SystemMessage, HumanMessage
import json
from .base_agent import BaseAgent
from config.logging_config import get_logger

logger = get_logger(__name__)

class DemandForecastAgent(BaseAgent):
    def __init__(self, context_store, retriever):
        super().__init__("DemandForecast", context_store, retriever)
        
    def _create_graph(self) -> StateGraph:
        """Create the demand forecasting workflow"""
        workflow = StateGraph(Dict)
        
        # Define nodes
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("retrieve_knowledge", self._retrieve_knowledge)
        workflow.add_node("generate_forecast", self._generate_forecast)
        workflow.add_node("validate_forecast", self._validate_forecast)
        
        # Define edges
        workflow.set_entry_point("analyze_input")
        workflow.add_edge("analyze_input", "retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "generate_forecast")
        workflow.add_edge("generate_forecast", "validate_forecast")
        workflow.add_conditional_edges(
            "validate_forecast",
            self._should_refine,
            {
                "refine": "generate_forecast",
                "accept": END
            }
        )
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _analyze_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the input data"""
        input_data = state.get("input", {})
        logger.info(f"Analyzing demand forecast input: {input_data}")
        
        analysis = {
            "product_type": input_data.get("product_type", "unknown"),
            "region": input_data.get("region", "global"),
            "time_period": input_data.get("time_period", "next_quarter"),
            "historical_data": input_data.get("historical_data", {}),
            "market_trends": input_data.get("market_trends", [])
        }
        
        state["analysis"] = analysis
        return state
    
    def _retrieve_knowledge(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant knowledge from RAG"""
        analysis = state.get("analysis", {})
        query = f"Demand forecasting for {analysis.get('product_type')} in {analysis.get('region')} region"
        
        knowledge = self._get_relevant_knowledge(query)
        state["knowledge"] = knowledge
        return state
    
    def _generate_forecast(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate demand forecast using LLM"""
        analysis = state.get("analysis", {})
        knowledge = state.get("knowledge", "")
        refinement = state.get("refinement_feedback", "")
        
        messages = [
            SystemMessage(content="""You are an expert demand forecasting agent for Adidas. 
            Generate accurate demand forecasts based on provided data and knowledge.
            Provide forecasts with confidence intervals and key assumptions."""),
            HumanMessage(content=f"""
            Knowledge Base:
            {knowledge}
            
            Analysis:
            {json.dumps(analysis, indent=2)}
            
            Previous Refinement Feedback (if any):
            {refinement}
            
            Generate a demand forecast including:
            1. Expected units by month
            2. Confidence intervals (80% and 95%)
            3. Key drivers and assumptions
            4. Risk factors
            5. Recommended safety stock levels
            """)
        ]
        
        response = self.llm.invoke(messages)
        state["forecast"] = response.content
        
        logger.info("Generated demand forecast")
        return state
    
    def _validate_forecast(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated forecast"""
        forecast = state.get("forecast", "")
        
        messages = [
            SystemMessage(content="Validate the demand forecast for reasonableness and consistency."),
            HumanMessage(content=f"Validate this forecast:\n{forecast}\n\nProvide validation status (accept/refine) and specific feedback if refinement needed.")
        ]
        
        response = self.llm.invoke(messages)
        validation = response.content
        
        if "accept" in validation.lower():
            state["validation"] = {"status": "accepted", "feedback": validation}
        else:
            state["validation"] = {"status": "needs_refinement", "feedback": validation}
            state["refinement_feedback"] = validation
        
        return state
    
    def _should_refine(self, state: Dict[str, Any]) -> str:
        """Determine if forecast needs refinement"""
        validation = state.get("validation", {})
        return "refine" if validation.get("status") == "needs_refinement" else "accept"
    
    def process(self, session_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process demand forecast request"""
        try:
            # Get session context
            context = self._get_session_context(session_id)
            
            # Prepare initial state
            initial_state = {
                "input": input_data,
                "session_context": context
            }
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Update session context
            self._update_session_context(session_id, {
                "last_forecast": final_state.get("forecast"),
                "forecast_analysis": final_state.get("analysis")
            })
            
            return {
                "forecast": final_state.get("forecast"),
                "analysis": final_state.get("analysis"),
                "validation": final_state.get("validation")
            }
            
        except Exception as e:
            logger.error(f"Error in demand forecast processing: {str(e)}")
            return {"error": str(e)}