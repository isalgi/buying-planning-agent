from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langchain.schema import SystemMessage, HumanMessage
import json
from .base_agent import BaseAgent
from config.logging_config import get_logger

logger = get_logger(__name__)

class SizeCurveAgent(BaseAgent):
    def __init__(self, context_store, retriever):
        super().__init__("SizeCurve", context_store, retriever)
        
    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(Dict)
        
        workflow.add_node("analyze_requirements", self._analyze_requirements)
        workflow.add_node("retrieve_size_knowledge", self._retrieve_size_knowledge)
        workflow.add_node("optimize_curve", self._optimize_curve)
        workflow.add_node("validate_curve", self._validate_curve)
        
        workflow.set_entry_point("analyze_requirements")
        workflow.add_edge("analyze_requirements", "retrieve_size_knowledge")
        workflow.add_edge("retrieve_size_knowledge", "optimize_curve")
        workflow.add_edge("optimize_curve", "validate_curve")
        workflow.add_conditional_edges(
            "validate_curve",
            self._should_refine,
            {
                "refine": "optimize_curve",
                "accept": END
            }
        )
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _analyze_requirements(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze size curve requirements"""
        input_data = state.get("input", {})
        
        analysis = {
            "product_category": input_data.get("product_category", "footwear"),
            "target_region": input_data.get("region", "global"),
            "historical_distribution": input_data.get("historical_sizes", {}),
            "demand_forecast": input_data.get("demand_forecast", {}),
            "special_requirements": input_data.get("special_requirements", [])
        }
        
        state["analysis"] = analysis
        logger.info(f"Analyzed size curve requirements for {analysis['target_region']}")
        return state
    
    def _retrieve_size_knowledge(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve size curve knowledge"""
        analysis = state.get("analysis", {})
        query = f"Size curve optimization for {analysis['product_category']} in {analysis['target_region']}"
        
        knowledge = self._get_relevant_knowledge(query)
        state["knowledge"] = knowledge
        return state
    
    def _optimize_curve(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize size distribution curve"""
        analysis = state.get("analysis", {})
        knowledge = state.get("knowledge", "")
        refinement = state.get("refinement_feedback", "")
        
        messages = [
            SystemMessage(content="""You are a size curve optimization expert for Adidas footwear.
            Optimize size distributions based on regional preferences and historical data."""),
            HumanMessage(content=f"""
            Knowledge Base:
            {knowledge}
            
            Requirements Analysis:
            {json.dumps(analysis, indent=2)}
            
            Refinement Feedback:
            {refinement}
            
            Provide optimized size curve including:
            1. Size distribution percentages for all sizes
            2. Regional adjustment factors
            3. Confidence levels for each size
            4. Recommendations for extreme sizes
            5. Buffer stock recommendations
            """)
        ]
        
        response = self.llm.invoke(messages)
        state["size_curve"] = response.content
        
        logger.info("Generated optimized size curve")
        return state
    
    def _validate_curve(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the size curve"""
        size_curve = state.get("size_curve", "")
        
        messages = [
            SystemMessage(content="Validate the size curve for practical feasibility and business constraints."),
            HumanMessage(content=f"Validate this size curve:\n{size_curve}\n\nProvide validation status and feedback.")
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
                "last_size_curve": final_state.get("size_curve"),
                "size_curve_analysis": final_state.get("analysis")
            })
            
            return {
                "size_curve": final_state.get("size_curve"),
                "analysis": final_state.get("analysis"),
                "validation": final_state.get("validation")
            }
            
        except Exception as e:
            logger.error(f"Error in size curve optimization: {str(e)}")
            return {"error": str(e)}