"""Demand Forecasting Agent for Adidas supply planning."""
import os
from typing import Dict, Any
from openai import OpenAI
from langsmith import traceable
from config import OPENAI_API_KEY, GEMINI_BASE_URL, LLM_MODEL, TEMPERATURE

# Initialize OpenAI-compatible client (pointed at Gemini)
client = OpenAI(api_key=OPENAI_API_KEY, base_url=GEMINI_BASE_URL)

@traceable(name="demand_forecast_agent", run_type="chain")
def demand_forecast_agent(query: str, context: str = None) -> Dict[str, Any]:
    """
    Demand Forecasting Agent - Analyzes and predicts product demand.
    
    Args:
        query: User query about demand forecasting
        context: Retrieved RAG context
    
    Returns:
        Dictionary with response and metadata
    """
    system_prompt = """You are Adidas's Demand Forecasting Expert. Your role is to:
    - Analyze historical sales data and market trends
    - Provide accurate demand predictions for products
    - Consider seasonal patterns, regional variations, and promotions
    - Recommend inventory levels based on forecasts
    - Highlight risks and opportunities in demand planning
    
    Use the provided context documents to inform your responses.
    Be specific with numbers and percentages when possible."""
    
    # Build the prompt with context
    user_prompt = f"""Context from Adidas documents:
    {context if context else 'No specific context provided.'}
    
    User Question: {query}
    
    Please provide a detailed demand forecast analysis."""
    
    # Call OpenAI with tracing
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return {
        "agent": "demand_forecast",
        "response": response.choices[0].message.content,
        "usage": response.usage.model_dump() if response.usage else None
    }

if __name__ == "__main__":
    # Test the agent independently
    print("Testing Demand Forecasting Agent...")
    
    test_query = "What should be the demand forecast for Ultraboost running shoes in Q4?"
    test_context = """Adidas Demand Forecasting Guidelines:
    - Q4 has 30% higher demand due to holiday season
    - Running shoes typically see 15% growth year-over-year
    - Ultraboost is a premium product with 25% market share in performance running"""
    
    result = demand_forecast_agent(test_query, test_context)
    
    print(f"\nQuery: {test_query}")
    print(f"\nResponse: {result['response']}")
    print(f"\nToken Usage: {result['usage']}")