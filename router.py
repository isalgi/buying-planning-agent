"""Router module for classifying user intent in supply planning queries."""
import os
from typing import Dict, Any
from openai import OpenAI
from langsmith import traceable
from config import OPENAI_API_KEY, LLM_MODEL, TEMPERATURE

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

@traceable(name="router_classification", run_type="chain")
def classify_intent(query: str) -> Dict[str, Any]:
    """
    Classify user query into one of the supply planning categories.
    
    Args:
        query: User's question
    
    Returns:
        Dictionary with classification result and confidence
    """
    system_prompt = """You are an intent classifier for Adidas Supply Planning System.
    Classify the user's query into one of these categories:
    
    1. demand_forecast - Questions about predicting future product demand, sales forecasts, inventory planning
    2. size_curve - Questions about size distribution, size optimization, regional size preferences
    3. price_optimization - Questions about pricing strategy, discounts, margins, promotions
    4. general - General questions not specific to the above categories
    
    Respond with JSON format: {"category": "category_name", "confidence": 0.0-1.0, "reasoning": "brief explanation"}
    """
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.3,  # Lower temperature for classification
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    
    import json
    try:
        result = json.loads(response.choices[0].message.content)
    except:
        result = {
            "category": "general",
            "confidence": 0.5,
            "reasoning": "Failed to parse response"
        }
    
    # Add usage info
    result["usage"] = response.usage.model_dump() if response.usage else None
    
    return result

@traceable(name="router_decision", run_type="chain")
def route_query(query: str) -> str:
    """
    Route query to appropriate agent based on intent.
    
    Args:
        query: User's question
    
    Returns:
        Agent name to route to
    """
    classification = classify_intent(query)
    return classification.get("category", "general")

if __name__ == "__main__":
    # Test router functionality
    print("Testing Router Module...")
    
    test_queries = [
        "What will be the demand for running shoes next quarter?",
        "How should I allocate sizes for the European market?",
        "What price should I set for the new collection?",
        "Tell me about Adidas history"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        # Get classification
        classification = classify_intent(query)
        print(f"Classification: {classification}")
        
        # Get route
        route = route_query(query)
        print(f"Routed to: {route}")