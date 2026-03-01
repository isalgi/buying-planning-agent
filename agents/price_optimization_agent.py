from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langchain.schema import SystemMessage, HumanMessage
import json
from .base_agent import BaseAgent
from config.logging_config import get_logger

logger = get_logger(__name__)

class PriceOptimizationAgent(BaseAgent):
    def __init__(self, context_store, retriever):
        super().__init__("PriceOptimization", context_store, retriever)
        
    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(Dict)
        
        workflow.add_node("analyze_market", self._analyze_market)
        workflow.add_node("retrieve_price_knowledge", self._retrieve_price_knowledge)
        workflow.add_node("optimize_price", self._optimize_price)
        workflow.add_node("validate_price", self._validate_price)
        
        workflow.set_entry_point("analyze_market")
        workflow.add_edge("analyze_market", "retrieve_price_knowledge")
        workflow.add_edge("retrieve_price_knowledge", "optimize_price")
        workflow.add_edge("optimize_price", "validate_price")
        workflow.add_conditional_edges(
            "validate_price",
            self._should_refine,
            {
                "refine": "optimize_price",
                "accept": END
            }
        )
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _analyze_market(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions"""
        input_data = state.get("input", {})
        
        analysis = {
            "product": input_data.get("product", {}),
            "competitor_prices": input_data.get("competitor_prices", {}),
            "market_segment": input_data.get("market_segment", "athletic"),
            "product_lifecycle": input_data.get("lifecycle_stage", "mature"),
            "cost_structure": input_data.get("costs", {}),
            "demand_elasticity": input_data.get("elasticity", 1.5)
        }
        
        state["analysis"] = analysis
        logger.info(f"Analyzed market for {analysis['product'].get('name', 'unknown')}")
        return state
    
    def _retrieve_price_knowledge(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve pricing knowledge"""
        analysis = state.get("analysis", {})
        query = f"Price optimization for {analysis['market_segment']} products in competitive landscape"
        
        knowledge = self._get_relevant_knowledge(query)
        state["knowledge"] = knowledge
        return state
    
    def _optimize_price(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pricing strategy"""
        analysis = state.get("analysis", {})
        knowledge = state.get("knowledge", "")
        refinement = state.get("refinement_feedback", "")
        
        messages = [
            SystemMessage(content="""You are a price optimization expert for Adidas.
            Develop optimal pricing strategies considering market position, costs, and competition."""),
            HumanMessage(content=f"""
            Knowledge Base:
            {knowledge}
            
            Market Analysis:
            {json.dumps(analysis, indent=2)}
            
            Refinement Feedback:
            {refinement}
            
            Provide optimized pricing strategy including:
            1. Recommended price point (MSRP)
            2. Price tiers/segments
            3. Discounting strategy
            4. Seasonal adjustments
            5. Competitive positioning
            6. Expected margin impact
            """)
        ]
        
        response = self.llm.invoke(messages)
        state["pricing_strategy"] = response.content
        
        logger.info("Generated optimized pricing strategy")
        return state
    
    def _validate_price(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pricing strategy"""
        pricing = state.get("pricing_strategy", "")
        
        messages = [
            SystemMessage(content="Validate the pricing strategy for market viability and profitability."),
            HumanMessage(content=f"Validate this pricing strategy:\n{pricing}\n\nProvide validation status and feedback.")
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
        validation = state.get("validation", {})
        return "refine" if validation.get("status") == "needs_refinement" else "accept"
    
    def process(self, session_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            context = self._get_session_context(session_id)
            
            initial_state = {
                "input": input_data,
                "session_context": context
            }
            
            final_state = self.graph.invoke(initial_state)
            
            self._update_session_context(session_id, {
                "last_pricing": final_state.get("pricing_strategy"),
                "pricing_analysis": final_state.get("analysis")
            })
            
            return {
                "pricing_strategy": final_state.get("pricing_strategy"),
                "analysis": final_state.get("analysis"),
                "validation": final_state.get("validation")
            }
            
        except Exception as e:
            logger.error(f"Error in price optimization: {str(e)}")
            return {"error": str(e)}