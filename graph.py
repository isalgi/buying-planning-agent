"""LangGraph workflow for Adidas Supply Planning System."""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from langsmith import traceable
import json

# Import agents
from agents.demand_agent import demand_forecast_agent
from agents.size_curve_agent import size_curve_agent
from agents.price_agent import price_optimization_agent
from router import route_query, classify_intent
from rag import rag_system
from db import db_manager
from openai import OpenAI

client = OpenAI()

# Define state schema with conversation context
class AgentState(TypedDict):
    """State for the LangGraph agent workflow."""
    query: str
    session_id: str
    conversation_context: str
    intent: str
    intent_confidence: float
    intent_reasoning: str
    rag_context: str
    agent_response: str
    agent_used: str
    usage: Dict
    error: str

@traceable(name="inject_context", run_type="chain")
def inject_context_node(state: AgentState) -> AgentState:
    """Node to inject RAG context based on intent."""
    try:
        # Get relevant context - include conversation context if available
        query = state["query"]
        context = state.get("conversation_context", "")
        
        # Enhance RAG with conversation context if available
        enhanced_query = query
        if context:
            # Use the last user message from context to enhance the query
            context_lines = context.split('\n')
            if context_lines:
                last_user_msg = None
                for line in reversed(context_lines):
                    if line.startswith("User:"):
                        last_user_msg = line.replace("User:", "").strip()
                        break
                if last_user_msg:
                    enhanced_query = f"Previous question: {last_user_msg}\nCurrent question: {query}"
        
        # Get relevant context
        context = rag_system.get_context_string(enhanced_query)
        state["rag_context"] = context
    except Exception as e:
        state["rag_context"] = ""
        state["error"] = f"RAG error: {str(e)}"
    
    return state

@traceable(name="router_node", run_type="chain")
def router_node(state: AgentState) -> AgentState:
    """Node to classify intent and route to appropriate agent with conversation context."""
    try:
        query = state["query"]
        context = state.get("conversation_context", "")
        
        # Enhance intent classification with conversation context
        enhanced_query = query
        if context:
            # Add context to help with intent classification
            context_lines = context.split('\n')
            recent_exchanges = context_lines[-4:] if len(context_lines) > 4 else context_lines
            enhanced_query = f"""Previous conversation:
{chr(10).join(recent_exchanges)}

Current question: {query}"""
        
        classification = classify_intent(enhanced_query)
        state["intent"] = classification.get("category", "general")
        state["intent_confidence"] = classification.get("confidence", 0.0)
        state["intent_reasoning"] = classification.get("reasoning", "")
        state["usage"] = classification.get("usage")
    except Exception as e:
        state["intent"] = "general"
        state["error"] = f"Router error: {str(e)}"
    
    return state

@traceable(name="demand_agent_node", run_type="chain")
def demand_agent_node(state: AgentState) -> AgentState:
    """Node for demand forecasting agent with conversation context."""
    query = state["query"]
    rag_context = state["rag_context"]
    conversation_context = state.get("conversation_context", "")
    
    # Pass both RAG context and conversation context to agent
    enhanced_context = rag_context
    if conversation_context:
        enhanced_context = f"""Previous conversation context:
{conversation_context}

Relevant documentation:
{rag_context}"""
    
    result = demand_forecast_agent(query, enhanced_context)
    state["agent_response"] = result["response"]
    state["agent_used"] = result["agent"]
    state["usage"] = result["usage"]
    return state

@traceable(name="size_curve_agent_node", run_type="chain")
def size_curve_agent_node(state: AgentState) -> AgentState:
    """Node for size curve optimization agent with conversation context."""
    query = state["query"]
    rag_context = state["rag_context"]
    conversation_context = state.get("conversation_context", "")
    
    enhanced_context = rag_context
    if conversation_context:
        enhanced_context = f"""Previous conversation context:
{conversation_context}

Relevant documentation:
{rag_context}"""
    
    result = size_curve_agent(query, enhanced_context)
    state["agent_response"] = result["response"]
    state["agent_used"] = result["agent"]
    state["usage"] = result["usage"]
    return state

@traceable(name="price_agent_node", run_type="chain")
def price_agent_node(state: AgentState) -> AgentState:
    """Node for price optimization agent with conversation context."""
    query = state["query"]
    rag_context = state["rag_context"]
    conversation_context = state.get("conversation_context", "")
    
    enhanced_context = rag_context
    if conversation_context:
        enhanced_context = f"""Previous conversation context:
{conversation_context}

Relevant documentation:
{rag_context}"""
    
    result = price_optimization_agent(query, enhanced_context)
    state["agent_response"] = result["response"]
    state["agent_used"] = result["agent"]
    state["usage"] = result["usage"]
    return state

@traceable(name="general_agent_node", run_type="chain")
def general_agent_node(state: AgentState) -> AgentState:
    """Node for handling general queries with conversation context."""

    
    query = state["query"]
    context = state.get("conversation_context", "")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant for Adidas supply planning. Provide general information and guide users to specific agents for detailed queries."}
    ]
    
    # Add conversation context if available
    if context:
        messages.append({"role": "system", "content": f"Previous conversation:\n{context}"})
    
    messages.append({"role": "user", "content": query})
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages
    )
    
    state["agent_response"] = response.choices[0].message.content
    state["agent_used"] = "general"
    state["usage"] = response.usage.model_dump() if response.usage else None
    return state

@traceable(name="save_to_db", run_type="chain")
def save_to_db_node(state: AgentState) -> AgentState:
    """Node to save conversation to database."""
    try:
        db_manager.save_conversation(
            session_id=state["session_id"],
            user_query=state["query"],
            assistant_response=state["agent_response"],
            agent_used=state["agent_used"],
            metadata={
                "intent": state["intent"],
                "confidence": state["intent_confidence"],
                "conversation_context": state.get("conversation_context", ""),  # Save context
                "usage": state["usage"]
            }
        )
    except Exception as e:
        state["error"] = f"Database error: {str(e)}"
    
    return state

def should_continue(state: AgentState) -> Literal["demand", "size_curve", "price", "general", END]:
    """Conditional edge to route to appropriate agent."""
    if state.get("error"):
        return END
    
    intent = state.get("intent", "general")
    
    if intent == "demand_forecast":
        return "demand"
    elif intent == "size_curve":
        return "size_curve"
    elif intent == "price_optimization":
        return "price"
    else:
        return "general"

# Build the graph
def build_supply_planning_graph():
    """Build and compile the LangGraph workflow."""
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("inject_context", inject_context_node)
    workflow.add_node("demand", demand_agent_node)
    workflow.add_node("size_curve", size_curve_agent_node)
    workflow.add_node("price", price_agent_node)
    workflow.add_node("general", general_agent_node)
    workflow.add_node("save_db", save_to_db_node)
    
    # Add edges
    workflow.set_entry_point("router")
    workflow.add_edge("router", "inject_context")
    
    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "inject_context",
        should_continue,
        {
            "demand": "demand",
            "size_curve": "size_curve",
            "price": "price",
            "general": "general"
        }
    )
    
    # Connect agents to database save
    workflow.add_edge("demand", "save_db")
    workflow.add_edge("size_curve", "save_db")
    workflow.add_edge("price", "save_db")
    workflow.add_edge("general", "save_db")
    workflow.add_edge("save_db", END)
    
    # Compile
    return workflow.compile()

# Create global graph instance
supply_planning_graph = build_supply_planning_graph()

if __name__ == "__main__":
    
    ascii_data = supply_planning_graph.get_graph().draw_ascii()
    print(ascii_data)

    # Test queries with context
    test_queries = [
        ("test_session_1", "What is the demand forecast for Ultraboost?"),
        ("test_session_1", "What about for running shoes?"),  # This should now have context
        ("test_session_2", "What size curve should I use for running shoes in Asia?"),
        ("test_session_3", "How should I price the new collection?")
    ]
    
    for session_id, query in test_queries:
        print(f"\nProcessing: {query}")
        print("-" * 50)
        
        # Initialize state with empty context first time
        initial_state = {
            "query": query,
            "session_id": session_id,
            "conversation_context": "",  # In real usage, this would come from UI
            "intent": "",
            "intent_confidence": 0.0,
            "intent_reasoning": "",
            "rag_context": "",
            "agent_response": "",
            "agent_used": "",
            "usage": {},
            "error": ""
        }
        
        # Run graph
        result = supply_planning_graph.invoke(initial_state)
        
        print(f"Intent: {result['intent']} (confidence: {result['intent_confidence']:.2f})")
        print(f"Agent Used: {result['agent_used']}")
        print(f"Response: {result['agent_response'][:100]}...")
        print(f"✓ Graph execution complete")