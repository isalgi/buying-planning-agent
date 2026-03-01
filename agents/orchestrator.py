from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from .demand_forecast_agent import DemandForecastAgent
from .size_curve_agent import SizeCurveAgent
from .price_optimization_agent import PriceOptimizationAgent
from memory.session_manager import ContextStore
from rag.retriever import RAGRetriever
from config.logging_config import get_logger

logger = get_logger(__name__)

class AgentOrchestrator:
    def __init__(self, context_store: ContextStore, retriever: RAGRetriever):
        self.context_store = context_store
        self.retriever = retriever
        
        # Initialize agents
        self.demand_agent = DemandForecastAgent(context_store, retriever)
        self.size_agent = SizeCurveAgent(context_store, retriever)
        self.price_agent = PriceOptimizationAgent(context_store, retriever)
        
        # Create orchestration graph
        self.graph = self._create_orchestration_graph()
        
    def _create_orchestration_graph(self) -> StateGraph:
        """Create the main orchestration workflow"""
        workflow = StateGraph(Dict)
        
        # Add nodes for each agent
        workflow.add_node("demand_forecast", self._run_demand_forecast)
        workflow.add_node("size_curve", self._run_size_curve)
        workflow.add_node("price_optimization", self._run_price_optimization)
        workflow.add_node("integrate_results", self._integrate_results)
        workflow.add_node("generate_report", self._generate_report)
        
        # Define the workflow edges based on requirements
        workflow.set_entry_point("demand_forecast")
        workflow.add_edge("demand_forecast", "size_curve")
        workflow.add_edge("size_curve", "price_optimization")
        workflow.add_edge("price_optimization", "integrate_results")
        workflow.add_edge("integrate_results", "generate_report")
        workflow.add_edge("generate_report", END)
        
        # Add conditional branching based on user needs
        workflow.add_conditional_edges(
            "demand_forecast",
            self._check_if_size_needed,
            {
                "yes": "size_curve",
                "no": "price_optimization"
            }
        )
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _run_demand_forecast(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run demand forecasting agent"""
        session_id = state.get("session_id")
        input_data = state.get("input", {})
        
        logger.info(f"Running demand forecast for session {session_id}")
        
        # Extract demand-specific inputs
        demand_input = {
            "product_type": input_data.get("product_type"),
            "region": input_data.get("region"),
            "time_period": input_data.get("forecast_period", "next_quarter"),
            "historical_data": input_data.get("historical_sales", {}),
            "market_trends": input_data.get("market_trends", [])
        }
        
        result = self.demand_agent.process(session_id, demand_input)
        state["demand_forecast_result"] = result
        
        return state
    
    def _run_size_curve(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run size curve optimization agent"""
        session_id = state.get("session_id")
        input_data = state.get("input", {})
        demand_result = state.get("demand_forecast_result", {})
        
        logger.info(f"Running size curve optimization for session {session_id}")
        
        # Extract size curve inputs, incorporating demand forecast
        size_input = {
            "product_category": input_data.get("product_type"),
            "region": input_data.get("region"),
            "historical_sizes": input_data.get("historical_size_distribution", {}),
            "demand_forecast": demand_result.get("forecast", {}),
            "special_requirements": input_data.get("size_requirements", [])
        }
        
        result = self.size_agent.process(session_id, size_input)
        state["size_curve_result"] = result
        
        return state
    
    def _run_price_optimization(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run price optimization agent"""
        session_id = state.get("session_id")
        input_data = state.get("input", {})
        demand_result = state.get("demand_forecast_result", {})
        size_result = state.get("size_curve_result", {})
        
        logger.info(f"Running price optimization for session {session_id}")
        
        # Extract pricing inputs, incorporating results from other agents
        price_input = {
            "product": {
                "name": input_data.get("product_name"),
                "type": input_data.get("product_type"),
                "cost": input_data.get("product_cost")
            },
            "competitor_prices": input_data.get("competitor_pricing", {}),
            "market_segment": input_data.get("market_segment"),
            "lifecycle_stage": input_data.get("product_lifecycle"),
            "costs": input_data.get("cost_structure", {}),
            "elasticity": input_data.get("price_elasticity", 1.5),
            "demand_forecast": demand_result.get("forecast"),
            "size_distribution": size_result.get("size_curve")
        }
        
        result = self.price_agent.process(session_id, price_input)
        state["price_optimization_result"] = result
        
        return state
    
    def _integrate_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate results from all agents"""
        logger.info("Integrating results from all agents")
        
        integration = {
            "demand_forecast": state.get("demand_forecast_result", {}),
            "size_curve": state.get("size_curve_result", {}),
            "price_optimization": state.get("price_optimization_result", {})
        }
        
        # Use LLM to synthesize integrated recommendations
        messages = [
            SystemMessage(content="You are a supply chain integration expert. Synthesize the outputs from demand forecasting, size curve optimization, and price optimization into a coherent supply plan."),
            HumanMessage(content=f"""
            Integrate these results into a cohesive supply plan:
            
            Demand Forecast: {json.dumps(integration['demand_forecast'], indent=2)}
            
            Size Curve: {json.dumps(integration['size_curve'], indent=2)}
            
            Price Optimization: {json.dumps(integration['price_optimization'], indent=2)}
            
            Provide:
            1. Overall supply plan summary
            2. Key synergies and trade-offs
            3. Recommendations for production planning
            4. Inventory positioning strategy
            5. Risk mitigation measures
            """)
        ]
        
        response = self.price_agent.llm.invoke(messages)  # Reusing price agent's LLM
        state["integrated_plan"] = response.content
        
        return state
    
    def _generate_report(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final report"""
        logger.info("Generating final supply planning report")
        
        report = {
            "executive_summary": self._generate_executive_summary(state),
            "detailed_findings": {
                "demand_forecast": state.get("demand_forecast_result", {}),
                "size_curve": state.get("size_curve_result", {}),
                "price_optimization": state.get("price_optimization_result", {})
            },
            "integrated_plan": state.get("integrated_plan"),
            "recommendations": self._extract_recommendations(state),
            "risk_assessment": self._assess_risks(state),
            "next_steps": self._define_next_steps(state)
        }
        
        state["final_report"] = report
        
        # Store in session context
        session_id = state.get("session_id")
        if session_id:
            self.context_store.set_context(session_id, "last_report", report)
        
        return state
    
    def _check_if_size_needed(self, state: Dict[str, Any]) -> str:
        """Check if size curve optimization is needed"""
        input_data = state.get("input", {})
        product_type = input_data.get("product_type", "").lower()
        
        # Size curve is more relevant for footwear and apparel
        if "footwear" in product_type or "apparel" in product_type or "clothing" in product_type:
            return "yes"
        return "no"
    
    def _generate_executive_summary(self, state: Dict[str, Any]) -> str:
        """Generate executive summary"""
        messages = [
            SystemMessage(content="Create a concise executive summary of the supply plan."),
            HumanMessage(content=f"Based on the integrated plan: {state.get('integrated_plan', '')}\n\nProvide a 3-paragraph executive summary.")
        ]
        
        response = self.price_agent.llm.invoke(messages)
        return response.content
    
    def _extract_recommendations(self, state: Dict[str, Any]) -> list:
        """Extract key recommendations"""
        messages = [
            SystemMessage(content="Extract the top 5 key recommendations from the supply plan."),
            HumanMessage(content=f"From this plan: {state.get('integrated_plan', '')}\n\nList the top 5 actionable recommendations.")
        ]
        
        response = self.price_agent.llm.invoke(messages)
        return response.content.split("\n")
    
    def _assess_risks(self, state: Dict[str, Any]) -> dict:
        """Assess risks in the supply plan"""
        messages = [
            SystemMessage(content="Identify and assess risks in the supply plan."),
            HumanMessage(content=f"Analyze risks in: {state.get('integrated_plan', '')}\n\nProvide risk assessment with mitigation strategies.")
        ]
        
        response = self.price_agent.llm.invoke(messages)
        return {"risk_assessment": response.content}
    
    def _define_next_steps(self, state: Dict[str, Any]) -> list:
        """Define next steps"""
        messages = [
            SystemMessage(content="Define the next steps for implementing this supply plan."),
            HumanMessage(content=f"Based on: {state.get('integrated_plan', '')}\n\nList the immediate next steps with timeline.")
        ]
        
        response = self.price_agent.llm.invoke(messages)
        return response.content.split("\n")
    
    def process_request(self, session_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a complete supply planning request"""
        try:
            logger.info(f"Processing supply planning request for session {session_id}")
            
            # Initialize state
            initial_state = {
                "session_id": session_id,
                "input": input_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Run the orchestration graph
            final_state = self.graph.invoke(initial_state)
            
            return {
                "success": True,
                "session_id": session_id,
                "report": final_state.get("final_report", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing supply planning request: {str(e)}")
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }